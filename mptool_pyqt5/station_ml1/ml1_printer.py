# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtPrintSupport import QPrinterInfo, QPrinter
import configparser
from PyQt5.QtGui import QImage, QPainter

class printer():
    def __init__(self):
        print("ml1 printer init")
        self.init_data()

    def init_data(self):
        self.read_config()

    def read_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            conf.read(config)
            self.ml1_printer = conf.get('Printer', 'ml1_printer')
        print("ml1 printer:", self.ml1_printer)

    def list(self):
        printer = []
        printerInfo = QPrinterInfo()
        for item in printerInfo.availablePrinters():
            printer.append(item.printerName())
        print("printer list:", printer)
        return printer

    def printing(self, file):
        printer = self.ml1_printer
        printerInfo = QPrinterInfo()
        p = QPrinter()
        for item in printerInfo.availablePrinters():
            if printer == item.printerName():
                p = QPrinter(item)

        print("get file:", file)
        print("dpix", p.logicalDpiX(), p.logicalDpiY())

        image = QImage()
        image.load(file)
        painter = QPainter()

        # rect = painter.viewport()
        # print("rect:", rect)
        # size = image.size()
        # print("size:",size)
        # #size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
        # print(rect.x(), rect.y(), size.width(), size.height())
        # #painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        # #painter.setWindow(image.rect())

        print("image rect:", image.rect())
        # set the printer DPI(POSTEK G-3106 300)
        p.setResolution(300)
        painter.begin(p)
        painter.drawImage(0, 0, image)
        painter.end()
