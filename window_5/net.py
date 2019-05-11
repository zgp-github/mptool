# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random
import logging
from urllib.request import urlretrieve
from urllib.request import urlcleanup


class network():
    headers = {'content-type': "application/json"}
    def __init__(self):
        self.init_data()

    def init_data(self):
        self.parser_config()

    def parser_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            print("config.ini exist")
            conf.read(config)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')

    def check_tn4cio(self):
        try:
            headers = {'content-type': "application/json"}
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/ping/"+tmp
            response = requests.post(url, headers=headers, timeout=5)
            ret = response.text
            print("ping tn4c.io ip:", ret)
            logging.debug(ret)
            text = json.loads(ret)
            ping_result = text['result']
            if ping_result == "pong":
                return True
        except Exception as e:
            print("Error:", e)
            return False

    def get_ml1_download_url(self, mac):
        body = {"macaddress": mac}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_ml1_label_download_url/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("request ml1 label response:", ret)
            logging.debug(ret)
            text =  json.loads(ret)
            url = text['messages'][0]['download_url']
            return url
        except Exception:
            return None

    def get_po_info(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_po_info/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print("get po info error:", e)

    def check_previous_station_already_done(self, macaddress: str) -> bool:
        data = self.get_sensor_info_by_mac(macaddress)
        try:
            text = json.loads(data)
            print("check_previous_station_already_done:", text)
            result = text['result']
            if result == "ok":
                pcbafts = text['messages'][0]['assemblyfts']
                if pcbafts == "none":
                    return False
                else:
                    return True
            else:
                return False
        except Exception as e:
            print(e)
            logging.debug(e)
            return False

    def get_sensor_info_by_mac(self, macaddress: str):
        mac = macaddress
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion,
                "macaddress": mac}
        tmp = str(random.randint(1, 1000))
        try:
            url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/get_sensor_station_info_by_mac/" + tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)
            return None