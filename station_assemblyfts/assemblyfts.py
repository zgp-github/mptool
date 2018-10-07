# -*- coding: utf-8 -*-
import sys
import os
import logging
import threading
from threading import Timer
from time import *
import json
import configparser
import re
import qrcode

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap
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
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import *


from station_assemblyfts.fts_data import Fts
from station_assemblyfts.net import network

class ASSEMBLY_FTS(QDialog):
    _signal_check_config = QtCore.pyqtSignal(dict)
    _signal_update_ui_and_info = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(ASSEMBLY_FTS, self).__init__()
        self._signal_check_config.connect(self.check_config_and_init)
        self._signal_update_ui_and_info.connect(self.update_ui_and_info)
        self.current_id = None
        self.current_mac = None
        self.initUI()
        self.init_data()

    def initUI(self):
        self.create_cmd_input()
        self.create_test_status_show()
        self.create_info_show()
        self.create_po_progressbar_show()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox_test_status)
        mainLayout.addWidget(self.QGroupBox_info_show)
        mainLayout.addWidget(self.QGridLayout_po_progress)

        mainLayout.setStretchFactor(self.gridGroupBox, 25)
        mainLayout.setStretchFactor(self.formGroupBox_test_status, 10)
        mainLayout.setStretchFactor(self.QGroupBox_info_show, 65)
        mainLayout.setStretchFactor(self.QGridLayout_po_progress, 5)
        self.setLayout(mainLayout)

    def init_data(self):
        self.parser_config()
        self.net = network()
        self.check_configuration()

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()

        station_info = QLabel("工站: 整机FTS测试")
        station_info.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(station_info, 0, 0)
        station_info.setAlignment(QtCore.Qt.AlignCenter)

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

        self.table = QTableWidget(3, 4)
        # auto adapt the width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # auto adapt the heigh
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set canot edit the table data
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)

        self.table.setHorizontalHeaderLabels(['类型', '数据', '类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        self.table.setFont(font)

        newItem = QTableWidgetItem("服务器IP")
        self.table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("FTS数据库")
        self.table.setItem(0, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(0, 3, newItem)

        newItem = QTableWidgetItem("订单总数")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("测试ID")
        self.table.setItem(1, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(1, 3, newItem)

        newItem = QTableWidgetItem("测试通过数量")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(2, 1, newItem)

        newItem = QTableWidgetItem("测试失败数量")
        self.table.setItem(2, 2, newItem)
        newItem = QTableWidgetItem("0")
        self.table.setItem(2, 3, newItem)

        layout.addWidget(self.table, 0, 1, 3, 1)
        layout.setColumnStretch(0, 70)
        layout.setColumnStretch(1, 30)
        self.gridGroupBox.setLayout(layout)

    def create_test_status_show(self):
        self.formGroupBox_test_status = QGroupBox("测试状态")
        layout = QFormLayout()

        self.status_bar = QLabel(self)
        self.status_bar.setStyleSheet(
            '''color: black; background-color: gray''')
        info = '测试状态'
        self.status_bar.setText(info)
        self.status_bar.setFont(QFont("Microsoft YaHei", 40))
        self.status_bar.setAlignment(QtCore.Qt.AlignCenter)
        layout.addRow(self.status_bar)
        self.formGroupBox_test_status.setLayout(layout)

    def create_info_show(self):
        self.QGroupBox_info_show = QGroupBox("作业信息")
        layout = QGridLayout()

        # info show
        self.info_show = QTextEdit()
        self.info_show.setPlainText("提示信息")
        self.info_show.setFont(QFont("Microsoft YaHei", 20))
        cursor = self.info_show.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.info_show.setTextCursor(cursor)
        layout.addWidget(self.info_show, 0, 0, 2, 1)
        self.info_show.setReadOnly(True)
        self.info_show.setFocusPolicy(QtCore.Qt.NoFocus)

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
        self.QGridLayout_po_progress = QGroupBox("订单进度")
        layout = QGridLayout()
        self.progressbar = QProgressBar(self)
        layout.addWidget(self.progressbar, 1, 0)
        self.progressbar.setFont(QFont("Microsoft YaHei", 10))
        self.QGridLayout_po_progress.setLayout(layout)

    def show_fts_test_status_bar(self, status):
        print("update status show: "+status)

        if status == "init":
            info = '请开始测试'
            self.status_bar.setStyleSheet(
                '''color: black; background-color: gray''')
        elif status == "testing":
            info = "测试中"
            self.status_bar.setStyleSheet(
                '''color: black; background-color: yellow''')
        elif status == "success":
            info = "测试通过"
            self.status_bar.setStyleSheet(
                '''color: black; background-color: green''')
        elif status == "fail":
            info = '测试失败'
            self.status_bar.setStyleSheet(
                '''color: black; background-color: red''')
        else:
            info = '未知状态'
            self.status_bar.setStyleSheet(
                '''color: black; background-color: gray''')
        self.status_bar.setText(info)

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)

        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.fts_db = conf.get('FTS_DB', 'db_name')
            return True
        else:
            return False

    def check_configuration(self):
        t = threading.Thread(target=self.check_configs)
        t.start()

    def check_configs(self):
        msg = "checking configuration"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)

        # 1.check tn4c.io
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
            else:
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

        # 3.check the FTS DB file
        msg = "checking fts database"
        data = {"message": msg}
        self._signal_check_config.emit(data)
        sleep(0.1)
        db_path = os.path.join(os.getcwd(), self.fts_db)
        if (os.path.exists(db_path) == True):
            msg = "check fts database success"
            data = {"message": msg}
            self._signal_check_config.emit(data)
        else:
            msg = "check fts database fail"
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
        print(data)

        self.timer = QTimer()
        self.stop_thread_get_fts_data()
        text = data
        msg = text['message']

        self.show_po_info()
        self.clear_sensor_info()
        if msg == "checking configuration":
            self.info_show.setText("正在检查您的配置信息，请稍等...")
        elif msg == "checking corelight":
            self.info_show.append("\n检查Corelight服务器: " + self.tn4cioip)
        elif msg == "check corelight ip success":
            self.info_show.append("通过")
            self.show_tn4cio_ip()
            self.show_po_total()
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
        elif msg == "check poinfo fail":
            self.info_show.append("错误:")
            self.info_show.append("订单信息设置错误,请检查确认...")
        elif msg == "checking fts database":
            self.info_show.append("\n检查FTS数据库: "+self.fts_db)
        elif msg == "check fts database success":
            self.info_show.append("通过")
            self.show_fts_db_name()
        elif msg == "check fts database fail":
            self.info_show.setText("错误:")
            self.info_show.append("FTS数据库文件无法找到,请检查...")
            self.info_show.append("\n提示:")
            self.info_show.append("1.找到FTS数据库文件存放的目录")
            self.info_show.append("2.把本程序放置在FTS数据库文件同一个目录")
        elif msg == "check configuration done":
            self.info_show.append("\n检查完成")
        elif msg == "init station":
            db_path = os.path.join(os.getcwd(), self.fts_db)
            self.fts = Fts(db_path)
            self.init_status_and_data()
            self.start_thread_get_fts_data()

    def confirm_fail(self):
        self.init_status_and_data()

    def init_status_and_data(self):
        self.show_fts_test_status_bar("init")
        self.show_tn4cio_ip()
        self.show_tested_number_and_progress()
        self.qr_CMD_init_show()
        self.show_init_msg()
        try:
            data = self.fts.get_Tests_data()
            self.current_id = data['fts_id']
            self.show_fts_current_test_id()
        except Exception:
            pass

    def start_thread_get_fts_data(self):
        if self.FTS_THREAD == False:
            self.FTS_THREAD = True
            t = threading.Thread(target=self.get_data)
            t.start()
        else:
            pass

    def stop_thread_get_fts_data(self):
        self.FTS_THREAD = False

    def get_data(self):
        while self.FTS_THREAD:
            try:
                # always read and parse the FTS DB
                tmp = self.fts.get_Tests_data()
                ftsid = tmp['fts_id']
                time = tmp['fts_time']
                macaddress = tmp['fts_mac']
                result = tmp['fts_result']
                status = tmp['fts_status']

                if status == "ERROR" and result == "NA" and macaddress == "0":
                    data = {"message": "FTS is testing"}
                    self._signal_update_ui_and_info.emit(data)
                elif status == "DONE":
                    if self.current_id != ftsid:
                        data = {"message": "FTS is testing done", "ftsid": ftsid, "time": time,
                                "macaddress": macaddress, "result": result, "status": status}
                        self._signal_update_ui_and_info.emit(data)
                    else:
                        print("thread is running, waiting for the new data current_id and get ftsid:", self.current_id, ftsid)
            except Exception:
                pass
            finally:
                sleep(1)
                print("thread is running, waiting for the new data")

    def update_ui_and_info(self, data: dict):
        text = data
        try:
            msg = text['message']
            print('---- update ui and info -----msg:', msg)
            if msg == "FTS is testing":
                self.clear_sensor_info()
                self.show_fts_test_status_bar("testing")
                self.info_show.setText("请等待整机FTS测试完成")
                self.info_show.append("(详情请参考SOP)")
            elif msg == "FTS is testing done":
                ftstime = text['time']
                ftsmac = text['macaddress']
                ftsresult = text['result']
                self.current_id = text['ftsid']
                self.current_mac = ftsmac

                sensor_info = "FTS ID: " + str(self.current_id) + "\nMAC: " + ftsmac + "\n时间: " + ftstime
                self.show_sensor_info(sensor_info)

                ret = self.check_pre_station_done(ftsmac)
                if ret is True:
                    pass
                else:
                    self.show_fts_test_status_bar("fail")
                    self.info_show.setText("警告:")
                    self.info_show.append("整机功能测试未完成")
                    self.qr_CMD_FTS_FAIL_CONFIRM_show()
                    return

                if ftsresult == "SUCCESS":
                    self.info_show.setText("当前当前感应器FTS测试通过\n")
                    self.info_show.append("请扫描感应器背面条码校验")
                    self.upload_fts_data_to_tn4cio(ftsmac, "pass")
                else:
                    self.show_fts_test_status_bar("fail")
                    self.upload_fts_data_to_tn4cio(ftsmac, "fail")
                    self.info_show.setText("FTS测试失败，请将该感应器送至维修工站维修\n")
                    self.info_show.append("然后扫描确认命令码开始下一台测试")
                    self.qr_CMD_FTS_FAIL_CONFIRM_show()
            else:
                print("fts is running, waiting for the new data")
        except Exception:
            pass

    def upload_fts_data_to_tn4cio(self, macaddress, ftsresult):
        fts_mac = macaddress
        fts_result = ftsresult
        try:
            ret = self.net.upload_assembly_fts(fts_mac, fts_result)
            print("upload mac:", ret)
            tmp = json.loads(ret)
            msg_type = tmp['messages'][0]['type']
            if msg_type == "ok":
                pass
            else:
                self.info_show.setText("更新FTS测试数据到Corelight服务器失败!")
        except Exception:
            pass

    def onTimerOut(self):
        print("-------------------timerout-------------")
        self.timer.stop()
        self.init_status_and_data()

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

    def show_tn4cio_ip(self):
        tmp = QTableWidgetItem(self.tn4cioip)
        self.table.setItem(0, 1, tmp)

    def show_po_info(self):
        if self.pokey != None and self.countrycode != None and self.hwversion != None:
            info = "订单: "+self.pokey+"-"+self.countrycode+"-"+self.hwversion
            self.po_info.setText(info)
        else:
            pass

    def show_po_total(self):
        try:
            ret = self.net.get_po_info()
            text = json.loads(ret)
            po_total = text['messages'][0]['total']
            tmp = QTableWidgetItem(str(po_total))
            self.table.setItem(1, 1, tmp)
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def show_init_msg(self):
        self.info_show.setText("作业提示:")
        self.info_show.append("请将待测试感应器置于测试治具上，并按下开始按钮开始测试")
        self.info_show.append("(详情请参考SOP)")

    def show_tested_number_and_progress(self):
        try:
            ret = self.net.get_assemblyfts_tested_info()
            total = ret['total']
            produced = ret['produced']
            pass_num = ret['assemblyfts_pass_count']
            fail_num = ret['assemblyfts_fail_count']
            tmp = QTableWidgetItem(str(pass_num))
            self.table.setItem(2, 1, tmp)

            tmp2 = QTableWidgetItem(str(fail_num))
            self.table.setItem(2, 3, tmp2)

            process = int(produced)*100 // int(total)
            self.show_po_process(process)
        except Exception:
            pass

    def show_fts_db_name(self):
        newItem = QTableWidgetItem(self.fts_db)
        self.table.setItem(0, 3, newItem)

    def show_fts_current_test_id(self):
        try:
            id = str(self.current_id)
            newItem = QTableWidgetItem(id)
            self.table.setItem(1, 3, newItem)
        except Exception:
            pass

    def handle_cmd(self):
        tmp = self.cmd_input.text()
        cmd = tmp.upper()
        log = "get cmd:"+cmd
        print(log)
        logging.debug(log)
        self.cmd_input.clear()

        if cmd == "CMD_FTS_FAIL_CONFIRM":
            self.confirm_fail()
        else:
            ret = self.mac_check(cmd)
            if ret is True:
                mac = cmd
                self.compare_mac_with_qr_label_on_sensor(mac)
            else:
                print("cmd:"+cmd+" not support")
                self.info_show.setText("错误:")
                self.info_show.append("命令: "+cmd+" 不支持!")
                self.timer.setInterval(1000)
                self.timer.start()
                self.timer.timeout.connect(self.onTimerOut)

    def confirm_fail(self):
        self.init_status_and_data()

    def compare_mac_with_qr_label_on_sensor(self, macaddress):
        mac = macaddress
        print("compare the mac:",mac)
        if mac == self.current_mac.upper():
            self.show_fts_test_status_bar("success")
            self.info_show.setText("条码校验通过")
            self.info_show.append("当前感应器测试完成，请开始下一台测试")

            self.timer.setInterval(2000)
            self.timer.start()
            self.timer.timeout.connect(self.onTimerOut)
            return True
        else:
            self.show_fts_test_status_bar("fail")
            self.info_show.setText("条码校验失败，当前条码信息有误")
            self.info_show.append("请将该感应器送至维修工站维修")
            self.info_show.append("然后扫描确认命令码开始下一台测试")
            self.info_show.append("(详情请参考SOP)")
            self.qr_CMD_FTS_FAIL_CONFIRM_show()
            return False

    def set_focus(self):
        self.cmd_input.setFocus()

    def qr_CMD_FTS_FAIL_CONFIRM_show(self):
        self.qr_cmd_name.setText("FTS测试失败确认码")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data('CMD_FTS_FAIL_CONFIRM')
        qr.make(fit=True)
        img = qr.make_image()
        img_path = os.path.join(os.getcwd(), "CMD_FTS_FAIL_CONFIRM.png")
        img.save(img_path)

        if os.path.exists(img_path):
            qr_cmd = QPixmap(img_path)
            self.qr_cmd.setPixmap(qr_cmd)
            os.remove(img_path)

    def qr_CMD_init_show(self):
        self.qr_cmd_name.setText("命令码名称")
        self.qr_cmd.setText("无")

    def show_sensor_info(self, info):
        self.sensor_info.setAlignment(QtCore.Qt.AlignLeft)
        self.sensor_info.setAlignment(QtCore.Qt.AlignVCenter)
        self.sensor_info_name.setText("感应器信息")
        self.sensor_info.setText(info)

    def clear_sensor_info(self):
        self.sensor_info.setAlignment(QtCore.Qt.AlignLeft)
        self.sensor_info.setAlignment(QtCore.Qt.AlignVCenter)
        self.sensor_info_name.setText("感应器信息")
        self.sensor_info.setText("FTS ID:" + "\nMAC:" + "\n时间:")

    def show_po_process(self, value):
        val = int(value)
        if val <= 0:
            val = 0

        if val >= 100:
            val = 100
        self.progressbar.setValue(val)

    def check_pre_station_done(self, macaddress: str) -> bool:
        pre_station_done = self.net.check_previous_station_already_done(macaddress)
        if pre_station_done == True:
            # data = {"message": "pre station done check success"}
            # self._signal_update_ui_and_info.emit(data)
            # sleep(1)
            return True
        else:
            # data = {"message": "pre station done check fail"}
            # self._signal_update_ui_and_info.emit(data)
            # sleep(1)
            return False

    def stop_all_thread(self):
        try:
            self.stop_thread_get_fts_data()
        except Exception as e:
            print(e)
            logging.debug(e)