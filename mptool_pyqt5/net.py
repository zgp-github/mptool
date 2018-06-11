# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import requests
import json
import configparser
import random

class network():
    url = 'http://192.168.10.150/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/1234'
    headers = {'content-type': "application/json"}

    def __init__(self):
        self.init_data()

    def init_data(self):
        print("net modle init data")
        self.read_config()

    def read_config(self):
        config = 'config.ini'
        conf = configparser.ConfigParser()
        if os.path.exists(config):
            print("config.ini exist")
            pass
        else:
            print("config.ini not exist, create it")
            conf.read(config)
            conf.add_section("Mptool4PC")
            conf.set("Mptool4PC","STATION","PCBA_FTS")
            conf.set("Mptool4PC","#station1","PCBA_FTS")
            conf.set("Mptool4PC","#station2","ASSEMBLY_PAIR")
            conf.set("Mptool4PC","#station3","ASSEMBLY_FTS")
            conf.set("Mptool4PC","#station4","ASSEMBLY_ML1")
            conf.set("Mptool4PC","#station5","ASSEMBLY_GCL")
            conf.set("Mptool4PC","#station6","ASSEMBLY_REPAIR")
            conf.set("Mptool4PC","TN4CIOIP","192.168.10.150")
            conf.write(open(config, "w"))

        conf.read(config)
        station = conf.get('Mptool4PC', 'STATION')
        tn4cioip = conf.get('Mptool4PC', 'TN4CIOIP')
        print("--------------------------------------------------------------:",station, tn4cioip)
        tmp = str(random.randint(1,1000))
        network.url = "'http://"+tn4cioip+"/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/"+tmp
        print("--------------------------------------------------------------url:",network.url)
    
    def upload_data(self, mac, fts_result):
        body = {"mac": mac, "FTS": fts_result}
        try:
            response = requests.post(network.url, data=json.dumps(body), headers=network.headers, timeout=5)
            print("response.text: ", response.text)
            print("response: ", response)
            return response.text
        except Exception as e:
            print("Error: network upload data Exception:",e)
            return "newtwork_error"
