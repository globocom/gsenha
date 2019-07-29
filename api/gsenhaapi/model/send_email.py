# -*- coding: utf-8 -*-
import smtplib
from email import utils
from email.mime.text import MIMEText
import sys
from gsenhaapi.exceptions import InvalidUsage
from gsenhaapi.model.log import Log
log = Log()

class Email:

	def __init__ (self, host, sender,name_sender):
		self.host = host
		self.sender = sender
		self.name_sender = name_sender


	def create_welcome_msg(self,name,group):

		if len(group) == 0:
			msg = """
%s, 
Welcome to GSenha.

Before starting, please, read the docs. Your private key will never be stored or sent to server, keep it safe!""" %(name)
		else:
			users = ""
			for i in range(0,len(group)):
				if group[i] != name:
					if i == 0:
						users = users+group[i]
					else:
						users = users+", "+group[i]
			msg = """
%s, 
Welcome to GSenha.

Before starting, please, read the docs. 

You are not the first member of your group, in this case it is necessary that an older member unlock you to see all passwords. 

Here there are some users that can do this: %s.

Your private key will never be stored or sent to server, keep it safe!""" %(name,users)
		return msg


# 	def create_passwd_added(self,name,name_from):
# 		msg = """
# Olá %s,

# o usuário %s acabou de adicionar uma senha para você. Confira na sua pasta "Externas".
# 		""" %(name,name_from)
# 		return msg


	def send_welcome_email(self,to,name,group):
		group = list(group)
		text = self.create_welcome_msg(name,group)
		msg = MIMEText(text.decode('utf-8'),'plain','UTF-8')

		recipient = to

		msg['To'] = utils.formataddr((name, recipient))
		msg['From'] = utils.formataddr((self.name_sender, self.sender))
		msg['Subject'] = 'Welcome'

		server = smtplib.SMTP(self.host,25)

		try:
			server.sendmail(self.sender, [recipient], msg.as_string())
		except smtplib.SMTPException:
			log_message = """action=|send_welcome_email| user=|%s| desc=|Failed to send welcome mail| result=|error|""" % (to)
			log.log_info(log_message)
		finally:
			server.quit()

	# def send_passwd_added_email(self,to,name,name_from):

	# 	text = self.create_passwd_added(name,name_from)

	# 	msg = MIMEText(text.decode('utf-8'),'plain','UTF-8')

	# 	recipient = to

	# 	msg['To'] = utils.formataddr((name, recipient))
	# 	msg['From'] = utils.formataddr((self.name_sender, self.sender))
	# 	msg['Subject'] = 'Senha adicionada'

	# 	server = smtplib.SMTP(self.host,25)

	# 	try:
	# 		server.sendmail(self.sender, [recipient], msg.as_string())
	# 	except smtplib.SMTPException:
	# 		raise InvalidUsage("Failed to send added password email",500)
	# 	finally:
	# 		server.quit()
