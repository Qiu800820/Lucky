#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import time


class Log:

	def __init__(self):
		self.logger = self.get_logging()

	def get_logging(self):
		logger = logging.getLogger('Bet')
		logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

		file_handler = logging.FileHandler('./log/%s.log' % time.strftime('%F'), encoding='utf-8')
		file_handler.setFormatter(formatter)
		logger.addHandler(file_handler)

		console_handler = logging.StreamHandler()
		console_handler.setLevel(logging.DEBUG)
		logger.addHandler(console_handler)

		return logger

	def info(self, msg, *args, **kwargs):
		self.logger.info(msg, *args, **kwargs)

	def warning(self, msg, *args, **kwargs):
		self.logger.warning(msg, *args, **kwargs)

	def debug(self, msg, *args, **kwargs):
		self.logger.debug(msg, *args, **kwargs)

	def error(self, msg, *args, **kwargs):
		self.logger.error(msg, *args, **kwargs)
