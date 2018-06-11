# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QTabWidget
from PyQt5.QtWidgets import *

from pcbafts_station import PCBAFTS
from page2 import page2
from page3 import page3
from page4 import page4

class Main_Page(QTabWidget):
    def __init__(self, parent=None):
        super(Main_Page, self).__init__(parent)
        title = 'MPTOOL4PC .IO NGxx Version 0.1'
        self.setWindowTitle(title)
        self.resize(800, 600)

        self.PCBA_FTS_PAGE = PCBAFTS()
        self.page2 = page2()
        self.page3 = page3()
        self.page4 = page4()
        self.addTab(self.PCBA_FTS_PAGE, u"PCBA FTS测试工站")
        self.addTab(self.page2, u"page2")
        self.addTab(self.page3, u"page3")
        self.addTab(self.page4, u"page4")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    t = Main_Page()
    t.show()
    app.exec_()
