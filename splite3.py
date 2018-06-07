
import sqlite3
import requests
import json

db = "ftsTestResults.db"
conn = sqlite3.connect(db)
c = conn.cursor()

cmd = "SELECT TestID, TestLimitsID, TimeStamp, TestStatus, TestResult, FtsSerialNumber, ChipSerialNumber, MACAddress, DUTSerialNumber, RaceConfigID   from Tests"
cursor = c.execute(cmd)
for row in cursor:
    print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
conn.close()

url = 'http://192.168.10.150/tn4cio/srv/copies_NGxx/app.php/python_daemon_test/1234'
body = {"type": "text"}
headers = {'content-type': "application/json"}


response = requests.post(url, data=json.dumps(body), headers=headers)
print("response.text: ", response.text)
print("response.status_code: ", response.status_code)


