from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget
)


class MyMainWidget(QWidget):
    myresize = pyqtSignal()
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

    def resizeEvent(self,e):
        self.myresize.emit()

