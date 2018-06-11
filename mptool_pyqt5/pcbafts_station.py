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

class PCBAFTS(QDialog):
    thread_get_FTS_data = False
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

        table = QTableWidget(3, 2)
        # auto adapt the width
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set canot edit the table data
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        table.setHorizontalHeaderLabels(['类型', '数据'])
        font = QFont("Microsoft YaHei", 10)
        table.setFont(font)

        newItem = QTableWidgetItem("MAC地址")
        table.setItem(0, 0, newItem)
        newItem = QTableWidgetItem("None")
        table.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("传感器类型")
        table.setItem(1, 0, newItem)
        newItem = QTableWidgetItem("None")
        table.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("传感器状态")
        table.setItem(2, 0, newItem)
        newItem = QTableWidgetItem("None")
        table.setItem(2, 1, newItem)

        layout.addWidget(table, 0, 2, 4, 1)
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
        self.bigEditor.append("daemon_start")
        self.thread_get_FTS_data = True
        t = threading.Thread(target=self.get_FTS_data)
        t.start()
    
    # overwrite the window close function
    def closeEvent(self, event):
        print("closeEvent: ", event)
        self.thread_get_FTS_data = False
    
    def get_FTS_data(self):
        while self.thread_get_FTS_data == True:
            print("get fts data")
            sleep(1)
