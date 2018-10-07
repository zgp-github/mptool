# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
                             QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout)
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QAbstractItemView, QHeaderView
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QTabWidget, QMessageBox
from PyQt5.QtWidgets import *
import os.path
import configparser
import random
import logging
import requests
import json
from time import sleep
import threading

from pcbafts import fts_database
from net import network

class TestTool(QTabWidget):
    def __init__(self, parent=None):
        super(TestTool, self).__init__(parent)
        self.init_title()
        screenRect = QApplication.instance().desktop().availableGeometry()
        # get the screen width and height
        width = screenRect.width()*60/100
        height = screenRect.height()*70/100
        self.resize(width, height)
        self.parser_config()
        self.initUI()
        self.init_data()

    def init_title(self):
        title = 'MPTOOL4PC .IO Test Tools(2018-07-26)'
        self.setWindowTitle(title)

    def initUI(self):
        self.test_unit_1()
        self.test_unit_2()
        self.create_info_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.gridGroup2)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)

    def init_data(self):
        print("init_data")
        self.fts = fts_database()
        self.thread_running = False
        self.net = network()
        self.cmd_input.returnPressed.connect(self.handle_cmd)

    def test_unit_1(self):
        self.gridGroupBox = QGroupBox("模拟FTS")
        layout = QGridLayout()

        self.fts_info = QLabel("点击按钮启动自动更新测试数据到FTS数据库...")
        self.fts_info.setFont(QFont("Microsoft YaHei", 15))
        layout.addWidget(self.fts_info, 0, 0)

        ButtonStart = QPushButton("Start")
        ButtonStart.setFont(QFont("Microsoft YaHei", 10))
        ButtonStart.clicked.connect(self.start_thread_update_fts_data)
        layout.addWidget(ButtonStart, 0, 1)

        ButtonStop = QPushButton("Stop")
        ButtonStop.setFont(QFont("Microsoft YaHei", 10))
        ButtonStop.clicked.connect(self.stop_thread_update_fts_data)
        layout.addWidget(ButtonStop, 0, 2)

        layout.setColumnStretch(0, 8)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        self.gridGroupBox.setLayout(layout)

    def test_unit_2(self):
        self.gridGroup2= QGroupBox("Test 2 上传mac到tn4cio")
        layout = QGridLayout()

        self.cmd_input = QLineEdit(self)
        self.cmd_input.setFont(QFont("Microsoft YaHei", 25))
        self.cmd_input.setStyleSheet("color:black")
        self.cmd_input.installEventFilter(self)
        layout.addWidget(self.cmd_input, 0, 0)
        self.gridGroup2.setLayout(layout)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("运行信息")
        layout = QGridLayout()
        print("info show for the process logs")
        self.info_show = QTextEdit()
        self.info_show.setPlainText("提示信息显示")
        self.info_show.setFont(QFont("Microsoft YaHei", 15))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)

        layout.addWidget(self.info_show, 0, 0)
        self.QGroupBox_info_show.setLayout(layout)
        self.info_show.setReadOnly(True)

    # overwrite the window close function
    def closeEvent(self, event):
        print("event:", event)
        self.stop_thread_update_fts_data()

    def parser_config(self):
        config = 'config.ini'
        cur_dir = os.getcwd()
        config_path = os.path.join(cur_dir, config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.station = conf.get('Station', 'station')
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.ml1_printer = conf.get('Printer', 'ml1_printer')
            self.pl2_printer = conf.get('Printer', 'pl2_printer')
            self.gcl_printer = conf.get('Printer', 'gcl_printer')
        else:
            pass

    def start_thread_update_fts_data(self):
        print("--------------start thread for auto update data to fts db-------------")
        if self.thread_running == False:
            self.thread_running = True
            t = threading.Thread(target=self.write_data)
            t.start()
        else:
            self.fts_info.setText("FTS 自动更新数据已经在运行中")
            print("thread already running")

    def stop_thread_update_fts_data(self):
        print("-----------------stop thread for update fts data-----------------")
        self.thread_running = False
        self.fts_info.setText("FTS 自动更新数据已经停止,点击启动开始")

    def write_data(self):
        while self.thread_running == True:
            ret = self.fts.wtite_fts_test_data()
            print(ret)
            text =  json.loads(ret)
            fts_id = text['fts_id']
            fts_mac = text['fts_mac']
            self.update_fts_data_show(fts_id, fts_mac)
            sleep(10)

    def update_fts_data_show(self, id, mac):
        self.fts_info.setText("Auto add     id: "+ id + "    mac: "+ mac)

    def handle_cmd(self):
        mac = self.cmd_input.text()
        self.cmd_input.clear()
        ret = self.net.upload_mac_and_fts(mac, "pass")
        print(ret)
        tmp = json.loads(ret)
        msg_type = tmp['messages'][0]['type']
        msg = tmp['messages'][0]['message']
        if msg_type == "ok":
            self.info_show.setText("成功更新MAC: "+mac)
        else:
            if msg == "db is full!":
                self.info_show.setText("上传MAC:"+mac+" 失败,数据库已经无可用空间!")
            elif msg == "update mac to db fail!":
                self.info_show.setText("上传MAC:"+mac+" 失败!")
            elif msg == "already exist in the database":
                self.info_show.setText("MAC:"+mac+" 已经在数据库中!")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    t = TestTool()
    t.show()
    app.exec_()
