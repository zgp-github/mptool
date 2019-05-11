# -*- coding: utf-8 -*-
import os
import threading
from threading import Timer
from time import *
import re
import json
import configparser
import qrcode
from urllib.request import urlretrieve
from urllib.request import urlcleanup
from urllib.request import urlopen
import logging
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QImage
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
from PyQt5.QtWidgets import *

from window6.net import network
from window6.gcl_printer import printer
from window6.weighter import Weighter
from window6.cartoning import Cartoning
from window6.gclid_reset_part import gclid_reset_part
from window6.gclid_reset_all import gclid_reset_all
from window6.gclid_reprint import gclid_reprint


class GCL(QDialog):
    _signal_check_config = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(GCL, self).__init__(parent)
        self._signal_check_config.connect(self.check_config_and_init)
        self.init_ui()
        self.init_data()

    def init_ui(self):
        self.create_cmd_input()
        self.create_info_show()
        self.create_po_progressbar_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        mainLayout.addWidget(self.QGridLayout_po_progress)

        mainLayout.setStretchFactor(self.gridGroupBox, 30)
        mainLayout.setStretchFactor(self.QGroupBox_info_show, 65)
        mainLayout.setStretchFactor(self.QGridLayout_po_progress, 5)
        self.setLayout(mainLayout)

    def init_data(self):
        self.net = network()
        self.GCLID_RUNNING_MODEL = None
        self.GET_WEIGHT_THREAD = False
        self.gcl_array = []
        self.weighter = Weighter()
        self.parser_config()
        self.gcl_printer = printer()
        self.check_configuration()

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        self.station_info = QLabel("工站: GCLID封箱")
        self.station_info.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(self.station_info, 0, 0)
        self.station_info.setAlignment(QtCore.Qt.AlignCenter)

        self.po_info = QLabel("订单:")
        self.po_info.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(self.po_info, 1, 0)
        self.po_info.setAlignment(QtCore.Qt.AlignCenter)

        self.cmd_input = QLineEdit(self)
        self.cmd_input.setFont(QFont("Microsoft YaHei", 20))
        self.cmd_input.setStyleSheet("color:black")
        self.cmd_input.installEventFilter(self)
        layout.addWidget(self.cmd_input, 2, 0)
        self.cmd_input.returnPressed.connect(self.handle_cmd)

        self.table = QTableWidget(5, 4)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['类型', '数据', '类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("服务器IP地址")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(0, 1, newItem)
        newItem = QTableWidgetItem("支持的称重机")
        self.table.setItem(0, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(0, 3, newItem)

        newItem = QTableWidgetItem("打印机配置")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(1, 1, newItem)
        newItem = QTableWidgetItem("称重机串口")
        self.table.setItem(1, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(1, 3, newItem)

        newItem = QTableWidgetItem("订单总数")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(2, 1, newItem)
        newItem = QTableWidgetItem("称重机波特率")
        self.table.setItem(2, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(2, 3, newItem)

        newItem = QTableWidgetItem("每箱数量")
        self.table.setItem(3, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(3, 1, newItem)
        newItem = QTableWidgetItem("最大值(单位/克)")
        self.table.setItem(3, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(3, 3, newItem)

        newItem = QTableWidgetItem("已入箱数量")
        self.table.setItem(4, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(4, 1, newItem)
        newItem = QTableWidgetItem("最小值(单位/克)")
        self.table.setItem(4, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(4, 3, newItem)

        layout.addWidget(self.table, 0, 1, 3, 1)
        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 30)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.gridGroupBox.setLayout(layout)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("提示信息")
        layout = QGridLayout()
        print("info show")

        # weight info
        self.weight_info = QLabel(self)
        self.weight_info.setText("感应器重量检测信息")
        self.weight_info.setFont(QFont("Microsoft YaHei", 15))
        self.weight_info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.weight_info, 0, 0, 1, 1)
        self.weight_info.setStyleSheet("border: 1px solid black")

        # info show
        self.info_show = QTextEdit()
        self.info_show.setPlainText("提示信息显示...")
        self.info_show.setFont(QFont("Microsoft YaHei", 20))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)
        self.info_show.setReadOnly(True)
        layout.addWidget(self.info_show, 1, 0, 1, 1)
        self.info_show.setFocusPolicy(QtCore.Qt.NoFocus)

        # QR code name
        self.qr_cmd_name = QLabel(self)
        self.qr_cmd_name.setText("命令码名称")
        self.qr_cmd_name.setFont(QFont("Microsoft YaHei", 15))
        self.qr_cmd_name.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.qr_cmd_name, 0, 1, 1, 1)
        self.qr_cmd_name.setStyleSheet("border: 1px solid black")

        # QR code show
        self.qr_cmd = QLabel(self)
        self.qr_cmd.setText("命令码")
        self.qr_cmd.setFont(QFont("Microsoft YaHei", 15))
        self.qr_cmd.setAlignment(QtCore.Qt.AlignCenter)
        self.qr_cmd.setStyleSheet("border: 1px solid black")
        layout.addWidget(self.qr_cmd, 1, 1, 1, 1)

        # QR code name
        self.qr_cmd_name2 = QLabel(self)
        self.qr_cmd_name2.setText("命令码")
        self.qr_cmd_name2.setFont(QFont("Microsoft YaHei", 15))
        self.qr_cmd_name2.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.qr_cmd_name2, 0, 2, 1, 1)
        self.qr_cmd_name2.setStyleSheet("border: 1px solid black")

        # QR code show
        self.qr_cmd2 = QLabel(self)
        self.qr_cmd2.setText("命令码")
        self.qr_cmd2.setFont(QFont("Microsoft YaHei", 15))
        self.qr_cmd2.setAlignment(QtCore.Qt.AlignCenter)
        self.qr_cmd2.setStyleSheet("border: 1px solid black")
        layout.addWidget(self.qr_cmd2, 1, 2, 1, 1)

        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 15)
        layout.setColumnStretch(2, 15)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 90)
        self.QGroupBox_info_show.setLayout(layout)

    def create_po_progressbar_show(self):
        self.QGridLayout_po_progress = QGroupBox("订单进度")
        layout = QGridLayout()
        self.procgressbar = QProgressBar(self)
        layout.addWidget(self.procgressbar, 1, 0)
        self.procgressbar.setFont(QFont("Microsoft YaHei", 10))
        self.QGridLayout_po_progress.setLayout(layout)

    def parser_config(self):
        config = "config.ini"
        cur_dir = os.getcwd()
        config_path = os.path.join(cur_dir, config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.gcl_printer_name = conf.get('Printer', 'gcl_printer')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.count_per_carton = conf.get('GclInfo', 'count_one_package')
            self.serialport = conf.get('Weighter', 'serialport')
            self.baudrate = conf.get('Weighter', 'baudrate')
            self.max_weight = conf.get('Weighter', 'max')
            self.min_weight = conf.get('Weighter', 'min')
        else:
            self.info_show.setText(config_path+" 不存在!!!")

    def check_configuration(self):
        t = threading.Thread(target=self.check_configs)
        t.start()

    def check_configs(self):
        msg = "checking configuration"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)

        # 1.check the tn4c.io ip address
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

        # 2.check the po info
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

        # 3.check the gcl printer
        msg = "checking printer"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        printer_list = self.gcl_printer.list()
        if self.gcl_printer_name in printer_list:
            msg = "check printer success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        else:
            msg = "check printer fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return

        # 4.check the Serial port
        msg = "checking serial port"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        system_port_list = self.weighter.port_list()
        print("port check list:", system_port_list)
        if self.serialport in system_port_list:
            msg = "check serial port success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        else:
            msg = "check serial port fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return

        # 5.check baudrate
        msg = "checking baudrate"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        if self.baudrate == "9600":
            msg = "checking baudrate success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        else:
            msg = "checking baudrate fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)

        # 6.check the weighter
        msg = "checking weighter"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        weight = self.weighter.get_weight()
        if weight == None:
            msg = "check weighter fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return
        else:
            msg = "check weighter success"
            data = {"message": msg}
            self._signal_check_config.emit(data)

        # 7.check configuration done
        msg = "check configuration done"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(2)

        # 8.init station
        msg = "init station"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(1)

    def check_config_and_init(self, data):
        text = data
        print("check_config_and_init-----------------------text:", text)
        msg = text['message']

        self.show_po_info()
        if msg == "checking configuration":
            self.info_show.setText("正在检查您的配置信息，请稍等...")
        elif msg == "checking corelight":
            self.info_show.append("\n检查Corelight服务器: "+self.tn4cioip)
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
            self.info_show.append("\n检查打印机: "+self.gcl_printer_name)
        elif msg == "check printer success":
            self.info_show.append("通过")
            self.show_printer_name()
        elif msg == "check printer fail":
            self.info_show.append("错误:")
            self.info_show.append("1.GCL打印机设置错误,请检查确认...")
            self.info_show.append("2.当前打印机设置: "+self.gcl_printer_name)
            self.info_show.append("\n提示:")
            self.info_show.append("1.请使用USB线连接打印机到本电脑")
            self.info_show.append("2.打开Windows控制面板,找到您的打印机名称")
            self.info_show.append("3.找到程序的配置文件config.ini")
            self.info_show.append("4.设置您的打印机到配置文件中的gcl_printer项并保存")
            self.info_show.append("5.重新启动本程序")
            self.info_show.append("\n当前系统打印机列表:")
            printer_list = self.gcl_printer.list()
            for item in printer_list:
                self.info_show.append(str(item))
        elif msg == "checking serial port":
            self.info_show.append("\n检查串口: "+self.serialport)
        elif msg == "check serial port success":
            self.info_show.append("通过")
            self.show_weighter_port()
        elif msg == "check serial port fail":
            self.info_show.append("错误:")
            self.info_show.append("1.当前称重机串口设置错误,请检查确认...")
            self.info_show.append("2.当前串口设置: "+self.serialport)
            self.info_show.append("\n提示:")
            self.info_show.append("1.请使用称重机ES-6KCC串口线连接到本电脑")
            self.info_show.append("2.打开Windows控制面板,找到您当前称重机串口号")
            self.info_show.append("3.找到程序的配置文件config.ini")
            self.info_show.append("4.设置到配置文件中的serialport项并保存")
            self.info_show.append("5.重新启动本程序")
            self.info_show.append("\n当前系统中的串口:")
            port_list = self.weighter.serial_list()
            for item in port_list:
                self.info_show.append(str(item))
                print("port: ",item)
        elif msg =="checking baudrate":
            self.info_show.append("\n检查波特率: "+self.baudrate)
        elif msg == "checking baudrate success":
            self.info_show.append("通过")
            self.show_weighter_baudrate()
        elif msg == "checking baudrate fail":
            self.info_show.append("错误:")
            self.info_show.append("1.当前称重机串口波特率设置错误,请检查确认...")
            self.info_show.append("2.当前波特率设置: "+self.baudrate)
            self.info_show.append("\n提示:")
            self.info_show.append("1.仅支持称重机型号: ES-6KCC")
            self.info_show.append("2.ES-6KCC 波特率应设置为: 9600")
            self.info_show.append("3.找到程序的配置文件config.ini")
            self.info_show.append("4.设置到配置文件中的baudrate项设置并保存")
            self.info_show.append("5.重新启动本程序")
        elif msg == "checking weighter":
            self.info_show.append("\n检查电子秤: ES-6KCC")
        elif msg == "check weighter success":
            self.info_show.append("通过")
            self.show_weighter_name()
        elif msg == "check weighter fail":
            self.info_show.append("错误:")
            self.info_show.append("无法获取称重机数据")
            self.info_show.append("\n提示:")
            self.info_show.append("1.请使用称重机ES-6KCC串口线连接到本电脑")
            self.info_show.append("2.打开称重机电源开关")
            self.info_show.append("3.重新启动本程序")
        elif msg == "check configuration done":
            self.info_show.append("\n检查完成")
        elif msg == "init station":
            self.init_status()

    def init_status(self):
        self.GCLID_RUNNING_MODEL = None
        # show po info
        self.show_po_info()

        # show tn4c.io ip
        self.show_tn4cio_ip()

        # show GCL printer name
        self.show_printer_name()

        # show number per carton
        self.show_total_one_carton()

        # show the count already in gcl
        self.show_num_already_in_gcl()

        # show the po total
        self.show_po_total()

        self.show_weighter_name()
        self.show_weighter_port()
        self.show_weighter_baudrate()
        self.show_weighter_max()
        self.show_weighter_min()
        self.show_qr_cmd_GCL_START()
        self.qr_GCLID_cancel_show()
        self.show_initiation_msg()

    def handle_cmd(self):
        tmp = self.cmd_input.text()
        cmd = tmp.upper()
        log = "gcl station get cmd:"+cmd
        print(log)
        logging.debug(log)
        self.cmd_input.clear()

        if cmd == "GCLID_START":
            self.GCLID_RUNNING_MODEL = "GCLID_START"
            self.info_show.clear()
            self.cartoning = None
            self.cartoning = Cartoning()
            self.cartoning._signal_cartoning.connect(self.update_ui_and_info_show)
            self.qr_CMD_init_show()
            self.qr_GCLID_cancel_show()
            self.gcl_array.clear()
        elif cmd == "GCLID_END":
            self.GCLID_RUNNING_MODEL = "GCLID_END"
            self.cartoning.cartoning_end()
        elif cmd == "GCLID_CANCEL":
            self.cartoning.cartoning_cancel()
        elif cmd == "RESET_GCLID":
            self.GCLID_RUNNING_MODEL = "RESET_GCLID"
            self.info_show.setText("重置整箱模式")
            self.info_show.append("\n提示:")
            self.info_show.append("1.请扫描箱号")
            self.info_show.append("2.或者扫描箱中任意一个感应器MAC地址")
            self.info_show.append("\n如果您需要结束当前操作,请扫描结束命令码...")
            self.gclid_reset_all = gclid_reset_all()
            self.qr_GCLID_END_show()
        elif cmd == "RESET_PARTIAL_SENSOR":
            self.GCLID_RUNNING_MODEL = "RESET_PARTIAL_SENSOR"
            self.info_show.setText("部分重置入箱模式")
            self.info_show.append("\n作业提示:")
            self.info_show.append("请扫描需要重置入箱的感应器MAC地址")
            self.gclid_reset_part = gclid_reset_part()
            self.qr_GCLID_RESET_PART_confirm_show()
            self.qr_GCLID_RESET_PART_cancel_show()
        elif cmd == "GCLID_REPACKAGE":
            self.GCLID_RUNNING_MODEL = "GCLID_REPACKAGE"
            self.info_show.setText("重新入箱模式")
            self.info_show.append("\n提示:")
            self.info_show.append("1.请扫描需要重入箱中的任意一个感应器的MAC地址")
            self.info_show.append("\n如果您需要结束当前操作,请扫描结束命令码...")
            self.qr_GCLID_END_show()
            self.gcl_array.clear()
        elif cmd == "REPRINT_GCLID":
            self.GCLID_RUNNING_MODEL = "REPRINT_GCLID"
            self.gclid_reprint = gclid_reprint()
            self.info_show.setText("重打印GCL模式")
            self.info_show.append("\n提示:")
            self.info_show.append("1.请扫描需要重新打印箱号条码")
            self.info_show.append("2.或者扫描GCL中任意一个感应器MAC地址")
            self.info_show.append("\n如果您需要结束当前操作,请扫描结束命令码...")
            self.qr_GCLID_END_show()
        elif self.GCLID_RUNNING_MODEL == "GCLID_START":
            mac = cmd
            self.cartoning.cartoning_start(mac)
        elif self.GCLID_RUNNING_MODEL == "RESET_GCLID":
            self.gcl_reset_all(cmd)
        elif self.GCLID_RUNNING_MODEL == "RESET_PARTIAL_SENSOR":
            if cmd == "GCLID_RESET_PART_CONFIRM":
                self.gclid_reset_part_start()
            elif cmd == "GCLID_RESET_PART_CANCEL":
                self.gclid_reset_part_cancel()
            else:
                mac = cmd
                self.add_mac_for_gclid_reset_part(mac)
        elif self.GCLID_RUNNING_MODEL == "GCLID_REPACKAGE":
            mac = cmd
            self.gcl_repackage(mac)
        elif self.GCLID_RUNNING_MODEL == "REPRINT_GCLID":
            self.reprint_gclid(cmd)
        else:
            log = "not supported cmd:"+cmd
            print(log)
            logging.debug(log)
            self.info_show.setText("错误:")
            self.info_show.append("无效的命令码:"+cmd)
            self.timer = QTimer()
            self.timer.setInterval(1000)
            self.timer.start()
            self.timer.timeout.connect(self.onTimerOut)

    def gclid_label_preview(self, img):
        file = img
        img = QImage(file, 'PNG')
        width = self.info_show.width()
        preview = img.scaledToWidth(width)
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertImage(preview)

    def onTimerOut(self):
        self.timer.stop()
        self.init_status()

    def check_mac_in_current_gcllist(self, mac):
        if mac in self.gcl_array:
            print("already exist in the gcl list")
            self.info_show.setText("MAC:"+mac+" 已经存在当前的列表中")
            return True
        else:
            return False

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

    def gcl_reset_all(self, cmd):
        ret = self.gclid_reset_all.reset_all(cmd)
        if ret is None:
            self.info_show.setText("重置箱号网络错误")
        elif ret == False:
            self.info_show.setText("重置箱号网络错误")
        elif ret == "corelight return data error":
            self.info_show.setText("重置箱号网络错误")
        elif ret == "no sensor in current gclid":
            self.info_show.setText("当前的箱号中不存在感应器")
        elif ret == "find mac fail":
            self.info_show.setText("当前感应器MAC: "+cmd+" 不存在数据库中")
        elif ret == "sensor not in gcl":
            self.info_show.setText("当前感应器MAC: " + cmd + " 还没有入箱")
        elif ret == "gcl reset all fail":
            self.info_show.setText("重置箱号错误")
        else:
            reset_gcl_id = ret['reset_gcl_id']
            reset_gcl_count = ret['reset_gcl_count']
            self.info_show.setText("重置箱号完成:")
            self.info_show.append("重置箱号: "+reset_gcl_id)
            self.info_show.append("重置数量: " + reset_gcl_count)

        self.show_num_already_in_gcl()
        self.info_show.append("\n即将5秒后自动回到初始状态...")
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def add_mac_for_gclid_reset_part(self, macaddress):
        mac = macaddress
        log = "gclid reset part sensor mac:"+mac
        print(log)
        logging.debug(log)

        ret = self.gclid_reset_part.set_gcl_reset_part_list(mac)
        if ret == "already in list":
            self.info_show.setText("当前MAC: "+mac+" 已经扫描\n")
        elif ret == "not exist":
            self.info_show.setText("当前MAC: " + mac + " 数据库中不存在\n")
        elif ret == "not in gcl":
            self.info_show.setText("当前MAC: " + mac + " 还未入箱\n")
        elif ret == True:
            self.info_show.setText("确认重置请扫描确认命令码，取消操作请扫描取消命令码\n")

        mac_list = self.gclid_reset_part.get_gcl_reset_part_list()
        count = len(mac_list)
        self.info_show.append("重置感应器，数量: "+str(count)+" 详细列表:")
        for item in mac_list:
            self.info_show.append(item)

    def gclid_reset_part_start(self):
        ret = self.gclid_reset_part.do_gclid_reset_part()
        if ret == False:
            pass
        else:
            gclid = ret['gclid']
            reset_count = ret['reset_count']
            gcl_count = ret['gcl_count']

            self.info_show.setText("重置感应器完成:\n")
            self.info_show.append("重置箱号: "+str(gclid))
            self.info_show.append("重置数量: "+str(reset_count))
            self.info_show.append("剩余数量: "+str(gcl_count))

        self.info_show.append("即将5秒后自动回到初始状态")
        self.show_num_already_in_gcl()
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def gclid_reset_part_cancel(self):
        self.info_show.setText("取消重置GCL:")
        self.gclid_reset_part.clear_gcl_reset_part_list()
        self.show_num_already_in_gcl()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def gcl_repackage(self, macaddress):
        mac = macaddress
        log = "start gcl_repackage mac:"+mac
        print(log)
        logging.debug(log)

        gcl_count = len(self.gcl_array)
        # first time get the mac list info by macaddress
        if gcl_count == 0:
            ret = self.net.get_gcl_info_by_mac(mac)
            if ret != None:
                print(ret)
                text = json.loads(ret)
                result = text['result']
                msg_type = text['messages'][0]['type']
                msg = text['messages'][0]['message']
                if result == "ok":
                    gcl_id = text['messages'][0]['gcl_id']
                    mac_list = text['messages'][0]['gcl_mac_list']
                    count =  len(mac_list)
                    self.info_show.setText("重入箱模式,当前GCL箱号: "+gcl_id+" 数量: "+str(count)+" 个")
                    print("get mac list:------", mac_list)

                    for mac in mac_list:
                        self.gcl_array.append(mac)
                    self.show_num_already_in_gcl()
                elif result == "fail":
                    if msg == "find mac fail":
                        self.info_show.setText("当前感应器MAC: "+mac+" 不在数据库中")
                    elif msg == "sensor not in gcl":
                        self.info_show.setText("当前感应器MAC: "+mac+" 还没有入箱")
            else:
                self.info_show.setText("重入箱网络错误")
            self.info_show.append("\n提示:")
            self.info_show.append("1.继续尝试扫描其他感应器的MAC地址...")
            self.info_show.append("2.如果您需要结束当前操作,请扫描以下命令码...")
            self.qr_GCLID_END_show()
        # this time, we add new sensor mac into the self.gcl_array
        elif gcl_count >= 1:
            print("gcl repackage mode add mac")
            check = self.mac_check(mac)
            if check is False:
                self.info_show.setText("重入箱模式,无效的MAC地址: "+mac)
                self.info_show.append("\n提示:")
                self.info_show.append("继续尝试扫描其他感应器的MAC地址...")
                return False
            else:
                if self.check_mac_in_current_gcllist(mac) == False:
                    self.gcl_array.append(mac)
                    count = len(self.gcl_array)
                    self.info_show.setText("重入箱模式,添加MAC地址: "+mac+" 数量: "+str(count))
                    self.show_num_already_in_gcl()
            self.info_show.append("\n提示:")
            self.info_show.append("如果您需要结束当前入箱,重新生成GCL然后打印,请扫描以下命令码...")
            self.qr_GCLID_END_show()

    def reprint_gclid(self, cmd):
        ret = self.gclid_reprint.get_file(cmd)
        print("------------------reprint_gclid------------------ret:", ret)

        if ret == None or ret == False:
            self.info_show.setText("错误:")
            self.info_show.append("网络错误")
        elif ret == "corelight return data is none":
            self.info_show.setText("错误:")
            self.info_show.append("服务器返回错误")
        elif ret == "not valid macaddress":
            self.info_show.setText("错误:")
            self.info_show.append("无效的MAC地址: "+cmd)
        elif ret == "gclid not valid":
            self.info_show.setText("错误:")
            self.info_show.append("无效的箱号: "+cmd)
        elif ret == "find mac fail":
            self.info_show.setText("错误:")
            self.info_show.append("当前MAC: " +cmd+" 不在订单中")
        elif ret == "sensor not in gcl":
            self.info_show.setText("错误:")
            self.info_show.append("当前MAC: " +cmd+" 还未入箱")
        elif ret == "gcl file not fond":
            self.info_show.setText("错误:")
            self.info_show.append("当前MAC: " +cmd+" 对应的GCL文件找不到")
        else:
            filepath_list = ret
            count = len(filepath_list)
            self.info_show.setText("重打印GCL成功")
            self.info_show.append("\nGCL数量: " + str(count))
            for filepath in filepath_list:
                filename = os.path.basename(filepath)
                self.info_show.append(filename)
            self.info_show.append("\n")

            for filepath in filepath_list:
                self.gclid_label_preview(filepath)
                self.gclid_reprint.print(filepath)

        self.info_show.append("\n5秒后自动回到初始界面")
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def clear_show_weight_intime(self):
        self.weight_info.setText("感应器重量检测信息")
        self.weight_info.setStyleSheet("border: 1px solid black; color:black")

    def check_weight_valid(self, sensor_weight):
        weight = sensor_weight
        weight = float(weight)

        if weight < 0:
            self.info_show.setText("错误:")
            self.info_show.append("1.当前称重: "+str(weight))
            self.info_show.append("2.请将移除电子称上物品，然后设置归零")
            self.info_show.append("3.重新称重")
            return False

        if weight < 0.5:
            self.info_show.setText("提示:")
            self.info_show.append("1.当前称重: "+str(weight))
            self.info_show.append("2.请将感应器放置电子称上称重")
            return False

        if weight >= float(self.min_weight) and weight <= float(self.max_weight):
            self.info_show.setText("提示:")
            self.info_show.append("当前称重: "+str(weight))
            count = len(self.gcl_array)
            self.info_show.append("当前入箱数量: "+str(count))
            self.info_show.append("\n如果您需要结束当前操作,请扫描以下命令码...")
            self.qr_GCLID_END_show()
            return True
        else:
            self.info_show.setText("错误:")
            self.info_show.append("该感应器重量异常，请检查包装是否缺件")
            self.info_show.append("\n当前称重: "+str(weight))
            self.info_show.append("最小值: "+str(self.min_weight))
            self.info_show.append("最大值: "+str(self.max_weight))
            self.info_show.append("\n如果您需要结束当前操作,请扫描以下命令码...")
            self.qr_GCLID_END_show()
            return False

    def show_initiation_msg(self):
        self.info_show.setText("作业提示:")
        self.info_show.append("请扫描右侧命令码开始入箱")

    def show_po_info(self):
        info = "订单: "+self.pokey+"-"+self.countrycode+"-"+self.hwversion
        self.po_info.setText(info)

    def show_tn4cio_ip(self):
        val = QTableWidgetItem(self.tn4cioip)
        self.table.setItem(0, 1, val)

    def show_printer_name(self):
        val = QTableWidgetItem(self.gcl_printer_name)
        self.table.setItem(1, 1, val)
    
    def show_po_total(self):
        obj = self.net.get_po_info()
        if obj == None:
            self.info_show.setText("GCL获取PO信息,解析JSON数据错误!")
            return
        text = json.loads(obj)
        result = text['result']
        msg_type = text['messages'][0]['type']

        if result == "fail":
            self.info_show.setText("错误:当前的订单不存在，请检查您的设置信息")
        elif result == "ok":
            total = text['messages'][0]['total']
            desc = text['messages'][0]['description']
            # show the total number
            tmp = QTableWidgetItem(str(total))
            self.table.setItem(2, 1, tmp)

    def show_total_one_carton(self):
        val = QTableWidgetItem(str(self.count_per_carton))
        self.table.setItem(3, 1, val)

    def show_num_already_in_gcl(self):
        ret = self.net.get_count_already_in_gcl()
        if ret != None:
            text = json.loads(ret)
            result = text['result']
            msg_type = text['messages'][0]['type']
            msg = text['messages'][0]['message']
            if result == "ok":
                total = text['messages'][0]['total']
                count = text['messages'][0]['count_gcl']
                tmp = QTableWidgetItem(str(count))
                self.table.setItem(4, 1, tmp)

                process = int(count)*100 // int(total)
                self.show_po_process(process)
        else:
            pass

    def show_weighter_name(self):
        name = "ES-6KCC"
        item = QTableWidgetItem(name)
        self.table.setItem(0, 3, item)

    def show_weighter_port(self):
        port = self.serialport
        item = QTableWidgetItem(port)
        self.table.setItem(1, 3, item)

    def show_weighter_baudrate(self):
        baudrate = self.baudrate
        item = QTableWidgetItem(baudrate)
        self.table.setItem(2, 3, item)
    
    def show_weighter_max(self):
        val = self.max_weight
        item = QTableWidgetItem(val)
        self.table.setItem(3, 3, item)

    def show_weighter_min(self):
        val = self.min_weight
        item = QTableWidgetItem(val)
        self.table.setItem(4, 3, item)

    def show_qr_cmd_GCL_START(self):
        self.qr_cmd_name.setText("开始封箱命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('GCLID_START')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "GCLID_START.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def qr_GCLID_END_show(self):
        self.qr_cmd_name.setText("确认封箱命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('GCLID_END')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "GCLID_END.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def qr_CMD_init_show(self):
        self.qr_cmd_name.setText("命令码名称")
        self.qr_cmd.setText("无")

    def qr_GCLID_RESET_PART_confirm_show(self):
        self.qr_cmd_name.setText("确认重置命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('GCLID_RESET_PART_CONFIRM')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "GCLID_RESET_PART_CONFIRM.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def qr_GCLID_RESET_PART_cancel_show(self):
        self.qr_cmd_name2.setText("取消重置命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('GCLID_RESET_PART_CANCEL')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "GCLID_RESET_PART_CANCEL.png")
        img.save(img_path)

        if os.path.exists(img_path):
            tmp = QPixmap(img_path)
            self.qr_cmd2.setPixmap(tmp)
            os.remove(img_path)

    def qr_GCLID_cancel_show(self):
        self.qr_cmd_name2.setText("取消封箱命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('GCLID_CANCEL')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "GCLID_CANCEL.png")
        img.save(img_path)

        if os.path.exists(img_path):
            tmp = QPixmap(img_path)
            self.qr_cmd2.setPixmap(tmp)
            os.remove(img_path)

    def show_po_process(self, value):
        val = int(value)
        if val <= 0:
            val = 0

        if val >= 100:
            val = 100
        self.procgressbar.setValue(val)

    def check_and_show_weight_intime(self, value):
        weight = value
        weight = float(weight)

        if weight < 0:
            info= "当前称重: "+str(weight)+" 请将移除电子称上物品，然后设置归零"
        elif weight < 0.5:
            info = "当前感应器重量: " + str(weight) + " ,请将感应器放置电子称上称重"
            self.weight_info.setStyleSheet("border: 1px solid black; color:red")
        elif weight >= float(self.min_weight) and weight <= float(self.max_weight):
            info = "当前感应器重量: "+str(weight)+" ,该感应器重量正常，请扫描MAC地址"
            self.weight_info.setStyleSheet("border: 1px solid black; color:green")
        else:
            info = "当前感应器重量: " + str(weight)+" 不符合设定范围, 该感应器重量异常，请检查包装是否缺件"
            self.weight_info.setStyleSheet("border: 1px solid black; color:red")
        self.weight_info.setText(info)

    def update_ui_and_info_show(self, data: dict):
        text = data
        print(text)
        logging.debug(text)

        try:
            msg = text['message']

            if msg == "macaddress check is not valid":
                macaddress = text['macaddress']
                self.info_show.setText("错误:")
                self.info_show.append("MAC: " + macaddress + " 不是有效的MAC地址")
            elif msg == "macaddress already in cartoning list":
                macaddress = text['macaddress']
                self.info_show.setText("MAC: " + macaddress + "已经存在当前的列表中")
            elif msg == "pre station done check success":
                self.info_show.append("整机FTS测试检查通过")
            elif msg == "pre station done check fail":
                macaddress = text['macaddress']
                self.info_show.setText("错误:")
                self.info_show.append("MAC: " + macaddress + " 整机FTS测试未完成，请检查确认")
            elif msg == "macaddress is already cartoned":
                macaddress = text['macaddress']
                self.info_show.setText("MAC: "+ macaddress + " 已经入箱")
            elif msg == "macaddress is not found in current po":
                macaddress = text['macaddress']
                self.info_show.setText("MAC: "+ macaddress + "不在当前的订单中")
            elif msg == "macaddress added in cartoning list success":
                macaddress = text['macaddress']
                total = text['total']
                maclist = text['maclist']
                self.info_show.setText("入箱MAC: " + macaddress + " 数量: " + total)

                cursor = self.info_show.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText("\n\n")
                # self.info_show.setFont(QFont("Microsoft YaHei", 15))
                data_str = None
                for mac in maclist:
                    if data_str is None:
                        data_str = mac
                    else:
                        data_str = data_str + " - " + mac
                cursor.insertText(data_str)
            elif msg == "download carton label success":
                filename = text['filename']
                self.info_show.setText(filename)
                self.info_show.append("打印包箱条码完成，请将该感应器按要求放入大包箱")
                self.info_show.append("并按要求将包箱条码粘贴到大包箱上")
                self.gclid_label_preview(filename)
            elif msg == "update sensor weight intime":
                weight = text['weight']
                self.check_and_show_weight_intime(weight)
            elif msg == "thread get sensor weight already stoped":
                self.clear_show_weight_intime()
            elif msg == "cartoning end":
                self.info_show.setText("正在结束入箱，请等待完成")
            elif msg == "carton is full catroning auto end":
                total = text['total']
                self.info_show.setText("该箱已满，正在结束入箱，请等待自动完成，数量: " + total)
            elif msg == "cartoning end done":
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "cartoning cancel done":
                self.info_show.setText("取消入箱操作")
                self.timer = QTimer()
                self.timer.setInterval(2000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            else:
                print("message not support:", msg)
        except Exception as e:
            print(e)
            logging.debug(e)

    def stop_all_thread(self):
        try:
            self.cartoning.cartoning_cancel()
        except Exception:
            pass
