# -*- coding: utf-8 -*-
from gsenhaapi import app, jwt
from flask import Flask, jsonify, request
from flask_jwt import JWT, jwt_required, current_user

from gsenhaapi.schema_wrapper import *
from gsenhaapi.exceptions import InvalidUsage
from gsenhaapi.exceptions import DatabaseError
from gsenhaapi.exceptions import CryptoError

import os
from unidecode import unidecode
from random import randrange
import bcrypt
import uuid
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from gsenhaapi.model.database import DataBase
from gsenhaapi.model.auth import Auth
from gsenhaapi.model.user import User
from gsenhaapi.model.ldapsearch import LdapSearch
from gsenhaapi.model.log import Log
from gsenhaapi.model.crypto import Crypto
from gsenhaapi.model.send_email import Email

from gsenhaapi.controller.databaseController import DatabaseController
from gsenhaapi.controller.authController import AuthController
from gsenhaapi.controller.userController import UserController
from gsenhaapi.controller.ldapController import LdapController

db = DataBase(os.environ.get('MYSQL_HOST'),os.environ.get('MYSQL_USERNAME'),os.environ.get('MYSQL_PASSWORD'),os.environ.get('MYSQL_DBNAME'))
m_auth = Auth(os.environ.get('LDAP_URI'))
ldap = LdapSearch(os.environ.get('LDAP_URI'))
log = Log()
mail = Email(os.environ.get('SMTP_SERVER'),os.environ.get('EMAIL_SENDER'),os.environ.get('EMAIL_SENDER_NAME'))

dbController = DatabaseController(db)
authapiController = AuthController(m_auth)
userController = UserController(dbController)
ldapController = LdapController(ldap)
crypto = Crypto(dbController)

KEYS = {}

@app.errorhandler(InvalidUsage)
def invalidUsage_exceptions(error):
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	if current_user != None:
		user = current_user.username
	elif request.json.get("username"):
		user = request.json["username"]
	elif request.json.get("user"):
		user = request.json["user"]
	else:
		user = ""

	log_message = """action=|%s| desc=|%s| result=|error| user=|%s| src=|%s|"""%(request.path,error.message,user,src)
	log.log_error(log_message)
	return jsonify({"status":"error","message":error.message}) , error.status_code

@app.errorhandler(DatabaseError)
def dataBaseError_exceptions(error):
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	if current_user != None:
		user = current_user.username
	elif request.json.get("username"):
		user = request.json["username"]
	elif request.json.get("user"):
		user = request.json["user"]
	else:
		user = ""

	log_message = """action=|%s| desc=|%s| result=|error| user=|%s| src=|%s|"""%(request.path,error.message,user,src)
	log.log_error(log_message)
	return jsonify({"status":"error","message":error.message}) , error.status_code

@app.errorhandler(CryptoError)
def cryptoError_exceptions(error):
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	if current_user != None:
		user = current_user.username
	elif request.json.get("username"):
		user = request.json["username"]
	elif request.json.get("user"):
		user = request.json["user"]
	else:
		user = ""

	log_message = """action=|%s| desc=|%s| result=|error| user=|%s| src=|%s|"""%(request.path,error.message,user,src)
	log.log_error(log_message)
	return jsonify({"status":"error","message":error.message}) , error.status_code	

@app.errorhandler(Exception)
def all_exceptions(error):
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr
	
	if current_user != None:
		user = current_user.username
	elif request.json.get("username"):
		user = request.json["username"]
	elif request.json.get("user"):
		user = request.json["user"]
	else:
		user = ""

	log_message = """action=|%s| desc=|%s| result=|error| user=|%s| src=|%s|"""%(request.path,error.message,user,src)
	log.log_error(log_message)
	return jsonify({"status":"error","message":"something unexpected occoured"}) , 500

