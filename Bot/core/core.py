#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import re
import threading
import time

import itchat
from itchat.content import *

from Bot.core.config import Config
from Bot.core.db.bot_dao import BotDao
from Bot.core.fetch import Fetch
from Bot.core.translate import Translate
from Bot.core.util import prepare_message_params

isReceived = False
isOpenGame = False
BossUserNameList = None
chat_room_name_list = None
last_answer_no = None
# 开奖服务
fetch = Fetch()
# 重要配置
config = Config()
# 译码服务
translate = Translate(config.translate_server, config.translate_param)
# DAO 服务
botDao = BotDao(config.odds)


@itchat.msg_register(TEXT, isGroupChat=False)  # 私聊打码
def private_chat(msg):
	if '识别码' in msg['Content']:
		return set_alias(msg)
	elif msg['FromUserName'] in get_boss_user_name():
		return command(msg)
	return received(msg)


@itchat.msg_register(TEXT, isGroupChat=True)  # 打码
def group_chat(msg):
	return received(msg)


def received(msg):  # TODO 群好友昵称问题
	if not isReceived:
		return None
	if not isOpenGame:
		return add_random_chat('已停止')
	print(msg)
	content, create_time, actual_nick_name, nick_name, msg_id = prepare_message_params(msg)
	if not nick_name:
		if msg['ToUserName'] in chat_room_name_list:
			return add_random_chat('群内不支持打码，请加我好友私聊')
		print('非自动群、打码消息，直接忽略')
		return None
	validity, number_array, message = translate.prepare(content)
	if not isReceived:
		print('控制者已停止程序')
		return None
	current_no = fetch.get_day_no(config.preview_time) + 1
	message_no = fetch.get_day_no(config.preview_time, create_time) + 1
	if current_no != message_no:
		validity = False
		message = '超过有效时间'
	if validity:  # 译码结果
		validity, message = botDao.save_user_number(  # 保存
			number_array,
			nick_name,
			msg_id,
			message_no,
			content
		)
	if validity:
		return add_random_chat("用户'%s' -- xx成功" % actual_nick_name)  # 回复打码成功
	elif '重复订单' in message:
		print('用户重复订单, 如果是重新登陆导致的请忽略')
		return None
	return add_random_chat("用户'%s' -- xx失败，原因：%s" % (actual_nick_name, message))


@itchat.msg_register(FRIENDS)
def add_friend(msg):
	msg.user.verify()
	msg.user.send('请告诉我你的识别码，以辨别你的身份!(识别码由财务提供)')


def set_alias(msg):
	check_code = re.search(r'[0-9]+', msg['Content']).group()
	if len(check_code) > 6:
		user_id = check_code[6:]
		code = check_code[0:6]
		user_name = botDao.get_user_name(user_id, code)
		if user_name:
			itchat.set_alias(msg['FromUserName'], user_name)
			return '识别成功'
		else:
			return '识别码错误'
	else:
		return '识别码格式错误'


def command(msg):
	global isReceived
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
		message = botDao.add_user_money(user_name, number, action, msg['MsgId'])
		return add_random_chat(message)
	elif '清算' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		message = botDao.clear_user(user_name, msg['MsgId'])
		return add_random_chat(message)
	elif '查询' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		message = botDao.query_user(user_name)
		return add_random_chat('剩余积分%s' % message)
	else:
		return add_random_chat('支持命令:\n开始\n停止\n上分|张三|1000\n清算|张三\n查询|张三')


def open_game():
	if not isReceived:
		return
	print('开始游戏')
	global isOpenGame, chat_room_name_list
	chat_room_name_list = get_chat_room_name_list()
	isOpenGame = True
	no = fetch.get_day_no(config.preview_time) + 1
	for chat_room in chat_room_name_list:
		itchat.send('%s.. 开始, %s' % (no, config.begin_game_hint), toUserName=chat_room)
	# 自动计算时间
	delay_run(get_time(), close_hint)


def get_chat_room_name_list():
	name_list = []
	chat_room_list = itchat.search_chatrooms(name=config.chatRoomName)
	if not chat_room_list or len(chat_room_list) == 0:
		print('警告：没有搜索到相关群信息！！！！！！！！！！！！！')
	else:
		for chat_room in chat_room_list:
			name_list.append(chat_room['UserName'])
	return name_list


def close_hint():
	print('倒计时')
	no = fetch.get_day_no() + 1
	if chat_room_name_list:
		for chat_room in chat_room_name_list:
			itchat.send('%s.. 倒计时30秒' % no, toUserName=chat_room)
	if isReceived:
		delay_run(30, close_game)


def close_game():
	print('停止游戏')
	global isOpenGame
	isOpenGame = False
	no = fetch.get_day_no() + 1
	if chat_room_name_list:
		for chat_room in chat_room_name_list:
			itchat.send('%s.. 停止' % no, toUserName=chat_room)
	if isReceived:
		# 10秒后开启下期
		delay_run(30, open_game)


def show_answer():
	if not isReceived:
		return
	global last_answer_no
	print('公布结果')
	result = fetch.query_answer()  # None or {'number', 'no', 'day_no'}
	if result and chat_room_name_list and last_answer_no != result['day_no']:
		last_answer_no = result['day_no']
		for chat_room in chat_room_name_list:
			itchat.send('%s.. %s' % (result['day_no'], result['number']), toUserName=chat_room)
		botDao.accounting(result['day_no'], result['number'])
	delay_run(config.answer_refresh_time, show_answer)  # 每段时间更新一次开奖结果


def get_boss_user_name():
	global BossUserNameList
	if not BossUserNameList:
		BossUserNameList = []
		friends = itchat.search_friends(name=config.BossName)
		if not friends or len(friends) == 0:
			print('警告：没有搜索到控制者！！！！！！！！！！！！！')
		for friend in friends:
			BossUserNameList.append(friend['UserName'])

	return BossUserNameList


def delay_run(delay_time, func):
	if delay_time and delay_time > 1:
		time.sleep(delay_time)
	func()


def get_time():
	current_second = int(time.time()) + config.preview_time + 30
	current_second %= 86400

	if (2 * 3600) <= current_second <= (14 * 3600):  # 10:00 - 22:00
		delay_second = 600 - (current_second % 600)
	elif (14 * 3600) < current_second < (18 * 3600):  # 22:00 - 02:00
		delay_second = 300 - (current_second % 300)
	else:
		delay_second = ((26 * 3600) - current_second) % 86400  # 10:00 时间差

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
		number = float(params[2])
	return action, user_name, number


def add_random_chat(msg):
	random_chat = config.chats[int(random.random() * len(config.chats))]
	return '%s%s%s' % (msg, random_chat, random_chat)


def run_threaded(delay_time, func):
	job_thread = threading.Thread(target=delay_run, args=(delay_time, func))
	job_thread.start()


def run():
	itchat.auto_login()
	# 初始化配置
	botDao.review(fetch)  # 对账
	itchat.run()
