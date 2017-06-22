# -*- coding:utf-8 -*-

import sys

sys.path.append("../")

import urllib2,json
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from threading import Lock
import time
from time import sleep

import inspect
import ctypes

from utils.GetConfig import GetConfig
# from utils.GlobalVar import GlobalVar
from utils.GlobalVar import *
from DB.MongodbDoubanRels import MongodbDoubanRels
from DB.MongodbDoubanUsers import MongodbDoubanUsers
from manager.ProxyManager import ProxyManager
from utils.utilFunction import getUrlContent
from utils.LogHandler import LogHandler

logging.basicConfig()

mutex = Lock()

class UserRelsCrawler(object):

	def __init__(self, proxy):
		self.db = MongodbDoubanRels()
		self.db_user = MongodbDoubanUsers()
		self.proxy = proxy
		self.retry_num = 0 
		self.max_retry = 1
		self.fail_count = 0
		self.max_fail_count = 3
		self.log = LogHandler('crawl_user_rels')
		self.log.info(u"当前使用代理%s"%proxy)

	def __getDoubanUserRelsOnePage(self, uid, s):
		#url = "https://api.douban.com/v2/user/{}"
		url = "https://api.douban.com/shuo/v2/users/{user}/following?count=50&start={start}".format(user=uid, start=s)
		content = getUrlContent(url, self.proxy)
		self.retry_num = 0 
		while not content:
			"""
			继续调用当前的proxy，3次后确认无效，释放该proxy		
			"""
			if self.retry_num>=self.max_retry:
				self.log.info(u"当前代理%s连接超时！"%self.proxy)
				break
			content = getUrlContent(url, self.proxy)
			self.retry_num += 1
		if content:
			rel_full_infos = json.loads(content)
			for p in rel_full_infos:
				if 'uid' in p:
					yield p['uid']

	def __getDoubanUserRels(self, uid):
		s = 0
		rels = tuple(self.__getDoubanUserRelsOnePage(uid, s))
		sleep(24) #休眠25秒后继续抓取
		if not rels:
			self.fail_count += 1
			self.log.info(u"当前用户%s关注关系抓取失败！"%uid)
			return None
		self.fail_count = 0
		while True:
			s += 50
			cur_rels = tuple(self.__getDoubanUserRelsOnePage(uid, s))
			if not cur_rels:
				break
			rels += cur_rels
			sleep(24) #休眠25秒后继续抓取
		self.log.info(u"已完成用户%s的关注关系抓取"%uid)
		return rels

	def getDoubanUserRels(self):
		global uncrawled_rels_users, uru_index, len_uru
		while uru_index<len_uru:
			u_index = -1
			if mutex.acquire():
				if uru_index<len_uru:
					u_index = uru_index
					uru_index += 1
				mutex.release()
			if u_index>=0:
				uid = uncrawled_rels_users[u_index][0]
				self.log.info(u'%s 开始抓取用户%s的关注关系' % (time.ctime(), uid))
				rels = self.__getDoubanUserRels(uid) #cost much time here
				if rels and self.retry_num<self.max_retry:
					self.db.putUserRels(uid, rels, 0)
					self.db_user.updateUserRelsCrawlTag(uid, 1)
					self.log.info(u"已将用户%s的关注用户加入关系表"%uid)
					for uid_in_rel in rels:
						self.db_user.putUser('{{"uid":"{id}", "has_crawled":{crawled}, "has_got_rels":{got_rels}}}'\
											.format(id=uid_in_rel, crawled=0, got_rels=0))
					self.log.info(u"已将用户%s的关注用户加入用户表"%uid)
			if u_index<0 or self.retry_num>=self.max_retry or self.fail_count>=self.max_fail_count:
				break
		self.log.info(u"当前的用户关注关系抓取线程任务已完成")

def userRelsCrawler(proxy):
	pm = ProxyManager()
	pm.useProxy(proxy)
	urc = UserRelsCrawler(proxy)
	urc.getDoubanUserRels()
	if urc.retry_num<urc.max_retry and urc.fail_count<urc.max_fail_count:
		pm.releaseProxy(proxy)
		urc.log.info(u"释放当前的代理%s"%proxy)
	else:
		urc.log.info(u"当前的代理%s失效"%proxy)

def main(process_num=5):
	pm = ProxyManager()
	mdu = MongodbDoubanUsers()
	global uncrawled_rels_users, uru_index, len_uru
	uncrawled_rels_users = uncrawled_rels_users[uru_index:]
	uncrawled_rels_users.extend(mdu.getUsersRelCrawled(0))
	len_uru = len(uncrawled_rels_users)
	unused_proxies = pm.getAllUnusedProxies()
	#1. 取出当前可用的代理
	#2. 取出当前需要抓取用户关系的用户列表
	#3. 利用代理获取用户列表中用户的关注关系
	pl = []
	proc_num = 0
	for proxy,used in unused_proxies:
		if used==0:
			proc_num += 1
			if proc_num>process_num:
				break
			proc = Thread(target=userRelsCrawler, args=(proxy,))
			pl.append(proc)

	for num in range(process_num):
		pl[num].start()

	for num in range(process_num):
		pl[num].join()

def run():
	sched = BlockingScheduler()
	sched.add_job(main, 'interval', minutes=1)
	sched.start()


if __name__ == '__main__':
    run()

# if __name__=='__main__':
# 	urc = UserRelsCrawler("123.152.42.222:8118")
# 	rels = urc.getDoubanUserRels('tadamiracle')
# 	if not rels and urc.retry_num>=self.max_retry:
# 		#use another proxy
# 		urc = UserRelsCrawler("114.92.133.64:8118")
# 	print rels
# 	#print type(tuple(urc._getDoubanUserRelsOnePage('tadamiracle',0)))
# 	# for p in urc.getDoubanUserRels('tadamiracle'):
# 	# 	print p