@jwt.authentication_handler
def authenticate(username, password):	
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	uid = authapiController.auth(username,password)

	user = User(username,uid)	

	userdb = dbController.search_user(user.username)

	user.set_userdb(userdb)
	
	userController.set_user(user)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	log_message = """action=|/login| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return user

@jwt.error_handler
def error_handler(error):
	return jsonify({"status":"error","message":error.description}), 401

@jwt.payload_handler
def make_payload(user):
	return {'username':user.username,'uid':user.uid}

@jwt.user_handler
def load_user(payload):
	if payload['username']:
		return User(payload['username'],payload["uid"])

def create_tree(folders):
	folders_answer = []
	tmp = {}

	tmp["name"] = folders[0]

	folders_answer_tmp = []
	for i in range(1,len(folders)):
		tmp2 = {}
		tmp2["name"] = folders[i]
		folders_answer_tmp.append(tmp2)	

	tmp["children"] = folders_answer_tmp

	folders_answer.append(tmp)

	return folders_answer

@app.route('/healthcheck',methods=['GET'])
def healthcheck():
	message = {}
	errors = 0
	try:
		dbController.healthcheck()
		message["database"] = "success"			
	except DatabaseError:
		message["database"] = "connection error"
		errors = errors + 1
	try:
		authapiController.healthcheck()
		message["authapi"] = "success"
	except InvalidUsage:
		message["authapi"] = "connection error"
		errors = errors + 1
	try:
		ldapController.healthcheck()
		message["ldap"] = "success"
	except InvalidUsage:
		message["ldap"] = "connection error"
		errors = errors + 1

	if errors > 0:
		return jsonify({"status":"success","message":message}) , 500
	else:
		return "WORKING"

@app.route('/get/passwords',methods=['GET'])
@jwt_required()
def get_passwords():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)
	dbgroups = dbController.get_user_group(user.userdb)	

	user_folders = dbController.get_user_folder(user.userdb)

	personal_answer_byfolder = {}
	for nameFolder,idFolder in user_folders:
		partial_personal_answer = []
		passwds = dbController.get_personal_passwords_by_folder(idFolder,user.username)
		for passwd in passwds:
			d = {}
			d['name'] = passwd[0].decode('latin-1').encode('utf-8')
			d['password'] = passwd[1].encode('base64','strict')
			d['login'] = passwd[2].encode('base64','strict')
			d['url'] = passwd[3].encode('base64','strict')
			d['description'] = passwd[4].encode('base64','strict')
			d['ID'] = passwd[5]
			partial_personal_answer.append(d)
		personal_answer_byfolder[nameFolder] = partial_personal_answer
	
	groups_db_name= []
	for idGrupo in dbgroups:
		name = dbController.get_groups_name(idGrupo[0])
		groups_db_name.append(name[0][0])	

	group_folder = []
	for group in groups_db_name:
		folder = dbController.get_group_folder(group)
		for nameFolder,idFolder in folder:
			group_folder.append([nameFolder,idFolder])

	shared_answer_byfolder = {}
	for nameFolder,idFolder in group_folder:
		partial_group_answer = []
		passwds = dbController.get_group_passwords_by_folder(idFolder,user.username)
		for passwd in passwds:
			d = {}
			d['name'] = passwd[0].decode('latin-1').encode('utf-8')
			d['password'] = passwd[1].encode('base64','strict')
			d['login'] = passwd[2].encode('base64','strict')
			d['url'] = passwd[3].encode('base64','strict')
			d['description'] = passwd[4].encode('base64','strict')
			d['ID'] = passwd[5]
			partial_group_answer.append(d)
		shared_answer_byfolder[nameFolder] = partial_group_answer

	log_message = """action=|/get/passwords| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","Personal Passwords":personal_answer_byfolder,"Shared Passwords":shared_answer_byfolder}) , 200

@app.route('/get/mygroups',methods=['GET'])
@jwt_required()
def get_mygroups():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)
	dbgroups = dbController.get_user_group(user.userdb)
	
	groups_name = []
	for idGrupo in dbgroups:
		name = dbController.get_groups_name(idGrupo[0])
		groups_name.append(name[0][0])

	log_message = """action=|/get/mygroups| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"Groups":groups_name,"status":"success"}) , 200

@app.route('/get/groups', methods=['GET'])
@jwt_required()
def get_groups():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	groups_tmp = dbController.get_groups()

	groups = []
	for group in groups_tmp:
		if "Personal" not in str(group[0]):
			groups.append(str(group[0]))

	log_message = """action=|/get/groups| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)			
	
	return jsonify({"Groups":groups,"status":"success"}) , 200

