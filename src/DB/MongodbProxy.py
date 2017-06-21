# -*- coding:utf-8 -*-

import sys

sys.path.append("../")

from utils.GetConfig import GetConfig
from DB.MongodbClient import MongodbClient
from utils.utilClass import Singleton

class MongodbProxy(MongodbClient):

	__metaclass__ = Singleton

	def __init__(self):
		self.config = GetConfig()
		MongodbClient.setDatabase(self, self.config.db_proxy_host\
			, self.config.db_proxy_port, self.config.db_proxy_name\
			, self.config.db_proxy_name)

	def putHost(self, host, used):
		MongodbClient.put(self, {"host": host}, {"host": host, "used": used})

	def updateHost(self, host, used):
		MongodbClient.update(self, {"host": host}, {"used": used})

	def getHost(self, host):
		return MongodbClient.get(self, {"host": host})

	def getAll(self):
		return [(p['host'], p['used']) for p in MongodbClient.getAll(self)]

	def getHostsUsage(self, used):
		usage = MongodbClient.getAll(self, {"used": used}) 
		if not usage:
			return None
		else:
			return [(p['host'], p['used']) for p in usage]

if __name__ =='__main__':
	mp = MongodbProxy()
	mp.putHost("localhost:1", 0)
	print mp.getHost("localhost:1")
	mp.updateHost("localhost:1", 1)
	print mp.getAll()
	print mp.getHostsUsage(1)
	mp.clean()
	print mp.getHost("localhost:1")
