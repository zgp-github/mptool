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
        config_path = os.path.join(os.getcwd(), config)
        conf = configparser.ConfigParser()
        if os.path.exists(config_path):
            conf.read(config_path)
            self.tn4cioip = conf.get('Corelight', 'tn4cioip')
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.total_per_carton = conf.get('GclInfo', 'count_one_package')

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

    def check_mac_valid(self, mac):
        headers = {'content-type': "application/json"}
        body = {"macaddress": mac, "pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/check_mac_valid_gcl/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            return ret
        except Exception as e:
            print(e)

    def get_po_info(self):
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_po_info/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("check gcl:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("gcl get po info error:", e)

    def upload_sensor_weight(self, mac, weight):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, \
                "macaddress": mac, "weight": weight}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip + \
                "/tn4cio/srv/copies_NGxx/app.php/upload_sensor_weight/"+tmp
            response = requests.post(url, data=json.dumps(
                body), headers=headers, timeout=5)
            ret = response.text
            print(ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            print("Error:", e)

    def create_gcl_label(self, macaddress_list):
        mac_list = macaddress_list
        print("create_gcl_label mac list:", mac_list)
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "maclist": mac_list}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/create_gcl_label/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=60)
            ret = response.text

            text = json.loads(ret)
            result = text['result']
            msg_type = text['messages'][0]['type']
            msg = text['messages'][0]['message']
            if result == "ok":
                url_list = text['messages'][0]['gcl_url_list']
                data = {"url_list": url_list}
                return data
            else:
                return None
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def get_gcl_download_url_by_gclid(self, gcl_id):
        gclid = gcl_id
        print("get_gcl_download_url_by_gclid gclid:", gclid)

        tmp = str(random.randint(1, 1000))
        url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_gcl_url_by_gclid/"+tmp
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "gcl_id": gclid}
        try:
            response = requests.post(url, data=json.dumps(body), headers=network.headers, timeout=5)
            ret = response.text
            print("gcl url:", ret)

            text = json.loads(ret)
            result = text['result']
            msg = text['messages'][0]['message']
            if result == "ok":
                url_list = text['messages'][0]['gcl_url_list']
                data = {"url_list": url_list}
                return data
            elif result == "fail":
                if msg == "gclid not valid":
                    return msg
            else:
                return None
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def get_gcl_download_url_by_mac(self, macaddress):
        mac = macaddress
        log = "get_gcl_download_url_by_mac mac: "+mac
        print(log)
        logging.debug(log)
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "macaddress": mac}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_gcl_download_url_by_mac/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=10)
            ret = response.text

            text = json.loads(ret)
            result = text['result']
            msg = text['messages'][0]['message']
            if result == "ok":
                url_list = text['messages'][0]['gcl_url_list']
                data = {"url_list": url_list}
                return data
            elif result == "fail":
                if msg == "find mac fail":
                    return msg
                elif msg == "sensor not in gcl":
                    return msg
                elif msg == "gcl file not fond":
                    return msg
            else:
                return None
        except Exception as e:
            logging.debug(e)
            print("error:", e)

    def gcl_reset_all_by_mac(self, macaddress):
        mac = macaddress
        print("gcl_reset_all mac:", mac)
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "macaddress": mac}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/gcl_reset_all_by_mac/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=10)
            ret = response.text
            print("response:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            logging.debug(e)
            print("error:", e)
            return None

    def gcl_reset_all_by_gclid(self, gcl_id):
        gclid = gcl_id
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "gcl_id": gclid}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://" + self.tn4cioip + "/tn4cio/srv/copies_NGxx/app.php/gcl_reset_all_by_gclid/" + tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=10)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            logging.debug(e)
            print("error:", e)
            return None

    def check_mac_already_in_gcl(self, mac):
        headers = {'content-type': "application/json"}
        body = {"macaddress": mac, "pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/check_mac_already_gcl/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            print("check_mac_already_in_gcl:", ret)
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def gclid_reset_part(self, mac_list):
        maclist = mac_list
        print("gclid reset part maclist:", maclist)
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "mac_list": maclist}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/gclid_reset_part/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=10)
            ret = response.text
            print("response:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            logging.debug(e)
            print(e)
            return None

    def get_gcl_info_by_mac(self, macaddress):
        mac = macaddress
        log = "get_gcl_info_by_mac mac: "+mac
        print(log)
        logging.debug(log)
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion, "macaddress": mac}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_gcl_maclist/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=10)
            ret = response.text
            print("response:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            logging.debug(e)
            print("error:", e)

    def get_count_already_in_gcl(self):
        headers = {'content-type': "application/json"}
        body = {"pokey": self.pokey, "countrycode": self.countrycode, "hwversion": self.hwversion}
        try:
            tmp = str(random.randint(1, 1000))
            url = "http://"+self.tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/get_count_already_in_gcl/"+tmp
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=10)
            ret = response.text
            print("response:", ret)
            logging.debug(ret)
            return ret
        except Exception as e:
            logging.debug(e)
            print("error:", e)

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
