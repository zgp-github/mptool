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
        print("net modle init data")
        self.read_config()

    def read_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            print("config.ini exist")
            conf.read(config)
            self.tn4cioip = conf.get('TN4CIO', 'TN4CIOIP')
            print("--------------------------------------------------------------tn4cioip:", self.tn4cioip)
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')

    def upload_mac_and_fts(self, mac, fts_result):
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion":self.hwversion, "macaddress": mac, "pcbafts": fts_result}
        print(body)
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip +"/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/"+tmp
            print("--------------------------------------------------------------url:", url)
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            print("response.text: ", response.text)
            print("response: ", response)
            return response.text
        except Exception as e:
            print("Error: network upload data Exception:",e)
            return "newtwork_error"

    def get_po_info(self):
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_po_info/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl get po info error:", e)

    def get_current_mac_num(self):
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip +"/tn4cio/srv/copies_NGxx/app.php/get_uploaded_mac_num/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl get po info error:", e)
