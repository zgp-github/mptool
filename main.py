from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import threading
from threading import Timer
from time import *

class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

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

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.gridGroupBox)
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.bigEditor)
        mainLayout.addWidget(buttonBox)
        mainLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(mainLayout)

    def createMenu(self):
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)
        self.exitAction.triggered.connect(self.accept)

    def create_cmd_input(self):
        self.gridGroupBox = QGroupBox("命令输入区")
        layout = QGridLayout()
        cmd_input = QLineEdit(self)
        cmd_input.setFont(QFont("Microsoft YaHei", 25))
        cmd_input.setStyleSheet("color:black")
        layout.addWidget(cmd_input, 0, 1)

        msg = QLabel("请扫描配对命令码")
        msg.setFont(QFont("Microsoft YaHei", 20))
        layout.addWidget(msg, 1, 1)

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
        info = ''
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)

        layout.addRow(self.test_result)
        self.formGroupBox.setLayout(layout)

    def update_test_resule_show(self, status='None'):
        print("update_test_resule_show")
        if status == "success":
            info = "测试通过"
            self.test_result.setStyleSheet('''color: black; background-color: green''')
        elif status == "fail":
            info = '测试失败'
            self.test_result.setStyleSheet('''color: black; background-color: red''')
        else:
            info = ''
            self.test_result.setStyleSheet('''color: black; background-color: gray''')
        self.test_result.setText(info)
        self.test_result.setFont(QFont("Microsoft YaHei", 20))
        self.test_result.setAlignment(QtCore.Qt.AlignCenter)
        
    def create_info_show(self):
        print("info show for the process logs")
        self.bigEditor = QTextEdit()
        self.bigEditor.setPlainText("This widget takes up all the remaining space "
                "in the top-level layout.")
        cursor=self.bigEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.bigEditor.setTextCursor(cursor)

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

    def auto_test_1(self):
        print("auto_test_1")
        self.bigEditor.append("start auto test 1")
        t = threading.Thread(target=self.test_unit_1)
        t.start()

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
            self.bigEditor.append("success")
            self.update_test_resule_show("success")
            sleep(1)
            self.update_test_resule_show("fail")
            self.bigEditor.append("fail")
            sleep(1)
            self.update_test_resule_show()
            self.bigEditor.append("no statues")
            sleep(1)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
