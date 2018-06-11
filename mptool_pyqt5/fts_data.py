# -*- coding: utf-8 -*-
import threading
from threading import Timer
from time import *
import sqlite3
import requests
import json

class fts_data():
    current_mac = None
    current_id = None
    def __init__(self):
        print("it is a init function")
        self.init_data()
    
    def init_data(self):
        print("fts_data init data")
        id_list = []
        db = "ftsTestResults.db"
        cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID   from Tests"
        conn = sqlite3.connect(db)
        c = conn.cursor()
        cursor = c.execute(cmd)
        for row in cursor:
            id_list.append(row[0])
        self.current_id = max(id_list)
        print("current_id:", self.current_id)

        sql_cmd = "SELECT MACAddress FROM Tests WHERE  TestID = "+str(self.current_id)
        cursor = c.execute(sql_cmd)
        for row in cursor:
            self.current_mac = row[0]
            print("current_mac:", self.current_mac)
        conn.close()
    
    def get_Tests_data(self):
        print("get the Tests table data")
        db = "ftsTestResults.db"
        cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID   from Tests"
        conn = sqlite3.connect(db)
        c = conn.cursor()
        cursor = c.execute(cmd)
        for row in cursor:
            data = []
            data.append(row[0])
            data.append(row[7])
            print("get fts data:", data)
        return data
        conn.close()
