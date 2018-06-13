# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtPrintSupport import QPrinterInfo, QPrinter
import configparser

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

    def printing(self, printer, context):
        printerInfo = QPrinterInfo()
        p = QPrinter()
        for item in printerInfo.availablePrinters():
            if printer == item.printerName():
                p = QPrinter(item)
        doc = QtGui.QTextDocument()
        doc.setHtml(u'%s' % context)
        doc.setPageSize(QtCore.QSizeF(p.logicalDpiX()*(80/25.4),
                                      p.logicalDpiY()*(297/25.4)))
        p.setOutputFormat(QPrinter.NativeFormat)
        doc.print_(p)
