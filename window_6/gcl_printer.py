# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtPrintSupport import QPrinterInfo
from PyQt5.QtPrintSupport import QPrinter
import configparser
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPainter

class printer():
    def __init__(self):
        print("gcl printer init")
        self.init_data()

    def init_data(self):
        self.parser_config()

    def parser_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            conf.read(config)
            self.gcl_printer = conf.get('Printer', 'gcl_printer')
        print("gcl printer:", self.gcl_printer)

    def list(self):
        printer = []
        printerInfo = QPrinterInfo()
        for item in printerInfo.availablePrinters():
            printer.append(item.printerName())
        print("printer list:", printer)
        return printer

    def printing(self, file):
        print("printer get file:", file)
        printer = self.gcl_printer
        printerInfo = QPrinterInfo()
        p = QPrinter()
        for item in printerInfo.availablePrinters():
            if printer == item.printerName():
                p = QPrinter(item)

        image = QImage()
        image.load(file)
        painter = QPainter()

        # set the printer DPI as 300(POSTEK G-3106)
        p.setResolution(300)
        painter.begin(p)
        painter.drawImage(0, 0, image)
        painter.end()
