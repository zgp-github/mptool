# -*- coding: utf-8 -*-
import os
import sys
import signal
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
import socket
import re

class ML1(QDialog):
    def __init__(self, parent=None):
        super(ML1, self).__init__(parent)
        self.initUI()

    def initUI(self):
        print("ml1 station initUI")
        self.create_cmd_input()
        self.create_info_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)

    def set_focus(self):
        self.cmd_input.setFocus()

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
        self.cmd_input.returnPressed.connect(self.updateUi)

        self.table = QTableWidget(2, 2)
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

        layout.addWidget(self.table, 0, 2, 4, 1)
        layout.setColumnStretch(1, 70)
        layout.setColumnStretch(2, 30)
        self.gridGroupBox.setLayout(layout)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("提示信息")
        layout = QFormLayout()
        print("ML1 info show for the process logs")
        self.bigEditor = QTextEdit()
        self.bigEditor.setPlainText("请扫描需要打印ML1的传感器MAC地址")
        self.bigEditor.setFont(QFont("Microsoft YaHei", 10))
        cursor = self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)

        layout.addRow(self.bigEditor)
        self.QGroupBox_info_show.setLayout(layout)

    def updateUi(self):
        cmd = self.cmd_input.text()
        self.bigEditor.setText(cmd)
        print(cmd)
        self.cmd_input.clear()

        # test secket
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        print("host:", host_name, host_ip)

        check = self.mac_check(cmd)
        if check == False:
            self.bigEditor.append("无效的MAC地址:"+cmd)
        print(check)


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
            ''',re.VERBOSE | re.IGNORECASE)
        return valid.match(addr) is not None
