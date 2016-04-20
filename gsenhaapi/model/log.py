# -*- coding: utf-8 -*-
import logging, sys
from logging.handlers import SysLogHandler


class Log():

	def __init__(self):
		self.stdout_logger = logging.getLogger('gsenha-api')
		if not self.stdout_logger.handlers:
			self.out_hdlr = logging.StreamHandler(sys.stdout)
			self.out_hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
			self.out_hdlr.setLevel(logging.INFO)
			self.stdout_logger.addHandler(self.out_hdlr)
			self.stdout_logger.setLevel(logging.INFO)

	def log_error(self,message):
		self.stdout_logger.error(message)

	def log_info(self,message):
		self.stdout_logger.info(message)