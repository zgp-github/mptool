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
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            conf.read(config)
            ip = conf.get('TN4CIO', 'TN4CIOIP')
        tmp = str(random.randint(1, 1000))
        self.url = "http://"+ip+"/tn4cio/srv/copies_NGxx/app.php/check_mac_valid/"+tmp

    def check_mac_valid(self, mac):
        body = {"macaddress": mac}
        try:
            response = requests.post(self.url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("check mac for gcl:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl error:", e)
