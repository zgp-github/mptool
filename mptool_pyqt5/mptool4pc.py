# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QTabWidget, QMessageBox
from PyQt5.QtWidgets import *
import os.path
import configparser
import random
import logging

from station_pcbafts.pcbafts import PCBAFTS
from station_assemblypair.assemblypair import ASSEMBLY_PAIR
from station_assemblyfts.assemblyfts import ASSEMBLYFTS
from station_ml1.ml1 import ML1
from station_gcl.gcl import GCL
from station_repair.repair import REPAIR

class Main_Page(QTabWidget):
    logs_path = os.path.join(os.getcwd(), "logs")
    log_file = os.path.join(os.getcwd(), "logs", "mptool4pc.log")

    def __init__(self, parent=None):
        super(Main_Page, self).__init__(parent)
        title = 'MPTOOL4PC .IO NGxx Version 0.1(2018-06-12)'
        self.setWindowTitle(title)
        screenRect = QApplication.instance().desktop().availableGeometry()
        # get the screen width and height
        width = screenRect.width()*60/100
        height = screenRect.height()*70/100
        self.resize(width, height)
        self.create_logs_path()

        station = self.station_config()
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG, format='%(asctime)s:%(message)s')
        logging.debug('--------------------------MPTOOL4PC Start--------------------------')
        logging.debug('main page station config:'+station)

        if station == "PCBA_FTS":
            self.pcbafts_station = PCBAFTS()
            self.addTab(self.pcbafts_station, u"单板FTS测试工站")
            self.pcbafts_station.set_focus()
        elif station == "ASSEMBLY_PAIR":
            self.assemblypair_station = ASSEMBLY_PAIR()
            self.addTab(self.assemblypair_station, u"组装线配对测试工站")
        elif station == "ASSEMBLY_FTS":
            self.assemblyfts_station = ASSEMBLYFTS()
            self.addTab(self.assemblyfts_station, u"组装线FTS测试工站")
        elif station == "ASSEMBLY_ML1":
            self.ml1_station = ML1()
            self.addTab(self.ml1_station, u"ML1打印工站")
            self.ml1_station.set_focus()
        elif station == "ASSEMBLY_GCL":
            self.gcl_station = GCL()
            self.addTab(self.gcl_station, u"入箱工站")
            self.gcl_station.cmd_input.setFocus()
        elif station == "ASSEMBLY_REPAIR":
            self.repair_station = REPAIR()
            self.addTab(self.repair_station, u"维修工站")

    def create_logs_path(self):
        print("main page create the logs path")
        if os.path.exists(self.logs_path):
            pass
        else:
            os.makedirs(self.logs_path)

    # overwrite the window close function
    def closeEvent(self, event):
        logging.debug('--------------------------MPTOOL4PC End----------------------------')
        station = self.station_config()
        if station == "PCBA_FTS":
            self.pcbafts_station.thread_get_FTS_data = False

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
            conf.add_section("TN4CIO")
            conf.set("TN4CIO", "TN4CIOIP", "192.168.10.150")
            conf.add_section("Printer")
            conf.set("Printer", "ml1_printer", "POSTEK G-3106_ml1")
            conf.set("Printer", "pl2_printer", "POSTEK G-3106_pl2")
            conf.set("Printer", "gcl_printer", "printer_gcl_name")
            conf.write(open(config, "w"))

        conf.read(config)
        station = conf.get('Mptool4PC', 'STATION')
        ip = conf.get('TN4CIO', 'TN4CIOIP')
        ml1 = conf.get('Printer', 'ml1_printer')
        pl2 = conf.get('Printer', 'pl2_printer')
        gcl = conf.get('Printer', 'gcl_printer')
        self.warm_msg_show = "\
            工站: "+station+"\n"+\
            "服务器IP地址: "+ip+"\n"+\
            "ML1打印机: "+ml1+"\n"+\
            "PL2打印机: "+pl2+"\n"+\
            "GCL打印机: "+gcl
        return station

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    t = Main_Page()
    t.show()
    msg_box = QMessageBox(QMessageBox.Warning, "配置信息", t.warm_msg_show)
    # msg_box.show()
    app.exec_()
