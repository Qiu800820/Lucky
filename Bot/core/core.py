#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sched
import time

import itchat
from itchat.content import *

from Bot.core.fetch import Fetch

isReceived = False
chatRoomName = '自动时时彩'
BossName = 'Boss'
chat_rooms = None
fetch = Fetch()

#
# @itchat.msg_register(TEXT, isGroupChat=True)
# def received(msg):
# 	if not isReceived and not msg['isAt']:
# 		return None
# 	print(msg)
# 	# 译码
# 	if isReceived:  # 打码结果
# 		# 保存
# 		# 回复打码成功
# 		return "用户'%s'打码成功" % msg['ActualNickName']
# 	else:
# 		return "， 用户'%s'打码失败" % msg['ActualNickName']


@itchat.msg_register(TEXT)
def command(msg):
	global isReceived
	if not msg['UserName'] == BossName:
		return None
	print(msg)
	if '开始' in msg['Content']:
		isReceived = True
	elif '停止' in msg['Content']:
		isReceived = False


def open_game():
	print('开盘')
	global chat_rooms
	chat_rooms = itchat.search_chatrooms(name=chatRoomName)
	for chat_room in chat_rooms:
		itchat.send('开盘时间， 开始打码', toUserName=chat_room['UserName'])


def close_game():
	print('收盘')
	if chat_rooms:
		for chat_room in chat_rooms:
			itchat.send('收盘时间， 停止打码', toUserName=chat_room['UserName'])

	delay_run(60, show_answer)


def show_answer():
	print('开奖')
	result = fetch.query_answer()  # None or {'number', 'no', 'day_no'}
	if result:
		result = result['number']
	if chat_rooms:
		for chat_room in chat_rooms:
			itchat.send('本期开奖结果：%s' % result, toUserName=chat_room['UserName'])


def delay_run(delay_time, func, *args):
	schedule = sched.scheduler()
	schedule.enter(delay_time, 0, func, *args)
	schedule.run()


def get_time():
	delay_second = None
	current_second = int(time.time()) - 10  # 提前10秒获取
	current_second %= 86400

	if (2 * 3600) <= current_second <= (14 * 3600):  # 10:00 - 22:00
		delay_second = 360
	elif (14 * 3600) < current_second < (18 * 3600):  # 22:00 - 02:00
		delay_second = 180
	return delay_second



itchat.auto_login(hotReload=True)
itchat.run()
