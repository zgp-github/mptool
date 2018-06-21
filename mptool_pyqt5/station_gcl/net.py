# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random
import logging

class network():
    headers = {'content-type': "application/json"}
    def __init__(self):
        self.init_data()

    def init_data(self):
        self.read_config()

    def read_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        conf = configparser.ConfigParser()
        if os.path.exists(config_path):
            conf.read(config_path)
            self.tn4cioip = conf.get('TN4CIO', 'TN4CIOIP')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.total_per_carton = conf.get('GclInfo', 'count_one_package')

    def check_mac_valid(self, mac):
        body = {"macaddress": mac}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/check_mac_valid/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("check mac for gcl:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl check mac error:", e)

    def get_po_info(self):
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_po_info/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("check gcl:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl get po info error:", e)

    def create_gcl_label(self, macaddress_list):
        mac_list = macaddress_list
        print("create_gcl_label mac list:", mac_list)
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "maclist": mac_list}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/create_gcl_label/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=60)
            ret = response.text
            print("check gcl:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl get po info error:", e)
