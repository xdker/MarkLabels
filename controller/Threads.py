from PyQt5.QtCore import QThread, pyqtSignal


class UploadThread(QThread):
    upload_status = pyqtSignal(bool)

    def __init__(self, main_ui):
        super(UploadThread, self).__init__()
        self.main_ui = main_ui

    def run(self):
        self.main_ui.upload_button.setEnabled(False)
        status = self.main_ui.manager.upload_data()
        self.upload_status.emit(status)