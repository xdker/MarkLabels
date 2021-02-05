from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from controller import Common

class PointSetting(QWidget):
    setting_change = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.config = Common.cfg
        self.style_list = Common.style_list
        self.setupUi()

    def setupUi(self):
        self.resize(705, 635)
        self.setWindowTitle("系统设置")
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(90, 50, 491, 441))
        self.groupBox.setTitle("系统设置")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(140, 280, 141, 41))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setText("确认")
        self.pushButton.clicked.connect(self.save_fn)
        self.horizontalLayout.addWidget(self.pushButton)
        self.cancel_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancel_btn.setText("取消")
        self.cancel_btn.clicked.connect(self.cancel_fn)
        self.horizontalLayout.addWidget(self.cancel_btn)
        self.gridLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 40, 400, 129))
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.point_size = QtWidgets.QLabel("点大小", self.gridLayoutWidget)
        self.gridLayout.addWidget(self.point_size, 0, 0, 1, 1)
        self.number_size = QtWidgets.QLabel("编号大小", self.gridLayoutWidget)
        self.gridLayout.addWidget(self.number_size, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel("自动保存时间(s)", self.gridLayoutWidget)
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel("主题配色", self.gridLayoutWidget)
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.point_size_spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.point_size_spinBox.setValue(Common.get_point_size())
        self.point_size_spinBox.setRange(3, 30)
        self.gridLayout.addWidget(self.point_size_spinBox, 0, 1, 1, 1)
        self.number_size_spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.number_size_spinBox.setValue(int(Common.get_number_size()))
        self.number_size_spinBox.setRange(3, 30)
        self.gridLayout.addWidget(self.number_size_spinBox, 1, 1, 1, 1)
        self.auto_save_spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.auto_save_spinBox.setValue(int(Common.get_auto_save()))
        self.auto_save_spinBox.setRange(30, 120)
        self.gridLayout.addWidget(self.auto_save_spinBox, 2, 1, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox.addItems(["default"] + self.style_list)
        self.comboBox.setCurrentText(self.config["setting"]["css_style"])
        self.gridLayout.addWidget(self.comboBox, 3, 1, 1, 1)

    def cancel_fn(self):
        self.close()

    def save_fn(self):
        self.config["setting"]["point_size"] = str(self.point_size_spinBox.value())
        self.config["setting"]["number_size"] = str(self.number_size_spinBox.value())
        self.config["setting"]["auto_save"] = str(self.auto_save_spinBox.value())
        self.config["setting"]["css_style"] = self.comboBox.currentText()
        self.setting_change.emit()
        self.close()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from qss import CommonHelper
    cfg = {"point_size": 10, "number_size": 10, "auto_save": 60, "css_style": "default"}
    app = QApplication(sys.argv)
    w = PointSetting(cfg,CommonHelper().style_list)
    w.show()
    sys.exit(app.exec_())
