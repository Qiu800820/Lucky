#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os
import threading

from Bot.core.db.bot_dao import *
from Bot.core.fetch import *
from Bot.core.mock_itchat import itchat

isReceived = False
BossUserName = None
chat_rooms = None
fetch = Fetch()
last_answer_no = None

close_game_img = os.path.join(os.path.dirname(__file__), '../resource/close_game.png')
open_game_img = os.path.join(os.path.dirname(__file__), '../resource/open_game.png')
# 读取配置
path = os.path.join(os.path.dirname(__file__), '../resource/config.json')
config = open(path, 'r', -1, 'utf-8').read()
config = json.loads(config)

chatRoomName = config['chatRoomName']
BossName = config['BossName']
preview_time = config['preview_time']  # 提前60秒收盘
answer_refresh_time = config['answer_refresh_time']
# 译码服务
# translate = Translate(config['translate_server'], config['translate_param'])
itchat = itchat()


# @itchat.msg_register(TEXT, isGroupChat=True)
def received(msg):
	if not isReceived and not msg['isAt']:
		return None
	content = msg['Content'].split('\u2005')
	if len(content) > 1:
		content = content[1]
	else:
		return None
	print(msg)

	validity, number_array, message = (True, [{'number': '1XX2', 'money': 1}], '')  # translate.prepare(content)
	if not isReceived:
		return None
	current_no = get_day_no(preview_time) + 1
	message_no = get_day_no(preview_time, msg['CreateTime']) + 1
	if current_no != message_no:
		validity = False
		message = '超过有效时间'
	if validity:  # 译码结果
		validity, message = save_user_number(  # 保存
			number_array,
			msg['ActualNickName'],
			msg['MsgId'],
			message_no,
			content
		)
	if validity:
		return "用户'%s' -- xx成功" % msg['ActualNickName']  # 回复打码成功
	else:
		return "用户'%s' -- xx失败，原因：%s" % (msg['ActualNickName'], message)


# @itchat.msg_register(TEXT)
def command(msg):
	global isReceived
	if not msg['FromUserName'] == get_boss_user_name():
		return None
	print(msg)
	if '开始' in msg['Content'] and not isReceived:
		isReceived = True
		run_threaded(None, open_game)
		run_threaded(None, show_answer)
	elif '停止' in msg['Content']:
		isReceived = False
		close_game()
	elif '上分' in msg['Content']:  # 上分|名字|5000
		action, user_name, number = parser(msg['Content'])
		message = add_user_money(user_name, number, action, msg['MsgId'])
		return message
	elif '清算' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		message = clear_user(user_name, msg['MsgId'])
		return message
	elif '查询积分' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		message = query_user(user_name)
		return message
	else:
		return '支持命令:\n开始\n停止\n上分|张三|1000\n清算|张三\n查询|张三'


def open_game():
	if not isReceived:
		return
	print('开始游戏')
	global chat_rooms
	chat_rooms = itchat.search_chatrooms(name=chatRoomName)
	no = get_day_no(preview_time) + 1
	for chat_room in chat_rooms:
		itchat.send('%s.. 开始' % no, toUserName=chat_room['UserName'])  # todo 附加提示
		itchat.send_image(open_game_img, toUserName=chat_room['UserName'])
	# 自动计算时间
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
	print('停止游戏')
	no = get_day_no() + 1
	if chat_rooms:
		for chat_room in chat_rooms:
			itchat.send('%s.. 停止' % no, toUserName=chat_room['UserName'])
			itchat.send_image(close_game_img, toUserName=chat_room['UserName'])
	if isReceived:
		# 10秒后开启下期
		delay_run(10, open_game)


def show_answer():
	if not isReceived:
		return
	global last_answer_no
	print('公布结果')
	result = fetch.query_answer()  # None or {'number', 'no', 'day_no'}
	if result and chat_rooms and last_answer_no != result['day_no']:
		last_answer_no = result['day_no']
		for chat_room in chat_rooms:
			itchat.send('%s.. %s' % (result['day_no'], result['number']), toUserName=chat_room['UserName'])
		# 结算服务
		# 汇报
	delay_run(answer_refresh_time, show_answer)  # 每段时间更新一次开奖结果


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


def parser(message):
	params = message.split('|')
	params_len = len(params)
	action, user_name, number = (None, None, None)
	if params_len > 0:
		action = params[0]
	if params_len > 1:
		user_name = params[1]
	if params_len > 2:
		number = params[2]
	return action, user_name, number


def run_threaded(delay_time, func):
	job_thread = threading.Thread(target=delay_run, args=(delay_time, func))
	job_thread.start()


def run():
	itchat.auto_login(hotReload=True)
	itchat.mock_run(received=received, command=command)
