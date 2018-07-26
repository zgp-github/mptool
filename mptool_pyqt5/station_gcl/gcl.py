# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
                             QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout)
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QAbstractItemView, QHeaderView
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QTextCursor, QImage
from PyQt5.QtCore import QEvent, QTimer
import threading
from threading import Timer
from time import *
import re
import json
import configparser
import os
from urllib.request import urlretrieve, urlcleanup, urlopen
from station_gcl.net import network

class GCL(QDialog):
    _signal = QtCore.pyqtSignal(object)

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
        self.read_po_config()

        self._signal.connect(self.update_ui_data)

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

        self.table = QTableWidget(3, 2)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("订单总数")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("每箱数量")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("0")
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
        self.gcl_info_show.setPlainText("请扫描开始入箱的命令码")
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
            self.gcl_array.clear()
        elif cmd == "GCLID_END":
            self.GCLID_STATUS = "END"
            self.gcl_end()
        elif self.GCLID_STATUS == "START":
            self.gcl_start(cmd)
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
                    self.gcl_array.append(mac)
                    self.update_info_show()
                    self.gcl_info_show.setText("MAC地址:"+mac)
            else:
                pass

    def update_info_show(self):
        count = len(self.gcl_array)
        tmp = QTableWidgetItem(str(count))
        self.table.setItem(2, 1, tmp)

    def gcl_end(self):
        print("gcl_end")
        self.GCLID_STATUS = None
        self.gcl_info_show.setText("入箱结束,正在生成GCL图片,请稍等...")
        t = threading.Thread(target=self.create_label)
        t.start()

    def create_label(self):
        print("thread create_label")
        ret = self.net.create_gcl_label(self.gcl_array)
        data = []
        data.append(ret)
        self._signal.emit(ret)

    def update_ui_data(self, data):
        msg = data
        print("signal update_ui_data:", msg)

        tmp = json.loads(msg)
        msg_type = tmp['messages'][0]['type']
        msg = tmp['messages'][0]['message']
        if msg_type == "ok":
            if msg == "create the gcl label success":
                gcl_file_name = None
                for i in tmp['result']:
                    if gcl_file_name == None:
                        gcl_file_name = i+"\n"
                    else:
                        gcl_file_name = gcl_file_name + i+"\n"
                    self.download_gcl_file(i)
                # info = gcl_file_name+"创建完成,请等待打印..."
                # self.gcl_info_show.setText(info)
        elif msg_type == "fail":
            pass
        else:
            info = "创建GCL文件错误!!!"
            self.gcl_info_show.setText(info)
        self.gcl_array.clear()
        self.update_info_show()

    def download_gcl_file(self, name):
        file_name = name
        tmp = self.net.request_gcl_download_url(file_name)
        text = json.loads(tmp)
        msg_type = text['messages'][0]['type']
        msg = text['messages'][0]['message']
        if msg_type == "ok":
            url = text['result'][0]
            try:
                # download the gcl file
                gcl = os.path.join(os.getcwd(), file_name)
                urlretrieve(url, gcl, self.download_callback)
                print("download_success:" + gcl)
                if self.percent == 100:
                    sleep(0.1)
                    self.per = 0
                    preview = QImage(gcl, 'PNG')
                    cursor = QTextCursor(self.gcl_info_show.document())
                    cursor.insertText("打印GCL成功\n")
                    cursor.insertImage(preview)
            except Exception as e:
                print("dowmload error:", e)
            finally:
                urlcleanup()
        elif msg_type == "fail":
            #fixme
            pass

    def download_callback(self, a, b, c):
        self.percent = 100.0*a*b/c
        if self.percent > 100:
            self.percent = 100
        print('%.2f%%' % self.percent)

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
            count_per_carton = conf.get('GclInfo', 'count_one_package')
            num = QTableWidgetItem(str(count_per_carton))
            self.table.setItem(1, 1, num)

            msg = self.net.get_po_info()
            if msg == None:
                return
            text = json.loads(msg)
            msg_type = text['messages'][0]['type']
            if msg_type == "fail":
                self.gcl_info_show.setText("错误:当前的订单不存在，请检查您的设置信息")
            else:
                total = text['result'][0]
                t = QTableWidgetItem(str(total))
                self.table.setItem(0, 1, t)

