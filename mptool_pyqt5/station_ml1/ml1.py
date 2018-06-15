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
from station_ml1.net import network
from PyQt5.QtGui import QImage, QPainter, QTextDocument
from station_ml1.ml1_printer import printer
from PyQt5.QtCore import QUrl

class ML1(QDialog):
    def __init__(self, parent=None):
        super(ML1, self).__init__(parent)
        self.initUI()
        self.init_data()

    def initUI(self):
        print("ml1 station initUI")
        self.create_cmd_input()
        self.create_info_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)

    def init_data(self):
        self.ml1_printer = printer()
        printer_list = self.ml1_printer.list()
        print(printer_list)

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

        self.cmd_input.setText("4910212021234585")
        self.cmd_input.returnPressed.connect(self.handle_cmd)

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
        self.bigEditor.setFont(QFont("Microsoft YaHei", 15))
        cursor = self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)
        self.bigEditor.setReadOnly(True)

        layout.addRow(self.bigEditor)
        self.QGroupBox_info_show.setLayout(layout)

    def handle_cmd(self):
        mac = self.cmd_input.text()
        print(mac)

        # clean data first before show
        self.cmd_input.clear()
        self.bigEditor.clear()
        tmp = QTableWidgetItem("None")
        self.table.setItem(0, 1, tmp)

        check = self.mac_check(mac)
        if check == False:
            self.bigEditor.append("无效的MAC地址:"+mac)
        else:
            ml1 = network()
            msg = ml1.request_print(mac)
            if "download_success:" in msg:
                tmp = QTableWidgetItem(mac)
                self.table.setItem(0, 1, tmp)
                path = msg.split(':', 1)[1]
                self.bigEditor.clear()
                img = QImage(path, 'PNG')
                cursor = QTextCursor(self.bigEditor.document())
                cursor.insertText("打印ML1成功\n")
                cursor.insertImage(img)
            else:
                self.bigEditor.setText(msg)

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

    def printTest(self):
        html = 'printer test...'
        self.ml1_printer.printing(html)