@app.route('/get/folders',methods=['GET'])
@jwt_required()
def get_folders():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)
	dbgroups = dbController.get_user_group(user.userdb)

	groups_db_name= []
	for idGrupo in dbgroups:
		name = dbController.get_groups_name(idGrupo[0])
		groups_db_name.append(name[0][0])

	group_folder = []
	for group in groups_db_name:
		folders = dbController.get_group_folder(group)
		for folder in folders:
			group_folder.append(str(folder[0]))

	user_folder_tmp = dbController.get_user_folder(user.userdb)

	user_folder = []
	for folder in user_folder_tmp:
		user_folder.append(str(folder[0]))

	log_message = """action=|/get/folders| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","Group Folders":group_folder,"Personal Folders":user_folder}) , 200

@app.route('/add/user',methods=['POST'])
@validate_json
@validate_schema("adduser")
def add_user():
	uid = authapiController.auth(request.json["user"],request.json["password"])
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	username = request.json["user"]
	try:
		userdb = dbController.search_user(username)
	except InvalidUsage,e:
		if e.status_code != 401:
			raise InvalidUsage(e.message,e.status_code)
	try:
		if userdb:
			raise InvalidUsage("User already exists",400)
	except UnboundLocalError:
		pass
	
	info = ldapController.search_info(username)
	email = info["mail"]
	name = info["name"]

	keydata = str(request.json.get("pubkey"))

	pubkey = crypto.load_pubkey(keydata)

	pubkey_db = str(pubkey.public_numbers().n) + "," + str(pubkey.public_numbers().e)

	dbController.add_user(name,email,username,pubkey_db)

	userdb = dbController.search_user(username)
	user = User(request.json["user"],0)
	user.set_userdb(userdb)

	ldapgroups = ldapController.get_groups(user.username)

	folderName = "/Personal/" + name

	dbController.add_user_folder(folderName,"/Personal",user.userdb)

	externalFolderName = "/Personal/"+name+"/External"
	path_external = "/Personal/"+name

	dbController.add_user_folder(externalFolderName,path_external,user.userdb)

	users_list = []
	for group in ldapgroups:
		g = dbController.add_group(group)
		dbController.add_user_group(user.userdb,g)

		users_group = dbController.get_userId_by_group(group)
		for users in users_group:
			user_name = dbController.get_user_name(users[0])
			users_list.append(user_name[0])

	user_info = dbController.get_user_info(user.username)
	try:
		mail.send_welcome_email(str(user_info[0][0]),str(user_info[0][1]),set(users_list))
	except InvalidUsage,e:
		log_message = """action=|/add/user| user=|%s| src=|%s| desc=|Failed to send welcome mail| result=|error|"""%(request.json["user"],src)

	log_message = """action=|/add/user| user=|%s| src=|%s| result=|success|"""%(request.json["user"],src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"user successfully added, now you can login"})

@app.route('/add/password/personal',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("addpasswd")
def add_personalpassword():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	info = ldapController.search_info(user.username)
	name = info['name']

	userController.check_group(ldapgroups,dbgroups)
	passwd_name = unidecode(request.json["name"])
	
	passwd_login = request.json.get("login")
	if not passwd_login:
		passwd_login = "-"
	else:
		passwd_login = unidecode(request.json["login"])
	
	passwd_url = request.json.get("url")
	if not passwd_url:
		passwd_url = "-"
	else:
		passwd_url = unidecode(request.json["url"])
	
	passwd_description = request.json.get("description")
	if not passwd_description:
		passwd_description = "-"
	else:
		passwd_description = unidecode(request.json["description"])
	
	folder = str(request.json["folder"])
	t = "/Personal/" + name	

	if not folder.startswith(t):
		raise InvalidUsage("You are trying to add a personal password in a folder you can not",400)

	ext = "/Personal/"+name+"/External"

	if folder == ext:
		raise InvalidUsage("You are trying to add a personal password in a folder you can not",400)

	folderdb = dbController.get_folder(folder)
	if len(folderdb) == 0:
		raise InvalidUsage("This folder does not exist",400)

	pub_key = crypto.get_pubkey(userdb)

	try:
		password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_login = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_url = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_description = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
	except Exception,e:
		raise InvalidUsage("Failed to encrypt password",500)

	dbController.add_personal_password(user.username,folder,password,passwd_name,passwd_login,passwd_url,passwd_description)

	log_message = """action=|/add/password/personal| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"password successfully added"})

