# -*- coding: utf-8 -*-

class User(object):

	def __init__(self,username,userid):
		self.username = username
		self.userdb = None
		self.uid = userid
		
	def set_userdb(self,userdb):
		self.userdb = userdb