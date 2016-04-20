# -*- coding: utf-8 -*-

from gsenhaapi.model.ldapsearch import LdapSearch
from gsenhaapi.exceptions import InvalidUsage

class LdapController(object):

	def __init__(self, ldap):
		self.ldap = ldap

	def healthcheck(self):
		response = self.ldap.healthcheck()
		if not response:
			raise InvalidUsage("Failed to connect to ldap",500)

	def get_groups(self,user):
		response , err = self.ldap.get_groups(user)
		if not err:
			raise InvalidUsage("Failed to get groups from ldap",500)
		return response

	def search_info(self,user):
		response , err = self.ldap.info_search(user)
		if not err:
			raise InvalidUsage("Failed to get email from user",500)
		return response
		