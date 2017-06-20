# -*- coding:utf-8 -*-

import sys

sys.path.append("../")

from utils.GetConfig import GetConfig
from DB.MongodbDoubanUsers import MongodbDoubanUsers

class DoubanUserManager(MongodbDoubanUsers):
	"""
	Douban user manager
	"""
	def __init__(self):
		self.config = GetConfig()
		self.db = MongodbDoubanUsers()
		

