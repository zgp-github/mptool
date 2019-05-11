# -*- coding: utf-8 -*-
import os
import configparser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QObject
from PyQt5.QtPrintSupport import QPrinterInfo
from PyQt5.QtPrintSupport import QPrinter

from time import sleep
from urllib.request import urlretrieve
from urllib.request import urlcleanup
from window5.net import network


class Printer(QObject):
    _signal_printer = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Printer, self).__init__(parent)
        self.ml1_printer = None
        self.corelight = None
        self.download_percent = 0
        self.init_data()

    def init_data(self):
        self.corelight = network()
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
        printerinfo = QPrinterInfo()
        p = QPrinter()
        for item in printerinfo.availablePrinters():
            if printer == item.printerName():
                p = QPrinter(item)

        print("printer get file:", file)

        image = QImage()
        image.load(file)
        painter = QPainter()

        print("image rect:", image.rect())
        # set the printer DPI(POSTEK G-3106 300)
        p.setResolution(300)
        painter.begin(p)
        painter.drawImage(0, 0, image)
        painter.end()

    def print_ml1_label(self, macaddress):
        mac = macaddress
        try:
            url = self.corelight.get_ml1_download_url(mac)
            filename = os.path.basename(url)
            filepath = os.path.join(os.getcwd(), filename)
            urlretrieve(url, filepath, self.download_callback)
            print("download ml1:", url, filename, filepath)

            if self.download_percent == 100:
                data = {"message": "print ML1 label success", "filepath": filepath}
                self._signal_printer.emit(data)
                sleep(0.1)
                self.download_percent = 0
                self.printing(filepath)
                sleep(0.1)

                if os.path.exists(filepath):
                    sleep(0.5)
                    os.unlink(filepath)
        except Exception as e:
            print(e)
            data = {"message": "print ML1 label fail"}
            self._signal_printer.emit(data)
        finally:
            urlcleanup()

    def download_callback(self, a, b, c):
        # download percent
        self.download_percent = 100.0*a*b/c
        if self.download_percent > 100:
            self.download_percent = 100
        print('%.2f%%' % self.download_percent)
