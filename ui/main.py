# -*- coding: utf-8 -*-
import settings

import os, sys
from flask import Flask, request
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SESSION_COOKIE_SECURE'] = True

from send_json import SendJson
import json, uuid

from flask import Flask, render_template, session, redirect, url_for, flash, jsonify, request
from flask_bootstrap import Bootstrap
import ast

from flask_wtf import FlaskForm
from forms import *
from datetime import timedelta

bootstrap = Bootstrap(app)

from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin

import logging 
from logging.handlers import SysLogHandler

stdout_logger = logging.getLogger('gsenha-web')
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
out_hdlr.setLevel(logging.INFO)
stdout_logger.addHandler(out_hdlr)
stdout_logger.setLevel(logging.INFO)

login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.init_app(app)

import requests

j = SendJson()

class User(UserMixin):
    def __init__(self, uid=None, name=None):
        self.active = False
        if name != None:
            self.name = name
            self.active = True
            self.id = uid

    def is_active(self):
        return self.active
        
    def get_id(self):
            return self.id

def log_handler(message):
	stdout_logger.info(message)            

@login_manager.user_loader
def load_user(userid):
    return User(uid=userid)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=25)

@app.errorhandler(Exception)
def all_exceptions(error):
	src = request.remote_addr
	
	if "user" in session:
		user = session["user"]
	else:
		user = ""

	log_message = """action=|%s| desc=|%s| result=|error| user=|%s| src=|%s|"""%(request.path,error.message,user,src)
	log_handler(log_message)

	return jsonify({"status":"error","message":"something unexpected occoured"}) , 500    

@login_manager.unauthorized_handler
def unauthorized():
	flash("Please log in to access this page.","danger")
	return redirect(settings.BASE_URL+'/login')   

@app.route('/healthcheck', methods = ['GET'])
def healthcheck():
	req = requests.get(os.environ.get('API_HEALTHCHECK'),verify=True)
	if req.text == "WORKING":
		return "WORKING"
	else:
		return "FAILED"

@app.route('/about',methods=['GET'])
def about():
	return render_template('docs.html')

@app.route('/',methods=['GET'])
def index():
	return redirect(settings.BASE_URL+'/login')

