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
            print(e)
            logging.debug(e)
            return False

    def upload_mac_and_fts(self, mac, fts_result):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion,
                "macaddress": mac, "pcbafts": fts_result}
        print(body)
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip +"/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def get_po_info(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_po_info/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def get_pcbafts_tested_info(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip +"/tn4cio/srv/copies_NGxx/app.php/get_pcbafts_tested_info/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text

            text = json.loads(ret)
            # print("---------------------get_pcbafts_tested_info-------------:", text)
            result = text['result']
            if result == "ok":
                total = text['messages'][0]['total']
                produced = text['messages'][0]['produced']
                pcbafts_pass_count = text['messages'][0]['pcbafts_pass_count']
                pcbafts_fail_count = text['messages'][0]['pcbafts_fail_count']
                data = {"total": total, "produced": produced, "pcbafts_pass_count": pcbafts_pass_count,
                        "pcbafts_fail_count": pcbafts_fail_count}
                return data
            else:
                return None
        except Exception as e:
            print(e)
            logging.debug(e)
            return None
