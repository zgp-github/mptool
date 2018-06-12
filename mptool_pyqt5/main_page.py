# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QTabWidget
from PyQt5.QtWidgets import *
import os.path
import configparser
import random

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

        station = self.station_config()
        print("----------------------------main page----------------------------------station:", station)
        if station == "PCBA_FTS":
            self.PCBA_FTS_PAGE = PCBAFTS()
            self.addTab(self.PCBA_FTS_PAGE, u"单板FTS测试工站")
        elif station == "ASSEMBLY_PAIR":
            self.page2 = page2()
            self.addTab(self.page2, u"组装线配对测试工站")
        elif station == "ASSEMBLY_FTS":
            self.page3 = page3()
            self.addTab(self.page3, u"组装线FTS测试工站")
        elif station == "ASSEMBLY_ML1":
            self.page4 = page4()
            self.addTab(self.page4, u"ML1打印工站")
        elif station == "ASSEMBLY_GCL":
            self.page5 = page5()
            self.addTab(self.page5, u"入箱工站")
        elif station == "ASSEMBLY_REPAIR":
            self.page6 = page6()
            self.addTab(self.page6, u"维修工站")
    
    # overwrite the window close function
    def closeEvent(self, event):
        print("closeEvent: ", event)
        station = self.station_config()
        if station == "PCBA_FTS":
            self.PCBA_FTS_PAGE.thread_get_FTS_data = False

    def station_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            print("config.ini exist")
            pass
        else:
            print("config.ini not exist, create it")
            conf.read(config)
            conf.add_section("Mptool4PC")
            conf.set("Mptool4PC", "STATION", "PCBA_FTS")

            conf.set("Mptool4PC", "#station1", "PCBA_FTS")
            conf.set("Mptool4PC", "#station2", "ASSEMBLY_PAIR")
            conf.set("Mptool4PC", "#station3", "ASSEMBLY_FTS")
            conf.set("Mptool4PC", "#station4", "ASSEMBLY_ML1")
            conf.set("Mptool4PC", "#station5", "ASSEMBLY_GCL")
            conf.set("Mptool4PC", "#station6", "ASSEMBLY_REPAIR")

            conf.set("Mptool4PC", "TN4CIOIP", "192.168.10.150")
            conf.write(open(config, "w"))

        conf.read(config)
        station = conf.get('Mptool4PC', 'STATION')
        return station

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    t = Main_Page()
    t.show()
    app.exec_()
