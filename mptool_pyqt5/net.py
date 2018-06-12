# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random

class network():
    url = 'http://192.168.10.150/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/1234'
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
            tn4cioip = conf.get('Mptool4PC', 'TN4CIOIP')
            print("--------------------------------------------------------------tn4cioip:", tn4cioip)
        tmp = str(random.randint(1,1000))
        network.url = "http://"+tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/"+tmp
        print("--------------------------------------------------------------url:",network.url)
    
    def upload_data(self, mac, fts_result):
        body = {"mac": mac, "FTS": fts_result}
        try:
            response = requests.post(network.url, data=json.dumps(body), headers=network.headers, timeout=5)
            print("response.text: ", response.text)
            print("response: ", response)
            return response.text
        except Exception as e:
            print("Error: network upload data Exception:",e)
            return "newtwork_error"
