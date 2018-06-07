#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import time

from Bot.core.config import default_odds
from Bot.core.db import sqlite_db


class OrderObject(sqlite_db.Table):
	def __init__(self):
		super(OrderObject, self).__init__("./resource/bot.db", "OddsOrder", [
			'number TEXT', 'message_id TEXT', 'user_name TEXT', 'money NUMBER', 'no TEXT', 'number_abb TEXT',
			'type NUMBER', 'accounting NUMBER', 'create_time TEXT'
		])

	def insert(self, *args):
		self.free(super(OrderObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(OrderObject, self).update(set_args, **kwargs))

	def delete(self, **kwargs):
		self.free(super(OrderObject, self).delete(**kwargs))

	def delete_all(self, **kwargs):
		self.free(super(OrderObject, self).delete_all())

	def drop(self):
		self.free(super(OrderObject, self).drop())

	def replace(self, *args):
		self.free(super(OrderObject, self).replace(*args))

	def get_all_accounting_by_no(self, no):
		cursor = self.select(
			'number', 'user_name', 'money', 'message_id',
			order_by=None, no=no, type=1, accounting=1
		)
		result = []
		order = cursor.fetchone()
		while order:
			result.append({'number': order[0], 'user_name': order[1], 'money': order[2], 'message_id': order[3]})
			order = cursor.fetchone()
		self.free(cursor)
		return result

	def get_missed_no(self):
		cursor = self.read('select distinct(no) from OddsOrder where type = ? and accounting = ?', [1, 1])
		result = []
		order = cursor.fetchone()
		while order:
			result.append(order[0])
			order = cursor.fetchone()
		self.free(cursor)
		return result

	def has_message_id(self, message_id):
		has = False
		cursor = self.select('message_id', order_by=None, message_id=message_id)
		result = cursor.fetchone()
		if result:
			has = True
		self.free(cursor)
		return has


class UserObject(sqlite_db.Table):
	def __init__(self):
		super(UserObject, self).__init__("./resource/bot.db", "user", [
			'user_id INTEGER PRIMARY KEY AUTOINCREMENT', 'user_name TEXT', 'money NUMBER', 'code TEXT'
		])

	def insert(self, *args):
		self.free(super(UserObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(UserObject, self).update(set_args, **kwargs))

	def delete(self, **kwargs):
		self.free(super(UserObject, self).delete(**kwargs))

	def delete_all(self, **kwargs):
		self.free(super(UserObject, self).delete_all())

	def drop(self):
		self.free(super(UserObject, self).drop())

	def replace(self, *args):
		self.free(super(UserObject, self).replace(*args))

	def get_user(self, user_name):
		cursor = self.read('select * from user where user_name = ?', [user_name])
		users = cursor.fetchall()
		self.free(cursor)
		if users and len(users) > 0:
			user = users[0]
			return {'user_id': user[0], 'user_name': user[1], 'money': user[2], 'code': user[3]}
		return None

	def get_user_by_code(self, user_id, code):
		cursor = self.read('select * from user where user_id = ? and code = ?', [user_id, code])
		users = cursor.fetchall()
		self.free(cursor)
		if users and len(users) > 0:
			user = users[0]
			return {'user_id': user[0], 'user_name': user[1], 'money': user[2], 'code': user[3]}
		return None

	def add_user_money(self, user_name, money):
		user = self.get_user(user_name=user_name)
		code = None
		if user:
			user['money'] = user['money'] + money
			self.update({'money': user['money']}, user_name=user_name)
		else:
			code = random.randint(100000, 999999)
			self.insert(None, user_name, money, code)
		self.commit()
		if code:
			user = self.get_user(user_name)
		return user

	def clear_user(self, user_name):
		if user_name:
			self.update({'money': 0}, user_name=user_name)
			self.commit()
			return True
		else:
			return False


class BotDao:

	def __init__(self, odds_config, log):
		self.orderDao = OrderObject()
		self.userDao = UserObject()
		if not odds_config or len(odds_config) != 4:
			odds_config = default_odds
		self.odds_config = odds_config
		self.log = log

	def save_user_number(self, number_array, user_name, message_id, no, number_abb):
		self.log.debug(
			'save_user_number ->> number_array:%s, user_name:%s, message_id:%s, no:%s, number_abb:%s',
			number_array, user_name, message_id, no, number_abb
		)
		if not (number_array and user_name and message_id and no and number_abb):
			return False, '信息有误'
		if self.orderDao.has_message_id(message_id):
			return False, '重复订单'
		else:
			user = self.userDao.get_user(user_name)
			consume = 0
			date_str = time.strftime('%F')
			for number in number_array:
				self.orderDao.insert(number['number'], message_id, user_name, number['money'], no, number_abb, 1, 1, date_str)
				consume += number['money']
			if not user or user['money'] < consume:
				self.orderDao.rollback()
				return False, '账号不存在或金额不足，请联系财务'
			else:
				self.orderDao.commit()
				self.add_user_money(user_name, (0 - consume), '下单', message_id)
				return True, '下单成功'

	def add_user_money(self, user_name, money, source, message_id, number='', answer_no=''):
		self.log.debug(
			'add_user_money ->> user_name:%s, money:%s, source:%s, message_id:%s, number:%s, answer_no:%s',
			user_name, money, source, message_id, number, answer_no
		)
		if not (user_name and money):
			return '用户或金额数据错误'
		user = self.userDao.add_user_money(user_name, money)
		self.orderDao.insert(number, message_id, user_name, money, answer_no, source, 0, 0, time.strftime("%F"))
		self.orderDao.commit()
		message = '上分成功, 识别码:%s%s 第一次下单的用户 需要先把识别码发给机器人' % (user['code'], user['user_id'])
		return message

	def get_user_name(self, user_id, code):
		self.log.debug(
			'get_user_name ->> user_id:%s, code:%s',
			user_id, code
		)
		user = self.userDao.get_user_by_code(user_id, code)
		user_name = None
		if user:
			user_name = user.get('user_name')
		self.log.debug('get_user_name <<- user_name:%s', user_name)

		return user_name

	def clear_user(self, user_name, message_id):
		self.log.debug(
			'clear_user ->> user_name:%s, message_id:%s',
			user_name, message_id
		)
		if not user_name:
			return '缺少用户参数'
		self.userDao.clear_user(user_name)
		self.orderDao.insert('', message_id, user_name, 0, '', '清算', 0, 0, time.strftime("%F"))
		self.orderDao.commit()
		return '清算%s成功' % user_name

	def query_user(self, user_name):
		self.log.debug('query_user ->> user_name:%s', user_name)
		if not user_name:
			return '缺少用户参数'
		cursor = self.userDao.select('money', order_by=None, user_name=user_name)
		result = cursor.fetchone()
		if result and len(result) > 0:
			result = result[0]
		else:
			result = '0'
		cursor.close()
		self.log.debug('query_user <<- result:%s', result)
		return result

	def review(self, fetch):
		self.log.debug('review ->>')
		no_list = self.orderDao.get_missed_no()
		self.log.debug('review ->> no_list: %s', no_list)
		for no in no_list:
			answer = fetch.query_answer(no)
			self.log.debug('review ->> answer: %s', answer)
			self.accounting(no, answer)

	def accounting(self, no, answer):
		self.log.debug('accounting ->> no:%s, answer:%s', no, answer)
		bingo_map = {}
		cost_map = {}
		accounting_message_id_map = {}
		order_list = self.orderDao.get_all_accounting_by_no(no)
		if order_list:
			for order in order_list:
				bingo_odds = self.get_bingo_odds(answer, order['number'])
				user_name = order['user_name']
				if bingo_odds > 0:
					bingo_money = order['money'] * bingo_odds
					count_money = bingo_map.get(user_name, 0) + bingo_money
					bingo_map.setdefault(user_name, count_money)
					bingo_map[user_name] = count_money
				cost = cost_map.get(user_name, 0) + order['money']
				cost_map.setdefault(user_name, cost)
				cost_map[user_name] = cost
				accounting_message_id_map.setdefault(order['message_id'], 1)
			if len(bingo_map) > 0:
				count = 0
				for k in bingo_map:
					self.add_user_money(k, bingo_map.get(k), '中奖', '', number='[%s]' % answer, answer_no=no)
					cost = cost_map.get(k)
					bingo = bingo_map.get(k)
					count += (cost - bingo)
					self.log.info('%s.. 打%s.. 中%s.. 赚%s' % (k, cost, bingo, cost - bingo))
					self.log.info('总盈亏%s' % count)
			else:
				self.log.info('本期%s没有人中奖' % no)

			if len(accounting_message_id_map) > 0:  # 修改状态
				for message_id in accounting_message_id_map:
					self.orderDao.update({'accounting': 0}, message_id=message_id)
				self.orderDao.commit()
		else:
			self.log.info('本期%s没有下单记录' % no)

	def get_bingo_odds(self, answer, user_number):
		answer = answer.replace(' ', '')
		size = 4
		answer = answer[1:]  # 只取4位
		odds_index = 0
		odds = self.odds_config[odds_index]  # 中奖比例
		if len(answer) == len(user_number):
			for i in range(size):
				if user_number[i] == 'X':
					odds_index += 1
					odds = self.odds_config[odds_index]
				elif user_number[i] != answer[i]:
					odds = 0
					break
		else:
			odds = 0
			self.log.warning('警告， 开奖号码长度有误')
		return odds
