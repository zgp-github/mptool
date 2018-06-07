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

class Dialog(QDialog):
    test_1_running = False

    def __init__(self):
        super(Dialog, self).__init__()
        self.initUI()

    def initUI(self):
        title = 'MPTOOL4PC .IO NGxx Version 0.1'
        self.setWindowTitle(title)
        self.createMenu()
        self.create_cmd_input()
        self.create_test_result_show()
        self.create_info_show()
        self.create_auto_test()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # buttonBox.accepted.connect(self.accept)
        # buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.QGroupBox_info_show)
        mainLayout.addWidget(buttonBox)
        mainLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(mainLayout)

        # It is a timer test code
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

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
            info = "测试通过"
            self.test_result.setStyleSheet('''color: black; background-color: green''')
        elif status == "fail":
            info = '测试失败'
            self.test_result.setStyleSheet('''color: black; background-color: red''')
        else:
            info = '请开始测试'
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
        cursor=self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)

        layout.addRow(self.bigEditor)
        self.QGroupBox_info_show.setLayout(layout)

    def create_auto_test(self):
        self.horizontalGroupBox = QGroupBox("功能自动测试")
        layout = QHBoxLayout()

        button_1 = QPushButton("自动测试 1")
        button_1.clicked.connect(self.auto_test_1)
        layout.addWidget(button_1)

        button_2 = QPushButton("自动测试 2")
        button_2.clicked.connect(self.auto_test_2)
        layout.addWidget(button_2)

        button_3 = QPushButton("自动测试 3")
        button_3.clicked.connect(self.auto_test_3)
        layout.addWidget(button_3)

        button_4 = QPushButton("自动测试 4")
        button_4.clicked.connect(self.auto_test_4)
        layout.addWidget(button_4)
        
        self.horizontalGroupBox.setLayout(layout)

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
                    #self.check_cmd()
                    # t = threading.Thread(target=self.check_cmd)
                    # t.start()
            else:
                pass
        return False

    def auto_test_1(self):
        if Dialog.test_1_running == False:
            Dialog.test_1_running = True
            print("auto_test_1")
            self.bigEditor.append("start auto test 1")
            t = threading.Thread(target=self.test_unit_1)
            t.start()
        else:
            self.bigEditor.append("test 1 is already running!")
            pass

    def auto_test_2(self):
        print("auto_test_2")
        self.bigEditor.append("start auto test 2")

    def auto_test_3(self):
        print("auto_test_3")
        self.bigEditor.append("start auto test 3")
        self.update_test_resule_show("success")

    def auto_test_4(self):
        print("auto_test_4")
        self.bigEditor.append("start auto test 4")
        self.update_test_resule_show("fail")

    def test_unit_1(self):
        while True:
            print("test_unit_1")
            self.cmd_input.setText("cmd_start_pair")
            self.update_msg_show(2)
            self.bigEditor.append("success")
            self.update_test_resule_show("success")
            sleep(1)
            self.cmd_input.setText("error cmd input test...")
            self.update_msg_show(3)
            self.update_test_resule_show("fail")
            self.bigEditor.append("fail")
            sleep(1)
            self.cmd_input.clear()
            self.update_msg_show(1)
            self.update_test_resule_show()
            self.bigEditor.append("no statues")
            sleep(1)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
