# -*- coding: utf-8 -*-
from gsenhaapi.model.user import User
from gsenhaapi.controller.databaseController import DatabaseController
from gsenhaapi.exceptions import InvalidUsage
from gsenhaapi.exceptions import DatabaseError

class UserController(object):

	def __init__(self,database):
		self.db = database
		self.user = None

	def set_user(self,user):
		self.user = user

	def check_group(self,ldapgroups,dbgroups):

		groups_db_name= []
		for idGrupo in dbgroups:
			try:
				name = self.db.get_groups_name(idGrupo[0])
				groups_db_name.append(name[0][0])
			except DatabaseError,e:
				raise InvalidUsage(e.message,500)

		groups_ldap = set(ldapgroups)
		groups_db = set(groups_db_name)

		if groups_db != groups_ldap:
			if len(groups_ldap) > len(groups_db):
				groups_to_add = list(groups_ldap - groups_db)
				if groups_to_add == groups_db_name:
					for group in groups_db_name:
						try:
							self.db.exclude_user_group(group,self.user.username)
						except DatabaseError,e:
							raise InvalidUsage(e.message,500)

					for group in ldapgroups:
						try:
							groupdb = self.db.add_group(group)
						except DatabaseError,e:
							raise InvalidUsage(e.message,500)
						try:
							self.db.add_user_group(self.user.userdb,groupdb)
						except DatabaseError,e:
							raise InvalidUsage(e.message,500)
				else:
					for group in groups_to_add:
						try:
							groupdb = self.db.add_group(group)
						except DatabaseError,e:
							raise InvalidUsage(e.message,500)
						try:
							self.db.add_user_group(self.user.userdb,groupdb)
						except DatabaseError,e:
							raise InvalidUsage(e.message,500)
			else:
				groups_to_remove = list(groups_db - groups_ldap)
				for group in groups_to_remove:
					try:
						self.db.exclude_user_group(group,self.user.username)
					except DatabaseError,e:
						raise InvalidUsage(e.message,500)

				groups_to_add = list(groups_ldap - groups_db)

				for group in groups_to_add:
					try:
						groupdb = self.db.add_group(group)
					except DatabaseError,e:
						raise InvalidUsage(e.message,500)
					try:
						self.db.add_user_group(self.user.userdb,groupdb)
					except DatabaseError,e:
						raise InvalidUsage(e.message,500)					

