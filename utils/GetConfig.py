# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetConfig.py  
   Description :  fetch config from config.ini
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3: get db property func
-------------------------------------------------
"""
__author__ = 'JHao'

import sys

sys.path.append("../")

import os
from utils.utilClass import ConfigParse
from utils.utilClass import LazyProperty

class GetConfig(object):
    """
    to get config from config.ini
    """

    def __init__(self):
        self.pwd = os.path.split(os.path.realpath(__file__))[0]
        self.config_path = os.path.join(os.path.split(self.pwd)[0], 'config.ini')
        self.config_file = ConfigParse()
        self.config_file.read(self.config_path)

    @LazyProperty
    def proxy_putter(self):
        return "http://{}/get_all/".format(self.config_file.get('Proxy','remote_db'))

    @LazyProperty
    def db_proxy_host(self):
        return self.config_file.get('Proxy', 'host')

    @LazyProperty
    def db_proxy_port(self):
        return int(self.config_file.get('Proxy', 'port'))

    @LazyProperty
    def db_proxy_name(self):
        return self.config_file.get('Proxy', 'name')

    @LazyProperty
    def db_douban_host(self):
        return self.config_file.get('DB', 'host')

    @LazyProperty
    def db_douban_port(self):
        return int(self.config_file.get('DB', 'port'))

    @LazyProperty
    def db_douban_name(self):
        return self.config_file.get('DB', 'name')

    @LazyProperty
    def db_douban_tab_user(self):
        return self.config_file.get('DB', 'user_tab')

    @LazyProperty
    def db_douban_tab_rel(self):
        return self.config_file.get('DB', 'rel_tab')


if __name__ == '__main__':
    gg = GetConfig()
    print gg.proxy_putter
