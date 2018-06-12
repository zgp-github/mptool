
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog

class ASSEMBLY_PAIR(QDialog):
    def __init__(self, parent=None):
        super(ASSEMBLY_PAIR, self).__init__(parent)
        self.setStyleSheet("background: red")
