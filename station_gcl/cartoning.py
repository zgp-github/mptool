# -*- coding: utf-8 -*-
import re
import sys
import json
import logging
import os.path
import threading
import configparser
from time import sleep
from urllib.request import urlretrieve
from urllib.request import urlcleanup

from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from station_gcl.net import network
from station_gcl.weighter import Weighter
from station_gcl.gcl_printer import printer


class Cartoning(QObject):
    _signal_cartoning = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Cartoning, self).__init__(parent)
        self.hwversion = None
        self.corelight = None
        self.percent = 0
        self.cartoning_mac_list = []
        self.printer = printer()
        self.weighter = Weighter()
        self.thread_get_sensor_weight = False
        self.current_sensor_weight = None
        self.init_data()

    def init_data(self):
        self.parser_config()
        self.corelight = network()
        self.start_get_weight()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.total_per_carton = conf.get('GclInfo', 'count_one_package')
            return True
        else:
            return False

    def start_get_weight(self):
        if self.thread_get_sensor_weight is False:
            self.thread_get_sensor_weight = True
            t = threading.Thread(target=self.get_weight)
            t.start()
        else:
            print("warming: thread for get sensor weight already running!!!")

    def stop_get_weight(self):
        self.thread_get_sensor_weight = False
        self.current_sensor_weight = 0

    def get_weight(self):
        print("thread get weight thread_get_sensor_weight:",self.thread_get_sensor_weight)
        while self.thread_get_sensor_weight is True:
            try:
                weight = self.weighter.get_weight()
                self.current_sensor_weight = weight
                print("-------ES-6KCC(weighter) get weight:",weight)
                data = {"message": "update sensor weight intime", "weight": weight}
                self._signal_cartoning.emit(data)
            except Exception:
                pass
            finally:
                sleep(0.5)
        data = {"message": "thread get sensor weight already stoped"}
        self._signal_cartoning.emit(data)

    def upload_sensor_weight_to_corelight(self, macaddress):
        try:
            weight = self.current_sensor_weight
            ret = self.corelight.upload_sensor_weight(macaddress, weight)
            text = json.loads(ret)
            result = text['result']
            if result == "ok":
                return True
            else:
                data = {"message": "upload sensor weight to corelight fail", "macaddress": macaddress, "weight": weight}
                self._signal_cartoning.emit(data)
                return False
        except Exception:
            return False

    def check_pre_station_done(self, macaddress: str) -> bool:
        ret = self.corelight.check_previous_station_already_done(macaddress)
        if ret is True:
            data = {"message": "pre station done check success"}
            self._signal_cartoning.emit(data)
            sleep(1)
            return True
        else:
            data = {"message": "pre station done check fail", "macaddress": macaddress}
            self._signal_cartoning.emit(data)
            sleep(1)
            return False

    def check_mac_in_cartoning_list(self, macaddress):
        mac = macaddress
        if mac in self.cartoning_mac_list:
            data = {"message": "macaddress already in cartoning list", "macaddress": macaddress}
            self._signal_cartoning.emit(data)
            return False
        else:
            return True

    def check_mac(self, macaddress):
        mac = macaddress
        valid = re.compile(r''' 
            (^([0-9A-F]{1,2}[-]){5}([0-9A-F]{1,2})$ 
            |^([0-9A-F]{1,2}[:]){5}([0-9A-F]{1,2})$ 
            |^([0-9A-F]{1,2}[.]){5}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}){5}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}[-]){7}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}[:]){7}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}[.]){7}([0-9A-F]{1,2})$
            |^([0-9A-F]{1,2}){7}([0-9A-F]{1,2})$) 
            ''', re.VERBOSE | re.IGNORECASE)
        ret = valid.match(mac) is not None
        if ret is True:
            pass
        else:
            data = {"message": "macaddress check is not valid", "macaddress": mac}
            self._signal_cartoning.emit(data)
        return ret

    def check_mac_not_already_cartoned(self, macaddress):
        mac = macaddress
        try:
            ret = self.corelight.check_mac_valid(mac)
            text = json.loads(ret)
            result = text['result']
            msg = text['messages'][0]['message']
            if result == "ok":
                if msg == "check mac for gcl success":
                    data = {"message": "macaddress is check valid in corelight"}
                    self._signal_cartoning.emit(data)
                    return True
            else:
                if msg == "already in gcl":
                    data = {"message": "macaddress is already cartoned", "macaddress": mac}
                    self._signal_cartoning.emit(data)
                    return False
                elif msg == "find mac fail":
                    data = {"message": "macaddress is not found in current po", "macaddress": mac}
                    self._signal_cartoning.emit(data)
                    return False
                else:
                    return False
        except Exception as e:
            print(e)
            logging.debug(e)

    def add_mac_to_cartoning_list(self, macaddress):
        mac = macaddress
        try:
            self.cartoning_mac_list.append(mac)
            total = len(self.cartoning_mac_list)
            data = {"message": "macaddress added in cartoning list success", "macaddress": mac, "total": str(total),
                    "maclist": self.cartoning_mac_list}
            self._signal_cartoning.emit(data)
        except Exception as e:
            print(e)
            logging.debug(e)
            return False

    def get_cartoning_mac_lsit(self):
        return self.cartoning_mac_list

    def clear_cartoning_mac_lsit(self):
        self.cartoning_mac_list.clear()

    def cartoning_start(self, macaddress):
        mac = macaddress
        ret = self.check_mac(mac)
        if ret is False:
            return

        ret = self.check_mac_in_cartoning_list(mac)
        if ret is False:
            return

        ret = self.check_mac_not_already_cartoned(mac)
        if ret is False:
            return

        ret = self.check_pre_station_done(mac)
        if ret is False:
            return

        ret = self.upload_sensor_weight_to_corelight(mac)
        if ret is False:
            return

        self.add_mac_to_cartoning_list(mac)
        maclist = self.get_cartoning_mac_lsit()
        total = len(maclist)
        if total >= int(self.total_per_carton):
            data = {"message": "carton is full catroning auto end", "total": str(total)}
            self._signal_cartoning.emit(data)
            sleep(2)
            self.cartoning_end()

    def create_cartoning_labels(self):
        try:
            mac_list = self.get_cartoning_mac_lsit()
            ret = self.corelight.create_gcl_label(mac_list)
            url_list = ret['url_list']
            return url_list
        except Exception as e:
            print(e)
            logging.debug(e)
            return False

    def download_label_file_by_url(self, url):
        try:
            filename = os.path.basename(url)
            urlretrieve(url, filename, self.download_callback)
            if self.percent == 100:
                self.per = 0
                data = {"message": "download carton label success", "filename": filename}
                self._signal_cartoning.emit(data)
        except Exception as e:
            print(e)
            logging.debug(e)
            return False
        finally:
            urlcleanup()

    def download_callback(self, a, b, c):
        self.percent = 100.0*a*b/c
        if self.percent > 100:
            self.percent = 100
        print('%.2f%%' % self.percent)

    def print_carton_labels_by_filepath(self, filepath):
        try:
            if os.path.exists(filepath):
                self.printer.printing(filepath)
            else:
                data = {"message": "print carton label fail file not found"}
                self._signal_cartoning.emit(data)
        except Exception:
            pass

    def do_cartoning_end(self):
        try:
            data = {"message": "cartoning end"}
            self._signal_cartoning.emit(data)
            sleep(1)
            label_url_list = self.create_cartoning_labels()
            for url in label_url_list:
                self.download_label_file_by_url(url)
                filename = os.path.basename(url)
                self.print_carton_labels_by_filepath(filename)
                sleep(1)
                if os.path.exists(filename):
                    os.unlink(filename)
        except Exception as e:
            print(e)
            logging.debug(e)
            return False
        finally:
            self.clear_cartoning_mac_lsit()
            self.stop_get_weight()
            data = {"message": "cartoning end done"}
            self._signal_cartoning.emit(data)

    def cartoning_end(self):
        t = threading.Thread(target=self.do_cartoning_end)
        t.start()

    def cartoning_cancel(self):
        try:
            self.clear_cartoning_mac_lsit()
            self.stop_get_weight()
            data = {"message": "cartoning cancel done"}
            self._signal_cartoning.emit(data)
        except Exception:
            pass
