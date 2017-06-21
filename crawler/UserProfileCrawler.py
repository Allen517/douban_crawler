# -*- coding:utf-8 -*-

import sys

sys.path.append("../")

import urllib2,json
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
		self.db = MongodbDoubanRels()
		self.db_user = MongodbDoubanUsers()
		self.proxy = proxy
		self.retry_num = 0 
		self.max_retry = 2

	def __getDoubanUser(self, uid):
		url = "https://api.douban.com/v2/user/{uid}".format(user=uid)
		# url = "https://api.douban.com/shuo/v2/users/{user}/following?count=50&start={start}".format(user=uid, start=s)
		print "using proxy %s"%self.proxy
		print url
		content = getUrlContent(url, self.proxy)
		self.retry_num = 0 
		while not content:
			"""
			继续调用当前的proxy，3次后确认无效，释放该proxy			
			"""
			if self.retry_num>=self.max_retry:
				break
			content = self.getUrlContent(url, self.proxy)
			self.retry_num += 1
		if content:
			full_infos = json.loads(content)
			return full_infos

	def getDoubanUserProfile(self):
		global uncrawled_users, uu_index, len_uu
		while uu_index<len_uu:
			u_index = -1
			if mutex.acquire():
				if uru_index<len_uru:
					u_index = uu_index
					uu_index += 1
			if u_index>=0:
				uid = uncrawled_users[u_index][0]
				full_infos = self.__getDoubanUser(uid)
				print full_infos
				if self.retry_num<self.max_retry:
					self.db_user.updateUser(uid, 1, 0, full_infos)
			sleep(25) #休眠25秒后继续抓取
			if u_index<0 or self.retry_num>=self.max_retry:
				break
		print "Thread complete"

def userProfileCrawler(proxy):
	pm = ProxyManager()
	pm.useProxy(proxy)
	upc = UserProfileCrawler(proxy)
	upc.getDoubanUserProfile()
	if upc.retry_num<upc.max_retry:
		pm.releaseProxy(proxy)

def main(process_num=10):
	pm = ProxyManager()
	mdu = MongodbDoubanUsers()
	global uncrawled_users, uu_index, len_uu
	uncrawled_users = uncrawled_users[uru_index:]
	uncrawled_users.extend(mdu.getUsersUsage(0))
	len_uu = len(uncrawled_users)
	unused_proxies = pm.getAllUnusedProxies()
	#1. 取出当前可用的代理
	#2. 取出当前需要抓取用户关系的用户列表
	#3. 利用代理获取用户列表中用户的关注关系
	pl = []
	proc_num = 0
	for proxy,used in unused_proxies:
		print "get proxy %s"%proxy
		if used==0:
			proc_num += 1
			if proc_num>process_num:
				break
			proc = Thread(target=userProfileCrawler, args=(proxy,))
			pl.append(proc)

	for num in range(process_num):
		pl[num].start()

	for num in range(process_num):
		pl[num].join()


def run():
	main()
	sched = BlockingScheduler()
	sched.add_job(main, 'interval', minutes=30)
	sched.start()


# if __name__ == '__main__':
#     run()

if __name__=='__main__':
	upc = UserProfileCrawler("123.152.42.222:8118")
	full_infos = upc.getDoubanUserRels('tadamiracle')
	if not rels and urc.retry_num>=self.max_retry:
		#use another proxy
		urc = UserRelsCrawler("114.92.133.64:8118")
	print rels
	#print type(tuple(urc._getDoubanUserRelsOnePage('tadamiracle',0)))
	# for p in urc.getDoubanUserRels('tadamiracle'):
	# 	print p