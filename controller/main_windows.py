import os
import time
from glob import glob
from os.path import join, basename, exists

import cv2
import numpy as np
from PyQt5 import sip
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPalette, QFont, QPixmap, QImage
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QFrame, QMessageBox, QVBoxLayout, QGridLayout, QComboBox, QApplication, QAction
)

from controller import Common
from controller.RewriteHandle import Splitter
from controller.Threads import UploadThread
from controller.base_widget import MyMainWidget
from controller.bubble_label import BubbleLabel
from controller.data_labels import Labels
from controller.doc_page import DocPage
from controller.key_points import KeyPointTable, KeypointsCluster
from controller.login import LoginWindow
from controller.menu import PointSetting
from controller.message_box import MyMessageBox, MySimpleMessageBox
from controller.picture import ImageController
from controller.slider import MySlide
from controller.utils import move2center
from tools.megvii import read_anno
from tools.transmission import DataManager


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("关键点标注工具")
        self.setWindowIcon(QIcon("pic/icon.ico"))
        self.cfg = Common.cfg
        self.MyStyleSheet = Common.get_style()
        self.save_dir = Common.ANNOTATION_DIRECTORY
        self.resize(*Common.windows_size)
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        Common.screen_height = self.screenRect.height()
        Common.screen_width = self.screenRect.width()
        move2center(self)
        menubar = self.menuBar()
        setting_menu = menubar.addMenu('&设置')
        setting = QAction('&系统设置', self)
        setting.triggered.connect(self.open_setting)
        setting_menu.addAction(setting)
        doc_menu = menubar.addMenu('&说明文档')
        mark_doc = QAction('&标注说明', self)
        mark_doc.triggered.connect(self.open_doc)
        mark_doc.setStatusTip('标注说明')
        doc_menu.addAction(mark_doc)
        self.timer = QTimer(self)
        # 将定时器超时信号与槽函数showTime()连接
        self.timer.timeout.connect(self._clicked_save_btn)
        self.timer.start(60000)
        timeArray = time.localtime(time.time())
        self.today = time.strftime("%Y-%m-%d", timeArray)
        self.today_cnt = 0
        self.current_speeds = []
        self.pic_start_time = time.time()
        self.current_dateset=Common.cfg["setting"]["dataset_name"]
        self.file = None
        self.login_win = LoginWindow(self)

    def open_setting(self):
        self.chile_win = PointSetting()
        self.chile_win.setting_change.connect(self.setting_change_fn)
        self.chile_win.show()

    def open_doc(self):
        self.chile_win = DocPage()
        self.chile_win.initUi(Common.DOC_DIR)
        self.chile_win.show()

    def setup_ui(self):
        self.manager = DataManager()
        # 中心布局
        self.splitter = Splitter(self)
        self.splitter.setHandleWidth(8)
        # ++++++++左布局+++++++++++
        self.left_widget = MyMainWidget(self)

        # self.sub_size = 1400
        self.toolbox_widget = QWidget(self.left_widget)
        self.toolbox_widget.setBaseSize(200, 300)
        self.toolbox = QVBoxLayout(self.toolbox_widget)
        # 抓手按钮
        self.hand_btn = QPushButton(self)
        self.hand_btn.setIcon(QIcon(QPixmap(QImage('pic/hand.png'))))
        # 框选按钮
        self.rectangle_btn = QPushButton(self)
        self.rectangle_btn.setIcon(QIcon(QPixmap(QImage('pic/rectangle.png'))))
        # 旋转按钮
        self.rotate_button = QPushButton(self.left_widget)
        self.rotate_button.setIcon(QIcon(QPixmap(QImage('pic/rotate.png'))))
        self.rotate_button.clicked.connect(self._clicked_rotate_btn)
        self.toolbox.addWidget(self.rotate_button)
        self.toolbox.addWidget(self.hand_btn)
        self.toolbox.addWidget(self.rectangle_btn)
        self.toolbox_widget.raise_()
        self.toolbox_widget.move(self.left_widget.width() - int(self.toolbox_widget.width() * 1.5),
                                 self.left_widget.height() - int(self.toolbox_widget.height() * 1.5))

        self.left_widget.setWindowFlags(Qt.FramelessWindowHint)
        self.left_widget.setAutoFillBackground(True)

        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.black)
        self.left_widget.setPalette(palette)
        self.left_widget.move(0, 0)
        self.left_widget.myresize.connect(self._resize_my_ele)
        self.splitter.addWidget(self.left_widget)

        # ++++++++++++++++++中间布局+++++++++++++++++++++
        self.mid_widget = MyMainWidget(self)

        self.right_hbox_widget = QWidget(self.mid_widget)
        self.hbox = QGridLayout(self.right_hbox_widget)
        self.right_hbox_widget.move(10, 10)
        self.save_btn = QPushButton("保存", self.mid_widget)
        self.save_btn.setShortcut("ctrl+s")
        font = QFont()
        font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(10)  # 括号里的数字可以设置成自己想要的字体大小
        self.save_btn.setFont(font)
        self.save_btn.clicked.connect(self._clicked_save_btn)

        self.hbox.addWidget(self.save_btn, 0, 0)

        self.show_number = QPushButton("显示编号", self.mid_widget)
        self.show_number.setFont(font)
        self.show_number.setShortcut('Q')
        self.show_number.clicked.connect(self._clicked_show_btn)
        self.hbox.addWidget(self.show_number, 0, 1)
        # self.show_number.setEnabled(True)

        self.view_button = QPushButton("查看全貌", self.mid_widget)
        self.view_button.setShortcut("V")
        self.view_button.setFont(font)
        self.view_button.clicked.connect(self._clicked_view_btn)
        self.hbox.addWidget(self.view_button, 0, 2)
        self.example_btn = QPushButton("标注样例", self.mid_widget)
        self.example_btn.setFont(font)
        self.example_btn.clicked.connect(self._show_example)
        self.hbox.addWidget(self.example_btn, 0, 3)

        self.before_button = QPushButton("上一个", self.mid_widget)
        self.before_button.setShortcut('A')
        self.before_button.setFont(font)
        self.before_button.clicked.connect(self.check_before)
        self.before_button.show()
        self.hbox.addWidget(self.before_button, 1, 0)

        self.next_button = QPushButton("下一个", self.mid_widget)
        self.next_button.setShortcut('D')
        self.next_button.setFont(font)
        self.next_button.clicked.connect(self.check_next)
        self.hbox.addWidget(self.next_button, 1, 1)

        self.upload_button = QPushButton("上传", self.mid_widget)
        self.upload_button.setShortcut('Ctrl+W')
        self.upload_button.setFont(font)
        self.upload_button.clicked.connect(self.check_upload)
        self.hbox.addWidget(self.upload_button, 1, 2)

        self.jump_button = QPushButton("跳过", self.mid_widget)
        self.jump_button.setShortcut('J')
        self.jump_button.setFont(font)
        self.jump_button.clicked.connect(self.jump_upload)
        self.hbox.addWidget(self.jump_button, 1, 3)

        self.dataset_change_box = QComboBox(self.mid_widget)
        self.dataset_change_box.addItems(['切换图片数据库'] + Common.dateset_list)
        self.dataset_change_box.setCurrentText(self.current_dateset)
        self.dataset_change_box.currentIndexChanged[str].connect(self.change_dataset_fn)
        self.hbox.addWidget(self.dataset_change_box, 2, 0)
        self.label_widget = QWidget(self.mid_widget)
        # self.label_widget.setStyleSheet("border:5px solid red;")
        self.label_widget.setGeometry(10, self.right_hbox_widget.height() + Common.screen_height // 80,
                                      self.mid_widget.width(), self.mid_widget.height())
        # 列表标签

        self.splitter.addWidget(self.mid_widget)
        # 属性标签
        self.right_widget = MyMainWidget(self)

        self.face_label = Labels(self.right_widget)

        self.splitter.addWidget(self.right_widget)
        # 滚动条
        self.adjust_bright_slide = MySlide(self.left_widget)
        self.adjust_size = 60
        self.adjust_bright_slide.resize(int(self.left_widget.width() * 0.7), self.adjust_size)
        self.adjust_bright_slide.move(int(self.left_widget.width() * 0.15),
                                      self.left_widget.height() - self.adjust_size - 10)
        self.adjust_bright_slide.bound_brightness(self._adjust_brightness)

        self.splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        self.next_message = MyMessageBox("还没保存，确定下一个？", self.next)
        self.before_message = MyMessageBox("还没保存，确定上一个？", self.before)
        self.upload_message = MyMessageBox("还没保存任何数据或存在未查看数据，确定上传？", self.upload)
        self.upload_status_message = MySimpleMessageBox("还没保存任何数据，确定上传？")

        self.can_check = True
        self.face_idx = 0
        self.clean_history()
        self.setStyleSheet(self.MyStyleSheet)

    def _show_example(self):
        im = cv2.imread("pic/example.png")
        cv2.imshow("example", im)

    # 清理历史数据
    def clean_history(self):
        if os.path.exists(Common.ANNOTATION_DIRECTORY):
            for file in glob(Common.ANNOTATION_DIRECTORY+"/*"):
                if (time.time() - os.stat(file).st_mtime) / (60 * 60 * 24) > 3:
                    os.remove(file)
        if os.path.exists(Common.DOWNLOAD_DIRECTORY):
            for file in glob(Common.DOWNLOAD_DIRECTORY+"/*"):
                if (time.time() - os.stat(file).st_mtime) / (60 * 60 * 24) > 3:
                    os.remove(file)
        if os.path.exists(Common.CACHE_DIR):
            for file in glob(Common.CACHE_DIR+"/*"):
                if (time.time() - os.stat(file).st_mtime) / (60 * 60 * 24) > 3:
                    if file.endswith(".log") or file.endswith(".html"):
                        os.remove(file)

    def change_dataset_fn(self, i):
        if i in Common.dateset_list:
            self.bubbleMsgShow("正在切换数据库：{}".format(i))
            self.current_dateset = i
            self.run()
            self.bubbleMsgShow("{}切换成功".format(i))
            Common.cfg["setting"]["dataset_name"]=i
            Common.save_config()
            self.mid_widget.myresize.emit()
            self.right_widget.myresize.emit()

    def setting_change_fn(self):
        self.pt_change()
        self.style_change()
        self.timer.stop()
        self.timer = QTimer(self)
        # 将定时器超时信号与槽函数showTime()连接
        self.timer.timeout.connect(self._clicked_save_btn)
        self.timer.start(int(Common.cfg["setting"]["auto_save"])*1000)
        Common.save_config()

    def pt_change(self):
        for pt in self.kp_cluster.pts:
            pt.change_size()

    def style_change(self):
        self.setStyleSheet(Common.get_style())
        self.repaint()

    def _resize_my_ele(self):
        self.adjust_bright_slide.resize(int(self.left_widget.width() * 0.7), self.adjust_size)
        self.adjust_bright_slide.move(int(self.left_widget.width() * 0.15),
                                      self.left_widget.height() - self.adjust_size - 10)
        self.toolbox_widget.move(self.left_widget.width() - int(self.toolbox_widget.width() * 1.5),
                                 self.left_widget.height() - int(self.toolbox_widget.height() * 1.5))

        self.label_widget.setGeometry(10, self.right_hbox_widget.height() + Common.screen_height // 80,
                                      self.mid_widget.width(), self.mid_widget.height())

    def resizeEvent(self, e):
        # 给左边的布局发送缩放信号
        self.left_widget.myresize.emit()
        # 给中间的布局发送缩放信号
        self.mid_widget.myresize.emit()

    def _get_manager(self):
        self.manager = DataManager()

    def mouseDoubleClickEvent(self, event):
        self.grabKeyboard()

    def run(self):
        if not self.can_check:
            self._clicked_view_btn()

        if self.face_idx == 0:
            status, self.file, anno, self.face_num, self.total_face_num = self.manager.download_data(
                self.current_dateset)
            if not status:
                # self.bubbleMsgShow("图片下载失败，请检查网络",500,500)
                MySimpleMessageBox("图片下载失败，请检查网络").show()
                return status
            anno = read_anno(anno)
            cnt = 0
            for i in glob(os.path.dirname(self.file) + "/*.json"):
                if time.strftime('%Y-%m-%d', time.localtime(os.stat(i).st_mtime)) == self.today:
                    cnt += 1
            self.today_cnt = cnt
            filename = self.file.split(".")[0]
            self.landmark_list = []
            self.attr_list = []
            for face_idx, single_face in enumerate(anno):
                if os.path.exists(
                        join("{}/{}_{:02d}.pts".format("annotation", basename(self.file).rsplit(".")[0], face_idx))):
                    with open(
                            join("{}/{}_{:02d}.pts".format("annotation", basename(self.file).rsplit(".")[0], face_idx)),
                            "r", encoding="utf8") as af:
                        anno_history = [i.replace("\n", "") for i in af.readlines()[2:]]
                        single_face["landmark"] = list(
                            np.array(anno_history[0].split(" "), dtype=float).reshape(-1, 4)[:, :2].reshape(-1))
                        single_face["attributes"]["age"] = anno_history[1][5:]
                        single_face["attributes"]["race"] = anno_history[2].split(",")[-1].strip()
                        single_face["attributes"]["gender"] = anno_history[3].split(",")[-1].strip()
                        single_face["attributes"]["expression"] = anno_history[4].split(",")[-1].strip()
                landmark = single_face["landmark"]
                self.landmark_list.append(np.array(landmark, dtype=float).reshape(-1, 2))
                landmark_tmp = np.array(landmark, dtype=float).reshape(-1, 2)
                landmark_tmp = np.hstack((landmark_tmp, np.ones_like(landmark_tmp)))
                f = open(filename + "_" + str(face_idx).zfill(2) + "_origin.pts", "w")
                f.write(self.file + "\n" + "1" + "\n")
                f.write(" ".join(["%.6f %.6f %d %d" % (i[0], i[1], i[2], i[3]) for i in landmark_tmp]) + "\n")
                f.write("age, " + single_face["attributes"].get("age", "未标") + "\n")
                f.write("race, " + single_face["attributes"].get("race", "未标") + "\n")
                f.write("gender, " + single_face["attributes"].get("gender", "未标") + "\n")
                f.write("expression, " + single_face["attributes"].get("expression", "未标") + "\n")
                f.close()
                self.attr_list.append(single_face["attributes"])
        if hasattr(self, "image_label") and self.image_label is not None:
            self._delete_controller(self.image_label)
            # self._delete_controller(self.face_label)
            self.face_label.reset_cbox()
            self._delete_controller(self.kp_cluster)
            # self._delete_controller(self.kp_cluster)
            self.left_widget.repaint()
        self.image_label = ImageController(self.file, self.left_widget)
        self.hand_btn.clicked.connect(self.image_label.set_drag)
        self.rectangle_btn.clicked.connect(self.image_label.set_marquee)
        self.image_label.show()
        self.image_label.move(0, 0)
        self.image_label.setFrameShape(QFrame.NoFrame)

        w, h = self.image_label.image_size()
        self.kp_cluster = KeypointsCluster(self.landmark_list[self.face_idx], self.image_label, w, h)
        self.image_label.bind_keypoints_move(self.kp_cluster.scale_loc)
        self.image_label.bind_show(self.update_message_status)
        self.kp_tabel = KeyPointTable(self.kp_cluster, self.label_widget)
        # self.kp_tabel.kp_tabel.setStyleSheet("border:5px solid blue;")
        self.mid_widget.myresize.connect(self.kp_tabel.kp_resize)
        self.right_widget.myresize.connect(self.kp_tabel.kp_resize)

        # self.face_label = Labels(self.right_widget)
        # 设置属性标注多选框的checkbox
        for name, value in self.attr_list[self.face_idx].items():
            self.face_label.set_label(name, value)
        # 开始统计标注起始时间
        self.pic_start_time = time.time()
        # 设置消息栏
        self.status = self.statusBar()
        self.status.showMessage("{}, {}x{}, ratio={}, {}/{}张".format(
            self.file, self.image_label.img.width(), self.image_label.img.height(), self.image_label.ratio,
            self.face_num, self.total_face_num
        ))
        self.mid_widget.myresize.emit()
        return status

    def check_next(self):
        anno = join("{}/{}_{:02d}.pts".format(self.save_dir, basename(self.file).rsplit(".")[0], self.face_idx))
        print(anno)
        if not exists(anno):
            self.next_message.show()
        else:
            self.next()

    def reset_anno(self, path):
        with open(path, "r", encoding="utf8") as f:
            anno = [i.replace("\n", "") for i in f.readlines()[2:]]

    def next(self):
        if self.face_idx < len(self.attr_list) - 1:
            self.face_idx += 1
            self.run()

    def _save_keypoints(self):
        if self.file:
            anno = join("{}/{}_{:02d}.pts".format(self.save_dir, basename(self.file).rsplit(".")[0], self.face_idx))
            with open(anno, "w", encoding="utf8") as f:
                f.write("{}\n".format(self.file))
                results = self.kp_cluster.get_points_str()
                f.write("%d\n" % len(results))
                for result in results:
                    f.write("%s\n" % result)
                results = self.face_label.get_labels()
                for name, value in results.items():
                    f.write("{}, {}\n".format(name, " ".join(value)))

    def check_upload(self):
        if time.time() - self.pic_start_time > 60:
            self._clicked_save_btn()
            anno = join("{}/{}_*.pts".format(self.save_dir, basename(self.file).rsplit(".")[0]))
            anno_files = glob(anno)
            if len(anno_files) == 0 or self.face_idx < len(self.landmark_list) - 1:
                print("wu")
                self.upload_message.show()
            else:
                self.upload()
        else:
            res = QMessageBox.question(self, '消息', '点击太快了，请确认是否标注完成', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    def jump_upload(self):
        if time.time() - self.pic_start_time > 60:
            anno = join("{}/{}_*.pts".format(self.save_dir, basename(self.file).rsplit(".")[0]))
            anno_files = glob(anno)
            for f in anno_files:
                os.remove(f)
            anno_files = []
            if len(anno_files) == 0 or self.face_idx < len(self.landmark_list) - 1:
                self.upload_message.show()
            else:
                self.upload()
        else:
            res = QMessageBox.question(self, '消息', '上传太快了，请确认是否标注完成', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    def upload(self):
        self.bubbleMsgShow("正在上传...", 300, 100)
        self.uploader_thread = UploadThread(self)
        self.uploader_thread.upload_status.connect(self.upload_receiver)
        self.uploader_thread.start()

    def upload_receiver(self, status):
        # 用于接收上传线程的结果
        self.statusBar().showMessage("上传成功" if status else "上传失败")
        if self.uploader_thread:
            # 结束线程
            self.uploader_thread.quit()
        if status:
            self.bubbleMsgShow("上传成功！")
            self.current_speeds.append((time.time() - self.pic_start_time) / 60)
            self.face_idx = 0
            self.run()
        else:
            self.bubbleMsgShow("上传失败")
        self.upload_button.setEnabled(True)
        return status

    def _clicked_save_btn(self):
        self._save_keypoints()
        now = int(time.time())
        timeArray = time.localtime(now)
        otherStyleTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
        tmp_speed = np.round(np.mean(0 if not self.current_speeds else self.current_speeds), 2)
        if tmp_speed < 5:
            word = "手速惊人啊！"
        elif tmp_speed < 7:
            word = "正常速度"
        else:
            word = "速度太慢了"
        self.bubbleMsgShow(
            "保存时间:{}\n今日完成:{}\n当前手速:{}\n{}".format(otherStyleTime, self.today_cnt, str(tmp_speed), word))
        self.statusBar().showMessage(
            "保存时间:{} 今日完成:{} 当前手速:{} {}".format(otherStyleTime, self.today_cnt, str(tmp_speed), word))

    def _clicked_show_btn(self):
        if "显示编号" == self.show_number.text():
            self.show_number.setText("隐藏编号")
            self.show_number.setShortcut('Q')
            self.kp_cluster.show_number(True)
        else:
            self.show_number.setText("显示编号")
            self.show_number.setShortcut('Q')
            self.kp_cluster.show_number(False)

    def _clicked_view_btn(self):
        if self.can_check:
            self.view_button.setText("关闭窗口")
            self.view_button.setShortcut("V")
            self.view_button.repaint()
            self.can_check = False
        else:
            cv2.destroyAllWindows()
            self.view_button.setText("查看全貌")
            self.view_button.setShortcut("V")
            self.view_button.repaint()
            self.can_check = True
            return
        image = cv2.imread(self.file)
        pts = self.kp_cluster.get_points_str()[0].split(" ")
        pts = np.array(pts).reshape(-1, 4).astype(float).astype(int)
        x1 = image.shape[1]
        y1 = image.shape[0]
        x2 = 0
        y2 = 0
        for pt in pts:
            x, y, v, c = pt
            if v == 0:
                cv2.circle(image, (round(x), round(y)), 1, (255, 0, 0), 1)
            else:
                cv2.circle(image, (round(x), round(y)), 1, (0, 255, 0), 1)
            x1 = min(x1, x)
            x2 = max(x2, x)
            y1 = min(y1, y)
            y2 = max(y2, y)
        w = x2 - x1
        h = y2 - y1
        expand_w = int(w * 0.1)
        expand_h = int(h * 0.1)
        x1 = max(x1 - expand_w, 0)
        y1 = max(y1 - expand_h, 0)
        x2 = min(x2 + expand_w, image.shape[1])
        y2 = min(y2 + expand_h, image.shape[0])
        image = image[y1:y2, x1: x2, :]
        cv2.namedWindow('check', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow("check", image)
        cv2.resizeWindow("check", 900, 900)
        cv2.waitKey()

    def _clicked_rotate_btn(self):
        self.image_label.rotate_image()
        self.kp_cluster.rotate90()

    def _adjust_brightness(self, v):
        self.image_label.adjust_brightness(v)

    def _clicked_withdraw_btn(self):
        self.kp_tabel.reset_point()

    def check_before(self):
        anno = join(
            "{}/{}_{:02d}.pts".format(self.save_dir, basename(self.file).rsplit(".")[0], self.face_idx))
        if not exists(anno):
            self.before_message.show()
        else:
            self.before()

    def before(self):
        self.face_idx -= 1
        if self.face_idx >= 0:
            self.run()
        else:
            self.face_idx = 0

    def update_message_status(self):
        self.status.showMessage("{}, {}x{}, ratio={:.1f}, {}/{}张".format(
            self.file, self.image_label.img.width(), self.image_label.img.height(), self.image_label.ratio,
            self.face_num, self.total_face_num
        ))

    def _delete_controller(self, controller):
        if isinstance(controller, QWidget):
            sip.delete(controller)
            controller = None
        else:
            for sub_con in dir(controller):
                if isinstance(sub_con, QWidget):
                    sip.delete(sub_con)
                    sub_con = None
            del controller

    def _load_had_anno(self, file):
        filename = basename(file).split(".")[0]
        anno_list = glob("annotation/{}*.pts".format(filename))

        with open(anno_list[0], encoding="utf8") as f:
            lines = f.readlines()
        pts = np.array(lines[2].split(" ")).reshape(-1, 4)
        return pts[:, :2].astype(np.float32), pts[:, 2:].astype(int)

    def closeEvent(self, QCloseEvent):
        res = QMessageBox.question(self, '消息', '是否关闭这个窗口？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

    # 气泡通知
    def bubbleMsgShow(self, msg, w=200, h=80):
        if hasattr(self, "_blabel"):
            self._blabel.stop()
            self._blabel.deleteLater()
            del self._blabel
        self._blabel = BubbleLabel()
        self._blabel.setText(msg)
        self._blabel.setMinimumWidth(w)
        self._blabel.setMinimumHeight(h)
        self._blabel.show()
