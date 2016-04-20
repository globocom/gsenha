# -*- coding: utf-8 -*-
from gsenhaapi.model.auth import Auth
from gsenhaapi.exceptions import InvalidUsage

class AuthController(object):
	
	def __init__(self,m_auth):
		self.m_auth = m_auth

	def auth(self,user,passwd):
		response = self.m_auth.authenticate(user,passwd)
		if response == -1:
			message = "Failed to connect to ldap"
			raise InvalidUsage(message,500)
		if response == 0:
			message = "Failed to authenticate user %s"%user
			raise InvalidUsage(message,401)
		return int(response)