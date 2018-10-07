# -*- coding: utf-8 -*-
import sys
import os.path
import requests
import json
import configparser
import random
import logging


class network():
    def __init__(self):
        self.pokey = None
        self.countrycode = None
        self.hwversion = None
        self.tn4cioip = None
        self.init_data()

    def init_data(self):
        self.parser_config()

    def parser_config(self):
        file = 'config.ini'
        path = os.path.join(os.getcwd(), file)
        if os.path.exists(path):
            conf = configparser.ConfigParser()
            conf.read(path)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
        else:
            pass

    def check_tn4cio(self):
        headers = {'content-type': "application/json"}
        tmp = str(random.randint(1, 1000))
        url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/ping/" + tmp
        try:
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
            return False

    def get_po_info(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        tmp = str(random.randint(1, 1000))
        url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/get_po_info/" + tmp
        try:
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            print("get_po_info:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print(e)
            return None

    def request_pl2_label(self, mac):
        headers = {'content-type': "application/json"}
        body = {"macaddress": mac}
        tmp = str(random.randint(1, 1000))
        url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/get_pl2_download_url/" + tmp
        try:
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            print("request pl2 label response:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("Error: network upload data Exception:", e)
            return "newtwork_error"

    def get_pl2_label_download_url(self, macaddress: str) -> str:
        try:
            mac = macaddress
            ret = self.request_pl2_label(mac)
            text = json.loads(ret)
            result = text['result']
            if result == "ok":
                file = text['messages'][0]['file']
                url = text['messages'][0]['url']
                hw = text['messages'][0]['hwversion']
                return url
            else:
                return "none"
        except Exception:
            return "none"

    def get_tested_sensors_info(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        tmp = str(random.randint(1, 1000))
        url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_factoryoqc_tested_info/"+tmp
        try:
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print(e)
            return None

    def upload_oqc_to_tn4cio(self, mac, val):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion,
                "macaddress": mac, "factoryoqc": val}
        tmp = str(random.randint(1, 1000))
        url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/update_factory_oqc_data/"+tmp
        try:
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print(e)
            return None

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