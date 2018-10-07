# -*- coding: utf-8 -*-
import os
import sys
import signal
import threading
from threading import Timer
from time import *
import time
import socket
import re
import json
import configparser
import qrcode
import logging

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
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QPixmap
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

from station_oqc.net import network
from station_oqc.sensor_type import sensor_type
from station_oqc.gateway_h10 import GatewayH10
from station_oqc.doorwindow import DoorWindow
from station_oqc.waterleakage import WaterLeakage
from station_oqc.temperature import Temperature
from station_oqc.motiondetector import MotionDetectot


class FACTORY_OQC(QDialog):
    _signal_check_config = QtCore.pyqtSignal(dict)
    _signal_update_ui_and_info = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(FACTORY_OQC, self).__init__(parent)
        self._signal_check_config.connect(self.check_config_and_init)
        self._signal_update_ui_and_info.connect(self.update_ui_and_info_show)
        self.timer = None
        self.RefTemperature = None
        self.TempRefRange = None
        self.useRefdefaultvaule = None
        self.initUI()
        self.init_data()

        obj = sensor_type()
        self.sensor_type = obj.get_sensor_type()
        if self.sensor_type == "DoorWindow":
            self.doorwindow_sensor = DoorWindow()
            self.doorwindow_sensor._signal_doorwindow.connect(self.update_ui_and_info_show)
        elif self.sensor_type == "WaterLeakage":
            self.waterleakage_sensor = WaterLeakage()
            self.waterleakage_sensor._signal_waterleakage.connect(self.update_ui_and_info_show)
        elif self.sensor_type == "Temperature":
            self.temperature_sensor = Temperature()
            self.temperature_sensor._signal_temperature.connect(self.update_ui_and_info_show)
        elif self.sensor_type == "MotionDetector":
            pass
        else:
            print("can't support the sensor type!!!")
            pass

    def initUI(self):
        self.create_cmd_input()
        self.create_status_show()
        self.create_info_show()
        self.create_po_progressbar_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox_test_status)
        mainLayout.addWidget(self.QGroupBox_info_show)
        mainLayout.addWidget(self.QGridLayout_po_progress)

        mainLayout.setStretchFactor(self.gridGroupBox, 25)
        mainLayout.setStretchFactor(self.formGroupBox_test_status, 5)
        mainLayout.setStretchFactor(self.QGroupBox_info_show, 65)
        mainLayout.setStretchFactor(self.QGridLayout_po_progress, 5)

        self.setLayout(mainLayout)

    def init_data(self):
        self.parser_config()
        self.net = network()
        self.gateway_h10 = GatewayH10()
        self.RUNNING_MODE = None
        self.check_configuration()

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        station_info = QLabel("工站: 工厂OQC")
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

        self.table = QTableWidget(3, 4)
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
        newItem = QTableWidgetItem("None")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("H10网关IP")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("订单总数")
        self.table.setItem(0, 2, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(0, 3, newItem)

        newItem = QTableWidgetItem("OQC已测试")
        self.table.setItem(1, 2, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(1, 3, newItem)

        newItem = QTableWidgetItem("温度参考值(单位/度)")
        self.table.setItem(2, 2, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(2, 3, newItem)

        layout.addWidget(self.table, 0, 1, 3, 1)
        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 30)
        self.gridGroupBox.setLayout(layout)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)

    def create_status_show(self):
        self.formGroupBox_test_status = QGroupBox("测试状态")
        layout = QFormLayout()

        self.test_result = QLabel(self)
        self.test_result.setStyleSheet(
            '''color: black; background-color: gray''')
        info = '测试状态'
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)
        layout.addRow(self.test_result)
        self.formGroupBox_test_status.setLayout(layout)

    def create_info_show(self):
        # info show
        self.QGroupBox_info_show = QGroupBox("作业信息")
        layout = QGridLayout()
        self.info_show = QTextEdit()
        self.info_show.setPlainText("提示信息")
        self.info_show.setFont(QFont("Microsoft YaHei", 20))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)
        self.info_show.setReadOnly(True)
        self.info_show.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(self.info_show, 0, 0, 2, 1)

        # sensor info name
        self.sensor_info_name = QLabel(self)
        self.sensor_info_name.setText("感应器信息")
        self.sensor_info_name.setFont(QFont("Microsoft YaHei", 15))
        self.sensor_info_name.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.sensor_info_name, 0, 1, 1, 1)
        self.sensor_info_name.setStyleSheet("border: 1px solid black")

        # sensor info
        self.sensor_info = QLabel(self)
        self.sensor_info.setText("无")
        self.sensor_info.setFont(QFont("Microsoft YaHei", 15))
        self.sensor_info.setAlignment(QtCore.Qt.AlignCenter)
        self.sensor_info.setStyleSheet("border: 1px solid black")
        layout.addWidget(self.sensor_info, 1, 1, 1, 1)

        # QR code name
        self.qr_cmd_name = QLabel(self)
        self.qr_cmd_name.setText("命令码名称")
        self.qr_cmd_name.setFont(QFont("Microsoft YaHei", 15))
        self.qr_cmd_name.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.qr_cmd_name, 0, 2, 1, 1)
        self.qr_cmd_name.setStyleSheet("border: 1px solid black")

        # QR code show
        self.qr_cmd = QLabel(self)
        self.qr_cmd.setText("无")
        self.qr_cmd.setFont(QFont("Microsoft YaHei", 15))
        self.qr_cmd.setAlignment(QtCore.Qt.AlignCenter)
        self.qr_cmd.setStyleSheet("border: 1px solid black")
        layout.addWidget(self.qr_cmd, 1, 2, 1, 1)

        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 15)
        layout.setColumnStretch(2, 15)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 90)
        self.QGroupBox_info_show.setLayout(layout)

    def create_po_progressbar_show(self):
        self.QGridLayout_po_progress = QGroupBox("OQC测试率(测试/总数)")
        layout = QGridLayout()
        self.progressbar = QProgressBar(self)
        layout.addWidget(self.progressbar, 1, 0)
        self.progressbar.setFont(QFont("Microsoft YaHei", 10))
        self.QGridLayout_po_progress.setLayout(layout)

    def parser_config(self):
        config = "config.ini"
        cur_dir = os.getcwd()
        config_path = os.path.join(cur_dir, config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.gateway_h10_ip = conf.get('Gateway_H10', 'ip')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.TempRefRange = conf.get('TemperatureRef', 'range')
            self.useRefdefaultvaule = conf.get('TemperatureRef', 'usedefaultvalue')
            self.Refdefaultvaule = conf.get('TemperatureRef', 'defaultvalue')
        else:
            pass

    def check_configuration(self):
        print("check_configuration")
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
            msg = "check corelight ip success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        else:
            msg = "check corelight ip fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return
        sleep(0.1)

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

        # 3. check the gateway(H10)
        msg = "checking gateway"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        ret = self.gateway_h10.Get_Facility()
        if ret == None:
            msg = "check gateway fail"
            data = {"message": msg}
            self._signal_check_config.emit(data)
            return
        else:
            msg = "check gateway success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        sleep(0.1)

        # clean up the H10 gateway when start
        msg = "init gateway"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        self.gateway_h10.clean_up()
        sleep(0.1)

        if self.sensor_type == "Temperature":
            if self.useRefdefaultvaule == "yes":
                pass
            else:
                TemperatureSensor = Temperature()
                ret = TemperatureSensor.check_reference_sensor_exist()
                if ret is True:
                    msg = "check reference TemperatureSensor success"
                    data = {"message": msg}
                    self._signal_check_config.emit(data)
                else:
                    msg = "check reference TemperatureSensor fail"
                    data = {"message": msg}
                    self._signal_check_config.emit(data)
                    return
                sleep(0.1)

        msg = "check configuration done"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(2)

        msg = "init station"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(2)

    def check_config_and_init(self, data):
        print("check config and init status:", data)
        text = data
        msg = text['message']

        self.show_po_info()
        self.show_qr_cmd_pair_start()
        print("---- check_config_and_init msg:", msg)
        if msg == "checking configuration":
            self.info_show.setText("正在检查您的配置信息，请稍等...")
        elif msg == "checking corelight":
            self.info_show.append("\n检查Corelight服务器: " + self.tn4cioip)
        elif msg == "check corelight ip success":
            self.info_show.append("通过")
            self.show_tn4cio_ip()
        elif msg == "check corelight ip fail":
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
            self.show_po_total()
            self.show_produced_sensor_number_and_progress()
        elif msg == "check poinfo fail":
            self.info_show.append("错误:")
            self.info_show.append("订单信息设置错误,请检查确认...")
            self.info_show.append("\n订单设置:")
            self.info_show.append("订单号: "+self.pokey)
            self.info_show.append("国家代码: "+self.countrycode)
            self.info_show.append("硬件版本: "+self.hwversion)
            self.info_show.append("\n提示:")
            self.info_show.append("1.找到程序的配置文件config.ini")
            self.info_show.append("2.设置正确的订单信息并保存")
            self.info_show.append("3.重新启动程序")
        elif msg == "checking gateway":
            self.info_show.append("\n检查网关: "+self.gateway_h10_ip)
        elif msg == "check gateway success":
            self.info_show.append("通过")
            self.show_gatewayH10_ip()
        elif msg == "check gateway fail":
            self.info_show.append("错误:")
            self.info_show.append("1.网关设置错误,请检查确认...")
            self.info_show.append("2.当前网关IP地址设置: "+self.gateway_h10_ip)
            self.info_show.append("\n提示:")
            self.info_show.append("1.请确认网关电源打开，连接到网络")
            self.info_show.append("2.确认网关的IP地址，并且设置到config.ini配置文件中的Gateway_H10项并保存")
            self.info_show.append("3.检查网关网络是否正常")
            self.info_show.append("4.重新启动本程序")
        elif msg == "init gateway":
            self.info_show.append("\n正在初始化网关")
        elif msg == "check reference TemperatureSensor success":
            self.info_show.append("通过")
        elif msg == "check reference TemperatureSensor fail":
            self.info_show.append("错误:")
            self.info_show.append("参考温度感应器不存在，请先扫命令码配对温度参考感应器")
            self.show_qr_cmd_pair_reference_start()
        elif msg == "check configuration done":
            self.info_show.append("\n检查完成")
        elif msg == "init station":
            self.init_status()

    def init_status(self):
        self.RUNNING_MODE = None
        self.update_status_show("init")
        self.show_tn4cio_ip()
        self.show_gatewayH10_ip()
        self.show_po_info()
        self.show_po_total()
        self.show_produced_sensor_number_and_progress()
        self.show_initation_msg()
        self.show_qr_cmd_pair_start()

    def set_focus(self):
        self.cmd_input.setFocus()

    def handle_cmd(self):
        cmd = self.cmd_input.text()
        cmd = cmd.upper()
        print('get cmd:'+cmd)
        # clean data first before show
        self.cmd_input.clear()
        self.info_show.clear()

        if cmd == "CMD_ASSEMBLY_PAIR_START":
            self.testing_thread_start()
        elif cmd == "CMD_COMFIRM_FUNCTION_TEST_FAIL":
            self.confirm_function_test_fail()
        elif cmd == "CMD_PAIRING_REF_SNESOR_START":
            temperature_sensor = Temperature()
            temperature_sensor._signal_temperature.connect(self.update_ui_and_info_show)
            t = threading.Thread(target=temperature_sensor.pairing_reference_temperature_sensor)
            t.start()
        elif cmd == "CMD_EXIT_QA_TEST":
            self.exit_qa_testing()
        else:
            self.info_show.setText("错误提示:")
            self.info_show.append("命令码: "+cmd+" 不支持,请根据作业指导书进行操作!")
            self.timer = QTimer()
            self.timer.setInterval(1000)
            self.timer.start()
            self.timer.timeout.connect(self.onTimerOut)

    def onTimerOut(self):
        self.timer.stop()
        self.init_status()

    def update_status_show(self, status='None'):
        print("update status show: "+status)
        if status == "init":
            info = '请开始测试'
            self.test_result.setStyleSheet(
                '''color: black; background-color: gray''')
        elif status == "testing":
            info = "测试中"
            self.test_result.setStyleSheet(
                '''color: black; background-color: yellow''')
        elif status == "pass":
            info = "测试通过"
            self.test_result.setStyleSheet(
                '''color: black; background-color: green''')
        elif status == "fail":
            info = '测试失败'
            self.test_result.setStyleSheet(
                '''color: black; background-color: red''')
        else:
            info = '未知状态'
            self.test_result.setStyleSheet(
                '''color: black; background-color: gray''')
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

    def show_tn4cio_ip(self):
        val = QTableWidgetItem(self.tn4cioip)
        self.table.setItem(0, 1, val)

    def show_gatewayH10_ip(self):
        val = QTableWidgetItem(self.gateway_h10_ip)
        self.table.setItem(1, 1, val)

    def show_produced_sensor_number_and_progress(self):
        ret = self.net.get_tested_sensors_info()
        if ret != None:
            text = json.loads(ret)
            result = text['result']
            if result == 'ok':
                total = text['messages'][0]['total']
                tested = text['messages'][0]['tested']

                item = QTableWidgetItem(str(tested))
                self.table.setItem(1, 3, item)

                process = int(tested)*100 // int(total)
                self.show_po_process(process)
            else:
                pass
        else:
            pass

    def show_Ref_temperature(self, temp: str):
        val = QTableWidgetItem(temp)
        self.table.setItem(2, 3, val)

    def show_po_info(self):
        if self.pokey != None and self.countrycode != None and self.hwversion != None:
            info = "订单: "+self.pokey+"-"+self.countrycode+"-"+self.hwversion
            self.po_info.setText(info)
        else:
            pass

    def show_po_total(self):
        ret = self.net.get_po_info()
        if ret != None:
            text = json.loads(ret)
            result = text['result']
            if result == "ok":
                total = text['messages'][0]['total']
                desc = text['messages'][0]['description']
                tmp = QTableWidgetItem(str(total))
                self.table.setItem(0, 3, tmp)
            else:
                pass
        else:
            pass

    def show_initation_msg(self):
        self.info_show.setText("作业提示:")
        self.info_show.append("请将待测试单板置于测试治具上，并扫描右侧启动配对命令码开始测试")
        self.info_show.append("(详情请参考SOP)")

    def show_qr_cmd_pair_start(self):
        self.qr_cmd_name.setText("配对启动命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('CMD_ASSEMBLY_PAIR_START')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "CMD_ASSEMBLY_PAIR_START.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def show_qr_cmd_pair_reference_start(self):
        self.qr_cmd_name.setText("温度参考配对命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('CMD_PAIRING_REF_SNESOR_START')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "CMD_PAIRING_REF_SNESOR_START.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def show_qr_cmd_failed_confirm(self):
        self.qr_cmd_name.setText("功能测试失败确认命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('CMD_COMFIRM_FUNCTION_TEST_FAIL')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "CMD_COMFIRM_FUNCTION_TEST_FAIL.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def show_qr_init_cmd(self):
        self.qr_cmd_name.setText("命令码名称")
        self.qr_cmd.setText("无")

    def testing_thread_start(self):
        self.show_qr_init_cmd()
        self.thread_for_testing = threading.Thread(target=self.start_testing)
        self.thread_for_testing.start()

    def testing_thread_stop(self):
        pass

    def start_testing(self):
        try:
            if self.sensor_type == "DoorWindow":
                self.doorwindow_sensor.function_test_start()
            elif self.sensor_type == "WaterLeakage":
                self.waterleakage_sensor.function_test_start()
            elif self.sensor_type == "Temperature":
                self.temperature_sensor.function_test_start()
            elif self.sensor_type == "MotionDetector":
                # fixme
                pass
            else:
                print("can't support the sensor type!!!")
                pass
            self.gateway_h10.clean_up()
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def confirm_function_test_fail(self):
        print("function test failed confirm")

        if self.sensor_type == "DoorWindow":
            self.doorwindow_sensor.set_function_test_confirm_failed()
        elif self.sensor_type == "WaterLeakage":
            self.waterleakage_sensor.set_function_test_confirm_failed()
        elif self.sensor_type == "Temperature":
            pass
        elif self.sensor_type == "MotionDetector":
            pass
        else:
            print("can't support the sensor type!!!")
            pass

        self.info_show.setText("\n提示:")
        self.info_show.append("确认功能测试失败，请将该单板送至维修工站维修")
        self.info_show.append("然后扫描确认命令码开始下一台测试")
        self.info_show.append("(详情请参考SOP)")
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

    def exit_qa_testing(self):
        if self.sensor_type == "DoorWindow":
            self.doorwindow_sensor.exit_qa_longtime_testing()
        elif self.sensor_type == "WaterLeakage":
            self.waterleakage_sensor.exit_qa_longtime_testing()
        elif self.sensor_type == "Temperature":
            self.temperature_sensor.exit_qa_longtime_testing()
        elif self.sensor_type == "MotionDetector":
            # fixme
            pass
        else:
            print("not support the sensor type!")
            pass

    def show_qr_cmd_exit_qa_test(self):
        self.qr_cmd_name.setText("退出QA测试命令码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('CMD_EXIT_QA_TEST')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "CMD_EXIT_QA_TEST.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def show_sensor_info(self, info):
        self.sensor_info.setAlignment(QtCore.Qt.AlignLeft)
        self.sensor_info.setAlignment(QtCore.Qt.AlignVCenter)
        self.sensor_info_name.setText("感应器信息")
        self.sensor_info.setText(info)

    def clear_sensor_info(self):
        self.sensor_info.setAlignment(QtCore.Qt.AlignCenter)
        self.sensor_info_name.setText("感应器信息")
        self.sensor_info.setText("无")

    def show_po_process(self, value):
        val = int(value)
        if val <= 0:
            val = 0

        if val >= 100:
            val = 100
        self.progressbar.setValue(val)

    def update_ui_and_info_show(self, data: dict):
        text = data
        try:
            msg = text['message']
            print("---- update_ui_and_info_show ---- msg:", msg)

            if msg == "pairing enable opening":
                self.info_show.setText("正在打开配对模式，请稍等...")
                self.update_status_show("testing")
                self.clear_sensor_info()
            elif msg == "gateway enable pairing success":
                self.info_show.setText("启动网关成功，请点击感应器配对按钮开始配对")
                self.info_show.append("\n(60秒超时将自动回到初始状态)")
            elif msg == "gateway enable pairing fail":
                self.info_show.setText("错误:")
                self.info_show.append("打开配对模式失败，请重新尝试配对测试")
                self.info_show.append("\n提示:")
                self.info_show.append("1.检查网关(H10)是否打开电源")
                self.info_show.append("2.检查网关(H10)网络连接是否正常")
                self.info_show.append("3.检查配置文件config.ini的网关(H10) IP地址设置")
                self.info_show.append("4.尝试重新再测试一次")

                self.info_show.append("\n即将5秒后自动回到初始界面...")
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "pairing timeout":
                self.info_show.setText("配对超时")
                self.timer = QTimer()
                self.timer.setInterval(2000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "doorwindow_sensor pairing done":
                macaddress = text['macaddress']
                model = text['model']
                vendor = text['vendor']
                timestamp = text['timestamp']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                self.info_show.setText("门窗感应器配对成功, 即将开始功能测试...")
                info = "名称: 门窗感应器\n\n" + "MAC: " + macaddress + "\n类型: " + model + "\n供应商: " + vendor + "\n时间: " + format_time
                self.show_sensor_info(info)
            elif msg == "waterleakage_sensor pairing done":
                macaddress = text['macaddress']
                model = text['model']
                vendor = text['vendor']
                timestamp = text['timestamp']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                self.info_show.setText("水浸感应器配对成功")
                info = "名称: 水浸感应器\n\n" + "MAC: " + macaddress + "\n类型: " + model + "\n供应商: " + vendor + "\n时间: " + format_time
                self.show_sensor_info(info)
                self.show_qr_cmd_failed_confirm()
            elif msg == "temperature_sensor pairing done":
                macaddress = text['macaddress']
                model = text['model']
                vendor = text['vendor']
                timestamp = text['timestamp']
                temperature = text['temperature']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                self.info_show.setText("温度感应器配对成功，即将开始功能测试...")
                info = "名称: 温度感应器\n\n" + "\nMAC: " + macaddress + "\n类型: " + model + "\n供应商: " + vendor + "\n时间: " + format_time + "\n温度: " + temperature
                self.show_sensor_info(info)
            elif msg == "error not temperature sensor":
                self.update_status_show("fail")
                self.info_show.append("\n错误:")
                self.info_show.append("不是温度感应器")
            elif msg == "error not doorwindow sensor":
                self.update_status_show("fail")
                self.info_show.append("\n错误:")
                self.info_show.append("不是门窗感应器")
            elif msg == "error not waterleakage sensor":
                self.update_status_show("fail")
                self.info_show.append("\n错误:")
                self.info_show.append("不是水浸感应器")
            elif msg == "pre station done check success":
                pass
            elif msg == "pre station done check fail":
                self.update_status_show("fail")
                self.info_show.append("\n警告:")
                self.info_show.append("整机FTS测试未完成")
                self.info_show.append("(10秒后自动恢复到初始状态)")

                self.timer = QTimer()
                self.timer.setInterval(10000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "start doowwindow sensor function test":
                self.info_show.setText("配对成功，请闭合门窗传感器")
                self.info_show.append("\n如果未检测到闭合状态，请将该感应器送至维修工站维修")
                self.info_show.append("然后扫描确认命令码开始下一台测试")
                self.info_show.append("(30秒超时)")
                self.show_qr_cmd_failed_confirm()
            elif msg == "doowwindow sensor is opened":
                self.info_show.setText("打开测试通过，请闭合门窗传感器")
                self.info_show.append("\n如果未检测到打开状态，请将该感应器送至维修工站维修")
                self.info_show.append("然后扫描确认命令码开始下一台测试")
                self.info_show.append("(详情请参考SOP)")

                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                status = text['status']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                self.info_show.append(
                    "名称: 门窗感应器\n\n" + "时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(
                        deviceID) + " 方案:" + vendor + " 型号:" + model + " 状态:" + status)

                self.show_qr_cmd_failed_confirm()
            elif msg == "doowwindow sensor is closed":
                self.info_show.setText("闭合测试通过，请打开门窗传感器")
                self.info_show.append("\n如果未检测到闭合状态，请将该感应器送至维修工站维修")
                self.info_show.append("然后扫描确认命令码开始下一台测试")
                self.info_show.append("(详情请参考SOP)")

                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                status = text['status']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                self.info_show.append(
                    "名称: 门窗感应器\n\n" + "时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(
                        deviceID) + " 方案:" + vendor + " 型号:" + model + " 状态:" + status)
                self.show_qr_cmd_failed_confirm()
            elif msg == "doowwindow sensor function test success":
                self.info_show.setText("功能测试通过，即将开始QA测试")
                val = "pass"
                macaddress = text['macaddress']
                self.net.upload_oqc_to_tn4cio(macaddress, val)
                self.show_produced_sensor_number_and_progress()
            elif msg == "comfirm doowwindow sensor function test failed":
                self.update_status_show("fail")
                val = "fail"
                macaddress = text['macaddress']
                self.net.upload_oqc_to_tn4cio(macaddress, val)
                self.show_produced_sensor_number_and_progress()
            elif msg == "waterleakage sensor function test start":
                self.info_show.setText("功能测试，请进行 浸水/干燥 测试")
                self.info_show.append("(30秒超时)")
                self.info_show.append("\n如果未检测到状态变化，请将该感应器送至维修工站维修")
                self.info_show.append("然后扫描确认命令码开始下一台测试")
                self.show_qr_cmd_failed_confirm()
            elif msg == "waterleakage sensor is wet":
                self.info_show.setText("浸水测试通过，请离开水")
                self.info_show.append("\n如果未检测到状态变化，请将该感应器送至维修工站维修")
                self.info_show.append("然后扫描确认命令码开始下一台测试")
                self.info_show.append("(详情请参考SOP)")

                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                status = text['status']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                self.info_show.append(
                    "名称: 水浸感应器\n\n" + "时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(
                        deviceID) + " 方案:" + vendor + " 型号:" + model + " 状态:" + status)
                self.show_qr_cmd_failed_confirm()
            elif msg == "waterleakage sensor is dry":
                self.info_show.setText("干燥测试通过，请浸水测试")
                self.info_show.append("\n如果未检测到状态变化，请将该感应器送至维修工站维修")
                self.info_show.append("然后扫描确认命令码开始下一台测试")
                self.info_show.append("(详情请参考SOP)")

                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                status = text['status']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                self.info_show.append(
                    "名称: 水浸感应器\n\n" + "时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(
                        deviceID) + " 方案:" + vendor + " 型号:" + model + " 状态:" + status)
                self.show_qr_cmd_failed_confirm()
            elif msg == "waterleakage sensor function test success":
                self.info_show.setText("功能测试通过，即将开始QA测试")

                val = "pass"
                mac = text['macaddress']
                mac = mac.replace('0x', '').upper()
                self.net.upload_oqc_to_tn4cio(mac, val)
                self.show_produced_sensor_number_and_progress()
            elif msg == "waterleakage sensor user set function test failed":
                self.update_status_show("fail")
                val = "fail"
                macaddress = text['macaddress']
                self.net.upload_oqc_to_tn4cio(macaddress, val)
                self.show_produced_sensor_number_and_progress()
            elif msg == "temperature sensor function test success":
                val = "pass"
                mac = text['macaddress']
                temperature = text['temperature']
                reference = text['reference']
                self.info_show.append(
                    "\nMAC:" + mac + " 温度: " + temperature + " 参考值: " + reference + " 符合误差范围: " + self.TempRefRange)
                self.net.upload_oqc_to_tn4cio(mac, val)
                self.show_produced_sensor_number_and_progress()
            elif msg == "temperature sensor function test fail":
                self.info_show.setText("功能测试失败，请将该单板送至维修工站维修")
                self.info_show.append("(详情请参考SOP)")
                self.update_status_show("fail")
                self.show_qr_cmd_failed_confirm()

                macaddress = text['macaddress']
                temperature = text['temperature']
                reference = text['reference']
                self.info_show.append(
                    "\nMAC: " + macaddress + " 温度: " + temperature + " 参考值: " + reference + " 误差范围大于设定值: " + self.TempRefRange)
                self.net.upload_oqc_to_tn4cio(macaddress, "fail")
                self.show_produced_sensor_number_and_progress()
            elif msg == "sensor function test timeout":
                self.info_show.setText("功能测试超时")
                self.timer = QTimer()
                self.timer.setInterval(2000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "reference temperature sensor pairing success":
                self.info_show.setText("温度参考感应器配对成功")
                self.RefTemperature = text['temperature']
                macaddress = text['macaddress']
                self.info_show.append("\n参考感应器 MAC: " + macaddress + " 温度: " + self.RefTemperature)
                self.show_Ref_temperature(self.RefTemperature)
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.start()
                self.timer.timeout.connect(self.restart_asseblyfunction)
            elif msg == "reference temperature sensor pairing fail":
                self.info_show.setText("温度参考感应器配对失败，请等待自动重启并重新尝试")
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.start()
                self.timer.timeout.connect(self.restart_asseblyfunction)
            elif msg == "update reference tempreture value":
                tempreture = text['tempreture']
                self.show_Ref_temperature(tempreture)
            elif msg == "doorwindow sensor qa longtime test starting":
                self.info_show.setText("门窗感应器: QA测试")
                self.show_qr_cmd_exit_qa_test()
            elif msg == "doorwindow sensor qa testing info":
                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                status = text['status']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                self.info_show.append("时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(
                    deviceID) + " 方案:" + vendor + " 型号:" + model + " 状态: " + status)
            elif msg == "exit doorwindow sensor qa testing":
                self.info_show.setText("门窗感应器: 退出QA测试")
                self.timer = QTimer()
                self.timer.setInterval(1000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "waterleakage sensor qa longtime testing starting":
                self.info_show.setText("水浸感应器: QA测试")
                self.show_qr_cmd_exit_qa_test()
            elif msg == "waterleakage sensor qa testing info":
                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                status = text['status']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                self.info_show.append("时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(
                    deviceID) + " 方案:" + vendor + " 型号:" + model + " 状态: " + status)
            elif msg == "exit waterleakage sensor qa testing":
                self.info_show.setText("水浸感应器: 退出QA测试")
                self.timer = QTimer()
                self.timer.setInterval(1000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            elif msg == "temperature sensor qa longtime testing starting":
                self.info_show.setText("温度感应器: QA测试")
                self.show_qr_cmd_exit_qa_test()
            elif msg == "temperature sensor qa testing info":
                timestamp = text['timestamp']
                macaddress = text['macaddress']
                deviceID = text['deviceID']
                vendor = text['vendor']
                model = text['model']
                temperature = text['temperature']

                timeArray = time.localtime(int(timestamp) / 1000)
                format_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                self.info_show.append("时间:" + str(format_time) + " MAC:" + str(macaddress) + " 设备ID:" + str(deviceID)
                                      + " 方案:" + vendor + " 型号:" + model + " 温度: " + temperature + " 参考温度: " + self.RefTemperature)
            elif msg == "exit temperature sensor qa testing":
                self.info_show.setText("温度感应器: 退出QA测试")
                self.timer = QTimer()
                self.timer.setInterval(1000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)
            else:
                print("message not support", msg)
        except Exception as e:
            print(e)
            logging.debug(e)

    def restart_asseblyfunction(self):
        if self.timer:
            self.timer.stop()
        self.init_data()

    def stop_all_trhread(self):
        try:
            self.exit_qa_testing()
        except Exception:
            pass
