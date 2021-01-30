from controller.main_windows import MainWindow
from PyQt5.QtWidgets import QApplication
from tools.transmission import ANNOTATION_DIRECTORY
import os
import cgitb
import sys
os.environ['QT_MAC_WANTS_LAYER'] = '1'  # 解决MAC big sur 无法打开的问题pyqt5.15.2无需设置
cgitb.enable(display=1, logdir='cache')

if __name__ == '__main__':
    app = QApplication([])
    main_win = MainWindow()
    main_win.set_out_dir(ANNOTATION_DIRECTORY)
    app.exec_()
