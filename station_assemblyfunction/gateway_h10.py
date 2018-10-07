# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random
import logging
from time import sleep
from urllib.request import urlretrieve
from urllib.request import urlcleanup


class GatewayH10():
    def __init__(self):
        self.gateway_ip = None
        self.TempRefMac = None
        self.init_data()

    def init_data(self):
        self.parser_config()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.gateway_ip = conf.get('Gateway_H10', 'ip')
            self.TempRefMac = conf.get('TemperatureRef', 'macaddress')
        else:
            pass

    # those apis and the work process all from Ray.song
    # Get Facility:
    # {"cmd": "get facility", "args": [true]}
    def Get_Facility(self):
        headers = {'content-type': "application/json"}
        body = {"cmd": "get facility", "args": [True]}
        try:
            url = "http://"+self.gateway_ip+":8511/v1/csd/simulation"
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print("pair network error:", e)
            return None

    # Pairing enable:
    # {"cmd": "permit joining", "args": [true]}
    def Pairing_enable(self):
        headers = {'content-type': "application/json"}
        body = {"cmd": "permit joining", "args": [True]}
        try:
            url = "http://"+self.gateway_ip +":8511/v1/csd/simulation"
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            return ret
        except Exception:
            return None

    # Pairing disable:
    # {"cmd": "permit joining", "args": [false]}
    def Pairing_disable(self):
        tmp = self.clear_buffer()
        if tmp == True:
            headers = {'content-type': "application/json"}
            body = {"cmd": "permit joining", "args": [False]}
            try:
                url = "http://"+self.gateway_ip+":8511/v1/csd/simulation"
                response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
                ret = response.text
                return ret
            except Exception as e:
                logging.debug(e)
                return False
        else:
            return False

    # Get Device:
    # {"cmd": "get device", "args": [0, true]}
    def Get_Device(self):
        headers = {'content-type': "application/json"}
        body = {"cmd": "get device", "args": [True]}
        try:
            # tmp = str(random.randint(1, 1000))
            url = "http://"+self.gateway_ip+":8511/v1/csd/simulation"
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print("pair network error:", e)

    # Get Endpoint:
    # {"cmd": "get endpoint", "args": [2, 1, true]}
    def Get_Endpoint(self, device_id):
        headers = {'content-type': "application/json"}
        body = {"cmd": "get endpoint", "args": [device_id, 1, True]}
        try:
            url = "http://"+self.gateway_ip+":8511/v1/csd/simulation"
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print(e)
            return None

    # Remove device:
    # {"cmd": "remove device", "args": [0]}
    def Remove_device(self, device_id):
        headers = {'content-type': "application/json"}
        body = {"cmd": "remove device", "args": [device_id]}
        try:
            url = "http://"+self.gateway_ip+":8511/v1/csd/simulation"
            response = requests.post(url, data=json.dumps(body), headers=headers, timeout=5)
            ret = response.text
            logging.debug(ret)
            return ret
        except Exception as e:
            print(e)

    def get_event(self, event_id):
        eventid = event_id
        url = 'http://'+self.gateway_ip +':8511/v1/csd/getevent?event_id=' + eventid
        try:
            response = requests.get(url)
            ret = response.text
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)

    def clear_buffer(self):
        url = 'http://'+self.gateway_ip+':8511/v1/csd/clear'
        try:
            response = requests.get(url)
            ret = response.text
            if ret == "null":
                return True
            else:
                return False
        except Exception as e:
            return False

    def getnext(self):
        url = 'http://'+self.gateway_ip+':8511/v1/csd/getnext'
        try:
            response = requests.get(url)
            ret = response.text
            return ret
        except Exception as e:
            print(e)
            logging.debug(e)
            return None

    def open_gateway_for_pair(self):
        self.clear_buffer()
        self.Pairing_enable()
        i = 0
        while i < 5:
            try:
                data = self.getnext()
                text = json.loads(data)
                permit = text['payload']['OnPermitJoiningChanged']
                code = text['payload']['code']
                if permit == "open" and code == "200":
                    print("pairing enable success")
                    return True
                else:
                    pass
            except Exception:
                pass
            finally:
                sleep(1)
                i = i + 1
                print("pairing enable retry:",i)
            if i > 4:
                return False

    def close_gateway_for_pair(self):
        self.clear_buffer()
        self.Pairing_disable()
        i = 0
        while i < 5:
            try:
                data = self.getnext()
                text = json.loads(data)
                msg = text['payload']['message']
                permit = text['payload']['OnPermitJoiningChanged']
                code = text['payload']['code']
                if permit == "closed" and code == "200":
                    print("pairing disable success")
                    return True
            except Exception:
                pass
            finally:
                sleep(1)
                i = i + 1
                print("pairing disable retry:",i)
            if i > 4:
                return False

    def remove_paired_sensor(self):
        self.clear_buffer()
        deviceid_list = self.get_sensor_deviceid_list()
        try:
            for id in deviceid_list:
                print("remove_paired_sensor---------------------------id:",id)
                self.Remove_device(id)
        except Exception:
            return False

    def get_sensor_deviceid_list(self):
        devices_id_list = []
        self.Get_Facility()
        sleep(1)
        i = 0
        while i < 5:
            try:
                data = self.getnext()
                text = json.loads(data)
                payload = text['payload']
                if payload:
                    devices_list = payload['facility']['inventory']['devices']
                    for device in devices_list:
                        deviceID = device['deviceID']
                        address64 = device['address64']
                        print("get sensor deviceid---------------------------get sensor deviceid :", deviceID, address64)
                        mac = address64.replace('0x', '').upper()
                        if mac == self.TempRefMac:
                            print(" -----it is TempRefMac:", mac)
                            pass
                        else:
                            devices_id_list.append(deviceID)
                    return devices_id_list
            except Exception:
                pass
            finally:
                i = i + 1
                sleep(1)

    def clean_up(self):
        self.close_gateway_for_pair()
        self.remove_paired_sensor()