@app.route('/add/password/shared',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("addpasswdshared")
def add_sharedpassword():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	folder = str(request.json["folder"])
	group = str(request.json["group"])

	folderdb = dbController.get_folder(folder)
	if len(folderdb) == 0:
		raise InvalidUsage("This folder does not exist",400)

	user_groups = dbController.get_user_group(user.userdb)

	user_groups_name = []
	for groups in user_groups:
		group_name = dbController.get_groups_name(str(groups[0]))
		user_groups_name.append(str(group_name[0][0]))

	test = folder.split('/')

	if test[2] not in user_groups_name:
		raise InvalidUsage("You are trying to add a shared password in a folder you can not",403)

	if test[2] != group:
		raise InvalidUsage("This folder does not belong to this group",400)		
		
	for group_name in user_groups_name:
		ext = "/Shared/"+group_name+"/External"
		if folder == ext:
			raise InvalidUsage("You can not add a password in this folder",400)

	sharedId = dbController.get_sharedId()
	if len(sharedId) == 0:
		sharedId = 1
	else:
		sharedId = randrange(int(sharedId[0])+1,int(sharedId[0])+10)

	passwd_name = unidecode(request.json["name"])
				
	passwd_login = request.json.get("login")
	if not passwd_login:
		passwd_login = "-"
	else:
		passwd_login = unidecode(request.json["login"])
			
	passwd_url = request.json.get("url")
	if not passwd_url:
		passwd_url = "-"
	else:
		passwd_url = unidecode(request.json["url"])
		
	passwd_description = request.json.get("description")
	if not passwd_description:
		passwd_description = "-"
	else:
		passwd_description = unidecode(request.json["description"])

	pub_key = crypto.get_pubkey(user.userdb)

	try:
		password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
	except Exception,e:
		raise InvalidUsage("Failed to encrypt password",500)

	dbController.add_shared_password(group,user.userdb,folder,sharedId,password,passwd_name,passwd_login_crypt,passwd_url_crypt,passwd_description_crypt)	

	users_group_id = dbController.get_userId_by_group(group)
	users = []
	for users_id in users_group_id:
		if not str(user.userdb[0]) in str(users_id[0]):
			users.append(str(users_id[0]))

	if len(users) > 0:
		for userid in users:
			pub_key = crypto.get_pubkey(userid)

			try:
				password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			except Exception,e:
				raise InvalidUsage("Failed to encrypt password",500)

			dbController.add_shared_password(group,userid,folder,sharedId,password,passwd_name,passwd_login_crypt,passwd_url_crypt,passwd_description_crypt)	

	log_message = """action=|/add/password/shared| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"password successfully added"}) , 200

@app.route('/add/folder',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("addfolder")
def add_folder():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	info = ldapController.search_info(user.username)
	name = info["name"]

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	path_tmp = str(request.json["path"])
	if path_tmp.endswith("/"):
		path_tmp = path_tmp[:-1]

	path = dbController.get_folder(path_tmp)
	if len(path) == 0:
		raise InvalidUsage("This path does not exist",400)

	test = path_tmp.split("/")
	try:
		if test[3] == "External":		
			raise InvalidUsage("You can not add a folder in this path",500)
	except IndexError:
		pass

	if test[1] == "Personal":
		if name != test[2]:
			raise InvalidUsage("You are trying to add a folder where you can not",403)

		folder_name = path_tmp + "/" + unidecode(request.json["name"])

		folder_name_tmp = dbController.get_folder_by_name(folder_name)
		if len(folder_name_tmp) > 0:
			raise InvalidUsage("This folder already exists",500)

		dbController.add_user_folder(folder_name,path_tmp,user.userdb)

	elif test[1] == "Shared":
		groups = dbController.get_user_group(user.userdb)

		group = dbController.get_group_id(test[2])
		if len(group) == 0:
			raise InvalidUsage("You are trying to add a shared folder to a group that does not exist",400)

		groups_to_check = []
		for g in groups:
			groups_to_check.append(int(g[0]))

		if group[0][0] not in groups_to_check:
			raise InvalidUsage("You are not a member of the group you are trying to add a folder.",403)

		folder_name = path_tmp + "/" + unidecode(request.json["name"])

		folder_name_tmp = dbController.get_folder_by_name(folder_name)
		if len(folder_name_tmp) > 0:
			raise InvalidUsage("This folder already exists",400)

		dbController.add_group_folder(folder_name,path_tmp,group[0][0])

	else:
		raise InvalidUsage("Failed to add folder, path may be wrong",500)

	log_message = """action=|/add/folder| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"Folder successfully added"}) , 200

