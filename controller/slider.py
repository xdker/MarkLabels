from PyQt5.Qt import QSlider, QLabel, QWidget, QHBoxLayout, Qt, QFont
from PyQt5 import QtGui
StyleSheet = """
QWidget {
    background: gray;
}

/*横向*/
QSlider:horizontal {
    min-height: 60px;
}
QSlider::groove:horizontal {
    height: 1px;
    background: white; 
}
QSlider::handle:horizontal {
    width: 30px;
    margin-top: -15px;
    margin-bottom: -15px;
    border-radius: 15px;
    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba(210, 210, 210, 255), stop:0.7 rgba(210, 210, 210, 100));
}
QSlider::handle:horizontal:hover {
    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba(255, 255, 255, 255), stop:0.7 rgba(255, 255, 255, 100));
}

/*竖向*/
QSlider:vertical {
    min-width: 60px;
}
QSlider::groove:vertical {
    width: 1px;
    background: white; 
}
QSlider::handle:vertical {
    height: 30px;
    margin-left: -15px;
    margin-right: -15px;
    border-radius: 15px;
    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba(210, 210, 210, 255), stop:0.7 rgba(210, 210, 210, 100));
}
QSlider::handle:vertical:hover {
    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba(255, 255, 255, 255), stop:0.7 rgba(255, 255, 255, 100));
}
"""
class Slider(QSlider):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent, *args,**kwargs)
        self.setup_UI()
        self.setMinimum(-10)
        self.setMaximum(10)
        self.action = None

    def setup_UI(self):
        self.label = QLabel('0', self)

        self.label.move(30, -1)
        self.label.adjustSize()
        self.label.show()
        self.setStyleSheet(StyleSheet)
        self.label.setText(str(self.value()))

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        super().mousePressEvent(ev)
        self.label.setText(str(self.value()))
        self.label.adjustSize()
        if self.action is not None:
            self.action(self.value())

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent):
        super().mouseMoveEvent(ev)
        self.label.setText(str(self.value()))
        self.label.adjustSize()
        if self.action is not None:
            self.action(self.value())

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent):
        super().mouseReleaseEvent(ev)


class MySlide(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.UI_test()

    def UI_test(self):
        self.label = QLabel("调节亮度")
        layout = QHBoxLayout()
        self.slider = Slider(Qt.Horizontal)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def bound_brightness(self, parent_action):
        self.slider.action = parent_action