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
from fts_data import fts_data
from net import network

class page4(QDialog):
    def __init__(self, parent=None):
        super(page4, self).__init__(parent)
        self.initUI()

    def initUI(self):
        print("ml1 station initUI")
        self.create_cmd_input()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        self.setLayout(mainLayout)


    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()
        self.cmd_input = QLineEdit(self)
        self.cmd_input.setFont(QFont("Microsoft YaHei", 25))
        self.cmd_input.setStyleSheet("color:black")
        self.cmd_input.installEventFilter(self)
        layout.addWidget(self.cmd_input, 0, 1)

        self.msg_show = QLabel("请扫描配对命令码")
        self.msg_show.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(self.msg_show, 1, 1)

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

        newItem = QTableWidgetItem("传感器状态")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(2, 1, newItem)

        layout.addWidget(self.table, 0, 2, 4, 1)
        layout.setColumnStretch(1, 70)
        layout.setColumnStretch(2, 30)
        self.gridGroupBox.setLayout(layout)
