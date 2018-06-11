# -*- coding: utf-8 -*-
import sys
import sqlite3
import requests
import json

class network():
    url = 'http://192.168.10.150/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/1234'
    headers = {'content-type': "application/json"}

    def __init__(self):
        self.init_data()

    def init_data(self):
        print("net modle init data")
    
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