@app.route('/update/password',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("update")
def update_password():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	info = ldapController.search_info(user.username)
	name = info["name"]

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	passwd_tmp = dbController.get_passwd_byid(request.json["id"])
	if len(passwd_tmp) == 0:
		raise InvalidUsage("This password does not exist",400)

	passwd_name = request.json.get("name")
	if not passwd_name:
		passwd_name  = passwd_tmp[0]
	else:
		passwd_name = unidecode(request.json["name"])
				
	passwd_login = request.json.get("login")
	if not passwd_login:
		passwd_login = passwd_tmp[3]
	else:
		passwd_login = unidecode(request.json["login"])
			
	passwd_url = request.json.get("url")
	if not passwd_url:
		passwd_url = passwd_tmp[2]
	else:
		passwd_url = unidecode(request.json["url"])

	passwd_description = request.json.get("description")
	if not passwd_description:
		passwd_description = passwd_tmp[4]
	else:
		passwd_description = unidecode(request.json["description"])

	if user.userdb[0] != passwd_tmp[6]:
		raise InvalidUsage("You are trying to update a password you do not own",403)

	if passwd_tmp[5] == 0:
		pub_key = crypto.get_pubkey(user.userdb)

		passwd_passwd = request.json.get("passwd")
		if not passwd_passwd:
			try:
				if len(passwd_description) < 512:
					passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				else:
					passwd_description_crypt = passwd_description
				if len(passwd_url) < 512:
					passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				else:
					passwd_url_crypt = passwd_url
				if len(passwd_login) < 512:
					passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				else:
					passwd_login_crypt = passwd_login
			except Exception,e:
				raise InvalidUsage("Failed to encrypt password",500)

			dbController.update_personal_password(request.json["id"],passwd_name,passwd_tmp[1],passwd_description_crypt,passwd_url_crypt,passwd_login_crypt)
		else:

			try:
				password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				if len(passwd_description) < 512:
					passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				else:
					passwd_description_crypt = passwd_description
				if len(passwd_url) < 512:
					passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				else:
					passwd_url_crypt = passwd_url
				if len(passwd_login) < 512:
					passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				else:
					passwd_login_crypt = passwd_login
			except Exception,e:
				raise InvalidUsage("Failed to encrypt password",500)

			dbController.update_personal_password(request.json["id"],passwd_name,password,passwd_description_crypt,passwd_url_crypt,passwd_login_crypt)

	else:
		p_tmp = dbController.get_passwd_by_sharedId(passwd_tmp[5])

		for password_tmp in p_tmp:
			passwd_passwd = request.json.get("passwd")
			pub_key = crypto.get_pubkey(password_tmp[1])

			if not passwd_passwd:
				passwd_passwd = password_tmp[2]

				try:
					if len(passwd_description) < 512:
						passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					else:
						passwd_description_crypt = password_tmp[5]
					if len(passwd_url) < 512:
						passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					else:
						passwd_url_crypt = password_tmp[3]
					if len(passwd_login) < 512:
						passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					else:
						passwd_login_crypt = password_tmp[4]
				except Exception,e:
					raise InvalidUsage("Failed to encrypt password",500)											

				dbController.update_shared_password(password_tmp[0],passwd_name,passwd_passwd,passwd_description_crypt,passwd_url_crypt,passwd_login_crypt)

			else:

				try:
					password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					if len(passwd_description) < 512:
						passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					else:
						passwd_description_crypt = password_tmp[5]
					if len(passwd_url) < 512:
						passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					else:
						passwd_url_crypt = password_tmp[3]
					if len(passwd_login) < 512:
						passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
					else:
						passwd_login_crypt = password_tmp[4]					
				except Exception,e:
					raise InvalidUsage("Failed to encrypt password",500)

				dbController.update_shared_password(password_tmp[0],passwd_name,password,passwd_description_crypt,passwd_url_crypt,passwd_login_crypt)

	log_message = """action=|/update/password| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"Password successfully updated"}) , 200				

@app.route('/update/publickey',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("updatepub")
def update_publickey():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	keydata = str(request.json.get("pubkey"))
	pub_key = crypto.load_pubkey(keydata)

	new_pubkey = str(pub_key.public_numbers().n) + "," + str(pub_key.public_numbers().e)

	privk_s = str(request.json["privkey"])

	privkey = crypto.load_privkey(privk_s)

	old_personal_passwd = dbController.get_personal_passwords(user.username)

	old_group_passwd = dbController.get_group_passwords(user.username)

	new_personal_passwd = []

	for passwd in old_personal_passwd:
		passwd = list(passwd)
		try:
			passwd_1_tmp = privkey.decrypt(passwd[1],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd_3_tmp = privkey.decrypt(passwd[3],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd_4_tmp = privkey.decrypt(passwd[4],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd_5_tmp = privkey.decrypt(passwd[5],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		except Exception,e:
			raise InvalidUsage("Failed to decrypt password",500)

		try:
			passwd[1] = pub_key.encrypt(passwd_1_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd[3] = pub_key.encrypt(passwd_3_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd[4] = pub_key.encrypt(passwd_4_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd[5] = pub_key.encrypt(passwd_5_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		except Exception,e:
			raise InvalidUsage("Failed to encrypt password",500)

		new_personal_passwd.append(passwd)

	new_group_passwd = []
	for passwd in old_group_passwd:
		passwd = list(passwd)
		try:
			passwd_1_tmp = privkey.decrypt(passwd[1],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd_3_tmp = privkey.decrypt(passwd[3],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd_4_tmp = privkey.decrypt(passwd[4],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd_5_tmp = privkey.decrypt(passwd[5],padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		except Exception,e:
			raise InvalidUsage("Failed to decrypt password",500)

		try:
			passwd[1] = pub_key.encrypt(passwd_1_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd[3] = pub_key.encrypt(passwd_3_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd[4] = pub_key.encrypt(passwd_4_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd[5] = pub_key.encrypt(passwd_5_tmp,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		except Exception,e:
			raise InvalidUsage("Failed to encrypt password",500)

		new_group_passwd.append(passwd)

	for password in new_personal_passwd:
		dbController.update_password_newpubkey(password[0],password[1],password[2],password[3],password[4],password[5])

	for password in new_group_passwd:
		dbController.update_password_newpubkey(password[0],password[1],password[2],password[3],password[4],password[5])
		
	dbController.update_pubkey(user.userdb,new_pubkey)

	log_message = """action=|/update/pubkey| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"Public key successfully updated"}) , 200

