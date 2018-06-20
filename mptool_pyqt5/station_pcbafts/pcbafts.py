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
import json
import configparser
import os
import re
from station_pcbafts.fts_data import database
from station_pcbafts.net import network

class PCBAFTS(QDialog):
    thread_get_FTS_data = False
    _signal_update = QtCore.pyqtSignal(list)

    def __init__(self):
        super(PCBAFTS, self).__init__()
        self.initUI()
        self.init_data()

    def initUI(self):
        self.create_cmd_input()
        self.create_test_result_show()
        self.create_info_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)

        # It is a timer test code
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def init_data(self):
        self.net = network()
        self.read_po_config()
        self.gets_fts_data()

    def onTimerOut(self):
        print("-------------------timer test (tieout=5000)...-------------")
        self.timer.stop()
    
    def set_focus(self):
        self.cmd_input.setFocus()

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        self.po_info = QLabel("订单信息:")
        self.po_info.setFont(QFont("Microsoft YaHei", 20))
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

        newItem = QTableWidgetItem("订单总数")
        self.table.setItem(3, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(3, 1, newItem)

        newItem = QTableWidgetItem("当前数量")
        self.table.setItem(4, 0, newItem)
        newItem = QTableWidgetItem("0")
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
        self.info_show = QTextEdit()
        self.info_show.setPlainText("请扫描配对命令码")
        self.info_show.setFont(QFont("Microsoft YaHei", 15))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)

        layout.addRow(self.info_show)
        self.QGroupBox_info_show.setLayout(layout)
        self.info_show.setReadOnly(True)

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
                    self.info_show.append(msg)
            else:
                pass
        return False

    def gets_fts_data(self):
        self.thread_get_FTS_data = True
        t = threading.Thread(target=self.get_FTS_data)
        t.start()

    def get_FTS_data(self):
        self._signal_update.connect(self.update_ui_and_upload_data)
        self.net = network()
        data = database().get_Tests_data()
        print("get fts data in FTS station: ", data)

        sensor_id = data[0]
        sensor_time = data[1]
        sensor_mac = data[2]

        dataList = []
        dataList.append(sensor_id)
        dataList.append(sensor_time)
        dataList.append(sensor_mac)

        FTSresult = "success"
        upload_result = self.net.upload_mac_and_fts(sensor_mac, FTSresult)
        dataList.append(upload_result)

        print("upload result:", upload_result)
        self._signal_update.emit(dataList)
        while self.thread_get_FTS_data == True:
            data = database().get_Tests_data()
            print("get fts data in FTS station: ", data)

            id = data[0]
            time = data[1]
            mac = data[2]

            if id != sensor_id and mac != sensor_mac:
                dataList = []
                dataList.append(id)
                dataList.append(time)
                dataList.append(mac)
                FTSresult = "success"
                upload_result = self.net.upload_mac_and_fts(mac, FTSresult)
                dataList.append(upload_result)
                print("get new data upload result:", upload_result)
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

        for val in list:
            print(val)
            self.info_show.append(str(val))
            logging.debug(str(val))

        upload_status = list[3]
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

        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)

    def read_po_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            conf.read(config)
            pokey = conf.get('PoInfo', 'pokey')
            countrycode = conf.get('PoInfo', 'countrycode')
            hwversion = conf.get('PoInfo', 'hwversion')
            info = "订单信息:"+pokey+"-"+countrycode+"-"+hwversion
            self.po_info.setText(info)

            msg = self.net.get_po_info(pokey, countrycode, hwversion)
            text = json.loads(msg)
            msg_type = text['messages'][0]['type']
            if msg_type == "fail":
                self.gcl_info_show.setText("错误:当前的订单不存在，请检查您的设置信息")
            else:
                total = text['result'][0]
                t = QTableWidgetItem(str(total))
                self.table.setItem(3, 1, t)

    def handle_cmd(self):
        cmd = self.cmd_input.text()
        print("get cmd:"+cmd)
        self.cmd_input.clear()
        self.update_mac_for_test(cmd)
    
    def update_mac_for_test(self, macaddress):
        mac = macaddress
        print("get mac:", mac)
        check = self.mac_check(mac)
        if check == False:
            self.info_show.setText("无效的MAC地址:"+mac)
            return

        val = "pass"
        tmp = self.net.upload_mac_and_fts(mac, val)
        text = json.loads(tmp)
        msg_type = text['messages'][0]['type']
        msg = text['messages'][0]['message']
        if msg_type == "fail":
            if msg == "already exist in the database":
                self.info_show.setText("MAC:"+mac+" 已经存在数据库中")
        elif msg_type == "ok":
            if msg == "add mac succes":
                self.info_show.setText("添加MAC:"+mac+" 完成")
        else:
            print("upload mac error!!!")
            self.info_show.setText("添加MAC错误,请检查")

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
