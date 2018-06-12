# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QTabWidget
from PyQt5.QtWidgets import *
import os.path
import configparser
import random

from station_pcbafts.pcbafts import PCBAFTS
from station_assemblypair.assemblypair import ASSEMBLY_PAIR
from station_assemblyfts.assemblyfts import ASSEMBLYFTS
from station_ml1.ml1 import ML1
from station_gcl.gcl import GCL
from station_repair.repair import REPAIR

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
        print("----------------------------main page----------------------------station: ", station)
        if station == "PCBA_FTS":
            self.PCBA_FTS_PAGE = PCBAFTS()
            self.addTab(self.PCBA_FTS_PAGE, u"单板FTS测试工站")
        elif station == "ASSEMBLY_PAIR":
            self.assemblypair_station = ASSEMBLY_PAIR()
            self.addTab(self.assemblypair_station, u"组装线配对测试工站")
        elif station == "ASSEMBLY_FTS":
            self.assemblyfts_station = ASSEMBLYFTS()
            self.addTab(self.assemblyfts_station, u"组装线FTS测试工站")
        elif station == "ASSEMBLY_ML1":
            self.ml1_station = ML1()
            self.addTab(self.ml1_station, u"ML1打印工站")
        elif station == "ASSEMBLY_GCL":
            self.gcl_station = GCL()
            self.addTab(self.gcl_station, u"入箱工站")
        elif station == "ASSEMBLY_REPAIR":
            self.repair_station = REPAIR()
            self.addTab(self.repair_station, u"维修工站")
    
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
