# -*- coding: utf-8 -*-
import threading
from threading import Timer
from time import *
import sqlite3
import requests
import json

class fts_data():
    def __init__(self):
        print("it is a init function")
    
    def get_Tests_data(self):
        data = []
        print("get the Tests table data")
        db = "ftsTestResults.db"
        cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID   from Tests"
        conn = sqlite3.connect(db)
        c = conn.cursor()
        cursor = c.execute(cmd)
        for row in cursor:
            data.append(row[0])
            data.append(row[7])
            sleep(1)
            print("get fts data:", data)
            return data
        conn.close()
