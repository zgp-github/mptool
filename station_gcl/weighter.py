# -*- coding: utf-8 -*-
import os
import configparser
import logging
import serial
import serial.tools.list_ports
from time import sleep


class Weighter():
    def __init__(self):
        self.serialport = None
        self.baudrate = None
        self.max_weight = None
        self.min_weight = None
        self.init_data()

    def init_data(self):
        self.parser_config()
        self.init_weighter()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.serialport = conf.get('Weighter', 'serialport')
            self.baudrate = conf.get('Weighter', 'baudrate')
            self.max_weight = conf.get('Weighter', 'max')
            self.min_weight = conf.get('Weighter', 'min')

    def init_weighter(self):
        serial_list = list(serial.tools.list_ports.comports())
        port_list = []
        for item in serial_list:
            port_list.append(item[0])

        if self.serialport in port_list:
            print("found COM: ", self.serialport)

    def serial_list(self):
        serial_list = list(serial.tools.list_ports.comports())
        return serial_list

    def port_list(self):
        port_list = []
        for item in self.serial_list():
            port_list.append(item[0])
        return port_list

    def get_weight(self):
        try:
            serialFd = serial.Serial(self.serialport, self.baudrate, timeout=60)
            weight = 0.0
            for i in range(0, 500):
                line = serialFd.readline()
                tmp = bytes.decode(line)
                # print("data read line: ", tmp)
                if "ST,GS," in tmp:
                    # Note: According the ES-6KCC(weighter) datasheet
                    # "ST" = STABLE "GS" = GROSS
                    # "US" = UNSTABLE
                    weight = tmp.split(",", 3)[2]
                    weight = weight.strip()
                    weight = weight.replace(' ', '')
                    break
                else:
                    pass
            serialFd.close()
            # print("----------------------------ES-6KCC(weighter) get sensor weight:", weight)
            return weight
        except Exception as e:
            print("Error:", e)
            logging.debug(e)
            return None
