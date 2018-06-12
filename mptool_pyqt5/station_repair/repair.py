# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog

class REPAIR(QDialog):
    def __init__(self, parent=None):
        super(REPAIR, self).__init__(parent)
        self.setStyleSheet("background: blue")
