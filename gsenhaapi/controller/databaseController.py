# -*- coding: utf-8 -*-
from gsenhaapi.model.database import DataBase
from gsenhaapi.exceptions import DatabaseError
from gsenhaapi.exceptions import InvalidUsage
from gsenhaapi.model.log import Log

class DatabaseController:
	
	def __init__(self,database):
		self.db = database
		self.log = Log()

	def healthcheck(self):
		response = self.db.healthcheck()
		if not response:
			raise DatabaseError("Connection failed",500)

	def search_user(self,username):
		response , err = self.db.search_user_db(username)
		if not err:
			log_message = """action=|database search| method=|search user| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to search user",500)
		if response == None:
			raise InvalidUsage("user does not exist, please add at /add/user",401)
		return list(response)

	def get_user_group(self,userdb):
		response , err = self.db.get_groups_from_user_db(userdb)
		if not err:
			log_message = """action=|database search| method=|get_user_group| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get groups from user",500)
		return list(response)

	def get_groups_name(self,idGrupo):
		response , err = self.db.get_groups_by_id_db(idGrupo)
		if not err:
			log_message = """action=|database search| method=|get_groups_name| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get groups name",500)			
		return list(response)
		
	def exclude_user_group(self,idGrupo,username):
		response , err = self.db.exclude_user_group_db(idGrupo,username)
		if not response:
			log_message = """action=|database search| method=|exclude_user_group| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError(response,500)

	def search_group(self,group):
		response , err = self.db.search_group_db(group)
		if not err:
			log_message = """action=|database search| method=|search_group| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError(response,500)
		if response == None:
			return []
		return list(response)

	def add_group(self,NomeGrupo):
		groupdb , err = self.db.search_group_db(NomeGrupo)
		if not err:
			log_message = """action=|database search| method=|add_group| desc=|%s| result=|error|"""%groupdb
			self.log.log_error(log_message)
			raise DatabaseError("Failed to search group",500)

		if groupdb == None:
	
			response , err = self.db.add_group_db(NomeGrupo)
			if not err:
				log_message = """action=|database search| method=|add_group| desc=|%s| result=|error|"""%response
				self.log.log_error(log_message)
				raise DatabaseError("Failed to add group",500)

			groupdb , err = self.db.search_group_db(NomeGrupo)
			if not err:
				log_message = """action=|database search| method=|add_group| desc=|%s| result=|error|"""%groupdb
				self.log.log_error(log_message)
				raise DatabaseError("Failed to search group",500)
	
			folderName = "/Shared/"+NomeGrupo
	
			response , err = self.db.add_groupfolder_db(folderName,"/Shared",groupdb)
			if not err:
				log_message = """action=|database search| method=|add_group| desc=|%s| result=|error|"""%response
				self.log.log_error(log_message)	
				raise DatabaseError("Failed to add group folder",500)
	
			externalFolderName = "/Shared/"+NomeGrupo+"/External"
			external_path = "/Shared/"+NomeGrupo
	
			response , err = self.db.add_groupfolder_db(externalFolderName,external_path,groupdb)
			if not err:
				log_message = """action=|database search| method=|add_group_db| desc=|%s| result=|error|"""%response
				self.log.log_error(log_message)				
				raise DatabaseError("Failed to add group folder",500)

		return list(groupdb)

	def add_user_group(self,userdb,groupdb):
		response , err = self.db.add_user_group_db(userdb,groupdb)
		if not err:
			log_message = """action=|database search| method=|add_user_group| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add user group",500)

	def get_user_folder(self,userdb):
		response , err = self.db.get_userfolder(userdb)
		if not err:
			log_message = """action=|database search| method=|get_user_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get user folder",500)
		return list(response)

	def get_personal_passwords_by_folder(self,idFolder,username):
		response , err = self.db.get_personal_passwords_byfolder_db(idFolder,username)
		if not err:
			log_message = """action=|database search| method=|get_personal_passwords_by_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get passwords by folder",500)
		return list(response)

	def get_group_folder(self,GroupName):
		response , err = self.db.get_groupfolder(GroupName)
		if not err:
			log_message = """action=|database search| method=|get_group_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get group folder",500)
		return list(response)

	def get_group_passwords_by_folder(self,idFolder,username):
		response , err = self.db.get_group_passwords_byfolder_db(idFolder,username)
		if not err:
			log_message = """action=|database search| method=|get_group_passwords_by_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get shared passwords",500)
		return list(response)

	def get_groups(self):
		response , err = self.db.get_groups_db()
		if not err:
			log_message = """action=|database search| method=|get_groups| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get groups from database",500)
		return list(response)

	def get_pubkey(self,userdb):
		response , err = self.db.get_publickey_db(userdb)
		if not err:
			log_message = """action=|database search| method=|get_pubkey| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get pubkey", 500)
		return list(response)

	def add_user(self,name,email,username,pubkey):
		response , err = self.db.add_user_db(name,email,username,pubkey)
		if not err:
			log_message = """action=|database search| method=|add_user| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add user", 500)			

	def add_user_folder(self,name,path,userdb):
		response , err = self.db.add_userfolder_db(name,path,userdb)
		if not err:
			log_message = """action=|database search| method=|add_user_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add user folder", 500)

	def get_folder(self,nameFolder):
		response , err = self.db.get_folder_db(nameFolder)
		if not err:
			log_message = """action=|database search| method=|get_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get folder",500)
		if response == None:
			return []
		return list(response)

	def add_personal_password(self,username,folderName,passwd,name,login,url,description):
		response , err = self.db.add_personalpassword_db("Personal",username,folderName,passwd,name,login,url,description)
		if not err:
			log_message = """action=|database search| method=|add_personal_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add personal password. You can not have two passwords with the same name in the same folder",400)

	def add_shared_password(self,group,userdb,folderName,sharedId,passwd,name,login,url,description):
		response , err = self.db.add_sharedpassword_db(group,userdb,folderName,sharedId,passwd,name,login,url,description)
		if not err:
			log_message = """action=|database search| method=|add_shared_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add shared password. You can not have two passwords with the same name in the same folder",500)

	def get_sharedId(self):
		response , err = self.db.get_idcompartilhados_db()
		if not err:
			log_message = """action=|database search| method=|get_sharedId| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get shared id",500)
		if response == None:
			return []
		return list(response)

	def get_userId_by_group(self,group):
		response , err = self.db.get_usersidbygroup_db(group)
		if not err:
			log_message = """action=|database search| method=|get_userId_by_group| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get users id bu group")
		if response == None:
			return []
		return list(response)

	def get_folder_by_name(self,folderName):
		response , err = self.db.get_folderbyname_db(folderName)
		if not err:
			log_message = """action=|database search| method=|get_folder_by_name| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get folder",500)
		if response == None:
			return []
		return list(response)

	def get_group_id(self,group):
		response , err = self.db.get_group_id_db(group)
		if not err:
			log_message = """action=|database search| method=|get_group_id| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get group",500)
		if response == None:
			return []
		return list(response)

	def add_group_folder(self,folderName,path,group):
		response , err = self.db.add_groupfolder_db(folderName,path,group)
		if not err:
			log_message = """action=|database search| method=|add_group_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add group folder",500)

	def get_passwd_byid(self,_id):
		response , err = self.db.get_passwd_byid_db(_id)
		if not err:
			log_message = """action=|database search| method=|get_passwd_by_id| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get passwd by id",500)
		if response == None:
			return []
		return list(response)

	def update_personal_password(self,_id,name,passwd,description,url,login):
		response , err = self.db.update_personal_password_db(_id,name,passwd,description,url,login)
		if not err:
			log_message = """action=|database search| method=|update_personal_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to update personal password",500)

	def update_shared_password(self,_id,name,passwd,description,url,login):
		response , err = self.db.update_shared_password_db(_id,name,passwd,description,url,login)
		if not err:
			log_message = """action=|database search| method=|update_shared_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to update shared password",500)

	def get_passwd_by_sharedId(self,sharedId):
		response , err = self.db.get_passwd_byidCompartilhado(sharedId)
		if not err:
			log_message = """action=|database search| method=|get_passwd_by_sharedId| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get password by sharedId",500)
		if response == None:
			return []
		return list(response)

	def get_personal_passwords(self,username):
		response , err = self.db.get_personal_passwords_db(username)
		if not err:
			log_message = """action=|database search| method=|get_personal_passwords| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get password by sharedId",500)
		if response == None:
			return []
		return list(response)

	def get_group_passwords(self,username):
		response , err = self.db.get_group_passwords_db(username)
		if not err:
			log_message = """action=|database search| method=|get_group_passwords| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get password by sharedId",500)
		if response == None:
			return []
		return list(response)

	def update_password_newpubkey(self,idPassword,passwd,nome,login,url,descricao):
		response , err = self.db.update_password_newpubkey(idPassword,passwd,nome,login,url,descricao)
		if not err:
			log_message = """action=|database search| method=|update_password_newpubkey| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to update password with new pubkey",500)

	def update_pubkey(self,userdb,pubkey):
		response , err = self.db.update_publickey(userdb,pubkey)
		if not err:
			log_message = """action=|database search| method=|update_pubkey| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to update pubkey",500)

	def delete_personal_password(self,_id):
		response , err = self.db.exclude_password_personal_db(_id)
		if not err:
			log_message = """action=|database search| method=|delete_personal_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed delete personal password",500)

	def delete_shared_password(self,_id):
		response , err = self.db.exclude_password_shared_db(_id)
		if not err:
			log_message = """action=|database search| method=|delete_shared_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to delete shared password",500)

	def get_personal_tree(self,userdb):
		response , err = self.db.get_personalfolder_tree(userdb)
		if not err:
			log_message = """action=|database search| method=|get_tree| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get personal tree",500)
		if response == None:
			return []
		return list(response)

	def get_group_tree(self,group):
		response , err = self.db.get_groupfolder_tree(group)
		if not err:
			log_message = """action=|database search| method=|get_tree| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get group tree",500)
		if response == None:
			return []
		return list(response)

	def get_user_name(self,userdb):
		response , err = self.db.get_user_name_db(userdb)
		if not err:
			log_message = """action=|database search| method=|get_user_name| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get user name",500)
		if response == None:
			return []
		return list(response)

	def add_password_root(self,group,userdb,folder,passwd,name,login,url,description):
		response , err = self.db.add_sharedpassword_special_db(group,userdb,folder,passwd,name,login,url,description)
		if not err:
			log_message = """action=|database search| method=|add_password_root| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add password",500)

	def delete_group_folder(self,folder,group):
		response , err = self.db.delete_groupfolder_db(folder,group)
		if not err:
			log_message = """action=|database search| method=|delete_group_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to delete folder. It must be empty",500)

	def delete_user_folder(self,folder,userdb):
		response , err = self.db.delete_userfolder_db(folder,userdb)
		if not err:
			log_message = """action=|database search| method=|delete_user_folder| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to delete folder. It must be empty",500)

	def get_pass_by_group_unlock(self,group,userdb,usertounlockdb):
		response , err = self.db.get_pass_by_group_unlock_db(group,userdb,usertounlockdb)
		if not err:
			log_message = """action=|database search| method=|get_pass_by_group_unlock| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get passwords to unlock",500)
		if response == None:
			return []
		return list(response)

	def set_hash(self,userdb,t_hash):
		response , err = self.db.set_hash(userdb,t_hash)
		if not err:
			log_message = """action=|database search| method=|set_hash| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to set hash",500)

	def set_token(self,userdb,token):
		response , err = self.db.set_token(userdb,token)
		if not err:
			log_message = """action=|database search| method=|set_token| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to set token",500)

	def get_token(self,userdb):
		response , err = self.db.get_token(userdb)
		if not err:
			log_message = """action=|database search| method=|get_token| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get token",500)
		if response == None:
			return []
		return list(response)

	def get_hash(self,userdb):
		response , err = self.db.get_hash(userdb)
		if not err:
			log_message = """action=|database search| method=|get_hash| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get hash",500)
		if response == None:
			return []
		return list(response)

	def add_unlocked_shared_password(self,group,usertounlock,folder,sharedId,passwd,name,login,url,description):
		response , err = self.db.add_unlocked_sharedpassword_db(group,usertounlock,folder,sharedId,passwd,name,login,url,description)
		if not err:
			log_message = """action=|database search| method=|add_unlocked_shared_password| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to add unlocked password",500)

	def get_user_info(self,userdb):
		response , err = self.db.get_user_info_db(userdb)
		if not err:
			log_message = """action=|database search| method=|get_user_info| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get user info password",500)
		return list(response)

	def search_passwd(self,idUsuario,folder,name):
		response , err = self.db.search_password(idUsuario,folder,name)
		if not err:
			log_message = """action=|database search| method=|search_passwd| desc=|%s| result=|error|"""%response
			self.log.log_error(log_message)
			raise DatabaseError("Failed to get user info password",500)
		return list(response)


