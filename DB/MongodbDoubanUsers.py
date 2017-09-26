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

	def updateUserProfileCrawlTag(self, uid, has_crawled, vals=dict()):
		vals['has_crawled'] = has_crawled
		MongodbClient.update(self, {"uid": uid}, vals)

	def updateUserRelsCrawlTag(self, uid, has_got_rels):
		MongodbClient.update(self, {"uid": uid}, {'has_got_rels':has_got_rels})

	def updateUser(self, uid, has_crawled, has_got_rels, vals=dict()):
		vals['has_crawled'] = has_crawled
		vals['has_got_rels'] = has_got_rels
		MongodbClient.update(self, {"uid": uid}, vals)

	def getUser(self, uid):
		return MongodbClient.get(self, {"uid": uid})

	def getAll(self, limit=None, skip=None):
		return [(p['uid'], p['has_crawled'], p['has_got_rels']) for p in MongodbClient.getAll(self, limit, skip)]

	def __removeNoUidRecords(self, vals):
		cnt = 0
		records = MongodbClient.getAll(self, vals)
		for r in records:
			if 'uid' not in r:
				obj_id = r['_id']
				MongodbClient.delete(self, {'_id':obj_id})
				cnt += 1
		print "remove %d no uid records"%cnt

	def getUsersUsage(self, has_crawled, limit=None, skip=None):
		# self.__removeNoUidRecords({'has_crawled':has_crawled})
		usage = MongodbClient.getAll(self, {"has_crawled": has_crawled}, limit, skip) 
		if not usage:
			return None
		else:
			return [(p['uid'], p['has_crawled']) for p in usage]

	def getUsersRelCrawled(self, has_got_rels, limit=None, skip=None):
		# self.__removeNoUidRecords({'has_got_rels':has_got_rels})
		hasRels = MongodbClient.getAll(self, {"has_got_rels": has_got_rels}, limit, skip) 
		if not hasRels:
			return None
		else:
			return [(p['uid'], p['has_got_rels']) for p in hasRels]

if __name__ =='__main__':
	mp = MongodbDoubanUsers()
	# vals = {u'loc_id': u'118281', u'uid': u'158563799', u'alt': u'https://www.douban.com/people/158563799/', u'created': u'2017-03-03 15:27:33', u'is_banned': False, u'desc': u'\u5de8\u87f9\u5973', u'is_suicide': False, u'has_crawled': 0, u'large_avatar': u'https://img3.doubanio.com/icon/up158563799-3.jpg', u'avatar': u'https://img3.doubanio.com/icon/u158563799-3.jpg', u'signature': u'', u'loc_name': u'\u5e7f\u4e1c\u5e7f\u5dde', u'has_got_rels': 1, u'type': u'user', u'id': u'158563799', u'name': u'Annie'}
	# mp.updateUser('158563799', 1, 0, vals)
	# print mp.getUser("158563799")

	mp.updateUser('tadamiracle', 0, 1)
	print mp.getUser('tadamiracle')

	# mp.clean()
	# mp.putUser('{"name":"tada","created":"2009-01-18 19:02:59","is_banned":false,"is_suicide":false,\
	# 	"avatar":"https://img1.doubanio.com\/icon\/u3513921-8.jpg","signature":"没有翅膀，但俯视阳光",\
	# 	"uid":"tadamiracle","alt":"https:\/\/www.douban.com\/people\/tadamiracle\/"}')
	# print mp.getUser("tadamiracle")
	# mp.updateUser("1231321",1)
	# print mp.getAll()
	# print mp.getUsersUsage(1)
	# mp.clean()
	# print mp.getUser("1231321")