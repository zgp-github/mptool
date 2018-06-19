# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
                             QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout)
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QAbstractItemView, QHeaderView
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import QEvent, QTimer
import threading
from threading import Timer
from time import *
import re
import json
from station_gcl.net import network

class GCL(QDialog):
    def __init__(self, parent=None):
        super(GCL, self).__init__(parent)
        self.initUI()

    def initUI(self):
        print("gcl station initUI")
        self.create_cmd_input()
        self.create_info_show()
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)
        self.init_data()

    def init_data(self):
        self.net = network()
        self.GCLID_STATUS = None
        self.gcl_array = []

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        self.msg_show = QLabel("订单信息:")
        self.msg_show.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(self.msg_show, 0, 1)

        self.cmd_input = QLineEdit(self)
        self.cmd_input.setFont(QFont("Microsoft YaHei", 25))
        self.cmd_input.setStyleSheet("color:black")
        self.cmd_input.installEventFilter(self)
        layout.addWidget(self.cmd_input, 1, 1)
        self.cmd_input.returnPressed.connect(self.handle_cmd)

        self.table = QTableWidget(3, 2)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("MAC地址")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("传感器类型")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("入箱数量")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(2, 1, newItem)

        layout.addWidget(self.table, 0, 2, 4, 1)
        layout.setColumnStretch(1, 70)
        layout.setColumnStretch(2, 30)
        self.gridGroupBox.setLayout(layout)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("提示信息")
        layout = QFormLayout()
        print("gcl info show for the process logs")
        self.gcl_info_show = QTextEdit()
        self.gcl_info_show.setPlainText("请扫描需要打印GCL的传感器MAC地址")
        self.gcl_info_show.setFont(QFont("Microsoft YaHei", 15))
        cursor = self.gcl_info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.gcl_info_show.setTextCursor(cursor)
        self.gcl_info_show.setReadOnly(True)

        layout.addRow(self.gcl_info_show)
        self.QGroupBox_info_show.setLayout(layout)

    def handle_cmd(self):
        cmd = self.cmd_input.text()
        print("get cmd:", cmd)
        self.cmd_input.clear()

        if cmd == "GCLID_START":
            self.GCLID_STATUS = "START"
            self.gcl_info_show.setText("启动入箱,请扫描需要入箱的传感器MAC地址")
        elif cmd == "GCLID_END":
            pass
        elif self.GCLID_STATUS == "START":
            self.gcl_start(cmd)
        elif self.GCLID_STATUS == "END":
            self.gcl_end()
        else:
            print("cmd:"+cmd+" not support")
            self.gcl_info_show.setText("命令:"+cmd+" 不支持!")

    def gcl_start(self, macaddress):
        print("gcl_start")
        mac = macaddress
        check = self.mac_check(mac)
        if check == False:
            self.gcl_info_show.setText("无效的MAC地址:"+mac)
        else:
            check2 = self.mac_in_gcl_array(mac)
            if check2 == True:
                msg = self.net.check_mac_valid(mac)
                text = json.loads(msg)
                msg_type = text['messages'][0]['type']
                if msg_type == "fail":
                    self.gcl_info_show.setText("错误MAC:"+mac+" 不在数据库中")
                else:
                    m = QTableWidgetItem(mac)
                    self.table.setItem(0, 1, m)
                    self.gcl_array.append(mac)
                    count = len(self.gcl_array)
                    tmp = QTableWidgetItem(str(count))
                    self.table.setItem(2, 1, tmp)
                    self.gcl_info_show.setText("MAC地址:"+mac)
            else:
                pass

    def gcl_end(self):
        print("gcl_end")
        self.GCLID_STATUS = None

    def mac_in_gcl_array(self, mac):
        if mac in self.gcl_array:
            print("already exist in the gcl list")
            self.gcl_info_show.setText("MAC:"+mac+" 已经存在当前的列表中")
            return False
        else:
            return True

    def mac_check(self, addr):
        valid = re.compile(r''' 
            (^([0-9A-F]{1,2}[-]){5}([0-9A-F]{1,2})$ 
            |^([0-9A-F]{1,2}[:]){5}([0-9A-F]{1,2})$ 
            |^([0-9A-F]{1,2}[.]){5}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}){5}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}[-]){7}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}[:]){7}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}[.]){7}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}){7}([0-9A-F]{1,2})$) 
            ''', re.VERBOSE | re.IGNORECASE)
        return valid.match(addr) is not None



