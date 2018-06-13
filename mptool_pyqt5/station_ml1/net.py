# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random

class network():
    ml1_print_url = None
    headers = {'content-type': "application/json"}

    def __init__(self):
        self.init_data()

    def init_data(self):
        self.read_config()

    def read_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            print("config.ini exist")
            conf.read(config)
            tn4cioip = conf.get('TN4CIO', 'TN4CIOIP')
        tmp = str(random.randint(1, 1000))
        self.ml1_print_url = "http://"+tn4cioip + \
            "/tn4cio/srv/copies_NGxx/app.php/print_ML1_label/"+tmp

    def request_print(self, mac):
        body = {"macaddress": mac}
        try:
            response = requests.post(self.ml1_print_url, data=json.dumps(
                body), headers=network.headers, timeout=5)
            print("response.text: ", response.text)
            print("response: ", response)

            text = json.loads(response.text)
            msg_type = text['messages'][0]['type']
            msg = text['messages'][0]['message']
            if msg_type == "fail":
                if msg == "find mac fail":
                    ret = "查找不到MAC:"+mac+" 的传感器"
                else:
                    ret = msg
            elif msg_type == "ok":
                ret = "成功"
            else:
                print("ml1_print error")
                ret = msg
                pass
            return ret
        except Exception as e:
            print("Error: network upload data Exception:", e)
            return "newtwork_error"
