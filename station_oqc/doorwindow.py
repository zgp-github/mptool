# -*- coding: utf-8 -*-
import sys
import json
import logging
import os.path
import configparser
from time import sleep
from time import localtime
from time import strftime
from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from station_oqc.gateway_h10 import GatewayH10
from station_oqc.net import network


class DoorWindow(QObject):
    _signal_doorwindow = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(DoorWindow, self).__init__(parent)
        self.hwversion = None
        self.gateway = None
        self.corelight = None
        self.QA_FUNCTION_TESTING = False
        self.init_data()

    def init_data(self):
        self.parser_config()
        self.gateway = GatewayH10()
        self.corelight = network()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.TempRefMac = conf.get('TemperatureRef', 'macaddress')
            return True
        else:
            return False

    def enable_gateway_pairing(self):
        data = {"message": "pairing enable opening"}
        self._signal_doorwindow.emit(data)

        ret = self.gateway.open_gateway_for_pair()
        if ret is True:
            data = {"message": "gateway enable pairing success"}
            self._signal_doorwindow.emit(data)
            return True
        else:
            data = {"message": "gateway enable pairing fail"}
            self._signal_doorwindow.emit(data)
            return False

    def disable_gateway_pairing(self):
        self.gateway.close_gateway_for_pair()

    def get_market_version(self, obj: object) -> str:
        data = obj
        try:
            text = json.loads(data)
            inbound_list = text['payload']['OnAttributeChanged']['applications'][0]['inbound']
            for item in inbound_list:
                cluster = item['cluster']
                print("-----get_market_version----cluster:", cluster)
                if cluster == "0x0000 \"basic\"":
                    attributes_list = item['attributes']
                    for attributes_item in attributes_list:
                        if attributes_item['attributeID'] == "0x0001":
                            value = attributes_item['value']
                            value = value.replace('[', '')
                            value = value.replace(']', '')
                            value = value.split(',', 1)[0]
                            market_version = value
                            return market_version
            return "none"
        except Exception as e:
            print(e)
            return "none"

    def get_paired_doorwindow_sensor(self):
        try:
            data = self.gateway.getnext()
            text = json.loads(data)

            code = text['payload']['code']
            if code == '200':
                address64 = text['payload']['OnAttributeChanged']['address64']
                deviceID = text['payload']['OnAttributeChanged']['deviceID']
                vendor = text['payload']['OnAttributeChanged']['vendor']
                model = text['payload']['OnAttributeChanged']['model']
                timestamp = text['timestamp']

                mac = address64.replace('0x', '').upper()
                if mac == self.TempRefMac:
                    return None
                else:
                    data = {"address64": address64, "model": model, "vendor": vendor, "deviceID": deviceID,
                            "timestamp": timestamp}
                    return data
        except Exception:
            return None

    def check_sensor_type(self, type: str) -> bool:
        sensor_type = type.upper()
        if sensor_type in self.hwversion:
            return True
        else:
            return False

    def get_doorwindow_sensor_status(self):
        data = self.gateway.getnext()
        print("---------get_doorwindow_sensor_status:",data)
        ret = self.parser_doorwindow_status(data)
        return ret

    def parser_doorwindow_status(self, obj):
        data = obj
        try:
            text = json.loads(data)
            timestamp = text['timestamp']
            address64 = text['payload']['OnAttributeChanged']['address64']
            deviceID = text['payload']['OnAttributeChanged']['deviceID']
            vendor = text['payload']['OnAttributeChanged']['vendor']
            model = text['payload']['OnAttributeChanged']['model']

            inbound_list = text['payload']['OnAttributeChanged']['applications'][0]['inbound']
            for item in inbound_list:
                cluster = item['cluster']
                if cluster == "0x0500 \"IAS zone\"":
                    attributes_list = item['attributes']
                    for attributes_item in attributes_list:
                        if attributes_item['attributeID'] == "0x0002":
                            value = attributes_item['value']
                            value = value.replace('[', '')
                            value = value.replace(']', '')
                            value = value.split(',', 1)[0]
                            if int(value) & 0x01 == 0:
                                status = "closed"
                            else:
                                status = "opened"
                            data = {"timestamp": timestamp, "address64": address64, "deviceID": deviceID,
                                    "vendor": vendor, "model": model, "status": status}
                            print("---------doorwindow sensor:", data)
                            return data
                        else:
                            pass
                else:
                    pass
        except Exception:
            pass

    def check_pre_station_done(self, macaddress: str) -> bool:
        ret = self.corelight.check_previous_station_already_done(macaddress)
        if ret is True:
            data = {"message": "pre station done check success"}
            self._signal_doorwindow.emit(data)
            sleep(1)
            return True
        else:
            data = {"message": "pre station done check fail"}
            self._signal_doorwindow.emit(data)
            sleep(1)
            return False

    def get_paired_sensor_info(self):
        i = 0
        while i < 60:
            try:
                ret = self.get_paired_doorwindow_sensor()
                print("-------- doorwindow sensor ------retry:", i, ret)
                address64 = ret['address64']
                macaddress = address64.replace('0x', '').upper()
                model = ret['model']
                vendor = ret['vendor']
                deviceid = ret['deviceID']
                timestamp = ret['timestamp']
                if macaddress:
                    data = {"message": "doorwindow_sensor pairing done",
                            "macaddress": macaddress, "model": model, "vendor": vendor, "deviceid": deviceid, "timestamp": timestamp}
                    self._signal_doorwindow.emit(data)
                    sleep(2)
                    return data
            except Exception:
                pass
            finally:
                i = i + 1
                sleep(1)
        print("-------- waitting sensor timeout-------retry:",i)
        data = {"message": "pairing timeout"}
        self._signal_doorwindow.emit(data)
        return None

    def set_function_test_confirm_failed(self):
        self.function_test_failed_confirm_flag = True

    def clear_function_test_confirm_failed(self):
        self.function_test_failed_confirm_flag = None

    def get_function_test_confirm_failed(self):
        return self.function_test_failed_confirm_flag

    def function_DoorWindow(self):
        sensor_open_test = None
        sensor_close_test = None
        macaddress = None
        self.clear_function_test_confirm_failed()

        data = {"message": "start doowwindow sensor function test"}
        self._signal_doorwindow.emit(data)
        sleep(1)

        i = 0
        while i < 30:
            ret = self.get_doorwindow_sensor_status()
            try:
                timestamp = ret['timestamp']
                address64 = ret['address64']
                macaddress = address64.replace('0x', '').upper()
                deviceID = ret['deviceID']
                vendor = ret['vendor']
                model = ret['model']
                status = ret['status']
                print("---- get Door/Window sensor: ", status, str(i))
                if status == "opened":
                    data = {"message": "doowwindow sensor is opened", "timestamp": timestamp, "macaddress": macaddress,
                            "deviceID": deviceID, "vendor": vendor, "model": model, "status": status}
                    self._signal_doorwindow.emit(data)
                    sensor_open_test = "pass"
                    sleep(2)
                elif status == "closed":
                    data = {"message": "doowwindow sensor is closed", "timestamp": timestamp, "macaddress": macaddress,
                            "deviceID": deviceID, "vendor": vendor, "model": model, "status": status}
                    self._signal_doorwindow.emit(data)
                    sensor_close_test = "pass"
                    sleep(2)
            except Exception:
                pass
            finally:
                i = i + 1
                print("------------------------function test times:",i)
                sleep(1)

            if sensor_open_test == "pass" and sensor_close_test == "pass":
                data = {"message": "doowwindow sensor function test success", "macaddress": macaddress}
                self._signal_doorwindow.emit(data)
                sleep(2)
                return True

            ret = self.get_function_test_confirm_failed()
            if ret is True:
                print("---- user confirmed the function failed ------")
                data = {"message": "comfirm doowwindow sensor function test failed", "macaddress": macaddress}
                self._signal_doorwindow.emit(data)
                sleep(2)
                return False

            if i >= 29:
                data = {"message": "sensor function test timeout"}
                self._signal_doorwindow.emit(data)
                return False

    def function_test_start(self):
        try:
            ret = self.enable_gateway_pairing()
            if ret is True:
                pass
            else:
                return False

            text = self.get_paired_sensor_info()
            model = text['model']
            ret = self.check_sensor_type(model)
            if ret is True:
                pass
            else:
                data = {"message": "error not doorwindow sensor"}
                self._signal_doorwindow.emit(data)
                return False

            macaddress = text['macaddress']
            ret = self.check_pre_station_done(macaddress)
            if ret is False:
                return

            ret = self.function_DoorWindow()
            if ret is True:
                sleep(2)
                self.qa_longtime_testing()
            else:
                pass
        except Exception:
            pass
        finally:
            self.disable_gateway_pairing()

    def qa_longtime_testing(self):
        data = {"message": "doorwindow sensor qa longtime test starting"}
        self._signal_doorwindow.emit(data)
        self.QA_FUNCTION_TESTING = True
        while self.QA_FUNCTION_TESTING == True:
            ret = self.get_doorwindow_sensor_status()
            try:
                timestamp = ret['timestamp']
                address64 = ret['address64']
                macaddress = address64.replace('0x', '').upper()
                deviceID = ret['deviceID']
                vendor = ret['vendor']
                model = ret['model']
                status = ret['status']
                data = {"message": "doorwindow sensor qa testing info", "timestamp": timestamp, "macaddress": macaddress,
                        "deviceID": deviceID, "vendor": vendor, "model": model, "status": status}
                print("---------doorwindow sensor QA:", data)
                self._signal_doorwindow.emit(data)
            except Exception:
                pass
            finally:
                sleep(1)

    def exit_qa_longtime_testing(self):
        if self.QA_FUNCTION_TESTING:
            self.QA_FUNCTION_TESTING = False
            data = {"message": "exit doorwindow sensor qa testing"}
            self._signal_doorwindow.emit(data)
        else:
            pass
