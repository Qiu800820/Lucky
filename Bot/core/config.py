#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os


default_odds = ['9500', '950', '95', '9.5']


class Config:

	def __init__(self):
		self.resource_path = os.path.dirname(__file__)
		print('配置文件路径%s', self.resource_path)
		self.close_game_img = os.path.join(self.resource_path, '../resource/close_game.png')
		self.open_game_img = os.path.join(self.resource_path, '../resource/open_game.png')
		self.chats = '!@#$^&*()><:"/'
		self.chatRoomName = None
		self.BossName = None
		self.preview_time = None
		self.answer_refresh_time = None
		self.begin_game_hint = None
		self.odds = default_odds
		self.load_config()

	def load_config(self):
		# 读取配置
		path = os.path.join(self.resource_path, '../resource/config.txt')
		with open(path, 'r', -1, 'utf-8') as f:
			config = f.read()
			if config.startswith(u'\ufeff'):
				config = config.encode('utf8')[3:].decode('utf8')
			config = json.loads(config)
			self.chatRoomName = config['chatRoomName']
			self.BossName = config['BossName']
			self.preview_time = config['preview_time']  # 提前60秒收盘
			self.answer_refresh_time = config['answer_refresh_time']
			self.begin_game_hint = config['begin_game_hint']
			self.odds = config['odds']

	def save_config(self):
		path = os.path.join(self.resource_path, '../resource/config.txt')
		with open(path, 'w') as f:
			config = {}
			config.setdefault('chatRoomName', self.chatRoomName)
			config.setdefault('BossName', self.BossName)
			config.setdefault('preview_time', self.preview_time)
			config.setdefault('answer_refresh_time', self.answer_refresh_time)
			config.setdefault('begin_game_hint', self.begin_game_hint)
			config.setdefault('odds', self.odds)
			json.dump(config, f)


