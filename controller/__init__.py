import configparser
import traceback
from PyQt5.QtCore import QFile, QTextStream
import os

from PyQt5.QtWidgets import QApplication

from qss.resources import *
import logging


class CommonHelper:
    """
    配置界面所有设置
    """

    def __init__(self):
        self.style_list = ['AMOLED', 'Aqua', 'black', 'blue', 'material', 'darkblack', 'darkblue', 'darkgray',
                           'darkorange', 'deepblue', 'ElegantDark', 'flatblack', 'flatwhite', 'gray', 'lightblack',
                           'lightblue', 'lightgray', 'MacOS', 'ManjaroMix', 'materialdark', 'NeonButtons', 'psblack',
                           'silvery', 'Ubuntu']
        self.CACHE_DIR = "./cache"
        self.CONFIG_PATH = "./cache/config.ini"
        self.LOG_PATH = "./cache/run.log"
        self.UPLOAD_URL = "http://songbook.ushow.media:91/face_annotation/face-annotation/upload-one"
        self.REQUEST_URL = "http://songbook.ushow.media:91/face_annotation/face-annotation/request-one"
        self.DOWNLOAD_DIRECTORY = "./dataset"
        self.ANNOTATION_DIRECTORY = "./annotation"
        self.DOC_DIR = "./docs"
        self.dateset_list = ["default", "wider", "matting"]
        self.current_dateset = "default"
        self.cfg = configparser.ConfigParser()
        self.screen_height = 0
        self.screen_width = 0
        self.point_size = 8
        self.number_size = 10
        self.windows_size = (1920, 1080)
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        logging.basicConfig(level=logging.INFO,
                            filename=self.LOG_PATH,
                            filemode='a',
                            format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(name=__name__)
        os.makedirs(self.DOWNLOAD_DIRECTORY, exist_ok=True)
        os.makedirs(self.ANNOTATION_DIRECTORY, exist_ok=True)
        os.makedirs(self.DOC_DIR, exist_ok=True)
        if os.path.exists(self.CONFIG_PATH):
            self.cfg.read(self.CONFIG_PATH)
            self.logger.info("读取配置文件成功")
        else:
            # ini文件模板
            self.cfg.add_section("user_info")
            self.cfg.set('user_info', 'user_name', "unknow")
            self.cfg.set('user_info', 'passwd', "unknow")
            self.cfg.add_section("setting")
            self.cfg.set('setting', 'dataset_name', "default")
            self.cfg.set('setting', 'point_size', "auto")
            self.cfg.set('setting', 'number_size', "auto")
            self.cfg.set('setting', 'auto_save', "60")
            self.cfg.set('setting', 'css_style', "default")

    def get_point_size(self):
        if self.cfg["setting"]["point_size"] == "auto":
            self.point_size = Common.screen_width // 110
        else:
            self.point_size = int(self.cfg["setting"]["point_size"])
        return self.point_size

    def get_auto_save(self):
        return int(self.cfg["setting"]["auto_save"])

    def save_config(self):
        with open(self.CONFIG_PATH, "w") as f:
            self.cfg.write(f)
        self.logger.info("保存配置文件成功")

    def get_number_size(self):
        if self.cfg["setting"]["number_size"] == "auto":
            self.number_size = int(Common.point_size * 1.1)
        else:
            self.number_size = int(self.cfg["setting"]["number_size"])
        return self.number_size

    def get_style(self):
        try:
            style_sheet = self.cfg["setting"]["css_style"]
            f = QFile(":/qss/%s.qss" % style_sheet)
            f.open(QFile.ReadOnly | QFile.Text)
            ts = QTextStream(f)
            stylesheet = ts.readAll()
        except ImportError as e:
            print("Style sheet not available. Use available_styles() to check for valid styles")
            return u""
        except Exception as e:
            print("Style sheet available, but an error occured...")
            traceback.print_exc()
            return u""
        return stylesheet


Common = CommonHelper()
