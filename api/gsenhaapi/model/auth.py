# -*- coding: utf-8 -*-
import requests, json
import ldap
import os

class Auth:

	def __init__(self,server):
		self.s = server 
		self.who = os.environ.get('LDAP_USER')
		self.cred = os.environ.get('LDAP_PASSWORD')
		self.baseDN = os.environ.get('BASE_USER_DN')

	def authenticate(self,user,password):
		try:
			self.l = ldap.initialize(self.s)

			self.l.protocol_version=ldap.VERSION3

			self.l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

			if os.environ.get('CERT') != None and os.environ.get('CLIENT_CERT') != None and os.environ.get('CLIENT_KEY') != None:
				self.l.set_option(ldap.OPT_X_TLS_CACERTFILE, os.environ.get('CERT'))
				self.l.set_option(ldap.OPT_X_TLS_CERTFILE, os.environ.get('CLIENT_CERT'))
				self.l.set_option(ldap.OPT_X_TLS_KEYFILE, os.environ.get('CLIENT_KEY'))
	
			self.l.set_option(ldap.OPT_X_TLS_NEWCTX,0)
		except ldap.LDAPError:
			return -1
		try:
			cn = "cn=%s,"%user
			self.l.simple_bind_s(cn+str(self.baseDN),password)
		except ldap.INVALID_CREDENTIALS:
			return 0

		scope = ldap.SCOPE_SUBTREE
		search = '(cn=%s)' %user
		searchAttribute = ["uidNumber"]

		# We try recover user data using previous authenticated connection. If user don't have permissions, we fallback to gsenha's user
		try:
			result = self.l.search_s(self.baseDN,scope,search,searchAttribute)
		except ldap.NO_SUCH_OBJECT:
			self.l.simple_bind_s(self.who, self.cred)
			result = self.l.search_s(self.baseDN,scope,search,searchAttribute)

		self.l.unbind()
		return result[0][1]['uidNumber'][0]