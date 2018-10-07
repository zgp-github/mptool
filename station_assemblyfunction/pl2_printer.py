# -*- coding: utf-8 -*-
import os
import configparser
from time import sleep
from urllib.request import urlretrieve
from urllib.request import urlcleanup
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPainter

from PyQt5.QtPrintSupport import QPrinterInfo
from PyQt5.QtPrintSupport import QPrinter

from station_assemblyfunction.assemblyfunction import network


class Printer(QObject):
    _signal_printer = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Printer, self).__init__(parent)
        self.corelight = None
        self.download_percent = 0
        self.pl2_printer = None
        self.init_data()

    def init_data(self):
        self.parser_config()
        self.corelight = network()

    def parser_config(self):
        file = 'config.ini'
        filepath = os.path.join(os.getcwd(), file)
        if os.path.exists(filepath):
            conf = configparser.ConfigParser()
            conf.read(filepath)
            self.pl2_printer = conf.get('Printer', 'pl2_printer')
        print("pl2 printer:", self.pl2_printer)

    def list(self):
        printer = []
        printer_info = QPrinterInfo()
        for item in printer_info.availablePrinters():
            printer.append(item.printerName())
        print("printer list:", printer)
        return printer

    def printing(self, file):
        printer = self.pl2_printer
        printer_info = QPrinterInfo()
        p = QPrinter()
        for item in printer_info.availablePrinters():
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

    def print_pl2_label(self, macaddress):
        mac = macaddress
        data = {"message": "printing PL2 label"}
        self._signal_printer.emit(data)
        sleep(0.5)
        try:
            url = self.corelight.get_pl2_label_download_url(mac)
            filename = os.path.basename(url)
            filepath = os.path.join(os.getcwd(), filename)
            urlretrieve(url, filepath, self.download_callback)
            print("download pl2:", url, filename, filepath)

            if self.download_percent == 100:
                self.download_percent = 0

            if os.path.exists(filepath):
                self.printing(filepath)
                sleep(0.1)
                data = {"message": "print PL2 label success", "filepath": filepath}
                self._signal_printer.emit(data)
                sleep(0.5)
                os.unlink(filepath)
        except Exception as e:
            print(e)
            data = {"message": "print PL2 label fail"}
            self._signal_printer.emit(data)
        finally:
            urlcleanup()

    def download_callback(self, a, b, c):
        # download percent
        self.download_percent = 100.0*a*b/c
        if self.download_percent > 100:
            self.download_percent = 100
        print('%.2f%%' % self.download_percent)
