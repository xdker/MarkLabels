import glob
import os

import markdown
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem


def md2html(filename):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']
    mdcontent = ""
    with open(filename, 'r', encoding='utf-8') as f:
        mdcontent = f.read()
    html = '''<html lang="zh-cn">
    <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type" />
    <link href="/static/default.qss" rel="stylesheet">
    <link href="/static/github.qss" rel="stylesheet" type="text/qss" />
    </head>
    <body>
    <div>
        %s
        </div>
    </body>
    </html>
    '''
    parser_md = markdown.markdown(mdcontent, extensions=exts)
    return html % parser_md


# 美化样式表
Stylesheet = """
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 120px;
    max-width: 200px;
    color: white;
    background: #06A0C5;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    background: rgb(52, 52, 52);
    border-left: 2px solid rgb(9, 187, 7);
}
/*鼠标悬停颜色*/
HistoryPanel::item:hover {
    background: rgb(52, 52, 52);
}

/*右侧的层叠窗口的背景颜色*/
QStackedWidget {
    background: rgb(30, 30, 30);
}
"""


class DocPage(QWidget):

    def __init__(self, *args, **kwargs):
        super(DocPage, self).__init__(*args, **kwargs)
        self.resize(1920, 1080)

        # 左右布局(左边一个QListWidget + 右边QStackedWidget)
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        # 左侧列表
        self.listWidget = QListWidget(self)
        layout.addWidget(self.listWidget)
        # 右侧层叠窗口
        self.stackedWidget = QStackedWidget(self)
        layout.addWidget(self.stackedWidget)

    def initUi(self, doc_dir):
        # 初始化界面
        # 通过QListWidget的当前item变化来切换QStackedWidget中的序号
        self.doc_dir = doc_dir
        self.listWidget.currentRowChanged.connect(
            self.stackedWidget.setCurrentIndex)
        self.listWidget.setFrameShape(QListWidget.NoFrame)
        doc_list = glob.glob(self.doc_dir + "/*.md")
        doc_list.sort()
        self.setWindowTitle("标注说明文档")
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 这里就用一般的文本配合图标模式了(也可以直接用Icon模式,setViewMode)
        for md_file in doc_list:
            item = QListWidgetItem(os.path.split(md_file)[-1][:-3], self.listWidget)
            # 设置item的默认宽高(这里只有高度比较有用)
            item.setSizeHint(QSize(16777215, 80))
            # 文字居中
            # item.setTextAlignment(Qt.AlignCenter)

        # 再模拟20个右侧的页面(就不和上面一起循环放了)
        for md_file in doc_list:
            qwebengine = QWebEngineView()
            html = md2html(md_file)
            # fixme 图片无法显示
            qwebengine.setHtml(html, QUrl("file:///" + os.path.abspath(doc_dir).replace("\\", "/")))
            self.stackedWidget.addWidget(qwebengine)
        self.setStyleSheet(Stylesheet)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyleSheet(Stylesheet)
    w = DocPage()
    w.initUi("../docs")
    w.show()
    sys.exit(app.exec_())
