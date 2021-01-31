import configparser
import json
import logging
import os
import zipfile
from glob import glob
from controller import Common
import requests

logging.basicConfig(level=logging.INFO,
                    filename=Common.LOG_PATH,
                    filemode='a',
                    format='%(asctime)s %(name)s]:[line:%(lineno)d]: %(message)s')
logger = logging.getLogger(name=__name__)



class Downloader:
    def __init__(self, name):
        self.post_data = {
            "user_name": name,
            "batch_name": "default"
        }

    def run(self):
        result = post_one(Common.REQUEST_URL, self.post_data)
        if result["err"] != "ok":
            logger.info("请求失败:", result["err"])
            return {"status": False, "image": None, "anno": None, "annotate_tot_num": None,
                    "annotate_user_num": None, "annotate_user_face_num": None,
                    "annotate_user_face_tot_num": None, "tot_num": None}
        if not os.path.exists(Common.DOWNLOAD_DIRECTORY):
            os.makedirs(Common.DOWNLOAD_DIRECTORY)

        image = os.path.join(Common.DOWNLOAD_DIRECTORY, result["img_name"])
        anno = os.path.join(Common.DOWNLOAD_DIRECTORY, "{}.json".format(result["img_name"].split(".")[0]))

        for i in range(5):
            if i != 0:
                logger.info("第%d次尝试下载...", i)
            logger.info("正在下载%s\n到%s" % (result["img_url"], image))
            status = self.download(result["img_url"], image)
            if not status:
                continue
            logger.info("正在下载%s" % result["face_annotation_url"])
            status = self.download(result["face_annotation_url"], anno)
            if status:
                break
        result = {
            "status": status,
            "image": image,
            "anno": anno,
            "annotate_tot_num": result["annotate_tot_num"],
            "annotate_user_num": result["annotate_user_num"],
            "annotate_user_face_num": result["annotate_user_face_num"],
            "annotate_user_face_tot_num": result["annotate_user_face_tot_num"],
            "tot_num": result["tot_num"]
        }
        return result

    def download(self, url, dst):
        try:
            if os.path.exists(dst):
                return True
            r = requests.get(url)
            with open(dst, 'wb') as f:
                f.write(r.content)
        except BaseException:
            logger.info("下载过程出了问题")
            return False
        return True


class Uploader:
    def __init__(self, name):
        self.post_data = {
            "user_name": name,
            "face_num": 1
        }

    def run(self, img_url, anno_url, face_num):
        # image_md5 = hashlib.md5(open(img_url, 'rb').read()).hexdigest()
        self.post_data["img_url"] = os.path.basename(img_url)
        self.post_data["face_num"] = face_num
        file = {'face_point': open(anno_url, "rb")}
        result = post_one(Common.UPLOAD_URL, self.post_data, files=file)
        return result


class DataManager:
    def __init__(self, name=None):
        if name is None:
            name = Common.cfg.get('user_info', 'user_name')
            password = Common.cfg.get('user_info', 'passwd')
        self.downloader = Downloader(name)
        self.uploader = Uploader(name)
        self.image = None
        self.anno = None

    def download_data(self, dataset_name=None):
        if dataset_name:
            self.downloader.post_data["batch_name"] = dataset_name
        result = self.downloader.run()
        if result["status"]:
            self.image = result["image"]
            self.anno = result["anno"]
        return result["status"],self.image, self.anno, result["annotate_user_face_num"], result["annotate_user_face_tot_num"]

    def upload_data(self):
        if self.image is not None and self.anno is not None:
            filename = os.path.basename(self.image).split(".")[0]
            anno_list = glob(os.path.join(Common.ANNOTATION_DIRECTORY, "{}*.pts".format(filename)))
            f = zipfile.ZipFile('upload_tmp_anno_data.zip', 'w', zipfile.ZIP_DEFLATED)
            for anno in anno_list:
                f.write(anno)
            f.close()
            result = self.uploader.run(self.image, "upload_tmp_anno_data.zip", len(anno_list))
            os.remove('upload_tmp_anno_data.zip')
            if result["err"] == "ok":
                return True
            else:
                logger.info(result["err"])
                return False
        else:
            return False


def post_one(url, post_data, files=None):
    try:
        req = requests.post(url, post_data, files=files)
    except:
        logger.info("post失败，可能是没网")
        return {"err": "ConnectionError"}
    txt = req.text
    try:
        txt = json.loads(txt)
    except:
        logger.info("请求发生错误:", txt)
        return {"err": txt}
    return txt


def test_request():
    post_data = {
        "user_name": "lixuesong"
    }
    return post_one(Common.REQUEST_URL, post_data)


def test_upload():
    img_url = "3c696038d77f2c13902351d008c2a60e.jpg"
    post_data = {
        "user_name": "lixuesong",
        "img_url": img_url,
        "face_num": 100
    }
    files = {'face_point': open("/Users/darkn/code/work/MarkLabels/tools/transmission.py", "rb")}
    r = post_one(Common.UPLOAD_URL, post_data, files=files)
    logger.info(r)


if __name__ == "__main__":
    logger.info(test_request())
