#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

PRIVATE_CHAT = 0x00
GROUP_CHAT = 0x01
FRIENDS = 0x10

msgList = [
	{
		'MsgId': '8862234331128478280',
		'Content': '开始',
		'FromUserName': 'Boss',
		'CreateTime': int(time.time()),
		'Type': PRIVATE_CHAT
	},
	{
		'MsgId': '8862234331128478281',
		'Content': '上分|Sum|1000',
		'CreateTime': int(time.time()),
		'FromUserName': 'Boss',
		'Type': PRIVATE_CHAT
	},
	{
		'MsgId': '8862234331128478283',
		'ActualNickName': 'Sum',
		'Content': '123十百=10',
		'CreateTime': int(time.time()),
		'FromUserName': 'Test',
		'Type': PRIVATE_CHAT
	},

	{
		'MsgId': '8862234331128478283',
		'ActualNickName': 'Sum',
		'Content': '123十百=10',
		'CreateTime': int(time.time()),
		'FromUserName': 'Test',
		'Type': GROUP_CHAT
	},
	{
		'MsgId': '8862234331128478283',
		'ActualNickName': 'Sum',
		'Content': '123十百=10',
		'CreateTime': int(time.time()),
		'FromUserName': 'Test',
		'Type': PRIVATE_CHAT
	},
]


def auto_login(self):
	print('账号登陆')


def search_chatrooms(self, name):
	return [{'UserName': 'SSC', 'NickName': '自动1'}]


def send(self, msg, toUserName):
	print('send --> msg: %s, userName: %s' % (msg, toUserName))


def send_image(self, msg, toUserName):
	pass


def search_friends(self, name):
	return [{'UserName': 'Boss'}]


def run(self, private_chat, group_chat, add_friend):
	for msg in msgList:
		if msg['Type'] == PRIVATE_CHAT:
			print(private_chat(msg))
		elif msg['Type'] == GROUP_CHAT:
			print(group_chat(msg))
		else:
			print(add_friend)
		time.sleep(10)
	time.sleep(10 * 3600)


def set_alias(self, param, user_name):
	pass
