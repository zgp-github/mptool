# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random
from urllib.request import urlretrieve
from station_ml1.ml1_printer import printer

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

    def request_print(self, mac):
        body = {"macaddress": mac}
        try:
            response = requests.post(self.get_ml1_url, data=json.dumps(
                body), headers=network.headers, timeout=5)

            print("response.text", response.text)

            text = json.loads(response.text)
            url = text['result'][0]
            print(url)

            ml1 = os.path.join(os.getcwd(), "ml1.png")
            urlretrieve(url, ml1)

            self.ml1_printer.printing(ml1)

            # text = json.loads(response.text)
            # msg_type = text['messages'][0]['type']
            # msg = text['messages'][0]['message']
            # if msg_type == "fail":
            #     if msg == "find mac fail":
            #         ret = "查找不到MAC:"+mac+" 的传感器"
            #     else:
            #         ret = msg
            # elif msg_type == "ok":
            #     ret = "成功"
            # else:
            #     print("ml1_print error")
            #     ret = msg
            #     pass
            # return ret
            return "ok"
        except Exception as e:
            print("Error: network upload data Exception:", e)
            return "newtwork_error"
