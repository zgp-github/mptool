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
            url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/ping/" + tmp
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

    def upload_assembly_fts(self, mac, fts_result):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode,
                "hwversion": self.hwversion, "macaddress": mac, "assemblyfts": fts_result}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/update_assembly_fts_data/" + tmp
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
            url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/get_po_info/" + tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def get_assemblyfts_tested_info(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/get_assemblyfts_tested_info/" + tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text

            text = json.loads(ret)
            print("---------------------get_assemblyfts_tested_info-------------:", text)
            result = text['result']
            if result == "ok":
                total = text['messages'][0]['total']
                produced = text['messages'][0]['produced']
                assemblyfts_pass_count = text['messages'][0]['assemblyfts_pass_count']
                assemblyfts_fail_count = text['messages'][0]['assemblyfts_fail_count']
                data = {"total": total, "produced": produced, "assemblyfts_pass_count": assemblyfts_pass_count,
                        "assemblyfts_fail_count": assemblyfts_fail_count}
                return data
            else:
                return None
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def check_previous_station_already_done(self, macaddress: str) -> bool:
        data = self.get_sensor_info_by_mac(macaddress)
        try:
            text = json.loads(data)
            print("check_previous_station_already_done:", text)
            result = text['result']
            if result == "ok":
                function = text['messages'][0]['function']
                if function == "none":
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