@app.route('/delete/password/<int:idPassword>',methods=['DELETE'])
@jwt_required()
def delete_password(idPassword):
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	id_tmp = idPassword

	passwd_tmp = dbController.get_passwd_byid(id_tmp)
	if len(passwd_tmp) == 0:
		raise InvalidUsage("This password does not exist",400)

	if user.userdb[0] != passwd_tmp[6]:
		raise InvalidUsage("You are trying to delete a password you do not own",403)

	if passwd_tmp[5] == 0:
		dbController.delete_personal_password(id_tmp)
	else:
		dbController.delete_shared_password(passwd_tmp[5])

	log_message = """action=|/delete/password| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)		

	return jsonify({"status":"success","message":"Password successfully deleted"}) , 200

@app.route('/get/tree', methods=['GET'])
@jwt_required()
def get_folder2():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	info = ldapController.search_info(user.username)
	name = info["name"]

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	idgroups = dbController.get_user_group(user.userdb)

	p_folders = {}
	personal = dbController.get_personal_tree(user.userdb)
	
	tmp_p_folders = []
	for p in personal:
		tmp_p_folders.append(p[0])

	t = create_tree(tmp_p_folders)
	p_folders["Personal Folders"] = t

	groups = []
	for g in idgroups:
		groupname = dbController.get_groups_name(g[0])
		groups.append(groupname[0][0])

	group_folders = []
	for g in groups:
		tmp = dbController.get_group_tree(g)
		tmp_g_folder = []
		for gr_folder in tmp:
			tmp_g_folder.append(gr_folder[0])
		tmp_g_folder2 = create_tree(tmp_g_folder)
		group_folders.append(tmp_g_folder2)

	tmp = []
	g_folders = {}
	g_folders["Group Folders"] = group_folders
	
	tmp.append(p_folders)
	tmp.append(g_folders)

	log_message = """action=|/get/tree| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)
	
	return jsonify({"status":"success","Folders":tmp}) , 200

