# -*- coding: utf-8 -*-
import os
import json
import configparser
import logging

from window6.net import network

class gclid_reset_part():
    def __init__(self):
        print("gclid reset part init")
        self.init_data()

    def init_data(self):
        self.GCLID_RESET_PARTIAL_MAC_LIST = []
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
            self.max_weight = conf.get('Weighter', 'max')
            self.min_weight = conf.get('Weighter', 'min')
        else:
            pass

    def set_gcl_reset_part_list(self, macaddress):
        mac = macaddress
        if mac in self.GCLID_RESET_PARTIAL_MAC_LIST:
            return "already in list"
        else:
            ret = self.corelight.check_mac_already_in_gcl(mac)
            try:
                text = json.loads(ret)
                result = text['result']
                msg = text['messages'][0]['message']
                if result == "ok":
                    self.GCLID_RESET_PARTIAL_MAC_LIST.append(mac)
                    return True
                elif result == "fail":
                    if msg == "not exist":
                        return msg
                    elif msg == "not in gcl":
                        return msg
                    else:
                        pass
                else:
                    pass
            except Exception as e:
                pass

    def get_gcl_reset_part_list(self):
        if self.GCLID_RESET_PARTIAL_MAC_LIST:
            return self.GCLID_RESET_PARTIAL_MAC_LIST

    def clear_gcl_reset_part_list(self):
        if self.GCLID_RESET_PARTIAL_MAC_LIST:
            self.GCLID_RESET_PARTIAL_MAC_LIST.clear()

    def do_gclid_reset_part(self):
        maclist = self.get_gcl_reset_part_list()
        print("do the gclid reset part list:", maclist)
        ret = self.corelight.gclid_reset_part(maclist)
        try:
            text = json.loads(ret)
            result = text['result']
            if result == "ok":
                gclid = text['messages'][0]['gclid']
                reset_count = text['messages'][0]['reset_count']
                gcl_count = text['messages'][0]['gcl_count']
                data ={"gclid": gclid, "reset_count": reset_count, "gcl_count": gcl_count}
                return data
            elif result == "fail":
                return False
        except Exception:
            return False
        finally:
            print("finally---clear up---")
            self.clear_gcl_reset_part_list()
