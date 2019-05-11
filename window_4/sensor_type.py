# -*- coding: utf-8 -*-
import sys
import os.path
import json
import configparser
import logging

class sensor_type():
    def __init__(self):
        self.init_data()

    def init_data(self):
        self.hwversion = None
        self.parser_config()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.hwversion = conf.get('PoInfo', 'hwversion')
        else:
            pass

    def get_sensor_type(self):
        # Note:
        # NG01 -- Door/Window Sensor
        # NG02 -- Water Leakage Sensor
        # NG03 -- Temperature Sensor
        # NG04 -- Motion Detector Sensor
        tmp1 = self.hwversion.find("NG01")
        tmp2 = self.hwversion.find("NG02")
        tmp3 = self.hwversion.find("NG03")
        tmp4 = self.hwversion.find("NG04")
        if tmp1 != -1:
            return "DoorWindow"
        elif tmp2 != -1:
            return "WaterLeakage"
        elif tmp3 != -1:
            return "Temperature"
        elif tmp4 != -1:
            return "MotionDetector"
        else:
            return "not support type"
