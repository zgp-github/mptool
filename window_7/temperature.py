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
from PyQt5.QtCore import QTimer

from window7.gateway_h10 import GatewayH10
from window7.net import network


class Temperature(QObject):
    _signal_temperature = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Temperature, self).__init__(parent)
        self.hwversion = None
        self.gateway = None
        self.corelight = None
        self.TempRefMac = None
        self.TempRefRange = None
        self.useRefdefaultvaule = None
        self.Refdefaultvaule = None
        self.RefTemperature = None
        self.timerRef = None
        self.init_data()

    def init_data(self):
        self.parser_config()
        self.gateway = GatewayH10()
        self.corelight = network()
        self.init_reference_temperature()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config_path)
            self.hwversion = conf.get('PoInfo', 'hwversion')
            self.TempRefMac = conf.get('TemperatureRef', 'macaddress')
            self.TempRefRange = conf.get('TemperatureRef', 'range')
            self.useRefdefaultvaule = conf.get('TemperatureRef', 'usedefaultvalue')
            self.Refdefaultvaule = conf.get('TemperatureRef', 'defaultvalue')
            return True
        else:
            return False

    def enable_gateway_pairing(self):
        data = {"message": "pairing enable opening"}
        self._signal_temperature.emit(data)

        ret = self.gateway.open_gateway_for_pair()
        if ret is True:
            data = {"message": "gateway enable pairing success"}
            self._signal_temperature.emit(data)
            return True
        else:
            data = {"message": "gateway enable pairing fail"}
            self._signal_temperature.emit(data)
            return False

    def disable_gateway_pairing(self):
        self.gateway.close_gateway_for_pair()

    def check_reference_sensor_exist(self):
        self.gateway.Get_Facility()
        sleep(1)
        i = 0
        while i < 5:
            try:
                data = self.gateway.getnext()
                text = json.loads(data)
                payload = text['payload']
                if payload:
                    devices_list = payload['facility']['inventory']['devices']
                    for device in devices_list:
                        deviceID = device['deviceID']
                        address64 = device['address64']
                        print("---check_reference_sensor_exist deviceid mac:", deviceID, address64)
                        mac = address64.replace('0x', '').upper()
                        if mac == self.TempRefMac:
                            print(" -----found TempRefMac:", mac)
                            return True
                        else:
                            pass
            except Exception:
                pass
            finally:
                print(" -----found TempRef:",i)
                i = i + 1
                sleep(1)
        if i >= 4:
            return False

    def get_market_version(self, obj: object) -> str:
        data = obj
        try:
            text = json.loads(data)
            inbound_list = text['payload']['OnAttributeChanged']['applications'][0]['inbound']
            for item in inbound_list:
                cluster = item['cluster']
                print("----temperature--get_market_version----cluster:", cluster)
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

    def parser_temperature_data(self, obj: object)-> str:
        data = obj
        try:
            text = json.loads(data)
            inbound_list = text['payload']['OnAttributeChanged']['applications'][0]['inbound']
            for item in inbound_list:
                cluster = item['cluster']
                if cluster == "0x0402 \"temperature measurement\"":
                    attributes_list = item['attributes']
                    for attributes_item in attributes_list:
                        if attributes_item['attributeID'] == "0x0000":
                            value = attributes_item['value']
                            value = value.replace('[', '')
                            value = value.replace(']', '')

                            T1 = value.split(',', 1)[0]
                            T2 = value.split(',', 1)[1]

                            temp = (int(T2)*265 + int(T1)) / 100
                            print("parser_temperature_data temp:", str(temp))
                            return str(temp)
            return "none"
        except Exception as e:
            print(e)
            return "none"

    def get_paired_temperature_sensor_info(self):
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
                # print("get paired temperature sensor info mac:", mac)
                if mac == self.TempRefMac:
                    return None
                else:
                    temperature = self.parser_temperature_data(data)
                    data = {"address64": address64, "model": model, "vendor": vendor, "deviceID": deviceID,
                            "timestamp": timestamp, "temperature": temperature}
                    return data
        except Exception:
            return None

    def check_sensor_type(self, type: str) -> bool:
        sensor_type = type.upper()
        if sensor_type in self.hwversion:
            return True
        else:
            return False

    # get reference temperature from a special NG03 sensor
    # then compare with the producing temperature sensor
    def get_reference_temperature(self):
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
                    temperature = self.parser_temperature_data(data)
                    data = {"address64": address64, "model": model, "vendor": vendor, "deviceID": deviceID,
                            "timestamp": timestamp, "temperature": temperature}
                    print("get Ref temperature:", data)
                    return data
                else:
                    return None
        except Exception:
            return None

    def pairing_reference_temperature_sensor(self):
        ret = self.enable_gateway_pairing()
        if ret is True:
            pass
        else:
            return False
        i = 0
        while i < 60:
            try:
                ret = self.get_reference_temperature()
                if ret is None:
                    pass
                else:
                    address64 = ret['address64']
                    macaddress = address64.replace('0x', '').upper()
                    temperature = ret['temperature']
                    data = {"message": "reference temperature sensor pairing success",
                            "macaddress": macaddress, "temperature": temperature}
                    self._signal_temperature.emit(data)
                    return True
            except Exception:
                pass
            finally:
                print("pairing_reference_temperature_sensor:", i)
                sleep(1)
                i = i + 1
                if i > 59:
                    data = {"message": "reference temperature sensor pairing fail"}
                    self._signal_temperature.emit(data)
                    break

    def init_reference_temperature(self):
        self.timerRef = QTimer()
        self.timerRef.setInterval(5000)
        self.timerRef.start()
        self.timerRef.timeout.connect(self.onTimerOutForGetRef)

    def onTimerOutForGetRef(self):
        try:
            if self.useRefdefaultvaule == "yes":
                self.RefTemperature = self.Refdefaultvaule
                data = {"message": "update reference tempreture value", "tempreture": self.RefTemperature}
                self._signal_temperature.emit(data)
            else:
                ret = self.get_reference_temperature()
                tmp = ret['temperature']
                if tmp != None and tmp != "none":
                    self.RefTemperature = tmp
                    data = {"message": "update reference tempreture value", "tempreture": self.RefTemperature}
                    print(data)
                    self._signal_temperature.emit(data)
                else:
                    pass
        except Exception:
            pass

    def check_pre_station_done(self, macaddress: str) -> bool:
        ret = self.corelight.check_previous_station_already_done(macaddress)
        if ret is True:
            data = {"message": "pre station done check success"}
            self._signal_temperature.emit(data)
            sleep(1)
            return True
        else:
            data = {"message": "pre station done check fail"}
            self._signal_temperature.emit(data)
            sleep(1)
            return False

    def get_paired_sensor_info(self):
        i = 0
        while i < 60:
            try:
                ret = self.get_paired_temperature_sensor_info()
                print("-------- temperature sensor ------retry:", i,ret)
                address64 = ret['address64']
                macaddress = address64.replace('0x', '').upper()
                model = ret['model']
                vendor = ret['vendor']
                deviceid = ret['deviceID']
                timestamp = ret['timestamp']
                temperature = ret['temperature']
                if address64:
                    data = {"message": "temperature_sensor pairing done", "macaddress": macaddress, "model": model,
                            "vendor": vendor, "deviceid":deviceid, "timestamp":timestamp, "temperature":temperature}
                    self._signal_temperature.emit(data)
                    sleep(2)
                    return data
            except Exception:
                pass
            finally:
                i = i + 1
                sleep(1)
                if i >= 59:
                    print("-------- pairing timeout-------retry:",i)
                    data = {"message": "pairing timeout"}
                    self._signal_temperature.emit(data)
                    return None

    def function_temperature(self, temperature: str, macaddress: str) -> bool:
        try:
            # compare the temperature value with the Reference
            diff = abs(float(temperature) - float(self.RefTemperature))

            print("compare_temperature_with_ref diff:", diff)
            if diff <= float(self.TempRefRange):
                data = {"message": "temperature sensor function test success",
                        "macaddress": macaddress, "temperature": temperature, "reference": self.RefTemperature}
                self._signal_temperature.emit(data)
                return True
            else:
                data = {"message": "temperature sensor function test fail",
                        "macaddress": macaddress, "temperature": temperature, "reference": self.RefTemperature}
                self._signal_temperature.emit(data)
                return False
        except Exception as e:
            print(e)
            logging.debug(e)
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
                data = {"message": "error not temperature sensor"}
                self._signal_temperature.emit(data)
                return False

            macaddress = text['macaddress']
            ret = self.check_pre_station_done(macaddress)
            if ret is False:
                return
            temp = text['temperature']
            ret = self.function_temperature(temp, macaddress)
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
        data = {"message": "temperature sensor qa longtime testing starting"}
        self._signal_temperature.emit(data)
        self.QA_FUNCTION_TESTING = True
        while self.QA_FUNCTION_TESTING == True:
            ret = self.get_paired_temperature_sensor_info()
            try:
                timestamp = ret['timestamp']
                address64 = ret['address64']
                macaddress = address64.replace('0x', '').upper()
                deviceID = ret['deviceID']
                vendor = ret['vendor']
                model = ret['model']
                temperature = ret['temperature']
                data = {"message": "temperature sensor qa testing info", "timestamp": timestamp, "macaddress": macaddress,
                        "deviceID": deviceID, "vendor": vendor, "model": model, "temperature": temperature}
                print("---------temperature sensor QA:", data)
                self._signal_temperature.emit(data)
            except Exception:
                pass
            finally:
                sleep(1)

    def exit_qa_longtime_testing(self):
        if self.QA_FUNCTION_TESTING:
            self.QA_FUNCTION_TESTING = False
            data = {"message": "exit temperature sensor qa testing"}
            self._signal_temperature.emit(data)
        else:
            pass
