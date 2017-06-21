# -*- coding:utf-8 -*-

import sys

sys.path.append("../")

import json,re
from utils.GetConfig import GetConfig
from DB.MongodbClient import MongodbClient
from utils.utilClass import Singleton
from utils.utilFunction import jsonStrFormat

class MongodbDoubanUsers(MongodbClient):

	__metaclass__ = Singleton

	def __init__(self):
		self.config = GetConfig()
		MongodbClient.setDatabase(self, self.config.db_douban_host\
			, self.config.db_douban_port, self.config.db_douban_name\
			, self.config.db_douban_tab_user)

	def putUser(self, json_str):
		json_str = jsonStrFormat(json_str)
		vals = json.loads(json_str)
		if 'uid' in vals:
			uid = vals['uid']
			vals['has_crawled'] = 0
			vals['has_got_rels'] = 0
			MongodbClient.put(self, {"uid": uid}, vals)

	def updateUser(self, uid, has_crawled, has_got_rels, vals=dict()):
		vals['has_crawled'] = has_crawled
		vals['has_got_rels'] = has_got_rels
		MongodbClient.update(self, {"uid": uid}, vals)

	def getUser(self, uid):
		return MongodbClient.get(self, {"uid": uid})

	def getAll(self):
		return [(p['uid'], p['has_crawled'], p['has_got_rels']) for p in MongodbClient.getAll(self)]

	def getUsersUsage(self, has_crawled):
		usage = MongodbClient.getAll(self, {"has_crawled": has_crawled}) 
		if not usage:
			return None
		else:
			return [(p['uid'], p['has_crawled']) for p in usage]

	def getUsersRelCrawled(self, has_got_rels):
		hasRels = MongodbClient.getAll(self, {"has_got_rels": has_got_rels}) 
		if not hasRels:
			return None
		else:
			return [(p['uid'], p['has_got_rels']) for p in hasRels]

if __name__ =='__main__':
	mp = MongodbDoubanUsers()
	mp.clean()
	mp.putUser('{"name":"tada","created":"2009-01-18 19:02:59","is_banned":false,"is_suicide":false,\
		"avatar":"https://img1.doubanio.com\/icon\/u3513921-8.jpg","signature":"没有翅膀，但俯视阳光",\
		"uid":"tadamiracle","alt":"https:\/\/www.douban.com\/people\/tadamiracle\/"}')
	print mp.getUser("tadamiracle")
	# mp.updateUser("1231321",1)
	# print mp.getAll()
	# print mp.getUsersUsage(1)
	# mp.clean()
	# print mp.getUser("1231321")