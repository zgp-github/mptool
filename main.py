# -*- coding: utf-8 -*-
import sys
import os.path
import configparser
import random
import logging
import requests
import json

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QMessageBox

from window_1.window1 import Window1
from window_2.window2 import Window2


class MainPage(QTabWidget):
    def __init__(self, parent=None):
        super(MainPage, self).__init__(parent)
        self.window_conf = None
        self.window_interface = None
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
        title = 'Version 0.1(2018-10-08)'
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
        log = "--------------------------Start--------------------------"
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
            self.window_conf = conf.get('ToolConfig', 'Window')
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

            conf.add_section("ToolConfig")
            conf.set("ToolConfig", "Window", "window1")
            conf.set("ToolConfig", "#option1", "window1")
            conf.set("ToolConfig", "#option2", "window2")
            conf.set("ToolConfig", "#option3", "window3")

            conf.write(open(config, "w"))

    def init_station(self):
        logging.debug('Station:'+self.window_conf)
        if self.window_conf == "window1":
            self.window_interface = Window1()
            self.addTab(self.window_interface, u"窗口一")
            self.window_interface.set_focus()
            self.showMaximized()
        elif self.window_conf == "window2":
            self.window_interface = Window2()
            self.addTab(self.window_interface, u"窗口二")
            self.window_interface.set_focus()
            self.showMaximized()
        else:
            pass

    # overwrite the window close function
    def closeEvent(self, event):
        log = "--------------------------End----------------------------"
        print(log)
        logging.debug(log)
        try:
            if self.window_conf == "window1":
                self.window_interface.stop_all_thread()
            elif self.window_conf == "window2":
                self.window_interface.stop_all_thread()
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
