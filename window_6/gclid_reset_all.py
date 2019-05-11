# -*- coding: utf-8 -*-
import os
import json
import configparser
import logging

from window6.net import network

class gclid_reset_all():
    def __init__(self):
        print("gclid reset all init")
        self.init_data()

    def init_data(self):
        self.corelight = network()
        self.parser_config()

    def parser_config(self):
        config = 'config.ini'
        config_path = os.path.join(os.getcwd(), config)
        if os.path.exists(config_path):
            conf = configparser.ConfigParser()
            conf.read(config)
            self.pokey = conf.get('PoInfo', 'pokey')
            self.countrycode = conf.get('PoInfo', 'countrycode')
            self.hwversion = conf.get('PoInfo', 'hwversion')
        else:
            pass

    def reset_all(self, cmd):
        if self.pokey in cmd:
            gclid = cmd
            ret = self.reset_by_gclid(gclid)
        else:
            mac = cmd
            ret = self.reset_by_mac(mac)
        return ret

    def reset_by_gclid(self, gclid):
        log = "reset gclid all by gclid:"+gclid
        print(log)
        logging.debug(log)

        ret = self.corelight.gcl_reset_all_by_gclid(gclid)
        if ret is None:
            return "corelight return data error"
        try:
            text = json.loads(ret)
            result = text['result']
            msg = text['messages'][0]['message']
            if result == "ok":
                reset_gcl_id = text['messages'][0]['reset_gcl_id']
                reset_gcl_count = text['messages'][0]['reset_gcl_count']
                data = {"reset_gcl_id": str(reset_gcl_id), "reset_gcl_count": str(reset_gcl_count)}
                return data
            elif result == "fail":
                if msg == "no sensor in current gclid":
                    return msg
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(e)
            logging.debug(e)
            return False

    def reset_by_mac(self, macaddress):
        mac = macaddress
        log = "reset gclid all by mac:"+mac
        print(log)
        logging.debug(log)

        ret = self.corelight.gcl_reset_all_by_mac(mac)
        if ret is None:
            return "corelight return data error"
        try:
            text = json.loads(ret)
            result = text['result']
            msg_type = text['messages'][0]['type']
            msg = text['messages'][0]['message']
            if result == "ok":
                reset_gcl_id = text['messages'][0]['reset_gcl_id']
                reset_gcl_count = text['messages'][0]['reset_gcl_count']
                data = {"reset_gcl_id": str(reset_gcl_id), "reset_gcl_count": str(reset_gcl_count)}
                return data
            elif result == "fail":
                if msg == "find mac fail":
                    return msg
                elif msg == "sensor not in gcl":
                    return msg
                elif msg == "gcl reset all fail":
                    return msg
                else:
                    return False
        except Exception as e:
            print(e)
            logging.debug(e)
            return False
