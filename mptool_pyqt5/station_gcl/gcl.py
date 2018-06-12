# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog


class GCL(QDialog):
    def __init__(self, parent=None):
        super(GCL, self).__init__(parent)
        self.setStyleSheet("background: yellow")
