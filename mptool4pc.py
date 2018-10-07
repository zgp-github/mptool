# -*- coding: utf-8 -*-
import sys
import os.path
import configparser
import random
import logging
import requests
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

from station_pcbafts.pcbafts import PCBAFTS
from station_assemblyfunction.assemblyfunction import AssemblyFunction
from station_assemblyfts.assemblyfts import ASSEMBLY_FTS
from station_ml1.ml1 import ML1
from station_gcl.gcl import GCL
from station_oqc.oqc import FACTORY_OQC
from station_iqa.iqa import NGSTB_IQA


class MainPage(QTabWidget):
    def __init__(self, parent=None):
        super(MainPage, self).__init__(parent)
        self.init_ui()
        self.init_data()

    def init_ui(self):
        self.init_icon()
        self.init_title()

    def init_data(self):
        self.init_logs()
        self.parser_config()
        self.init_station()

    def init_icon(self):
        resource_path = os.path.join(os.getcwd(), "resource")
        icon_name = 'icon.ico'
        icon_path = os.path.join(resource_path, icon_name)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def init_title(self):
        title = 'Mptool4pc.IO Version 0.13(2018-09-17)'
        self.setWindowTitle(title)

    def init_logs(self):
        print("init log")
        logs_path = os.path.join(os.getcwd(), "logs")
        log_file = logs_path + os.sep + "mptool4pc.log"
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
            if not os.path.exists(log_file):
                f = open(log_file, 'w')
                f.close()
            else:
                pass
        else:
            pass
        logging.basicConfig(level=logging.DEBUG, filename=log_file, format='%(asctime)s:%(message)s')
        log = "--------------------------MPTOOL4PC Start--------------------------"
        print(log)
        logging.debug(log)

    def parser_config(self):
        config = 'config.ini'
        cur_dir = os.getcwd()
        config_path = os.path.join(cur_dir, config)
        if os.path.exists(config_path):
            print("config.ini exist")
            pass
        else:
            self.create_configration()

        conf = configparser.ConfigParser()
        if os.path.exists(config):
            conf.read(config)
            self.station = conf.get('Station', 'station')
        else:
            pass

    def create_configration(self):
        config = 'config.ini'
        cur_dir = os.getcwd()
        config_path = os.path.join(cur_dir, config)
        if os.path.exists(config_path):
            pass
        else:
            print("config.ini not exist, create it")
            conf = configparser.ConfigParser()

            conf.add_section("Station")
            conf.set("Station", "STATION", "PCBA_FTS")
            conf.set("Station", "#station1", "PCBA_FTS")
            conf.set("Station", "#station2", "ASSEMBLY_FUNCTION")
            conf.set("Station", "#station3", "ASSEMBLY_FTS")
            conf.set("Station", "#station4", "ASSEMBLY_SINGLE_PACKAGE")
            conf.set("Station", "#station5", "ASSEMBLY_GCL")
            conf.set("Station", "#station6", "FACTORY_OQC")
            conf.set("Station", "#station7", "NGSTB_IQA")

            conf.add_section("Corelight")
            conf.set("Corelight", "tn4cioip", "192.168.1.150")

            conf.add_section("Gateway_H10")
            conf.set("Gateway_H10", "ip", "192.168.1.6")

            conf.add_section("Printer")
            conf.set("Printer", "ml1_printer", "POSTEK G-3106_ML1")
            conf.set("Printer", "pl2_printer", "POSTEK G-3106_PL2")
            conf.set("Printer", "gcl_printer", "GCL_printer_name")

            conf.add_section("PoInfo")
            conf.set("PoInfo", "pokey", "185010")
            conf.set("PoInfo", "countrycode", "104")
            conf.set("PoInfo", "hwversion", "NG01.12.AA")

            conf.add_section("GclInfo")
            conf.set("GclInfo", "count_one_package", "225")

            conf.add_section("FTS_DB")
            conf.set("FTS_DB", "db_name", "ftsTestResults.db")

            conf.add_section("Weighter")
            conf.set("Weighter", "serialport", "COM5")
            conf.set("Weighter", "baudrate", "9600")
            conf.set("Weighter", "max", "200")
            conf.set("Weighter", "min", "20")

            conf.add_section("TemperatureRef")
            conf.set("TemperatureRef", "macaddress", "00155F0074A3D39C")
            conf.set("TemperatureRef", "defaultvalue", "25")
            conf.set("TemperatureRef", "usedefaultvalue", "yes")
            conf.set("TemperatureRef", "#usedefaultvalue_option1", "yes")
            conf.set("TemperatureRef", "#usedefaultvalue_option2", "no")
            conf.set("TemperatureRef", "range", "2")

            # conf.add_section("Version")
            # conf.set("Version", "marketversion", "0.3")
            # conf.set("Version", "firmwareversion", "0.3(11012.0102.0017.0)")

            conf.write(open(config, "w"))

    def init_station(self):
        logging.debug('Station:'+self.station)
        if self.station == "PCBA_FTS":
            self.pcbafts_station = PCBAFTS()
            self.addTab(self.pcbafts_station, u"单板FTS测试工站")
            self.pcbafts_station.set_focus()
            self.showMaximized()
        elif self.station == "ASSEMBLY_FUNCTION":
            self.assemblypair_station = AssemblyFunction()
            self.addTab(self.assemblypair_station, u"组装线配对测试工站")
            self.assemblypair_station.set_focus()
            self.showMaximized()
        elif self.station == "ASSEMBLY_FTS":
            self.assemblyfts_station = ASSEMBLY_FTS()
            self.addTab(self.assemblyfts_station, u"组装线FTS测试工站")
            self.showMaximized()
            self.assemblyfts_station.set_focus()
        elif self.station == "ASSEMBLY_SINGLE_PACKAGE":
            self.ml1_station = ML1()
            self.addTab(self.ml1_station, u"ML1打印工站")
            self.ml1_station.set_focus()
            self.showMaximized()
        elif self.station == "ASSEMBLY_GCL":
            self.gcl_station = GCL()
            self.addTab(self.gcl_station, u"入箱工站")
            self.gcl_station.cmd_input.setFocus()
            self.showMaximized()
        elif self.station == "FACTORY_OQC":
            self.factory_oqc_station = FACTORY_OQC()
            self.addTab(self.factory_oqc_station, u"工厂质检工站")
            self.showMaximized()
            self.factory_oqc_station.set_focus()
        elif self.station == "NGSTB_IQA":
            self.ngstb_iqa_station = NGSTB_IQA()
            self.addTab(self.ngstb_iqa_station, u"NGSTB质检工站")
            self.showMaximized()
            self.ngstb_iqa_station.set_focus()

    # overwrite the window close function
    def closeEvent(self, event):
        log = "--------------------------MPTOOL4PC End----------------------------"
        print(log)
        logging.debug(log)
        try:
            if self.station == "PCBA_FTS":
                self.pcbafts_station.stop_all_thread()
            elif self.station == "ASSEMBLY_GCL":
                self.gcl_station.stop_all_thread()
            elif self.station == "ASSEMBLY_FTS":
                self.assemblyfts_station.stop_all_thread()
            elif self.station == "FACTORY_OQC":
                self.factory_oqc_station.stop_all_thread()
            elif self.station == "NGSTB_IQA":
                self.ngstb_iqa_station.stop_all_thread()
            else:
                pass
        except Exception as e:
            print(e)
            logging.debug(e)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    t = MainPage()
    t.show()
    app.exec_()
