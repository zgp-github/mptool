# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random
from urllib.request import urlretrieve, urlcleanup
from station_ml1.ml1_printer import printer
import logging

class network():
    headers = {'content-type': "application/json"}
    def __init__(self):
        self.init_data()

    def init_data(self):
        self.read_config()
        self.ml1_printer = printer()
        printer_list = self.ml1_printer.list()
        print(printer_list)

    def read_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            print("config.ini exist")
            conf.read(config)
            tn4cioip = conf.get('TN4CIO', 'TN4CIOIP')
        tmp = str(random.randint(1, 1000))
        self.get_ml1_url = "http://"+tn4cioip + \
            "/tn4cio/srv/copies_NGxx/app.php/get_ml1_label_url/"+tmp

    def request_ml1_label(self, mac):
        body = {"macaddress": mac}
        try:
            response = requests.post(self.get_ml1_url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("request ml1 label response:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("Error: network upload data Exception:", e)
            return "newtwork_error"
