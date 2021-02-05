import logging
import logging
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QPushButton, \
    QLabel, QWidget, QApplication, QMessageBox

from controller import Common
from tools.transmission import Downloader

logging.basicConfig(level=logging.INFO,
                    filename=Common.LOG_PATH,
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger(name=__name__)


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.cfg = parent.cfg
        self.main_win = parent
        flag = self.check_login()
        if flag:
            logger.info("登录成功")
            self.main_win.setup_ui()
            self.main_win.show()
            self.main_win.run()
            self.close()
            return
        self.title_label = QLabel("登录", self)
        self.user_label = QLabel("用户名", self)
        self.password_label = QLabel("密码", self)
        self.user_txt = QLineEdit(self)
        self.password_txt = QLineEdit(self)
        self.password_txt.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("登录", self)
        self.setWindowTitle("登录")
        self.resize(600, 300)
        self.move(600, 400)
        self.title_label.move(130, 10)
        self.user_label.move(30, 60)
        self.user_txt.move(100, 60)
        self.password_label.move(30, 90)
        self.password_txt.move(100, 90)
        self.login_btn.move(130, 140)

        self.login_btn.clicked.connect(self._login_btn_clicked)
        self.show()
        self.main_win.hide()

    def check_login(self, user_name=None, password=None):
        if user_name is None:
            if os.path.exists(Common.CONFIG_PATH):

                self.cfg.read(Common.CONFIG_PATH)
            user_name = self.cfg.get('user_info', 'user_name')
            password = self.cfg.get('user_info', 'passwd')
            if user_name == "unknow" and password == "unknow":
                return False
        d = Downloader(user_name)
        if d.run()["status"]:
            return True
        else:
            return False

    def _login_btn_clicked(self):
        logger.debug("登录了")
        user_name, user_password = self.user_txt.text(), self.password_txt.text()
        logger.debug("用户{}\n密码{}".format(user_name, user_password))
        if self.check_login(user_name, user_password):
            QMessageBox.information(self, "登录消息", "登陆成功!")
            self.save_user_info(user_name, user_password)
            self.main_win.setup_ui()
            self.main_win.show()
            self.main_win.run()
            self.close()
        else:
            QMessageBox.information(self, "登录消息", "登录失败，用户名或密码错误!")

    def save_user_info(self, user_name, user_password):
        self.cfg.set('user_info', 'user_name', user_name)
        self.cfg.set('user_info', 'passwd', user_password)
        with open(Common.CONFIG_PATH, "w") as f:
            self.cfg.write(f)

    def keyPressEvent(self, event):
        # 如果按下xxx则xxx
        if event.key() == Qt.Key_Return:
            self._login_btn_clicked()


if __name__ == '__main__':
    app = QApplication([])
    window = LoginWindow(None)
    window.show()
    app.exec_()
