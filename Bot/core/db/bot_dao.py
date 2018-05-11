#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Bot.core.db import sqlite_db


class OrderObject(sqlite_db.Table):
	def __init__(self):
		super(OrderObject, self).__init__("./resouce/bot.db", "order", [
			'number TEXT', 'user TEXT', 'user_name TEXT', 'money NUMBER', 'no TEXT', 'number_abb TEXT'
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


class UserObject(sqlite_db.Table):
	def __init__(self):
		super(UserObject, self).__init__("./resouce/bot.db", "user", [
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
		cursor = self.read('select * from user where user_name = ?' % user_name)
		users = cursor.fetchall()
		self.free(cursor)
		if users and len(users) > 0:
			user = users[0]
			return {'user_id': user[0], 'user_name': user[1], 'money': user[2]}
		return None

	def add_user_money(self, user_name, money):  # 用户名称存在重复 todo
		user = self.get_user(user_name=user_name)
		if user:
			money = user['money'] + money
			self.update({'money': money}, user_name=user_name)
		else:
			self.insert('None', user_name, money)
		self.commit()

orderDao = OrderObject()
userDao = UserObject()


def save_user_number(number_array, user, no, number_abb):
	if not (number_array and user and no and number_abb):
		return False, '信息有误'

	else:
		user = userDao.get_user(user['userName'])
		consume = 0
		for number in number_array:
			orderDao.insert(number['number'], user['userId'], user['userName'], number['money'], no, number_abb)
			consume += number
		if not user or user['money'] < consume:
			orderDao.rollback()
			return False, '余额不足，请充值'
		else:
			orderDao.commit()
			userDao.add_user_money(user['userName'], consume)
			return True, '下单成功'
