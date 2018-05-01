#!/usr/bin/python
# -*- coding: UTF-8 -*-

import itchat
from itchat.content import *

isReceived = False
chatRoomName = '自动时时彩'


@itchat.msg_register(TEXT, isGroupChat=True)
def received(msg):
	if not isReceived and not msg['isAt']:
		return None
	print(msg)
	chat_rooms = itchat.search_chatrooms(name=chatRoomName)
	for chat_room in chat_rooms:
		print(chat_room)
		itchat.send('开盘时间， 开始打码', toUserName=chat_room['UserName'])
	# 译码
	if isReceived:
		# 保存
		# 回复打码成功
		return "用户'%s'打码成功" % msg['ActualNickName']
	else:
		return "已经收盘， 用户'%s'打码失败" % msg['ActualNickName']


def open_game():
	chat_rooms = itchat.search_chatrooms(name=chatRoomName)
	for chat_room in chat_rooms:
		print(chat_room)
		itchat.send('开盘时间， 开始打码', toUserName=chat_room[''])


def close_game():
	print('闭盘')
	return '闭盘，停止下单'


def show_answer():
	print('开奖')
	return '本期开奖结果:%s' % 'xxxx'

itchat.auto_login(hotReload=True)
itchat.run()
