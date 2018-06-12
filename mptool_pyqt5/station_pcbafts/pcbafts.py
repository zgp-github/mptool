# -*- coding: utf-8 -*-
import sys
import os
import logging
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
from station_pcbafts.fts_data import fts_data
from station_pcbafts.net import network

class PCBAFTS(QDialog):
    thread_get_FTS_data = False
    _signal_update = QtCore.pyqtSignal(list)

    def __init__(self):
        super(PCBAFTS, self).__init__()
        self.initUI()

    def initUI(self):
        self.create_cmd_input()
        self.create_test_result_show()
        self.create_info_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)

        self.gets_fts_data()

        # It is a timer test code
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def onTimerOut(self):
        self.bigEditor.append("timer test...")
        self.timer.stop()

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

        self.table = QTableWidget(5, 2)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("测试ID")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("测试时间")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("MAC地址")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(2, 1, newItem)

        newItem = QTableWidgetItem("传感器类型")
        self.table.setItem(3, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(3, 1, newItem)

        newItem = QTableWidgetItem("传感器状态")
        self.table.setItem(4, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(4, 1, newItem)

        layout.addWidget(self.table, 0, 2, 4, 1)
        layout.setColumnStretch(1, 70)
        layout.setColumnStretch(2, 30)
        self.gridGroupBox.setLayout(layout)

    def create_test_result_show(self):
        self.formGroupBox = QGroupBox("测试结果")
        layout = QFormLayout()

        self.test_result = QLabel(self, text="测试结果")
        self.test_result.setStyleSheet(
            '''color: black; background-color: gray''')
        info = '请开始测试'
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

        layout.addRow(self.test_result)
        self.formGroupBox.setLayout(layout)

    def update_test_resule_show(self, status='None'):
        print("update_test_resule_show: "+status)
        if status == "success":
            info = "测试通过"
            self.test_result.setStyleSheet(
                '''color: black; background-color: green''')
        elif status == "fail":
            info = '测试失败'
            self.test_result.setStyleSheet(
                '''color: black; background-color: red''')
        else:
            info = '请开始测试'
            self.test_result.setStyleSheet(
                '''color: black; background-color: gray''')
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("运行信息")
        layout = QFormLayout()
        print("info show for the process logs")
        self.bigEditor = QTextEdit()
        self.bigEditor.setPlainText("log shows in here")
        self.bigEditor.setFont(QFont("Microsoft YaHei", 10))
        cursor = self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)

        layout.addRow(self.bigEditor)
        self.QGroupBox_info_show.setLayout(layout)

    def update_msg_show(self, id=None):
        if id == 1:
            msg = "请扫描配对命令码"
        elif id == 2:
            msg = "请按下传感器的配对按钮"
        elif id == 3:
            msg = "命令码错误"
        else:
            msg = "请扫描配对命令码"
        self.msg_show.setText(msg)

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
                    self.bigEditor.append(msg)
            else:
                pass
        return False

    def gets_fts_data(self):
        self.bigEditor.append("gets_fts_data")
        self.thread_get_FTS_data = True
        t = threading.Thread(target=self.get_FTS_data)
        t.start()
    
    def get_FTS_data(self):
        self._signal_update.connect(self.update_ui_and_upload_data)
        net = network()
        while self.thread_get_FTS_data == True:
            data = fts_data().get_Tests_data()
            print("get fts data in FTS station: ", data)

            sensor_id = data[0]
            sensor_time = data[1]
            sensor_mac = data[2]
            sensor_type = "door_window_sensor"

            dataList = []
            dataList.append(sensor_id)
            dataList.append(sensor_time)
            dataList.append(sensor_mac)
            dataList.append(sensor_type)

            FTSresult = "success"
            upload_result = net.upload_data(sensor_mac, FTSresult)
            dataList.append(upload_result)

            print("upload result:", upload_result)
            self._signal_update.emit(dataList)
            sleep(1)

    # count = 0
    def update_ui_and_upload_data(self, list):
        print("---------------list:", list)
        # sensor ID
        sensor_id = str(list[0])
        newItem = QTableWidgetItem(sensor_id)
        self.table.setItem(0, 1, newItem)

        # test time
        t = list[1]
        newItem = QTableWidgetItem(t)
        self.table.setItem(1, 1, newItem)

        # sensor mac
        mac = list[2]
        newItem = QTableWidgetItem(mac)
        self.table.setItem(2, 1, newItem)

        # sensor type
        sensor_type = list[3]
        newItem = QTableWidgetItem(sensor_type)
        self.table.setItem(3, 1, newItem)

        for val in list:
            print(val)
            self.bigEditor.append(str(val))
            logging.debug(str(val))

        upload_status = list[4]
        if upload_status == "newtwork_error":
            self.update_test_resule_show("fail")
            msg = "网络错误,请检查您的网络连接和TN4C.IO IP地址"
            self.msg_show.setText(msg)
        else:
            self.update_test_resule_show("success")

        # if self.count % 3 == 1:
        #     self.update_test_resule_show("success")
        # elif self.count % 3 == 2:
        #     self.update_test_resule_show("fail")
        # else:
        #     self.update_test_resule_show()
        # self.count = self.count + 1

        cursor = self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)
