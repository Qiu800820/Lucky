#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Bot.core.db import sqlite_db


class OrderObject(sqlite_db.Table):
	def __init__(self):
		super(OrderObject, self).__init__("./resource/bot.db", "OddsOrder", [
			'number TEXT', 'message_id TEXT', 'user_name TEXT', 'money NUMBER', 'no TEXT', 'number_abb TEXT'
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

	def get_all_by_no(self, no):
		cursor = self.select('number', 'user_name', 'money', order_by=None, no=int(no))
		result = []
		order = cursor.fetchone()
		while order:
			result.append({'number': order[0], 'user_name': order[1], 'money': order[2]})
			order = cursor.fetchone()
		self.free(cursor)
		return result


class UserObject(sqlite_db.Table):
	def __init__(self):
		super(UserObject, self).__init__("./resource/bot.db", "user", [
			'user_id TEXT', 'user_name TEXT', 'money NUMBER'
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
			return {'user_id': user[0], 'user_name': user[1], 'money': user[2]}
		return None

	def add_user_money(self, user_name, money):
		user = self.get_user(user_name=user_name)
		if user:
			money = user['money'] + money
			self.update({'money': money}, user_name=user_name)
		else:
			self.insert('None', user_name, money)
		self.commit()

	def clear_user(self, user_name):
		if user_name:
			self.update({'money': 0}, user_name=user_name)
			self.commit()
			return True
		else:
			return False


orderDao = OrderObject()
userDao = UserObject()


def save_user_number(number_array, user_name, message_id, no, number_abb):
	if not (number_array and user_name and message_id and no and number_abb):
		return False, '信息有误'

	else:
		user = userDao.get_user(user_name)
		consume = 0
		for number in number_array:
			orderDao.insert(number['number'], message_id, user_name, number['money'], no, number_abb)
			consume += number['money']
		if not user or user['money'] < consume:
			orderDao.rollback()
			return False, '余额不足，请充值'
		else:
			orderDao.commit()
			add_user_money(user_name, (0 - consume), '下单', message_id)
			return True, '下单成功'


def add_user_money(user_name, money, source, message_id, number='', answer_no=''):
	if not (user_name and money):
		return '用户或金额数据错误'
	userDao.add_user_money(user_name, money)
	orderDao.insert(number, message_id, user_name, money, answer_no, source)
	orderDao.commit()
	return '上分成功'


def clear_user(user_name, message_id):
	if not user_name:
		return '缺少用户参数'
	userDao.clear_user(user_name)
	orderDao.insert('', message_id, user_name, 0, '', '清算')
	orderDao.commit()
	return '清算%s成功' % user_name


def query_user(user_name):
	if not user_name:
		return '缺少用户参数'
	cursor = userDao.select('money', order_by=None, user_name=user_name)
	result = cursor.fetchone()
	if result and len(result) > 0:
		result = result[0]
	else:
		result = '0'
	cursor.close()
	return result


def settlement(no, answer):
	bingo_map = {}
	order_list = orderDao.get_all_by_no(no)
	if order_list:
		for order in order_list:
			bingo_odds = get_bingo_odds(answer, order['number'])
			if bingo_odds > 0:
				user_name = order['user_name']
				bingo_money = order['money'] * bingo_odds
				bingo_map.setdefault(user_name, bingo_map.get(user_name, 0) + bingo_money)
		if len(bingo_map) > 0:
			for k in bingo_map:
				add_user_money(k, bingo_map.get(k), '中奖', '', number='[%s]' % answer, answer_no=no)
		else:
			print('本期没有人中奖')
	else:
		print('本期没有下单记录')


def get_bingo_odds(answer, user_number):
	size = 4
	answer = answer[1:]  # 只取4位
	money = 10000  # 中奖比例
	if len(answer) == len(user_number):
		for i in range(size):
			if user_number[i] == 'X':
				money /= 10
			elif user_number[i] != answer[i]:
				money = 0
				break
	return money
