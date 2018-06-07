#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import time

PRIVATE_CHAT = 0x00
GROUP_CHAT = 0x01
FRIENDS = 0x10


def msg_generate(content, user_name, message_type):
	message = {
		'MsgId': str(time.time() * 1000),
		'Content': content,
		'FromUserName': user_name,
		'CreateTime': int(time.time()),
		'Type': message_type,
		'User': {
			'RemarkName': user_name,
			'NickName': 'Sum'
		}
	}
	if message_type == GROUP_CHAT:
		group_message = {'ActualNickName': user_name}
		message.update(group_message)
	return message


def auto_login():
	print('账号登陆')


def search_chatrooms(name):
	return [{'UserName': 'SSC', 'NickName': '自动1'}]


def send(msg, toUserName):
	print('send --> msg: %s, userName: %s' % (msg, toUserName))


def send_image(msg, toUserName):
	pass


def search_friends(name):
	return [{'UserName': 'Boss'}]


def run(private_chat, group_chat, add_friend):

	message = None
	while not message or '停止' not in message['Content']:
		try:
			raw = input('input message: (content, user_name, message_type)')
			raw = '{"content":"%s","user_name":"%s","message_type":%s}' % tuple(raw.split(','))
			message_params = json.loads(raw)
			message = msg_generate(
				message_params['content'], message_params['user_name'],
				message_params['message_type']
			)
			if message['Type'] == PRIVATE_CHAT:
				print(private_chat(message))
			elif message['Type'] == GROUP_CHAT:
				print(group_chat(message))
			else:
				print(add_friend)
		except:
			message = None


def set_alias(param, user_name):
	pass
