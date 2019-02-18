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
		self.last_no = None
		self.last_order_id = None
		self.agent_url = None
		self.follow_spacing = None
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
			self.last_no = config['last_no']
			self.last_order_id = config['last_order_id']
			self.max_shu = config['max_shu']
			self.bet = config['bet']
			self.token = config['token']
			self.base_url = config['base_url']
			self.position = config['position']
			self.agent_url = config['agent_url']
			self.follow_spacing = config['follow_spacing']

	def save_config(self):
		with open('./resource/config.txt', 'w', -1, 'utf-8') as f:
			config = {}
			config.setdefault('bet', self.bet)
			config.setdefault('max_ying', self.max_ying)
			config.setdefault('max_shu', self.max_shu)
			config.setdefault('last_no', self.last_no)
			config.setdefault('last_order_id', self.last_order_id)
			config.setdefault('token', self.token)
			config.setdefault('position', self.position)
			config.setdefault('base_url', self.base_url)
			config.setdefault('agent_url', self.agent_url)
			config.setdefault('follow_spacing', self.follow_spacing)
			json.dump(config, f, ensure_ascii=False)