@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		req = j.send_login(form.user.data,form.password.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			uid = uuid.uuid4()
			user = User(name=form.user.data,uid=uid)
			session['user'] = form.user.data
			session['token'] = r['token']
			if user.active is not False:
				login_user(user)
				log_message = """action=|login| user=|%s| result=|success| src=|%s|""" %(form.user.data,request.remote_addr)
				log_handler(log_message)				
				return redirect(settings.BASE_URL+'/passwords')
			else:
				return redirect(settings.BASE_URL+'/passwords')
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('login.html',form = form)			
	else:
		return render_template('login.html',form = form)

@app.route('/passwords',methods=['GET'])
@login_required
def show_passwords():
	req = j.send_get_passwords(session['token'])
	if req.status_code == 200:
		r = ast.literal_eval(req.text)
		folders = get_folders()
		if folders.status_code == 401:
			r = ast.literal_eval(folders.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|passwords| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)
			return redirect(settings.BASE_URL+'/login')

		tree = get_tree()
		if tree.status_code == 401:
			r = ast.literal_eval(tree.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|passwords| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)
			return redirect(settings.BASE_URL+'/login')

		t = ast.literal_eval(tree.text)
		f = ast.literal_eval(folders.text)

		for folder_tmp in f['Personal Folders']:
			for passwd_tmp in r['Personal Passwords'][folder_tmp]:
				passwd_tmp['password'] = passwd_tmp['password'].replace('\n','')
				passwd_tmp['description'] = passwd_tmp['description'].replace('\n','')
				passwd_tmp['url'] = passwd_tmp['url'].replace('\n','')
				passwd_tmp['login'] = passwd_tmp['login'].replace('\n','')

		for folder_tmp in f['Group Folders']:
			for passwd_tmp in r['Shared Passwords'][folder_tmp]:
				passwd_tmp['password'] = passwd_tmp['password'].replace('\n','')
				passwd_tmp['description'] = passwd_tmp['description'].replace('\n','')
				passwd_tmp['url'] = passwd_tmp['url'].replace('\n','')
				passwd_tmp['login'] = passwd_tmp['login'].replace('\n','')				

		log_message = """action=|passwords| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return render_template('passwords.html',passwd=r,folders=f,tree=t)
	else:
		r = ast.literal_eval(req.text)
		message = str(r['message'])
		flash(message,"danger")
		return redirect(settings.BASE_URL+'/login')

@app.route('/add/user',methods=['GET','POST'])
def add_user():
	form = AddUserForm()
	if form.validate_on_submit():
		req = j.send_add_user(form.user.data,form.password.data,form.pk.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			log_message = """action=|add user| user=|%s| result=|success| src=|%s|""" %(form.user.data,request.remote_addr)
			log_handler(log_message)				
			message = str(r['message'])
			flash(message,"success")
			return redirect(settings.BASE_URL+'/login')
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('adduser.html',form = form)
	else:
		return render_template('adduser.html',form = form)

@app.route('/add/password/personal',methods=['GET','POST'])
@login_required
def add_password_personal():
	form = AddPasswordPersonalForm()
	tmp = get_folders()
	if tmp.status_code == 200:
		tmp = ast.literal_eval(tmp.text)
		personal = list(tmp['Personal Folders'])
		folders = personal
		form.folder.choices = [(c, c) for c in folders]
	elif tmp.status_code == 401:
		tmp = ast.literal_eval(tmp.text)
		message = str(tmp['message'])
		flash(message,"danger")
		log_message = """action=|add password personal| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return redirect(settings.BASE_URL+'/login')
	elif tmp.status_code != 200 and tmp.status_code != 401:
		tmp = ast.literal_eval(tmp.text)
		message = str(tmp['message'])
		flash(message,"danger")
		return render_template('addpassword.html',form=form)
	if form.validate_on_submit():
		if not form.url.data:
			req = j.send_add_password_personal_url(session['token'],form.name.data,form.passwd.data,form.folder.data,form.login.data,form.description.data)
		else:
			req = j.send_add_password_personal(session['token'],form.name.data,form.passwd.data,form.folder.data,form.login.data,form.url.data,form.description.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|add personal password| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|add personal password| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')			
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('addpassword.html',form=form)
	else:
		return render_template('addpassword.html',form=form)

@app.route('/add/password/extuser',methods=['GET','POST'])
@login_required
def add_password_personal_ext():
	form = AddPasswordExtUserForm()
	if form.validate_on_submit():
		if not form.url.data:
			req = j.send_add_password_personal_ext_url(session['token'],form.name.data,form.passwd.data,form.username.data,form.login.data,form.description.data)
		else:
			req = j.send_add_password_personal_ext(session['token'],form.name.data,form.passwd.data,form.username.data,form.login.data,form.url.data,form.description.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|add external personal password| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|add external password| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')			
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('addpassword.html',form=form)
	else:
		return render_template('addpassword.html',form=form)

@app.route('/add/password/extgroup',methods=['GET','POST'])
@login_required
def add_password_group_ext():
	form = AddPasswordExtGroupForm()
	tmp = get_groups()
	if tmp.status_code == 200:
		tmp = ast.literal_eval(tmp.text)
		groups = list(tmp['Groups'])
		folders = groups
		form.group.choices = [(c, c) for c in folders]
	elif tmp.status_code == 401:
		r = ast.literal_eval(tmp.text)
		message = str(r['message'])
		flash(message,"danger")
		log_message = """action=|add password extgroup| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return redirect(settings.BASE_URL+'/login')		
	elif tmp.status_code != 200 and tmp.status_code != 401:
		tmp = ast.literal_eval(tmp.text)
		message = str(tmp['message'])
		flash(message,"danger")
		return render_template('addpassword.html',form=form)	
	if form.validate_on_submit():
		if not form.url.data:
			req = j.send_add_password_group_ext_url(session['token'],form.name.data,form.passwd.data,form.group.data,form.login.data,form.description.data)
		else:
			req = j.send_add_password_group_ext(session['token'],form.name.data,form.passwd.data,form.group.data,form.login.data,form.url.data,form.description.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|add external group password| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|add external group password| user=|%s| desc=|toke expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)
			return redirect(settings.BASE_URL+'/login')			
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('addpassword.html',form=form)
	else:
		return render_template('addpassword.html',form=form)

@app.route('/add/password/group',methods=['GET','POST'])
@login_required
def add_password_group():
	form = AddPasswordGroupForm()
	tmp = get_folders()
	if tmp.status_code == 200:
		tmp = ast.literal_eval(tmp.text)
		groups = list(tmp['Group Folders'])
		folders = groups
		form.folder.choices = [(c, c) for c in folders]
	elif tmp.status_code == 401:
		r = ast.literal_eval(tmp.text)
		message = str(r['message'])
		flash(message,"danger")
		log_message = """action=|add password group| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return redirect(settings.BASE_URL+'/login')		
	elif tmp.status_code != 200 and tmp.status_code != 401:
		tmp = ast.literal_eval(tmp.text)
		message = str(tmp['message'])
		flash(message,"danger")
		return render_template('addpassword.html',form=form)
	tmp2 = get_mygroups()
	if tmp2.status_code == 200:
		tmp2 = ast.literal_eval(tmp2.text)
		groups = list(tmp2['Groups'])
		form.group.choices = [(c, c) for c in groups]
	elif tmp2.status_code == 401:
		r = ast.literal_eval(tmp2.text)
		message = str(r['message'])
		flash(message,"danger")
		log_message = """action=|add password group| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return redirect(settings.BASE_URL+'/login')	
	elif tmp2.status_code != 200 and tmp2.status_code != 401:
		tmp = ast.literal_eval(tmp2.text)
		message = str(tmp['message'])
		flash(message,"danger")
		return render_template('addpassword.html',form=form)
	if form.validate_on_submit():
		if not form.url.data:
			req = j.send_add_password_group_url(session['token'],form.name.data,form.passwd.data,form.folder.data,form.group.data,form.login.data,form.description.data)
		else:
			req = j.send_add_password_group(session['token'],form.name.data,form.passwd.data,form.folder.data,form.group.data,form.login.data,form.url.data,form.description.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|add group password| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|add group password| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')			
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('addpassword.html',form=form)
	else:
		return render_template('addpassword.html',form=form)

@app.route('/unlock',methods=['GET','POST','PUT'])
@login_required
def unlock():
	form = UnlockForm()
	if request.method == 'GET':
		tmp2 = get_mygroups()
		if tmp2.status_code == 200:
			tmp2 = ast.literal_eval(tmp2.text)
			groups = list(tmp2['Groups'])
			form.group.choices = [(c, c) for c in groups]
			return render_template('unlock.html',form=form)
		elif tmp2.status_code == 401:
			tmp = ast.literal_eval(tmp2.text)
			message = str(tmp['message'])
			flash(message,"danger")
			log_message = """action=|unlock| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')
		else:
			r = ast.literal_eval(tmp2)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('unlock.html',form = form)			
	if request.method == 'POST':
		req = j.send_unlock(session['token'],form.group.data,form.usertounlock.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			for passwds in r['passwords']:
				passwds['passwd'] = passwds['passwd'].replace("\n","")
			passwds = r['passwords']
			token = str(r['token'])
			pubkey = str(r['pubkey'])
			return render_template('unlocking.html',token=token,passwds=passwds,pubkey=pubkey,usertounlock=form.usertounlock.data,group=form.group.data)
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|unlock| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')			
		else:
			tmp2 = get_mygroups()
			if tmp2.status_code == 200:
				tmp2 = ast.literal_eval(tmp2.text)
				groups = list(tmp2['Groups'])
				r = ast.literal_eval(req.text)
				message = str(r['message'])
				flash(message,"success")				
				form.group.choices = [(c, c) for c in groups]
				return render_template('unlock.html',form=form)
			elif tmp2.status_code == 401:
				tmp = ast.literal_eval(tmp2.text)
				message = str(tmp['message'])
				flash(message,"danger")
				log_message = """action=|unlock| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
				log_handler(log_message)			
				return redirect(settings.BASE_URL+'/login')
	if request.method == 'PUT':
		data = request.json
		keys = ['passwords','token']
		for key in keys:
			if key not in data.keys():
				flash("Information missing, cant continue this operation, please try again.","danger")
				log_message = """action=|unlock| user=|%s| desc=|Information missing| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
				log_handler(log_message)
				return render_template('unlock.html',form=form)

		req = j.send_unlock2(session['token'],data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|unlock| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)		
			return message
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|unlock| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|unlock| user=|%s| result=|error| desc=|%s| src=|%s|""" %(session['user'],message,request.remote_addr)
			log_handler(log_message)
			return "error"

@app.route('/privkey',methods=['GET'])
@login_required
def get_privkey():
	return render_template('privkey.html')

@app.route('/add/folder',methods=['GET','POST'])
@login_required
def add_folder():
	form = AddFolderForm()
	tmp = get_folders()
	if tmp.status_code == 200:
		tmp = ast.literal_eval(tmp.text)
		personal = list(tmp['Personal Folders'])
		groups = list(tmp['Group Folders'])
		folders = personal + groups
		form.path.choices = [(c, c) for c in folders]
	elif tmp.status_code == 401:
		r = ast.literal_eval(tmp.text)
		message = str(r['message'])
		flash(message,"danger")
		log_message = """action=|add folder| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return redirect(settings.BASE_URL+'/login')		
	elif tmp.status_code != 200 and tmp.status_code != 401:
		tmp = ast.literal_eval(tmp.text)
		message = str(tmp['message'])
		flash(message,"danger")
		return render_template('addfolder.html',form=form)
	if form.validate_on_submit():
		req = j.send_add_folder(session['token'],form.path.data,form.name.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|add folder| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|add folder | user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')					
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('addfolder.html',form=form)
	else:
		return render_template('addfolder.html',form=form)

@app.route('/delete/folder',methods=['GET','POST'])
@login_required
def del_folder():
	form = DeleteFolderForm()
	tmp = get_folders()
	if tmp.status_code == 200:
		tmp = ast.literal_eval(tmp.text)
		personal = list(tmp['Personal Folders'])
		groups = list(tmp['Group Folders'])
		folders = personal + groups
		form.folder.choices = [(c, c) for c in folders]
	elif tmp.status_code == 401:
		r = ast.literal_eval(tmp.text)
		message = str(r['message'])
		flash(message,"danger")
		log_message = """action=|delete folder| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)
		return redirect(settings.BASE_URL+'/login')		
	elif tmp.status_code != 200 and tmp.status_code != 401:
		tmp = ast.literal_eval(tmp.text)
		message = str(tmp['message'])
		flash(message,"danger")
		return render_template('delfolder.html',form=form)
	if form.validate_on_submit():
		req = j.send_del_folder(session['token'],form.folder.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|delete folder| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|delete folder| user=|%s| desc=|toke expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')			
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('delfolder.html',form=form)
	else:
		return render_template('delfolder.html',form=form)

@app.route('/update/password',methods=['GET','POST'])
@login_required
def update_passwd():
	form = UpdatePasswdForm()
	if form.validate_on_submit():

		if not form.passwd.data:
			passwd = None
		else:
			passwd = form.passwd.data
		if not form.login.data:
			login = None
		else:
			login = form.login.data	
		if not form.name.data:
			name = None
		else:
			name = form.name.data
		if not form.description.data:
			description = None
		else:
			description = form.description.data
		if not form.url.data:
			url = None
		else:
			url = form.url.data			
		req = j.send_update(session['token'],form.id_passwd.data,passwd,url,login,name,description)
		
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			log_message = """action=|update password| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/passwords')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|update password| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			return render_template('updatepass.html',form=form)
	else:
		return render_template('updatepass.html',form=form)

@app.route('/update/pubkey',methods=['GET','POST'])
@login_required
def update_pubkey():
	form = UpdatePubKeyForm()
	if form.validate_on_submit():
		req = j.send_update_pubkey(session['token'],form.pubkey.data,form.privkey.data)
		if req.status_code == 200:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"success")
			return redirect(settings.BASE_URL+'/privkey')
		if req.status_code == 401:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|update pubkey| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return redirect(settings.BASE_URL+'/login')			
		else:
			r = ast.literal_eval(req.text)
			message = str(r['message'])
			flash(message,"danger")
			log_message = """action=|update pubkey| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
			log_handler(log_message)			
			return render_template('updatepk.html',form=form)
	else:
		return render_template('updatepk.html',form=form)

def get_folders():
	return j.send_get_folders(session['token'])

def get_tree():
	return j.send_get_tree(session['token'])

def get_groups():
	return j.send_get_groups(session['token'])

def get_mygroups():
	return j.send_get_mygroups(session['token'])

@app.route('/delete/password/<int:idPassword>',methods=['DELETE'])
@login_required
def delete_passwd(idPassword):
	try:
		req = j.send_delete_password(session["token"],str(idPassword))
	except Exception,e:
		log_message = """action=|delete password| user=|%s| desc=|%s| result=|error| src=|%s|""" %(session['user'],e,request.remote_addr)
		log_handler(log_message)
		return "Failed to send request to delete password"
	if req.status_code == 200:
		r = ast.literal_eval(req.text)
		message = str(r['message'])
		log_message = """action=|delete password| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)		
		return message
	if req.status_code == 401:
		r = ast.literal_eval(req.text)
		message = str(r['message'])
		flash(message,"danger")
		log_message = """action=|delete password| user=|%s| desc=|token expired| result=|error| src=|%s|""" %(session['user'],request.remote_addr)
		log_handler(log_message)			
		return redirect(settings.BASE_URL+'/login')			
	else:
		r = ast.literal_eval(req.text)
		message = str(r['message'])
		return message

@app.route('/import',methods=['GET','POST'])
@login_required
def import_passwd():
	if request.method == 'GET':
		return render_template('import.html')
	if request.method == 'POST':
		r = send_import_passwd(request.json)
		return r


@app.route('/plugin-chrome', methods=['GET'])
def plugin_chrome():
	return render_template('plugin_chrome.html')


@app.route("/logout", methods=["GET"])
@login_required
def logout():
	log_message = """action=|logout| user=|%s| result=|success| src=|%s|""" %(session['user'],request.remote_addr)
	log_handler(log_message)
	logout_user()
	return redirect(settings.BASE_URL+'/login')

def send_import_passwd(passwds):
	folder = get_folders()
	f = ast.literal_eval(folder.text)
	errors = []
	if len(passwds["passwds"]) == 0:
		return "There are no passwords to be added, or could not understand import file."
	
	for tmp in passwds["passwds"]:
		if tmp["url"] == "":
			tmp.pop("url")

		if tmp["description"] == "": 
			tmp.pop("description")

		if tmp["login"] == "":
			tmp.pop("login")

		stdout_logger.info(tmp["folder"])

		if tmp["folder"] == "":
			tmp["folder"] = f["Personal Folders"][0]
		
		else:
			subfolders = tmp["folder"].split('.')
			for i in range(0,len(subfolders)):
				path = f["Personal Folders"][0]
				for k in range(0,i):
					path = path+"/"+subfolders[k]

				req_folder = j.send_add_folder(session['token'],path,subfolders[i])
			
			tmp["folder"] = path+"/"+subfolders[i]

		req = j.send_import(session['token'],tmp)
		if req.status_code != 200:
			errors.append(tmp["name"])

	if len(errors) > 0:
		error_msg = "Failed to add the following passwords: "
		for i in range(0,len(errors)):
			error_msg = error_msg +", "+str(errors[i])
		return error_msg
	else:
		return "All passwords successfully added."

if __name__ == '__main__':
    porta = 8081
    print 'Starting server on port:{0}'.format(porta)
    app.run(host='127.0.0.1', port=porta, debug=True)