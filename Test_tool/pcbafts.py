# -*- coding: utf-8 -*-
import os
import threading
from threading import Timer
from time import *
import sqlite3
import requests
import json
import random
from PyQt5.QtCore import QTimer
import datetime
import configparser
from time import sleep

class fts_database():
    current_mac = None
    current_id = None
    current_time = None

    def __init__(self):
        self.parser_config()
        self.init_data()

    def init_data(self):
        print("database init data")
        self.get_current_id_and_mac()

    def parser_config(self):
        file = 'config.ini'
        path = os.path.join(os.getcwd(), file)
        if os.path.exists(path):
            print("fond the fts db:"+path+" success!")
            conf = configparser.ConfigParser()
            conf.read(path)
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.fts_db = conf.get('FTS_DB', 'db_name')
        else:
            print("fond the fts db:"+path+" fail!")

    # get the last id and mac
    def get_current_id_and_mac(self):
        id_list = []
        conn = sqlite3.connect(self.fts_db)
        cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID from Tests"

        c = conn.cursor()
        cursor = c.execute(cmd)
        for row in cursor:
            tmp_id = row[0]
            id_list.append(tmp_id)
            print("id:",tmp_id)
        self.current_id = max(id_list)
        self.t1 = self.current_id
        print("current_id:", self.current_id)
        conn.close()

    def wtite_fts_test_data(self):
        conn = sqlite3.connect(self.fts_db)

        i = datetime.datetime.now()
        y = "%04d" % i.year
        m = "%02d" % i.month
        d = "%02d" % i.day
        h = "%02d" % i.hour
        minute = "%02d" % i.minute
        s = "%02d" % i.second
        t = str(y)+"-"+str(m)+"-"+str(d)+" "+str(h)+":"+str(minute)+":"+str(s)

        self.t1 = self.t1 + 1

        t2 = 1
        t3 = t
        status = 'ERROR'
        result = 'NA'
        t6 = 'B1737030002'
        t7 = 'AE1ED4004A45A06D'
        mac = '0'
        t9 = '0000000000000000'
        t10 = '0'
        params = (self.t1, t2, t3, status, result, t6, t7, mac, t9, t10)
        sql = "INSERT OR IGNORE INTO Tests (TestID, TestLimitsID, 'TimeStamp', TestStatus, TestResult, FtsSerialNumber,ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID) VALUES(?,?,?,?,?,?,?,?,?,?)"
        conn.execute(sql, params)
        conn.commit()

        sleep(5)
        status = 'DONE'
        if self.t1%2 == 0:
            result = 'SUCCESS'
        else:
            result = 'PASSFAILLIMITERROR'

        mac = "%016s" % str(random.randint(1, 9999999999999999))
        # params = (status, result, mac, self.t1)
        # sql = "UPDATE Tests (TestStatus, TestResult, MACAddress) WHERE TestID = ? VALUES(?,?,?,?)"

        sql = "UPDATE Tests SET TestStatus = ?, TestResult = ?, MACAddress = ? WHERE TestID ="+str(self.t1)
        params = (status, result, mac)
        print("-------------------add fts db for QA id:"+str(self.t1)+" mac: "+mac)
        conn.execute(sql, params)
        conn.commit()

        conn.close()

        text = {"fts_id": str(self.t1), "fts_mac": mac}
        data = json.dumps(text)
        return data
