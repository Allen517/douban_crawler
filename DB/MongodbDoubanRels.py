import sys

sys.path.append("../")

from utils.GetConfig import GetConfig
from DB.MongodbClient import MongodbClient
from utils.utilClass import Singleton

class MongodbDoubanRels(MongodbClient):

	__metaclass__ = Singleton

	def __init__(self):
		self.config = GetConfig()
		MongodbClient.setDatabase(self, self.config.db_douban_host\
			, self.config.db_douban_port, self.config.db_douban_name\
			, self.config.db_douban_tab_rel)

	def putUserRels(self, uid, rels, used):
		MongodbClient.put(self, {"uid": uid}, {"uid": uid, "rels": rels, "used": used})

	def updateUserRels(self, uid, rels):
		MongodbClient.update(self, {"uid": uid}, {"rels": rels, "used": used})

	def getUserRels(self, uid):
		return MongodbClient.get(self, {"uid": uid})

	def getAll(self):
		return [(p['uid'], p['rels'], p['used']) for p in MongodbClient.getAll(self)]

if __name__ =='__main__':
	mp = MongodbDoubanRels()
	mp.putUserRels("1231321", "{1,2,3}")
	print mp.getUserRels("1231321")
	mp.updateUserRels("1231321","{2,3,4}")
	print mp.getAll()
	mp.clean()
	print mp.getUserRels("1231321")