# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QTabWidget
from PyQt5.QtWidgets import *

from pcbafts_station import PCBAFTS
from page2 import page2
from page3 import page3
from page4 import page4
from page5 import page5
from page6 import page6

class Main_Page(QTabWidget):
    def __init__(self, parent=None):
        super(Main_Page, self).__init__(parent)
        title = 'MPTOOL4PC .IO NGxx Version 0.1'
        self.setWindowTitle(title)
        screenRect = QApplication.instance().desktop().availableGeometry()
        # get the screen width and height
        width = screenRect.width()*80/100
        height = screenRect.height()*70/100
        self.resize(width, height)

        self.PCBA_FTS_PAGE = PCBAFTS()
        self.page2 = page2()
        self.page3 = page3()
        self.page4 = page4()
        self.page5 = page5()
        self.page6 = page6()
        self.addTab(self.PCBA_FTS_PAGE, u"单板FTS测试工站")
        self.addTab(self.page2, u"组装线配对测试工站")
        self.addTab(self.page3, u"组装线FTS测试工站")
        self.addTab(self.page4, u"ML1打印工站")
        self.addTab(self.page5, u"入箱工站")
        self.addTab(self.page6, u"维修工站")
    
    # overwrite the window close function
    def closeEvent(self, event):
        print("closeEvent: ", event)
        self.PCBA_FTS_PAGE.thread_get_FTS_data = False

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    t = Main_Page()
    t.show()
    app.exec_()
