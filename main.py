from controller.main_windows import MainWindow, Common
from PyQt5.QtWidgets import QApplication
import os
import cgitb

import sys
sys.argv.append("-disable-web-security")
os.environ['QT_MAC_WANTS_LAYER'] = '1'  # 解决MAC big sur 无法打开的问题pyqt5.15.2无需设置
cgitb.enable(display=1, logdir=Common.CACHE_DIR)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    app.exec_()