@app.route('/add/password/personal/external',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("addpasswdexternal")
def add_password_personal_external():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	if user.username == request.json["username"]:
		raise InvalidUsage("You can not add a password to yourself with this method",400)

	try:
		user2db = dbController.search_user(request.json["username"])
	except DatabaseError:
		raise InvalidUsage("The user you are trying to add a password does not exist",400)

	user2 = User(request.json["username"],0)
	user2.set_userdb(user2db)

	passwd_name = unidecode(request.json["name"])

	passwd_login = request.json.get("login")
	if not passwd_login:
		passwd_login = "-"
	else:
		passwd_login = unidecode(request.json["login"])
	
	passwd_url = request.json.get("url")
	if not passwd_url:
		passwd_url = "-"
	else:
		passwd_url = unidecode(request.json["url"])

	passwd_description = request.json.get("description")
	if not passwd_description:
		passwd_description = "-"
	else:
		passwd_description = unidecode(request.json["description"])		

	user2name = dbController.get_user_name(user2.userdb)

	folder = "/Personal/"+user2name[0]+"/External"

	pub_key = crypto.get_pubkey(user2.userdb)

	try:
		password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_login = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_url = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		passwd_description = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
	except Exception,e:
		raise InvalidUsage("Failed to encrypt password",500)	

	dbController.add_personal_password(user2.username,folder,password,passwd_name,passwd_login,passwd_url,passwd_description)

	log_message = """action=|/add/password/personal/external| desc=|password added to %s| user=|%s| src=|%s| result=|success|"""%(request.json["username"],user.username,src)
	log.log_info(log_message)

	message = "Password successfully added to %s"%request.json["username"]
	return jsonify({"status":"success","message":message}) , 200


@app.route('/add/password/shared/external',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("addpasswdsharedexternal")
def add_password_shared_external():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	group_tmp = request.json["group"]

	groupid = dbController.search_group(group_tmp)
	if len(groupid) == 0:
		raise InvalidUsage("Group does not exist",400)

	passwd_name = unidecode(request.json["name"])

	passwd_login = request.json.get("login")
	if not passwd_login:
		passwd_login = "-"
	else:
		passwd_login = unidecode(request.json["login"])
	
	passwd_url = request.json.get("url")
	if not passwd_url:
		passwd_url = "-"
	else:
		passwd_url = unidecode(request.json["url"])
	passwd_description = request.json.get("description")

	if not passwd_description:
		passwd_description = "-"
	else:
		passwd_description = unidecode(request.json["description"])		

	passwd_folder = "/Shared/"+group_tmp+"/External"

	sharedId = dbController.get_sharedId()
	if len(sharedId) == 0:
		sharedId = 1
	else:
		sharedId = randrange(int(sharedId[0])+1,int(sharedId[0])+10)

	users_group = dbController.get_userId_by_group(group_tmp)

	users = []
	for userid in users_group:
		if str(user.userdb[0]) in str(userid[0]):
			raise InvalidUsage("You are trying to add a password to a group you are member",400)
		users.append(str(userid[0]))

	if len(users) > 0:
		for userid in users:
			pub_key = crypto.get_pubkey(userid)

			try:
				password = pub_key.encrypt(str(request.json["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				passwd_login_crypt = pub_key.encrypt(passwd_login,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				passwd_url_crypt = pub_key.encrypt(passwd_url,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
				passwd_description_crypt = pub_key.encrypt(passwd_description,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			except Exception,e:
				raise InvalidUsage("Failed to encrypt password",500)

			dbController.add_shared_password(group_tmp,userid,passwd_folder,sharedId,password,passwd_name,passwd_login_crypt,passwd_url_crypt,passwd_description_crypt)

	log_message = """action=|/add/password/shared/external| desc=|password added to %s| user=|%s| src=|%s| result=|success|"""%(request.json["group"],user.username,src)
	log.log_info(log_message)

	message = "Password successfully added to %s"%request.json["group"]
	return jsonify({"status":"success","message":message}) , 200


@app.route('/delete/folder',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("delfolder")
def delete_folder():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	name_folder = str(request.json["folder"]).split('/')

	if len(name_folder) == 1:
		raise InvalidUsage("Could not understand folders name",400)

	if len(name_folder) < 4:
		raise InvalidUsage("You can not delete this folder",400)

	if name_folder[3] == "External":
		raise InvalidUsage("You can not delete this folder",400)

	groups_db = dbController.get_user_group(user.userdb)

	groups_name = []
	for groups in groups_db:
		name = dbController.get_groups_name(groups[0])
		groups_name.append(name[0][0])

	if name_folder[1] == "Shared":
		if name_folder[2] not in groups_name:
			raise InvalidUsage("You are not a member of this group",403)

		groupdb = dbController.get_group_id(name_folder[2])

		dbController.delete_group_folder(str(request.json["folder"]),groupdb)

		log_message = """action=|/delete/folder| user=|%s| src=|%s| result=|success|"""%(user.username,src)
		log.log_info(log_message)

		return jsonify({"status":"success","message":"Folder successfully deleted"}) , 200

	if name_folder[1] == "Personal":
		user_folders_tmp = dbController.get_user_folder(user.userdb)

		user_folders = []
		for folder in user_folders_tmp:
			user_folders.append(folder[0])

		if str(request.json["folder"]) not in user_folders:
			raise InvalidUsage("You do not own this folder",403)

		dbController.delete_user_folder(str(request.json["folder"]),user.userdb)

		log_message = """action=|/delete/folder| user=|%s| src=|%s| result=|success|"""%(user.username,src)
		log.log_info(log_message)

		return jsonify({"status":"success","message":"Folder successfully deleted"}) , 200

	else:
		raise InvalidUsage("Could not understand folder name"), 400

@app.route('/unlock',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("unlock")
def unlock():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	if user.username == request.json["usertounlock"]:
		raise InvalidUsage("You can not unlock your self",400)

	try:
		usertounlockdb = dbController.search_user(request.json["usertounlock"])
	except InvalidUsage:
		raise InvalidUsage("The user you are trying to unlock does not exist",400)
	
	usertounlock = User(request.json["usertounlock"],0)
	usertounlock.set_userdb(usertounlockdb)

	user_groups = dbController.get_user_group(user.userdb)

	group = dbController.get_group_id(str(request.json["group"]))
	if len(group) == 0:
		raise InvalidUsage("This group does not exist",400)

	groups_check = []
	for g in user_groups:
		groups_check.append(int(g[0]))

	if group[0][0] not in groups_check:
		raise InvalidUsage("You are not a member of this group",403)

	usertounlock_groups = dbController.get_user_group(usertounlock.userdb)

	groups_check = []
	for g in usertounlock_groups:
		groups_check.append(int(g[0]))

	if group[0][0] not in groups_check:
		raise InvalidUsage("User to unlock is not a member of this group",403)

	passwd = dbController.get_pass_by_group_unlock(str(request.json["group"]),user.userdb,usertounlock.userdb)

	if len(passwd) == 0:
		raise InvalidUsage("User already unlocked",400)

	response = {}
	passwds = []
	t_hash = ""
	for password in passwd:
		tmp = {}
		tmp["idGrupo"] = password[0]
		tmp["idPastas"] = password[2]
		tmp["idCompartilhado"] = password[3]
		tmp["passwd"] = password[4].encode('base64','strict')
		tmp["name"] = password[5].decode('latin-1').encode('utf-8')
		tmp["login"] = password[6].encode('base64','strict')
		tmp["url"] = password[7].encode('base64','strict')
		tmp["description"] = password[8].encode('base64','strict')
		t_hash = t_hash+str(password[0])+str(password[2])+str(password[3])+str(password[5].decode('latin-1').encode('utf-8'))
		passwds.append(tmp)

	private_key = crypto.generate_privkey()
	public_key = private_key.public_key()

	pem = crypto.generate_pem_public(public_key)

	response["pubkey"] = pem
	response["passwords"] = passwds
	token = bcrypt.hashpw(str(uuid.uuid4()),bcrypt.gensalt())
	t_hash = bcrypt.hashpw(t_hash,bcrypt.gensalt())
	response["token"] = token

	KEYS[token] = crypto.generate_pem_private(private_key)

	dbController.set_hash(user.userdb,t_hash)
	dbController.set_token(user.userdb,token)

	log_message = """action=|/unlock| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","pubkey":pem,"passwords":passwds,"token":token}) , 200


@app.route('/unlocking',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("unlocking")
def unlocking():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	if user.username == request.json["usertounlock"]:
		raise InvalidUsage("You can not unlock your self",400)

	try:
		usertounlockdb = dbController.search_user(request.json["usertounlock"])
	except DatabaseError:
		raise InvalidUsage("The user you are trying to add a password does not exist",400)
	
	usertounlock = User(request.json["usertounlock"],0)
	usertounlock.set_userdb(usertounlockdb)

	group = dbController.get_group_id(str(request.json["group"]))
	if len(group) == 0:
		raise InvalidUsage("This group does not exist",400)

	user_groups = dbController.get_user_group(user.userdb)

	groups_check = []
	for g in user_groups:
		groups_check.append(int(g[0]))

	if group[0][0] not in groups_check:
		raise InvalidUsage("You are not a member of this group",403)

	usertounlock_groups = dbController.get_user_group(usertounlock.userdb)

	groups_check = []
	for g in usertounlock_groups:
		groups_check.append(int(g[0]))

	if group[0][0] not in groups_check:
		raise InvalidUsage("User to unlock is not a member of this group",403)

	token = dbController.get_token(user.userdb)
	if len(token) == 0:
		raise InvalidUsage("You dont have a token. You should do the /unlock method first",400)

	if token[0][0] != request.json["token"]:
		raise InvalidUsage("Invalid token",403)

	_hash = dbController.get_hash(user.userdb)
	if len(_hash) == 0:
		raise Invalid("You dont have a hash. You should do the /unlock method first",400)

	passwords = request.json["passwords"]

	t_hash = ""
	for password in passwords:
		t_hash = t_hash + str(password["idGrupo"])+str(password["idPastas"])+str(password["idCompartilhado"])+str(password["name"])

	if not bcrypt.hashpw(t_hash, _hash[0][0]) == _hash[0][0]:
		raise InvalidUsage("Integrity check failed",403)

	pub_key = crypto.get_pubkey(usertounlock.userdb)

	privkey = crypto.load_privkey(KEYS[token[0][0]])

	for passwd in passwords:
		try:
			passwd["passwd"] = privkey.decrypt(str(passwd["passwd"]).decode('base64','strict'),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd["description"] = privkey.decrypt(str(passwd["description"]).decode('base64','strict'),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd["url"] = privkey.decrypt(str(passwd["url"]).decode('base64','strict'),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd["login"] = privkey.decrypt(str(passwd["login"]).decode('base64','strict'),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		except Exception,e:
			raise InvalidUsage("Failed to decrypt password",500)
		
	try:
		KEYS.pop(token[0][0])
	except KeyError:
		pass

	for passwd in passwords:
		try:
			passwd["passwd"] = pub_key.encrypt(str(passwd["passwd"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd["description"] = pub_key.encrypt(str(passwd["description"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd["url"] = pub_key.encrypt(str(passwd["url"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
			passwd["login"] = pub_key.encrypt(str(passwd["login"]),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
		except Exception,e:
			raise InvalidUsage("Failed to encrypt password",500)

	for passwd in passwords:
		dbController.add_unlocked_shared_password(passwd["idGrupo"],usertounlockdb[0],passwd["idPastas"],passwd["idCompartilhado"],passwd["passwd"], passwd["name"],passwd["login"],passwd["url"],passwd["description"])

	dbController.set_hash(user.userdb,"0")
	dbController.set_token(user.userdb,"0")

	log_message = """action=|/unlocking| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	return jsonify({"status":"success","message":"Passwords successfully unlocked"}) , 200

@app.route('/search/password',methods=['POST'])
@jwt_required()
@validate_json
@validate_schema("search")
def search_passwd():
	if request.headers.get('x-real-ip'):
		src = request.headers.get('x-real-ip')
	else:
		src = request.remote_addr

	user = current_user

	userdb = dbController.search_user(user.username)
	user.set_userdb(userdb)

	dbgroups = dbController.get_user_group(user.userdb)

	ldapgroups = ldapController.get_groups(user.username)

	userController.check_group(ldapgroups,dbgroups)

	passwd = dbController.search_passwd(user.userdb,str(request.json['folder']),str(request.json['name']))
	if len(passwd) == 0:
		raise InvalidUsage("Password does not exist",400)

	log_message = """action=|/search/password| user=|%s| src=|%s| result=|success|"""%(user.username,src)
	log.log_info(log_message)

	tmp = {}
	tmp["name"] = passwd[0][0]
	tmp["passwd"] = passwd[0][1].encode('base64','strict')
	tmp["url"] = passwd[0][2].encode('base64','strict')
	tmp["login"] = passwd[0][3].encode('base64','strict')
	tmp["description"] = passwd[0][4].encode('base64','strict')

	return jsonify({"status":"success","password":tmp}) , 200