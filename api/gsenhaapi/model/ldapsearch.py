# -*- coding: utf-8 -*-
import ldap, ldif, sys
import os

class LdapSearch:

	def __init__(self,server):
		self.s = server 
		self.who = os.environ.get('LDAP_USER')
		self.cred = os.environ.get('LDAP_PASSWORD')
		self.baseUserDN = os.environ.get('BASE_USER_DN')
		self.baseGroupDN = os.environ.get('BASE_GROUP_DN')

	def healthcheck(self):
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
			return 0
		try:
			self.l.simple_bind_s(self.who,self.cred)
		except ldap.LDAPError:
			return 0

		self.l.unbind()
		return 1

	def get_groups(self,user):
		
		try:
			
			self.l = ldap.initialize(self.s)

			self.l.protocol_version=ldap.VERSION3			

			self.l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
	
			if os.environ.get('CERT') != None and os.environ.get('CLIENT_CERT') != None and os.environ.get('CLIENT_KEY') != None:
				self.l.set_option(ldap.OPT_X_TLS_CACERTFILE, os.environ.get('CERT'))
				self.l.set_option(ldap.OPT_X_TLS_CERTFILE, os.environ.get('CLIENT_CERT'))
				self.l.set_option(ldap.OPT_X_TLS_KEYFILE, os.environ.get('CLIENT_KEY'))
	
			self.l.set_option(ldap.OPT_X_TLS_NEWCTX,0)	
		except ldap.LDAPError,e:
			return "Erro ao iniciar conexao com o LDAP",0

		try:
			self.l.simple_bind_s(self.who,self.cred)
		except ldap.LDAPError,e:
			return "Erro ao se conectar com o LDAP" , 0

		base_dn = str(self.baseGroupDN)
		scope = ldap.SCOPE_SUBTREE
		search = '(memberUid=%s)' %user

		result = self.l.search_s(base_dn,scope,search)

		groups = []

		for i in range(len(result)):
			tmp = result[i][1]['cn'][0]
			if tmp != user:
				groups.append(tmp)
		
		self.l.unbind()

		return groups , 1

	def info_search(self,user):
		try:
			
			self.l = ldap.initialize(self.s)

			self.l.protocol_version=ldap.VERSION3			

			self.l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
	
			if os.environ.get('CERT') != None and os.environ.get('CLIENT_CERT') != None and os.environ.get('CLIENT_KEY') != None:
				self.l.set_option(ldap.OPT_X_TLS_CACERTFILE, os.environ.get('CERT'))
				self.l.set_option(ldap.OPT_X_TLS_CERTFILE, os.environ.get('CLIENT_CERT'))
				self.l.set_option(ldap.OPT_X_TLS_KEYFILE, os.environ.get('CLIENT_KEY'))
	
			self.l.set_option(ldap.OPT_X_TLS_NEWCTX,0)	
		except ldap.LDAPError,e:
			return "Erro ao iniciar conexao com o LDAP",0

		try:
			self.l.simple_bind_s(self.who,self.cred)
		except ldap.LDAPError,e:
			return "Erro ao se conectar com o LDAP" , 0

		base_dn = str(self.baseUserDN)
		scope = ldap.SCOPE_SUBTREE
		search = '(cn=%s)' %user
		searchAttribute = ["mail","sn","givenname"]

		result = self.l.search_s(base_dn,scope,search,searchAttribute)
		
		self.l.unbind()

		return {"mail":result[0][1]['mail'][0],"name":result[0][1]['givenName'][0] + " " + result[0][1]['sn'][0]} , 1