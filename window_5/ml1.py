# -*- coding: utf-8 -*-
import os
import sys
import signal
import threading
from threading import Timer
from time import *
import socket
import re
import json
import configparser
from urllib.request import urlretrieve
from urllib.request import urlcleanup
from urllib.request import urlopen

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import *

from window5.net import network
from window5.ml1_printer import Printer


class ML1(QDialog):
    _signal_check_config = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(ML1, self).__init__(parent)
        self._signal_check_config.connect(self.check_config_and_init)
        self.initUI()
        self.init_data()

    def initUI(self):
        self.create_cmd_input()
        self.create_info_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        self.setLayout(mainLayout)

    def init_data(self):
        self.parser_config()
        self.net = network()
        self.ml1_printer = Printer()
        self.ml1_printer._signal_printer.connect(self.update_ui_and_info_show)
        self.check_configuration()

    def set_focus(self):
        self.cmd_input.setFocus()

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        station_info = QLabel("工站: 整机包装")
        station_info.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(station_info, 0, 0)
        station_info.setAlignment(QtCore.Qt.AlignCenter)

        self.po_info = QLabel("订单: ")
        self.po_info.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(self.po_info, 1, 0)
        self.po_info.setAlignment(QtCore.Qt.AlignCenter)

        self.cmd_input = QLineEdit(self)
        self.cmd_input.setFont(QFont("Microsoft YaHei", 20))
        self.cmd_input.setStyleSheet("color:black")
        self.cmd_input.installEventFilter(self)
        layout.addWidget(self.cmd_input, 2, 0)
        self.cmd_input.returnPressed.connect(self.handle_cmd)

        self.table = QTableWidget(3, 2)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("服务器IP地址")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("打印机配置")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("订单总数: ")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(2, 1, newItem)

        layout.addWidget(self.table, 0, 1, 3, 1)
        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 30)
        self.gridGroupBox.setLayout(layout)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("提示信息")
        layout = QGridLayout()
        print("ML1 info show for the process logs")
        self.info_show = QTextEdit()
        self.info_show.setPlainText("提示信息")
        self.info_show.setFont(QFont("Microsoft YaHei", 20))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)
        self.info_show.setReadOnly(True)

        # name
        self.sensor_preview_name = QLabel(self)
        self.sensor_preview_name.setText("感应器效果图")
        self.sensor_preview_name.setFont(QFont("Microsoft YaHei", 15))
        self.sensor_preview_name.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.sensor_preview_name, 0, 1, 1, 1)
        self.sensor_preview_name.setStyleSheet("border: 1px solid black")

        # sensor preview
        self.sensor_preview = QLabel(self)
        self.sensor_preview.setText("无")
        self.sensor_preview.setFont(QFont("Microsoft YaHei", 15))
        self.sensor_preview.setAlignment(QtCore.Qt.AlignCenter)
        self.sensor_preview.setStyleSheet("border: 1px solid black")
        layout.addWidget(self.sensor_preview, 1, 1, 1, 1)

        self.info_show.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(self.info_show, 0, 0, 2, 1)
        self.QGroupBox_info_show.setLayout(layout)
        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 30)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 90)

    def parser_config(self):
        config = "config.ini"
        cur_dir = os.getcwd()
        config_path = os.path.join(cur_dir, config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.ml1_printer_name = conf.get('Printer', 'ml1_printer')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
        else:
            self.info_show.setText(config_path+" 不存在!!!")

    def check_configuration(self):
        print("check_configuration")
        info = "正在检查您的配置信息,请稍等..."
        self.info_show.setText(info)
        t = threading.Thread(target=self.check_configs)
        t.start()

    def check_configs(self):
        msg = "checking configuration"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)

        # 1.check the corelight ip address
        msg = "checking corelight"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        ret = self.net.check_tn4cio()
        if ret == True:
            msg = "corelight ip check success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        elif ret == False:
            msg = "corelight ip check fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return

        # 2.check the po
        msg = "checking poinfo"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        ret = self.net.get_po_info()
        try:
            text = json.loads(ret)
            result = text['result']
            if result == "ok":
                msg = "check poinfo success"
                data = {"message": msg}
                self._signal_check_config.emit(data)
            elif result == "fail":
                msg = "check poinfo fail"
                data = {"message": msg}
                self._signal_check_config.emit(data)
                return
        except Exception:
            msg = "check poinfo fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return
        finally:
            sleep(0.1)

        # 3.check the ml1 printer
        msg = "checking printer"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        printer_list = self.ml1_printer.list()
        if self.ml1_printer_name in printer_list:
            msg = "check printer success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        else:
            msg = "check printer fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return

        # 4.check configuration done
        msg = "check configuration done"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(2)

        # 5.init station
        msg = "init station"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(2)

    def check_config_and_init(self, data):
        print("check_config_and_init-----------------------data:", data)
        text = data
        msg = text['message']

        self.show_po_info()
        if msg == "checking configuration":
            self.info_show.setText("正在检查您的配置信息，请稍等...")
        elif msg == "checking corelight":
            self.info_show.append("\n检查Corelight服务器: " + self.tn4cioip)
        elif msg == "corelight ip check success":
            self.info_show.append("通过")
            self.show_tn4cio_ip()
        elif msg == "corelight ip check fail":
            self.info_show.append("错误:")
            self.info_show.append("Corelight服务器无法连接...")
            self.info_show.append("\n提示:")
            self.info_show.append("1.请检查网络连接状态")
            self.info_show.append("2.找到程序的配置文件config.ini")
            self.info_show.append("3.设置正确的Corelight服务器IP地址并保存")
            self.info_show.append("4.重新启动程序")
        elif msg == "checking poinfo":
            self.info_show.append("\n检查订单信息: "+self.pokey+"-"+self.countrycode+"-"+self.hwversion)
        elif msg == "check poinfo success":
            self.info_show.append("通过")
        elif msg == "check poinfo fail":
            self.info_show.append("错误:")
            self.info_show.append("订单信息设置错误,请检查确认...")
        elif msg == "checking printer":
            self.info_show.append("\n检查打印机: "+self.ml1_printer_name)
        elif msg == "check printer success":
            self.info_show.append("通过")
            self.show_printer_name()
        elif msg == "check printer fail":
            self.info_show.append("错误:")
            self.info_show.append("1.ML1打印机设置错误,请检查确认...")
            self.info_show.append("2.当前打印机设置: "+self.ml1_printer_name)
            self.info_show.append("\n提示:")
            self.info_show.append("1.请使用USB线连接打印机到本电脑")
            self.info_show.append("2.打开Windows控制面板,找到您的打印机名称")
            self.info_show.append("3.找到程序的配置文件config.ini")
            self.info_show.append("4.设置您的打印机到配置文件中的ml1_printer项并保存")
            self.info_show.append("5.重新启动本程序")
            self.info_show.append("\n当前系统打印机列表:")
            printer_list = self.ml1_printer.list()
            for item in printer_list:
                self.info_show.append(str(item))
        elif msg == "check configuration done":
            self.info_show.append("\n检查完成")
        elif msg == "init station":
            self.init_status()

    def init_status(self):
        self.show_po_info()
        self.show_tn4cio_ip()
        self.show_printer_name()
        self.show_po_total()
        self.show_init_msg()
        self.show_sensor_preview()

    def show_po_info(self):
        if self.pokey != None and self.countrycode != None and self.hwversion != None:
            info = "订单: "+self.pokey+"-"+self.countrycode+"-"+self.hwversion
            self.po_info.setText(info)
        else:
            self.info_show.setText("无法获取到Po信息,请检查确认...\n")
            return

    def show_tn4cio_ip(self):
        # show the tn4c.io ip
        if self.tn4cioip != None:
            tmp = QTableWidgetItem(self.tn4cioip)
            self.table.setItem(0, 1, tmp)
        else:
            self.info_show.setText("无法获取到Corelight信息,请检查确认...\n")

    def show_printer_name(self):
        # show the ML1 printer
        if self.ml1_printer_name != None:
            tmp = QTableWidgetItem(self.ml1_printer_name)
            self.table.setItem(1, 1, tmp)
        else:
            self.info_show.setText("无法获取到打印机信息,请检查确认...\n")

    def show_po_total(self):
        tmp = self.net.get_po_info()
        if tmp != None:
            text = json.loads(tmp)
            result = text['result']
            msg_type = text['messages'][0]['type']
            if result == "fail":
                self.info_show.setText("错误:当前的订单不存在，请检查您的设置信息")
            elif result == "ok":
                # show the po total number
                total = text['messages'][0]['total']
                des = text['messages'][0]['description']
                tmp = QTableWidgetItem(str(total))
                self.table.setItem(2, 1, tmp)
        else:
            pass

    def show_init_msg(self):
        # show the introduce
        self.info_show.setText("作业提示:")
        self.info_show.append("请扫描待包装感应器背面条码")
        self.info_show.append("(详情请参考SOP)")

    def handle_cmd(self):
        cmd = self.cmd_input.text()

        self.cmd_input.clear()
        self.info_show.clear()

        mac = cmd.upper()
        check = self.mac_check(mac)
        if check is False:
            self.info_show.setText("错误:")
            self.info_show.append("无效的MAC地址:"+mac)
            self.timer = QTimer()
            self.timer.setInterval(2000)
            self.timer.start()
            self.timer.timeout.connect(self.onTimerOut)
            return False

        ret = self.net.check_previous_station_already_done(mac)
        if ret is True:
            self.ml1_printer.print_ml1_label(mac)
        else:
            self.info_show.setText("警告:")
            self.info_show.append("整机FTS测试未完成")
            self.timer = QTimer()
            self.timer.setInterval(5000)
            self.timer.start()
            self.timer.timeout.connect(self.onTimerOut)
            return False

    def update_ui_and_info_show(self, data: dict):
        text = data
        try:
            msg = text['message']
            print("---- update_ui_and_info_show ---- msg:", msg)
            if msg == "print ML1 label success":
                self.info_show.setText("打印包装条码成功")
                self.info_show.append("请按右侧图示包装感应器")
                self.info_show.append("并将包装条码贴于指定位置")
                self.info_show.append("完成后请扫描下一台待包装的感应器背面条码")
                self.info_show.append(" (详情请参考SOP)\n")

                img = text['filepath']
                preview = QImage(img, 'PNG')
                cursor = self.info_show.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertImage(preview)
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "print ML1 label fail":
                self.info_show.setText("错误:")
                self.info_show.append("打印PL2标签失败")
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
        except Exception:
            self.info_show.setText("错误:")
            self.info_show.append("打印ML1标签失败")
            self.timer = QTimer()
            self.timer.setInterval(2000)
            self.timer.start()
            self.timer.timeout.connect(self.onTimerOut)

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

    def onTimerOut(self):
        self.timer.stop()
        self.init_status()

    def show_sensor_preview(self):
        self.sensor_preview.clear()
        margin = self.sensor_preview.getContentsMargins()

        img = "resource/NG01.jpg"
        cur_dir = os.getcwd()
        img_path = os.path.join(cur_dir, img)
        if os.path.exists(img_path):
            preview = QPixmap(img_path)
            width = self.sensor_preview.width() - (margin[0] + margin[2])
            scaled_img = preview.scaledToWidth(width)
            self.sensor_preview.setPixmap(scaled_img)
        else:
            pass
