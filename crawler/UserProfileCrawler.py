# -*- coding:utf-8 -*-

import sys

sys.path.append("../")

import urllib2,json
import logging,time
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from threading import Lock
from time import sleep

from utils.GetConfig import GetConfig
from utils.GlobalVar import *
from DB.MongodbDoubanRels import MongodbDoubanRels
from DB.MongodbDoubanUsers import MongodbDoubanUsers
from manager.ProxyManager import ProxyManager
from utils.utilFunction import getUrlContent

from utils.LogHandler import LogHandler

logging.basicConfig()

mutex = Lock()

class UserProfileCrawler(object):

	def __init__(self, proxy):
		self.db_user = MongodbDoubanUsers()
		self.proxy = proxy
		self.retry_num = 0 
		self.max_retry = 2
		self.log = LogHandler('crawl_user_profile')
		# self.log.info(u"当前使用代理%s"%proxy)
		self.fail_count = 0
		self.max_fail_count = 3
		self.sleep_time = 3

	def __getDoubanUser(self, uid):
		url = "https://api.douban.com/v2/user/{}?apikey=09ec337ecc4d17531dc49a7c64e745f9".format(uid)
		# url = "http://api.douban.com/shuo/v2/users/{user}/following?count=50&start={start}".format(user=uid, start=s)
		content = getUrlContent(url, self.proxy)
		sleep(self.sleep_time)
		self.retry_num = 0 
		while not content:
			"""
			继续调用当前的proxy，3次后确认无效，释放该proxy			
			"""
			if self.retry_num>=self.max_retry:
				self.log.info(u"当前代理%s连接超时！"%self.proxy)
				break
			content = getUrlContent(url, self.proxy)
			sleep(self.sleep_time)
			self.retry_num += 1
		if content:
			full_infos = json.loads(content)
			if 'uid' in full_infos:
				self.fail_count = 0
				return full_infos
			else:
				self.log.info(u"当前用户%s信息抓取失败！"%uid)
				self.fail_count += 1
				return None

	def getDoubanUserProfile(self):
		global uncrawled_users, uu_index, len_uu
		while uu_index<len_uu:
			u_index = -1
			if mutex.acquire():
				if uu_index<len_uu:
					u_index = uu_index
					uu_index += 1
				mutex.release()
			if u_index>=0:
				uid = uncrawled_users[u_index][0]
				self.log.info(u'%s 开始抓取用户%s的用户信息' % (time.ctime(), uid))
				full_infos = self.__getDoubanUser(uid)
				if self.retry_num<self.max_retry and full_infos:
					self.db_user.updateUserProfileCrawlTag(uid, 1, full_infos)
					self.log.info(u"已将用户%s的用户信息加入用户表"%uid)
				if self.retry_num<self.max_retry and not full_infos:
					self.db_user.updateUserProfileCrawlTag(uid, 1)
					self.log.info(u"用户%s的用户信息无法抓取"%uid)
			if u_index<0 or self.retry_num>=self.max_retry or self.fail_count>=self.max_fail_count:
				break
		self.log.info(u"当前的用户信息抓取线程任务已完成")

def userProfileCrawler(proxy):
	# pm = ProxyManager()
	# pm.useProxy(proxy)
	upc = UserProfileCrawler(proxy)
	upc.getDoubanUserProfile()
	if upc.retry_num<upc.max_retry and upc.fail_count<upc.max_fail_count:
		# pm.releaseProxy(proxy)
		upc.log.info(u"释放当前的代理%s"%proxy)
	else:
		upc.log.info(u"当前的代理%s失效"%proxy)

def main(process_num=1):
	# pm = ProxyManager()
	mdu = MongodbDoubanUsers()
	global uncrawled_users, uu_index, len_uu
	uncrawled_users = uncrawled_users[uu_index:]
	uncrawled_users.extend(mdu.getUsersUsage(0))
	len_uu = len(uncrawled_users)
	uu_index = 0
	# unused_proxies = pm.getAllUnusedProxies()
	#1. 取出当前可用的代理
	#2. 取出当前需要抓取用户关系的用户列表
	#3. 利用代理获取用户列表中用户的关注关系
	pl = []
	for proc_num in range(process_num):
		proc = Thread(target=userProfileCrawler, args=("",))
		pl.append(proc)

	# proc_num = 0
	# for proxy,used in unused_proxies:
	# 	if used==0:
	# 		proc_num += 1
	# 		if proc_num>process_num:
	# 			break
	# 		proc = Thread(target=userProfileCrawler, args=(proxy,))
	# 		pl.append(proc)

	for num in range(process_num):
		pl[num].start()

	for num in range(process_num):
		pl[num].join()


def run():
	sched = BlockingScheduler()
	sched.add_job(main, 'interval', minutes=2)
	sched.start()


if __name__ == '__main__':
    run()

# if __name__=='__main__':
# 	upc = UserProfileCrawler("123.152.42.222:8118")
# 	full_infos = upc.getDoubanUserProfile('tadamiracle')
# 	if not rels and urc.retry_num>=self.max_retry:
# 		#use another proxy
# 		upc = UserProfileCrawler("114.92.133.64:8118")
# 	print rels
	#print type(tuple(urc._getDoubanUserRelsOnePage('tadamiracle',0)))
	# for p in urc.getDoubanUserRels('tadamiracle'):
	# 	print p