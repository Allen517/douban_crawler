# -*- coding: utf-8 -*-

import urllib2,sys,json

sys.path.append("../")

from utils.GetConfig import GetConfig
from DB.MongodbProxy import MongodbProxy
from utils.utilFunction import verifyProxy

class ProxyManager(object):
	"""
	proxy manager
	"""
	def __init__(self):
		self.config = GetConfig()
		self.db = MongodbProxy()

	def getProxiesUsage(self, used):
		"""
		get unused proxy from mongodb
		"""
		return self.db.getHostsUsage(used)

	def useProxy(self, host):
		self.db.updateHost(host, 1)

	def releaseProxy(self, host):
		self.db.updateHost(host, 0)

	def getAllUnusedProxies(self):
		return self.db.getHostsUsage(0)

	def refresh(self):
		"""
		get proxy from ssdb
		"""
		ipPool = self.__getProxies()
		for host in ipPool:
			if verifyProxy(host):
				self.db.putHost(host, 0)

	def __getProxies(self):
		content = urllib2.urlopen(self.config.proxy_putter).read()
		return json.loads(content)

if __name__=="__main__":
	pm = ProxyManager()
	pm.refresh()
	proxies = pm.getProxiesUsage(0)
	print len(proxies)
	pm.useProxy(proxies[0][0])
	usedProxies = pm.getProxiesUsage(1)
	print usedProxies
	for p in usedProxies:
		pm.releaseProxy(p[0])
	print len(pm.getProxiesUsage(0))