# -*- coding: utf-8 -*-
import sys
import os
import logging

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView

import threading
from threading import Timer
from time import *
import json
import configparser
import os
import re

from PyQt5 import QtCore


class Window1(QDialog):
    _signal_update_info = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(Window1, self).__init__()
        self._signal_update_info.connect(self.update_info_show)
        self.thread_running = False
        self.init_ui()
        self.init_data()

    def init_ui(self):
        self.create_cmd_input()
        self.create_test_result_show()
        self.create_info_show()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.gridGroupBox)
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.QGroupBox_info_show)
        self.setLayout(main_layout)

        # It is a timer test code
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def init_data(self):
        self.thread_start()

    def onTimerOut(self):
        self.timer.stop()
    
    def set_focus(self):
        self.cmd_input.setFocus()

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        self.po_info = QLabel("标题: 窗口一")
        self.po_info.setFont(QFont("Microsoft YaHei", 20))
        self.po_info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.po_info, 0, 1)

        self.cmd_input = QLineEdit(self)
        self.cmd_input.setFont(QFont("Microsoft YaHei", 25))
        self.cmd_input.setStyleSheet("color:black")
        self.cmd_input.installEventFilter(self)
        layout.addWidget(self.cmd_input, 1, 1)
        self.cmd_input.returnPressed.connect(self.handle_cmd)

        self.table = QTableWidget(5, 2)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("类型_1")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("数据_1")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("类型_2")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("数据_2")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("类型_3")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("数据_3")
        self.table.setItem(2, 1, newItem)

        newItem = QTableWidgetItem("类型_4")
        self.table.setItem(3, 0, newItem)
        newItem = QTableWidgetItem("数据_4")
        self.table.setItem(3, 1, newItem)

        newItem = QTableWidgetItem("类型_5")
        self.table.setItem(4, 0, newItem)
        newItem = QTableWidgetItem("数据_5")
        self.table.setItem(4, 1, newItem)

        layout.addWidget(self.table, 0, 2, 4, 1)
        layout.setColumnStretch(1, 70)
        layout.setColumnStretch(2, 30)
        self.gridGroupBox.setLayout(layout)

    def create_test_result_show(self):
        self.formGroupBox = QGroupBox("测试结果")
        layout = QFormLayout()

        self.test_result = QLabel(self)
        self.test_result.setStyleSheet(
            '''color: black; background-color: gray''')
        info = '状态显示'
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

        layout.addRow(self.test_result)
        self.formGroupBox.setLayout(layout)

    def update_test_result_show(self, status='None'):
        if status == "success":
            info = "通过"
            self.test_result.setStyleSheet(
                '''color: black; background-color: green''')
        elif status == "fail":
            info = '失败'
            self.test_result.setStyleSheet(
                '''color: black; background-color: red''')
        else:
            info = '初始'
            self.test_result.setStyleSheet(
                '''color: black; background-color: gray''')
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("运行信息")
        layout = QFormLayout()
        print("info show for the process logs")
        self.info_show = QTextEdit()
        self.info_show.setPlainText("提示信息显示")
        self.info_show.setFont(QFont("Microsoft YaHei", 15))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)

        layout.addRow(self.info_show)
        self.QGroupBox_info_show.setLayout(layout)
        self.info_show.setReadOnly(True)

    def eventFilter(self, widget, event):
        if widget == self.cmd_input:
            if event.type() == QEvent.FocusOut:
                print("focus out")
                pass
            elif event.type() == QEvent.FocusIn:
                print("focus in")
            elif event.type() == QEvent.KeyPress:
                pass
            elif event.type() == QEvent.KeyRelease:
                if event.key() == QtCore.Qt.Key_Return:
                    msg = self.cmd_input.text()
                    print("get: "+msg)
                    self.info_show.append(msg)
            else:
                pass
        return False

    def thread_start(self):
        t = threading.Thread(target=self.work_start)
        t.start()

    def thread_stop(self):
        self.thread_running = False

    def work_start(self):
        i = 0
        if self.thread_running:
            data = {"message": "thread is running"}
            self._signal_update_info.emit(data)

        self.thread_running = True
        while self.thread_running:
            data = {"message": "thread running test", "data": str(i)}
            self._signal_update_info.emit(data)
            i = i + 1
            sleep(1)
        data = {"message": "thread exited"}
        self._signal_update_info.emit(data)

    def handle_cmd(self):
        cmd = self.cmd_input.text()
        print("get cmd:"+cmd)
        self.cmd_input.clear()
        if cmd == "CMD_TEST_1":
            print("CMD_TEST_1")
            pass
        else:
            data = {"message": "not support cmd"}
            self._signal_update_info.emit(data)
    
    def update_info_show(self, data):
        print(data)
        try:
            text = data
            msg = text['message']

            if msg == "not support cmd":
                self.info_show.setText("不支持的命令")
            elif msg == "thread running test":
                num = text['data']
                self.info_show.setText("线程测试: " + str(num))
            else:
                self.info_show.setText("不支持的命令")
        except Exception as e:
            print(e)

    def stop_all_thread(self):
        try:
            self.thread_stop()
        except Exception as e:
            print(e)

