# -*- coding: utf-8 -*-
import sys
import json
import logging
import os.path
import configparser
from time import sleep
from time import localtime
from time import strftime

from window4.gateway_h10 import GatewayH10


class MotionDetectot():
    def __init__(self):
        self.hwversion = None
        self.gateway = None
        self.init_data()

    def init_data(self):
        self.parser_config()
        self.gateway = GatewayH10()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.hwversion = conf.get('PoInfo', 'hwversion')
            return True
        else:
            return False

    def get_market_version(self, obj: object) -> str:
        data = obj
        try:
            text = json.loads(data)
            inbound_list = text['payload']['OnAttributeChanged']['applications'][0]['inbound']
            for item in inbound_list:
                cluster = item['cluster']
                print("-----get_market_version----cluster:", cluster)
                if cluster == "0x0000 \"basic\"":
                    attributes_list = item['attributes']
                    for attributes_item in attributes_list:
                        if attributes_item['attributeID'] == "0x0001":
                            value = attributes_item['value']
                            value = value.replace('[', '')
                            value = value.replace(']', '')
                            value = value.split(',', 1)[0]
                            market_version = value
                            return market_version
            return "none"
        except Exception as e:
            print(e)
            return "none"

    def get_paired_motiondetector_sensor_info(self):
        try:
            data = self.gateway.getnext()
            text = json.loads(data)

            code = text['payload']['code']
            if code == '200':
                print("get_paired_waterleakage_sensor_info:",text)
                address64 = text['payload']['OnAttributeChanged']['address64']
                deviceID = text['payload']['OnAttributeChanged']['deviceID']
                vendor = text['payload']['OnAttributeChanged']['vendor']
                model = text['payload']['OnAttributeChanged']['model']
                timestamp = text['timestamp']

                market_version = self.get_market_version(data)

                mac = address64.replace('0x', '').upper()
                if mac == self.TempRefMac:
                    return None
                else:
                    data = {"address64": address64, "model": model, "vendor": vendor, "deviceID": deviceID,
                            "timestamp": timestamp, "market_version": market_version}
                    return data
        except Exception:
            return None