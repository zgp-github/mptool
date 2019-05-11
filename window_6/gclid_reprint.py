# -*- coding: utf-8 -*-
import os
import re
import json
import logging
import configparser
from time import sleep
from urllib.request import urlcleanup
from urllib.request import urlretrieve

from window6.net import network
from window6.gcl_printer import printer


class gclid_reprint():
    def __init__(self):
        print("gclid reprint init")
        self.init_data()

    def init_data(self):
        self.corelight = network()
        self.gcl_printer = printer()
        self.parser_config()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
        else:
            pass

    def get_file(self, cmd):
        if self.pokey in cmd:
            gclid = cmd
            ret = self.get_file_by_gclid(gclid)
        else:
            mac = cmd
            ret = self.get_file_by_mac(mac)
        return ret

    def get_file_by_gclid(self, gcl_id):
        gclid = gcl_id
        log = "get gcl file by gclid: " + gclid
        print(log)
        logging.debug(log)

        ret = self.corelight.get_gcl_download_url_by_gclid(gclid)
        if ret is None:
            return "corelight return data is none"
        elif ret == "gclid not valid":
            return ret

        try:
            url_list = ret['url_list']
            data_list = []
            for url in url_list:
                name = os.path.basename(url)
                filepath = self.download_gclid(url, name)
                data_list.append(filepath)
            return data_list
        except Exception as e:
            print(e)
            logging.debug(e)
            return False

    def get_file_by_mac(self, macaddress):
        mac = macaddress
        log = "get gclid file by mac:" + mac
        print(log)
        logging.debug(log)

        check = self.mac_check(mac)
        if check == False:
            return "not valid macaddress"

        ret = self.corelight.get_gcl_download_url_by_mac(mac)
        if ret is None:
            return "corelight return data is none"
        elif ret == "find mac fail":
            return ret
        elif ret == "sensor not in gcl":
            return ret
        elif ret == "gcl file not fond":
            return ret

        try:
            url_list = ret['url_list']
            data_list = []
            for url in url_list:
                name = os.path.basename(url)
                print("-------------------------------------------------:", name, url)
                filepath = self.download_gclid(url, name)
                data_list.append(filepath)
            return data_list
        except Exception as e:
            print(e)
            logging.debug(e)
            return False

    def download_gclid(self, url, filename):
        try:
            urlretrieve(url, filename, self.download_callback)
            if self.percent == 100:
                sleep(0.5)
                self.per = 0
                gcl_file = os.path.join(os.getcwd(), filename)
                return gcl_file
        except Exception as e:
            print(e)
            logging.debug(e)
            return None
        finally:
            urlcleanup()

    def print(self, filepath):
        gcl_file = filepath
        if gcl_file is None:
            return False

        self.gcl_printer.printing(gcl_file)
        if os.path.exists(gcl_file):
            sleep(0.5)
            print("reprint gcl done, remove file:-------:" + gcl_file)
            os.unlink(gcl_file)
        else:
            pass

    def download_callback(self, a, b, c):
        self.percent = 100.0 * a * b / c
        if self.percent > 100:
            self.percent = 100
        print('%.2f%%' % self.percent)

    def mac_check(self, addr):
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
        return valid.match(addr) is not None
