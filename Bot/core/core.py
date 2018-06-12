#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import re
import threading
import time

import itchat
from itchat import msg_register
from itchat.content import *

from Bot.core import util
from Bot.core.config import Config
from Bot.core.db.bot_dao import BotDao
from Bot.core.fetch import Fetch
from Bot.core.log import Log
from Bot.core.translate import Translate

isReceived = False
isOpenGame = False
BossUserNameList = None
chat_room_name_list = None
last_answer_no = None
log = Log()
# 开奖服务
fetch = Fetch()
# 重要配置
config = Config()
# 译码服务
translate = Translate(config)
# DAO 服务
botDao = BotDao(config.odds, log)


@msg_register(TEXT, isGroupChat=False)  # 私聊打码
def private_chat(msg):
	try:
		if '识别码' in msg['Content']:
			message = set_alias(msg)
		elif msg['FromUserName'] in get_boss_user_name():
			message = command(msg)
		else:
			message = received(msg)
	except Exception:
		log.error('private_chat', exc_info=True)
		message = None
	return message


@msg_register(TEXT, isGroupChat=True)  # 打码
def group_chat(msg):
	try:
		message = received(msg)
	except Exception:
		log.error('group_chat', exc_info=True)
		message = None
	return message


def received(msg):  # TODO 部分账户无法获取User字段
	log.debug('received ->> message:%s', msg)
	if not isReceived:
		return None
	if not isOpenGame:
		log.warning('已停止')
		return add_random_chat('已停止')
	content, create_time, actual_nick_name, nick_name, msg_id = util.prepare_message_params(msg)
	if not nick_name:
		if msg['FromUserName'] in chat_room_name_list:
			log.debug('群内不支持打码，请加我好友私聊')
			return add_random_chat('群内不支持打码，请加我好友私聊')
		log.debug('非自动群、打码消息，直接忽略')
		return None
	validity, number_array, message = translate.prepare(content)
	if not isReceived:
		log.warning('控制者已停止程序')
		return None
	current_no = fetch.get_day_no(config.preview_time) + 1
	message_no = fetch.get_day_no(config.preview_time, create_time) + 1
	if current_no != message_no or not isOpenGame:
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
	if validity:  # 保存成功
		validity, message = translate.post_number(number_array)
	if validity:
		reply_message = "用户'%s' -- %sxx成功" % (actual_nick_name, message_no)
		log.debug('received <<- message:%s', reply_message)
		return add_random_chat(reply_message)  # 回复打码成功
	elif '重复订单' in message:
		log.warning('用户重复订单, 如果是重新登陆导致的请忽略')
		return None
	reply_message = "用户'%s' -- xx失败，原因：%s" % (actual_nick_name, message)
	log.debug('received <<- message:%s', reply_message)
	return add_random_chat(reply_message)


@msg_register(FRIENDS)
def add_friend(msg):
	try:
		log.debug('add_friend ->> message:%s', msg)
		msg.user.verify()
		msg.user.send('请告诉我你的识别码，以辨别你的身份!(识别码由财务提供)')
	except Exception:
		log.error('group_chat', exc_info=True)


def set_alias(msg):
	log.debug('set_alias ->> msg:%s' % msg)
	check_code = re.search(r'[0-9]+', msg['Content']).group()
	if len(check_code) > 6:
		user_id = check_code[6:]
		code = check_code[0:6]
		user_name = botDao.get_user_name(user_id, code)
		if user_name:
			itchat.set_alias(msg['FromUserName'], user_name)
			message = '识别成功'
		else:
			message = '识别码错误'
	else:
		message = '识别码格式错误'
	log.debug('set_alias <<- message:%s' % message)
	return message


def command(msg):
	global isReceived
	log.debug('command ->> msg: %s' % msg)
	if '开始' in msg['Content'] and not isReceived:
		log.debug('command ->> 开始')
		isReceived = True
		run_threaded(None, open_game)
		run_threaded(None, show_answer)
	elif '停止' in msg['Content']:
		log.debug('command ->> 停止')
		isReceived = False
		close_game()
	elif '上分' in msg['Content']:  # 上分|名字|5000
		action, user_name, number = parser(msg['Content'])
		log.debug('command ->> 上分 user_name:%s, number:%s', user_name, number)
		message = botDao.add_user_money(user_name, float(number), action, msg['MsgId'])
		log.debug('command ->> message:%s', message)
		return add_random_chat(message)
	elif '清算' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		log.debug('command ->> 清算 user_name:%s', user_name)
		message = botDao.clear_user(user_name, msg['MsgId'])
		log.debug('command ->> message:%s', message)
		return add_random_chat(message)
	elif '查询' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		log.debug('command ->> 查询 user_name:%s', user_name)
		message = botDao.query_user(user_name)
		log.debug('command ->> message:剩余积分%s', message)
		return add_random_chat('剩余积分%s' % message)
	elif '打码' in msg['Content']:
		_, user_name, number = parser(msg['Content'])
		log.debug('command ->> 打码 user_name:%s number:%s', user_name, number)
		msg['User']['RemarkName'] = user_name
		msg['User']['NickName'] = user_name
		return received(msg)
	else:
		return add_random_chat('支持命令:\n开始\n停止\n上分|张三|1000\n清算|张三\n查询|张三')


def open_game():
	if not isReceived:
		return
	log.info('开始游戏')
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
	nick_name_list = []
	chat_room_list = itchat.search_chatrooms(name=config.chatRoomName)
	if not chat_room_list or len(chat_room_list) == 0:
		log.warning('警告：没有搜索到相关群信息！！！！！！！！！！！！！')
	else:
		for chat_room in chat_room_list:
			name_list.append(chat_room['UserName'])
			nick_name_list.append(chat_room['NickName'])
		log.info('自动群：%s', nick_name_list)

	return name_list


def close_hint():
	log.info('倒计时')
	no = fetch.get_day_no() + 1
	if chat_room_name_list:
		for chat_room in chat_room_name_list:
			itchat.send('%s.. 倒计时30秒' % no, toUserName=chat_room)
	if isReceived:
		delay_run(30, close_game)


def close_game():
	log.info('停止游戏')
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
	result, history_result = fetch.query_answer()  # None or {'number', 'no', 'day_no'}
	if result and chat_room_name_list and last_answer_no != result['no']:
		last_answer_no = result['no']
		log.info('公布结果%s', last_answer_no)
		message = util.format_history_message(history_result)
		log.debug('show_answer ->> message: %s', message)
		for chat_room in chat_room_name_list:
			itchat.send(message, toUserName=chat_room)
		botDao.accounting(result['no'], result['number'])
	delay_run(config.answer_refresh_time, show_answer)  # 每段时间更新一次开奖结果


def get_boss_user_name(refresh=False):
	log.debug('get_boss_user_name ->>')
	global BossUserNameList
	if not BossUserNameList or refresh:
		BossUserNameList = []
		friends = itchat.search_friends(name=config.BossName)
		if not friends or len(friends) == 0:
			log.warning('警告：没有搜索到控制者！！！！！！！！！！！！！')
		else:
			log.debug('控制者: %s', friends)
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
	log.debug('get_time <<- delay_second:%s', delay_second)
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


def add_random_chat(msg):
	random_chat = config.chats[int(random.random() * len(config.chats))]
	return '%s%s%s' % (msg, random_chat, random_chat)


def run_threaded(delay_time, func):
	job_thread = threading.Thread(target=delay_run, args=(delay_time, func))
	job_thread.start()


def run():
	itchat.auto_login()
	botDao.review(fetch)  # 对账
	# itchat.run(private_chat, group_chat, add_friend) mock 测试
	itchat.run()




