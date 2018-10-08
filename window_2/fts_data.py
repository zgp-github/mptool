# -*- coding: utf-8 -*-
import threading
from threading import Timer
import sqlite3
import requests
import json
import random
import datetime
import logging


class Fts(object):
    def __init__(self, db_file):
        self.db = db_file
        self.current_mac = None
        self.current_id = None
        self.current_time = None
        self.current_fts_result = None
        self.init_data()

    def init_data(self):
        self.get_last_id_and_mac()

    def get_last_id_and_mac(self):
        id_list = []
        cmd = "SELECT TestID from Tests"
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            cursor = c.execute(cmd)
            for row in cursor:
                id_list.append(row[0])
            self.current_id = max(id_list)
            print("current_id:", self.current_id)

            sql_cmd = "SELECT MACAddress, TimeStamp, TestResult FROM Tests WHERE TestID = "+str(self.current_id)
            cursor = c.execute(sql_cmd)
            for row in cursor:
                self.current_mac = row[0]
                self.current_time = row[1]
                self.current_fts_result = row[2]
            conn.close()
        except Exception:
            return None

    def get_last_fts_id(self):
        id_list = []
        cmd = "SELECT TestID from Tests"
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            cursor = c.execute(cmd)
            for row in cursor:
                id_list.append(row[0])
            last_id = max(id_list)
            print("last_id:", last_id)
            conn.close()
            return last_id
        except Exception:
            return None

    def get_fts_data_by_id(self, ftsid):
        fts_id = ftsid
        sql_cmd = "SELECT TestID, TimeStamp, TestStatus, TestResult, MACAddress FROM Tests WHERE TestID = "+str(fts_id)
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            cursor = c.execute(sql_cmd)
            for row in cursor:
                fts_id = row[0]
                fts_time = row[1]
                fts_status = row[2]
                fts_result = row[3]
                fts_mac = row[4]
            conn.close()
            data = {"fts_id": fts_id, "fts_time": fts_time, "fts_status": fts_status, "fts_result":fts_result,
                    "fts_mac":fts_mac}
            return data
        except Exception:
            return None

    def get_Tests_data(self):
        try:
            last_id = self.get_last_fts_id()
            data = self.get_fts_data_by_id(last_id)
            return data
        except Exception:
            return None
