
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
    def __init__(self):
        self.init_data()

    def init_data(self):
        self.parser_config()

    def parser_config(self):
        file = 'config.ini'
        path = os.path.join(os.getcwd(), file)
        if os.path.exists(path):
            conf = configparser.ConfigParser()
            print("config.ini exist")
            conf.read(path)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
        else:
            pass

    def upload_mac_and_fts(self, mac, fts_result):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "macaddress": mac, "pcbafts": fts_result}
        print(body)
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            return response.text
        except Exception as e:
            print("Error:",e)
            return "newtwork_error"
