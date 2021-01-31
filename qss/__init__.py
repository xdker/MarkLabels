import traceback

from PyQt5.QtCore import QFile, QTextStream

from .resources import *


class CommonHelper:
    def __init__(self):
        self.style_list = ['AMOLED', 'Aqua', 'black', 'blue', 'material', 'darkblack', 'darkblue', 'darkgray',
                           'darkorange', 'deepblue', 'ElegantDark', 'flatblack', 'flatwhite', 'gray', 'lightblack',
                           'lightblue', 'lightgray', 'MacOS', 'ManjaroMix', 'materialdark', 'NeonButtons', 'psblack',
                           'silvery', 'Ubuntu']

    @staticmethod
    def get_style(style_sheet):
        try:
            f = QFile(":/qss/%s.qss" % style_sheet)
            f.open(QFile.ReadOnly | QFile.Text)
            ts = QTextStream(f)
            stylesheet = ts.readAll()
        except ImportError as e:
            print("Style sheet not available. Use available_styles() to check for valid styles")
            return u""
        except Exception as e:
            print("Style sheet available, but an error occured...")
            traceback.print_exc()
            return u""
        return stylesheet