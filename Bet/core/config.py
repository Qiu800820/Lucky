#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json


class Config:

	def __init__(self):
		self.bet = None
		self.max = None
		self.token = None
		self.base_url = None
		self.position = '%sXX%s'
		self.load_config()

	def load_config(self):
		# 读取配置
		with open('./resource/config.txt', 'r', -1, 'utf-8') as f:
			config = f.read()
			if config.startswith(u'\ufeff'):
				config = config.encode('utf8')[3:].decode('utf8')
			config = json.loads(config)
			self.max = config['max']
			self.bet = config['bet']
			self.token = config['token']
			self.base_url = config['base_url']
			self.position = config['position']

	def save_config(self):
		with open('./resource/config.txt', 'w', -1, 'utf-8') as f:
			config = {}
			config.setdefault('bet', self.bet)
			config.setdefault('max', self.max)
			config.setdefault('token', self.token)
			config.setdefault('position', self.position)
			config.setdefault('base_url', self.base_url)
			json.dump(config, f, ensure_ascii=False)


