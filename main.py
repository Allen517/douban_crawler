# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main.py  
   Description :  运行主函数
   Author :       JHao
   date：          2017/4/1
-------------------------------------------------
   Change Activity:
                   2017/4/1: 
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from multiprocessing import Process

from schedule.ProxyRefreshSchedule import run as RefreshRun
from crawler.UserProfileCrawler import run as ProfileCrawlerRun
from crawler.UserRelsCrawler import run as RelsCrawlerRun

def run():
    p_list = list()
    # p1 = Process(target=RefreshRun, name='RefreshRun')
    # p_list.append(p1)
    p2 = Process(target=RelsCrawlerRun, name='RelsCrawlerRun')
    p_list.append(p2)
    p3 = Process(target=ProfileCrawlerRun, name='ProfileCrawlerRun')
    p_list.append(p3)
    for p in p_list:
        p.start()
    for p in p_list:
        p.join()

if __name__ == '__main__':
    run()