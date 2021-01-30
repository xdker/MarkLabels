import sys
import time
from collections import OrderedDict
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QApplication, QLabel, QWidget, QGridLayout

AGE = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']
RACE = ["黄", "白", "黑", "棕", "未知"]
ILLUMINATION = ["有", "无", "未知"]
POSITION = ["有", "无", "未知"]
GENDER = ["男", "女", "未知"]
EXPRESSION = ["无", "笑", "愤怒", "哭", "未知"]

attribute_list = OrderedDict({"性别": ["男", "女", "未知"],
                              "光照": ["有", "无", "未知"],
                              "姿态": ["有", "无", "未知"],
                              "肤色": ["黄", "白", "黑", "棕", "未知"],
                              "表情": ["无", "笑", "愤怒", "哭", "未知"],
                              "年龄": ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)',
                                     '(60, 100)'],
                              })

translate_map = {'gender': "性别",
                 "age": "年龄",
                 "expression": "表情",
                 "headpose": "头部姿态",
                 "illumination": "光照",
                 "position": "姿态",
                 "race": "肤色"}
translate_map = dict(translate_map, **dict([(value, key) for (key, value) in translate_map.items()]))


# AGE=attribute_list["年龄"]
# print(AGE)
# class Selector(QWidget):
#     def __init__(self, name, values, parent):
#         super(Selector, self).__init__(parent)
#         self.check_boxes = []
#         span = 40
#         label = QLabel(name, self)
#         label.setStyleSheet("border:1px solid black;")
#         values.append("未标")
#         for i, v in enumerate(values):
#             height_b = 25
#
#             num_lines = len(v) // 10 + 1
#             if num_lines > 1:
#                 v = list(v)
#                 v = "\n".join(["".join(v[s:s + 3]) for s in range(0, len(v), 3)])
#                 cb = QCheckBox(v, self)
#             else:
#                 cb = QCheckBox(v, self)
#             cb.move(0, span)
#             cb.resize(80, height_b * num_lines)
#             span += height_b * num_lines
#             if v == "未知":
#                 self.unknow_box_idx = i
#             cb.stateChanged.connect(partial(self.set_unknow, i))
#             self.check_boxes.append(cb)
#         self.check_boxes[-1].setChecked(True)
#         self.values = values
#
#     def get_selected_value(self):
#         results = []
#         for b, v in zip(self.check_boxes, self.values):
#             if b.isChecked():
#                 results.append(v)
#         return results
#
#     def set_unknow(self, idx):
#         for c in self.check_boxes:
#             c.disconnect()
#         if hasattr(self, "unknow_box_idx") and self.check_boxes[idx].isChecked():
#             if idx == self.unknow_box_idx:
#                 for i, v in enumerate(self.check_boxes):
#                     if i != self.unknow_box_idx:
#                         v.setChecked(False)
#             else:
#                 self.check_boxes[self.unknow_box_idx].setChecked(False)
#
#         if idx == len(self.check_boxes) - 1:
#             for c in self.check_boxes[:-1]:
#                 c.setChecked(False)
#             self.check_boxes[idx].setChecked(True)
#         elif not self.check_boxes[idx].isChecked():
#             has_select = False
#             for c in self.check_boxes[:-1]:
#                 if c.isChecked():
#                     has_select = True
#             if not has_select:
#                 self.check_boxes[-1].setChecked(True)
#         else:
#             self.check_boxes[-1].setChecked(False)
#         for i, c in enumerate(self.check_boxes):
#             c.stateChanged.connect(partial(self.set_unknow, i))
#
#     def set_selected_value(self, value):
#         for i, v in enumerate(self.values):
#             if v == value:
#                 self.check_boxes[i].setChecked(True)
#                 self.set_unknow(i)
#                 break


class Labels(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.grid_layout = QGridLayout(self)
        self.CheckBox_list = {}
        for col_idx, k in enumerate(attribute_list.keys()):
            label_header = QLabel(k, self)
            label_header.setObjectName("{}".format(k))
            self.grid_layout.addWidget(label_header, 0, col_idx)
            self.CheckBox_list[k] = []
            for row_idx, v in enumerate(attribute_list[k]):
                label_item = QCheckBox(v, self)
                label_item.setObjectName("{}_{}".format(k, row_idx))
                self.grid_layout.addWidget(label_item, 1 + row_idx, col_idx)
                label_item.stateChanged.connect(self.changeCheck)
                self.CheckBox_list[k].append(label_item)
            label_item = QCheckBox("未标", self)
            label_item.setObjectName("{}_unlabeled".format(k))
            label_item.setChecked(True)
            label_item.stateChanged.connect(self.changeCheck)
            self.CheckBox_list[k].append(label_item)
            self.grid_layout.addWidget(label_item, len(attribute_list[k]) + 1, col_idx)

    # 勾选事件
    def changeCheck(self):
        header, idx = str(self.sender().objectName()).split("_")
        if self.sender().checkState() == Qt.Checked:
            if idx == "unlabeled":
                for i in self.CheckBox_list[header][:-1]:
                    i.setChecked(False)
            else:
                self.CheckBox_list[header][-1].setChecked(False)
        # font = QFont()
        # font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        # font.setPointSize(10)
        # self.set_font(font)

    def set_font(self, font):
        self.age.setFont(font)
        self.race.setFont(font)
        self.gender.setFont(font)
        self.expression.setFont(font)
        self.illumination.setFont(font)
        self.position.setFont(font)

    def get_labels(self):
        # 保存标签的时候有序
        results = OrderedDict({'age': [], 'race': [], 'gender': [], 'expression': []})
        for k, v in self.CheckBox_list.items():
            for item in v:
                if item.checkState() == Qt.Checked:
                    attr_type, value_idx = item.objectName().split("_")
                    if translate_map[k] in results:
                        if value_idx != "unlabeled":
                            results[translate_map[k]] += [attribute_list[k][int(value_idx)]]
                        else:
                            results[translate_map[k]] = ["未标"]
        return results

    def set_label(self, attr_name, attr_value):
        if translate_map[attr_name] in self.CheckBox_list:
            try:
                # 未标 没有在这个list里面特殊处理包括其他值也改成未标
                box_idx = attribute_list[translate_map[attr_name]].index(attr_value)
            except:
                box_idx = -1
            self.CheckBox_list[translate_map[attr_name]][box_idx].setChecked(True)

    def reset_cbox(self):
        for cboxs in self.CheckBox_list.values():
            for cbox in cboxs[:-1]:
                cbox.setChecked(False)
            cboxs[-1].setChecked(True)


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(900, 600)
        label = Labels(self)

        label.move(0, 0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
