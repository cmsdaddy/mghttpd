# -*- coding: UTF-8 -*-
__author__ = 'lijie'


class Scada:
    def __init__(self):
        self.pcs_list = list()
        self.bms_list = list()
        self.air_list = list()

        self.ws_list = list()

        self.status = '初始化'

        self.errors_list = list()
        self.warning_list = list()

        self.net_offline = True
        self.usb_offline = True

    def ws_push(self, ws):
        pass

    def ws_pop(self, ws):
        pass

    def push_to_all(self):
        pass

    def push_to_user(self):
        pass

    def push_to_page(self):
        pass


class Device(object):
    pass


class YaoTiao(object):
    pass


class YaoKong(object):
    pass


class YaoCe(object):
    pass


class YaoXin(object):
    pass
