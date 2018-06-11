
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog


class page2(QDialog):
    def __init__(self, parent=None):
        super(page2, self).__init__(parent)
        self.setStyleSheet("background: red")
