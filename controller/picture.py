import cv2
from PyQt5.QtWidgets import QLabel, QTableWidget, QPushButton, \
    QTableWidgetItem, QApplication, QHeaderView, QAbstractItemView, QPinchGesture, QMenu
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPalette, QKeySequence, QPixmap, QPainter, QImage, QPen, QCursor
from controller.utils import Rotator
from functools import partial
from PIL import ImageQt, ImageEnhance, Image
import numpy as np

MAX_SCALE = 20
MIN_SCALE = 1

PADDING = 100

LEFT_POINT = QPoint(0, 0)


class FloatPoints:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def multi(self, s):
        self.x *= s
        self.y *= s


class ImageController(QLabel):
    location = pyqtSignal(int, int, int, int)
    def __init__(self, image_path, parent):
        super().__init__(parent)
        self.resize(parent.width(), parent.height())
        parent.myresize.connect(self.my_resize)
        self.parent_ele = parent
        self.img = QPixmap(self.cvimg_to_qtimg(image_path))
        self.scaled_img = self.img.copy()
        self.point = LEFT_POINT
        self.left_point = LEFT_POINT
        self.right_point = QPoint(self.img.width(), self.img.height())
        self.global_shift = FloatPoints(LEFT_POINT.x(), LEFT_POINT.y())
        self.ratio = 1.0
        self.kp_move = None
        self.brightness_v = 0
        self.contrast_v = 0
        self.angle_v = 0
        self.mode = 'drag'
        self.marquee_flag = False
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        self.setCursor(Qt.OpenHandCursor)
        self.lower()
        self.pts = []
        # 创建QMenu
        self.contextMenu = QMenu(self)
        self.actionA = self.contextMenu.addAction(u'可见/不可见')
        # self.actionB = self.contextMenu.addAction(u'不可见')
        self.actionC = self.contextMenu.addAction(u'确定/不确定')
        self.actionA.triggered.connect(self.actionHandler)
        # self.actionB.triggered.connect(self.actionHandler)
        self.actionC.triggered.connect(self.actionHandler)
        self.selected_set = set()

    def actionHandler(self):
        if self.sender().text() == "可见/不可见":
            for kp in self.selected_set:
                kp.visiable_click.emit()
                kp.set_important_point(False)
        if self.sender().text() == "确定/不确定":
            for kp in self.selected_set:
                kp.mid_click.emit()
                kp.set_important_point(False)
        self.selected_set = set()

    def cvimg_to_qtimg(self, cvimg):
        cvimg = cv2.imread(cvimg)
        height, width, depth = cvimg.shape
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        cvimg = QImage(cvimg.data, width, height, width * depth, QImage.Format_RGB888)
        return cvimg

    def my_resize(self):
        # 拖动中间分割缩放关键点
        self.resize(self.parent_ele.width(), self.parent_ele.height())
        self.global_shift = FloatPoints(0, 0)
        if self.kp_move is not None:
            self.kp_move(self.ratio, self.global_shift)
        self.repaint()

    # def set_drag(self):
    #     self.mode = 'drag'
    #     self.setCursor(Qt.OpenHandCursor)
    #     # 关闭右键
    #     self.setContextMenuPolicy(Qt.DefaultContextMenu)
    #     self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
    #     for i in self.pts:
    #         i.set_important_point(False)
    #     self.repaint()

    def set_marquee(self):
        self.mode = 'marquee'
        self.setCursor(Qt.CrossCursor)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        self.contextMenu.move(QCursor().pos())
        self.contextMenu.show()

    def image_size(self):
        return self.img.width(), self.img.height()

    def bind_show(self, update_show_status):
        self.update_show_status = update_show_status

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.begin(self)
        self.draw_img(painter)
        if self.mode == "marquee":
            rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
            # painter = QPainter()
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(rect)
        painter.end()

    def draw_img(self, painter):
        painter.drawPixmap(self.point, self.scaled_img)

    def resizeEvent(self, e):
        self.point = LEFT_POINT
        self.update()

    def mouseMoveEvent(self, e):  # 重写移动事件
        if self.mode == 'drag':
            if self.left_click:
                move_distance = e.pos() - self._startPos
                # move_distance += self.global_shift * self.ratio
                move_distance += QPoint(self.global_shift.x * self.ratio, self.global_shift.y * self.ratio)
                delta_x, delta_y = move_distance.x(), move_distance.y()
                delta_x = min(max(delta_x, self.width() - self.scaled_img.width() - PADDING), PADDING)
                delta_y = min(max(delta_y, self.height() - self.scaled_img.height() - PADDING), PADDING)
                move_distance.setX(delta_x)
                move_distance.setY(delta_y)
                # self.global_shift = move_distance / self.ratio
                self.global_shift = FloatPoints(move_distance.x() / self.ratio, move_distance.y() / self.ratio)
                self.point = LEFT_POINT + move_distance
                self.right_point = self.right_point + move_distance
                self._startPos = e.pos()
                if self.kp_move is not None:
                    self.kp_move(self.ratio, self.global_shift)
        else:
            self.x1 = e.x()
            self.y1 = e.y()
            for i in self.pts:
                if self.x0 < i.fact_x<i.fact_x+20< self.x1 and self.y0 < i.fact_y<i.fact_y+20 < self.y1:
                    i.set_important_point(True)
                    self.selected_set.add(i)
                else:
                    i.set_important_point(False)
                    if i in self.selected_set:
                        self.selected_set.remove(i)
            self.update()
        self.repaint()

    def mousePressEvent(self, e):
        # print(e.pos())
        if self.mode == 'drag':
            if e.button() == Qt.LeftButton:
                self.setCursor(Qt.ClosedHandCursor)
                self.left_click = True
            else:
                for pt in self.pts:
                    pt.set_label(True)
                    pt.repaint()
            self._startPos = e.pos()
        else:
            self.marquee_flag = True
            self.x0 = e.x()
            self.y0 = e.y()
            self.x1 = e.x()
            self.y1 = e.y()
            self.repaint()
            if e.button() == 1:
                for kp in self.selected_set:
                    kp.set_important_point(False)
                self.selected_set = set()

    def mouseReleaseEvent(self, e):
        if self.mode == 'drag':
            if e.button() == Qt.LeftButton:
                self.left_click = False
                self.setCursor(Qt.OpenHandCursor)
            else:
                for pt in self.pts:
                    pt.set_label(False)
                    pt.repaint()
        else:
            self.marquee_flag = False
            self.location.emit(self.x0, self.y0, self.x1, self.y1)

    def wheelEvent(self, e):
        cpoint = QPoint(e.x(), e.y())
        last_ratio = self.ratio
        if e.angleDelta().y() > 0:
            self.ratio = min(self.ratio + 1, MAX_SCALE)
        elif e.angleDelta().y() < 0:
            self.ratio = max(self.ratio - 1, MIN_SCALE)
        self.scaled_img = self._filter()
        self.point = cpoint - (cpoint - self.point) * self.ratio / last_ratio
        # self.global_shift = self.point / self.ratio
        self.global_shift = FloatPoints(self.point.x() / self.ratio, self.point.y() / self.ratio)
        delta_x = min(max(self.point.x(), self.width() - self.scaled_img.width()), 0)
        delta_y = min(max(self.point.y(), self.height() - self.scaled_img.height()), 0)
        self.point = QPoint(delta_x, delta_y)
        # self.global_shift = self.point / self.ratio
        self.global_shift = FloatPoints(self.point.x() / self.ratio, self.point.y() / self.ratio)
        self.right_point = QPoint(self.scaled_img.height(), self.scaled_img.width()) + self.point
        if self.kp_move is not None:
            self.kp_move(self.ratio, self.global_shift)
        self.update_show_status()
        self.repaint()

    def bind_keypoints_move(self, rescale_shift):
        self.kp_move = rescale_shift

    def adjust_brightness(self, value):
        self.brightness_v = value
        self.scaled_img = self._filter()
        self.repaint()

    def adjust_contrast(self, value):
        self.contrast_v = value
        self.scaled_img = self._filter()
        self.repaint()

    def _filter(self):
        image = ImageQt.fromqpixmap(self.img)
        # image = ImageEnhance.Brightness(image)
        # image = image.enhance(self.brightness_v)
        v = int(self.brightness_v * 10)
        contrast_v = int(self.contrast_v)
        if v != 0 or contrast_v != 0:
            image = np.array(image, dtype=int)
            image += v
            image = (image * (1. + contrast_v / 10.)).astype(np.int)
            image = np.clip(image, 0, 255)
            image = Image.fromarray(np.uint8(image))
        if self.angle_v != 0:
            image = image.transpose(getattr(Image, "ROTATE_{}".format(self.angle_v)))
        scaled_img = ImageQt.toqpixmap(image)
        if self.angle_v == 90 or self.angle_v == 270:
            scaled_img = scaled_img.scaled(int(self.img.height() * self.ratio), int(self.img.width() * self.ratio))
        else:
            scaled_img = scaled_img.scaled(int(self.img.width() * self.ratio), int(self.img.height() * self.ratio))

        return scaled_img

    def rotate_image(self):
        """
        旋转之后，将上一个角度的平移量清零。
        """
        # self.global_shift = QPoint()
        self.global_shift = FloatPoints(0, 0)
        self.point = QPoint()
        self.angle_v = (self.angle_v + 90) % 360
        self.scaled_img = self._filter()
        self.repaint()
