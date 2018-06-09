import sys
import sqlite3
import requests
import json
import threading
from time import sleep

# db = "ftsTestResults.db"
# conn = sqlite3.connect(db)
# c = conn.cursor()

# cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID from Tests"
# cursor = c.execute(cmd)
# for row in cursor:
#     print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
#     mac = row[7]

# sqlcmd = "SELECT TestID, Status, BistID, Name, ResultCode, Result from TestResults_Bist"
# cursor = c.execute(sqlcmd)
# for row in cursor:
#     print(row[0], row[1], row[2], row[3], row[4], row[5])
# conn.close()

# url = 'http://192.168.10.150/tn4cio/srv/copies_NGxx/app.php/python_daemon_test/1234'
# body = {"mac": mac}
# headers = {'content-type': "application/json"}


# response = requests.post(url, data=json.dumps(body), headers=headers)
# print("response.text: ", response.text)
# print("response.status_code: ", response.status_code)

class FTS_data():
    db = "ftsTestResults.db"
    url = 'http://192.168.10.150/tn4cio/srv/copies_NGxx/app.php/update_NGxx_mac_to_database/1234'

    def __init__(self):
        self.init()

    def init(self):
        print("init function")
        t = threading.Thread(target=self.get_fts_data)
        t.start()

    def get_fts_data(self):
        while True:
            print("start get the data from FTS database")
            conn = sqlite3.connect(FTS_data.db)
            c = conn.cursor()
            cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID from Tests"
            cursor = c.execute(cmd)
            for row in cursor:
                print(row[0], row[1], row[2], row[3], row[4],
                      row[5], row[6], row[7], row[8], row[9])
            mac = row[7]
            FTS_test_result = "success"

            sqlcmd = "SELECT TestID, Status, BistID, Name, ResultCode, Result from TestResults_Bist"
            cursor = c.execute(sqlcmd)
            for row in cursor:
                print(row[0], row[1], row[2], row[3], row[4], row[5])

            headers = {'content-type': "application/json"}
            body = {"mac": mac, "FTS": FTS_test_result}
            response = requests.post(
                FTS_data.url, data=json.dumps(body), headers=headers)
            print("response.text: ", response.text)
            sleep(2)
        conn.close()

def main():
    FTS_data()

if __name__ == '__main__':
    main()
