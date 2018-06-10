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
import sqlite3
import requests
import json

class Dialog(QDialog):
    thread_get_FTS_data = False
    current_mac_data = None
    _signal=QtCore.pyqtSignal(list)

    def __init__(self):
        super(Dialog, self).__init__()
        self.initUI()

    def initUI(self):
        title = 'MPTOOL4PC .IO NGxx Version 0.1'
        screenRect = QApplication.instance().desktop().availableGeometry()
        # get the screen width and height
        width = screenRect.width()*2/5
        height = screenRect.height()*4/5
        self.setGeometry(400, 100, width, height)

        self.setWindowTitle(title)
        self.createMenu()
        self.create_cmd_input()
        self.create_test_result_show()
        self.create_info_show()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # buttonBox.accepted.connect(self.accept)
        # buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        # It is a timer test code
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)
        self.thread_get_FTS_data = True
        self.daemon_start()

    # overwrite the window close function
    def closeEvent(self, event):
        print("closeEvent: ", event)
        self.thread_get_FTS_data = False

    def onTimerOut(self):
        self.bigEditor.append("timer test...")
        self.timer.stop()

    def createMenu(self):
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("文件", self)
        self.exitAction = self.fileMenu.addAction("退出")
        self.about = QMenu("帮助", self)
        self.about.addAction("关于")
        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.about)
        self.exitAction.triggered.connect(self.accept)

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("数据显示")
        layout = QGridLayout()

        self.table = QTableWidget(4, 2)
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

        newItem = QTableWidgetItem("MAC地址")
        self.table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("传感器类型")
        self.table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(2, 1, newItem)

        newItem = QTableWidgetItem("传感器状态")
        self.table.setItem(3, 0, newItem)
        newItem = QTableWidgetItem("None")
        self.table.setItem(3, 1, newItem)

        layout.addWidget(self.table, 0, 2, 4, 1)
        layout.setColumnStretch(2, 100)
        self.gridGroupBox.setLayout(layout)

    def create_test_result_show(self):
        self.formGroupBox = QGroupBox("数据上传结果")
        layout = QFormLayout()

        self.test_result = QLabel(self, text="测试结果")
        self.test_result.setStyleSheet('''color: black; background-color: gray''')
        info = '请开始测试'
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

        layout.addRow(self.test_result)
        self.formGroupBox.setLayout(layout)

    def update_test_resule_show(self, status='None'):
        print("update_test_resule_show: "+status)
        if status == "success":
            info = "数据上传成功"
            self.test_result.setStyleSheet('''color: black; background-color: green''')
        elif status == "fail":
            info = '数据上传失败'
            self.test_result.setStyleSheet('''color: black; background-color: red''')
        else:
            info = '等待数据中'
            self.test_result.setStyleSheet('''color: black; background-color: gray''')
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
        layout.addRow(self.bigEditor)
        self.QGroupBox_info_show.setLayout(layout)

    def daemon_start(self):
        self.bigEditor.append("daemon_start")
        t = threading.Thread(target=self.get_FTS_data)
        t.start()

    count=0
    def update_ui_and_upload_data(self, list):
        print("---------------",list)

        sensor_id = str(list[0])
        newItem = QTableWidgetItem(sensor_id)
        self.table.setItem(0, 1, newItem)

        sensor_mac = list[1]
        newItem = QTableWidgetItem(sensor_mac)
        self.table.setItem(1, 1, newItem)

        sensor_type = list[2]
        newItem = QTableWidgetItem(sensor_type)
        self.table.setItem(2, 1, newItem)

        msg = list[3]
        self.bigEditor.append(msg)
        print(self.count)
        if self.count % 3 == 1:
            self.update_test_resule_show("success")
        elif self.count % 3 == 2:
            self.update_test_resule_show("fail")
        else:
            self.update_test_resule_show()
        self.count = self.count + 1

        cursor=self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)

    def get_FTS_data(self):
        self._signal.connect(self.update_ui_and_upload_data)
        db = "ftsTestResults.db"
        conn = sqlite3.connect(db)
        c = conn.cursor()
        cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID   from Tests"

        while self.thread_get_FTS_data == True:
            cursor = c.execute(cmd)
            for row in cursor:
                print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                msg = str(row[0])+" "\
                    +str(row[1])+" "\
                    +str(row[2])+" "\
                    +str(row[3])+" "\
                    +str(row[4])+" "\
                    +str(row[5])+" "\
                    +str(row[6])+" "\
                    +str(row[7])+" "\
                    +str(row[8])+" "\
                    +str(row[9])
                index = (row[0])
                mac = row[7]
                dataList = []
                dataList.append(index)
                dataList.append(mac)
                dataList.append("door_window_sensor")
                dataList.append(msg)
                self._signal.emit(dataList)
                sleep(1)
        print("-------close database-------")
        conn.close()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
