#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os
import threading

import itchat
from itchat.content import *

from Bot.core.fetch import *

isReceived = False
BossUserName = None
chat_rooms = None
fetch = Fetch()
last_answer_no = None

close_game_img = os.path.join(os.path.dirname(__file__), '../resource/close_game.png')
open_game_img = os.path.join(os.path.dirname(__file__), '../resource/open_game.png')

path = os.path.join(os.path.dirname(__file__), '../resource/config.json')
config = open(path, 'r', -1, 'utf-8').read()
config = json.loads(config)

chatRoomName = config['chatRoomName']
BossName = config['BossName']
preview_time = config['preview_time']  # 提前60秒收盘
answer_refresh_time = config['answer_refresh_time']


@itchat.msg_register(TEXT, isGroupChat=True)
def received(msg):
	if not isReceived and not msg['isAt']:
		return None
	print(msg)
	# 译码
	if isReceived:  # 打码结果
		# 保存
		# 回复打码成功
		return "用户'%s'打码成功" % msg['ActualNickName']
	else:
		return "， 用户'%s'打码失败" % msg['ActualNickName']


@itchat.msg_register(TEXT)
def command(msg):
	global isReceived
	if not msg['FromUserName'] == get_boss_user_name():
		return None
	print(msg)
	if '开始' in msg['Content']:
		isReceived = True
		run_threaded(None, open_game)
		run_threaded(None, show_answer)
	elif '停止' in msg['Content']:
		isReceived = False
		close_game()



def open_game():
	if not isReceived:
		return
	print('开盘')
	global chat_rooms
	chat_rooms = itchat.search_chatrooms(name=chatRoomName)
	no = get_day_no(preview_time) + 1
	for chat_room in chat_rooms:
		itchat.send('%s.. 开始 \n财务请加:%s' % (no, ), toUserName=chat_room['UserName'])
		itchat.send_image(open_game_img, toUserName=chat_room['UserName'])
	# 自动计算收盘时间
	delay_run(get_time(), close_hint)


def close_hint():
	print('倒计时')
	no = get_day_no() + 1
	if chat_rooms:
		for chat_room in chat_rooms:
			itchat.send('%s.. 倒计时30秒' % no, toUserName=chat_room['UserName'])
			itchat.send_image(close_game_img, toUserName=chat_room['UserName'])
	if isReceived:
		delay_run(30, close_game)


def close_game():
	print('收盘')
	no = get_day_no() + 1
	if chat_rooms:
		for chat_room in chat_rooms:
			itchat.send('%s.. 停止' % no, toUserName=chat_room['UserName'])
			itchat.send_image(close_game_img, toUserName=chat_room['UserName'])
	if isReceived:
		# 10秒后开启下期盘口
		delay_run(10, open_game)


def show_answer():
	if not isReceived:
		return
	global last_answer_no
	print('开奖')
	result = fetch.query_answer()  # None or {'number', 'no', 'day_no'}
	if result and chat_rooms and last_answer_no != result['day_no']:
		last_answer_no = result['day_no']
		for chat_room in chat_rooms:
			itchat.send('%s.. %s' % (result['day_no'], result['number']), toUserName=chat_room['UserName'])
	delay_run(answer_refresh_time, show_answer)  # 每分钟更新一次开奖结果


def get_boss_user_name():
	global BossUserName
	if not BossUserName:
		friends = itchat.search_friends(name=BossName)
		for friend in friends:
			BossUserName = friend['UserName']
			break

	return BossUserName


def delay_run(delay_time, func):
	if delay_time and delay_time > 1:
		time.sleep(delay_time)
	func()


def get_time():
	current_second = int(time.time()) + preview_time - 30
	current_second %= 86400

	if (2 * 3600) <= current_second <= (14 * 3600):  # 10:00 - 22:00
		delay_second = 600 - (current_second % 600)
	elif (14 * 3600) < current_second < (18 * 3600):  # 22:00 - 02:00
		delay_second = 300 - (current_second % 300)
	else:
		delay_second = ((26 * 3600) - current_second) % 86400  # 10:00 时间差

	print("delay_second : %s" % delay_second)
	return delay_second


def run_threaded(delay_time, func):
	job_thread = threading.Thread(target=delay_run, args=(delay_time, func))
	job_thread.start()


def run():
	itchat.auto_login(hotReload=True)
	itchat.run()



