#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os

from db import sqlite_db


class AnswerObject(sqlite_db.Table):
	def __init__(self):
		super(AnswerObject, self).__init__("./resouce/ssc.db", "answer", ['no TEXT PRIMARY KEY', 'number TEXT', 'day_no TEXT'])

	def insert(self, *args):
		self.free(super(AnswerObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(AnswerObject, self).update(set_args, **kwargs))

	def delete(self, **kwargs):
		self.free(super(AnswerObject, self).delete(**kwargs))

	def delete_all(self, **kwargs):
		self.free(super(AnswerObject, self).delete_all())

	def drop(self):
		self.free(super(AnswerObject, self).drop())

	def replace(self, *args):
		self.free(super(AnswerObject, self).replace(*args))

	# 获取本地最新开奖记录
	def get_last_answer(self):
		cursor = self.select_all('*', order_by='no DESC')
		last_answer = cursor.fetchone()
		while last_answer:
			if last_answer[1]:  # 过滤空数据(未开奖)
				break
			else:
				last_answer = cursor.fetchone()
		self.free(cursor)
		if not last_answer:
			print('error : 本地服务中没有开奖记录， 请检查路径：%s 是否存在' % os.path.abspath("./resouce/ssc.db"))
		return {'no': last_answer[0], 'number': last_answer[1], 'day_no': last_answer[2]}

	# 获取本地某期后的开奖记录
	def get_new_answer(self, no, order_by='asc'):
		cursor = self.read('select * from answer where no > ? order by no %s' % order_by, [no])
		answer = cursor.fetchone()
		while answer:
			yield {'no': answer[0], 'number': answer[1], 'day_no': answer[2]}
			answer = cursor.fetchone()
		self.free(cursor)

	def diff_no(self, last_no, current_no):
		cursor = self.read("select count(*) as count from answer where no > ? and no < ? and number <> ''", [last_no, current_no])
		diff_no = cursor.fetchone()
		self.free(cursor)
		return diff_no[0]


class TwoStarObject(sqlite_db.Table):
	def __init__(self):
		super(TwoStarObject, self).__init__("./resouce/ssc.db", "TwoStar",
		                                    ["id TEXT PRIMARY KEY", "max_omit_number NUMERIC", "last_no TEXT"])

	def insert(self, *args):
		self.free(super(TwoStarObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(TwoStarObject, self).update(set_args, **kwargs))

	def delete(self, **kwargs):
		self.free(super(TwoStarObject, self).delete(**kwargs))

	def delete_all(self, **kwargs):
		self.free(super(TwoStarObject, self).delete_all())

	def drop(self):
		self.free(super(TwoStarObject, self).drop())

	def replace(self, *args):
		self.free(super(TwoStarObject, self).replace(*args))

	def get_all(self):
		cursor = self.select_all('*', order_by=None)
		two_star = cursor.fetchone()
		while two_star:
			yield {'id': two_star[0], 'max_omit_number': two_star[1], 'last_no': two_star[2]}
			two_star = cursor.fetchone()
		self.free(cursor)

	def get_one_by_id(self, id):
		cursor = self.select('*', order_by=None, id=id)
		two_star = cursor.fetchone()
		self.free(cursor)
		if two_star:
			two_star = {'id': two_star[0], 'max_omit_number': two_star[1], 'last_no': two_star[2]}
		return two_star

class Config:

	def __init__(self):
		self.path = './resouce/config.json'

	def read(self, key: str):
		file = open(self.path)
		json_obj = json.load(file)
		file.close()
		return json_obj[key]

	def write(self, key: str, value):
		file = open(self.path)
		json_obj = json.load(file)
		file.close()

		file = open(self.path, 'w')
		json_obj[key] = value
		json.dump(json_obj, file)
		file.close()

