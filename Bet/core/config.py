#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json


class Config:

	def __init__(self):
		self.bet = None
		self.max_ying = None
		self.max_shu = None
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
			self.max_ying = config['max_ying']
			self.max_shu = config['max_shu']
			self.bet = config['bet']
			self.token = config['token']
			self.base_url = config['base_url']
			self.position = config['position']

	def save_config(self):
		with open('./resource/config.txt', 'w', -1, 'utf-8') as f:
			config = {}
			config.setdefault('bet', self.bet)
			config.setdefault('max_ying', self.max_ying)
			config.setdefault('max_shu', self.max_shu)
			config.setdefault('token', self.token)
			config.setdefault('position', self.position)
			config.setdefault('base_url', self.base_url)
			json.dump(config, f, ensure_ascii=False)


