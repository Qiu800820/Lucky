#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os

from Invoker.db import sqlite_db


class AwardObject(sqlite_db.Table):
	def __init__(self):
		super(AwardObject, self).__init__("./resouce/ssc.db", "award",
		                                  ['period TEXT UNIQUE', 'number TEXT', 'id INTEGER PRIMARY KEY AUTOINCREMENT'])

	def insert(self, *args):
		self.free(super(AwardObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(AwardObject, self).update(set_args, **kwargs))

	def delete(self, **kwargs):
		self.free(super(AwardObject, self).delete(**kwargs))

	def delete_all(self, **kwargs):
		self.free(super(AwardObject, self).delete_all())

	def drop(self):
		self.free(super(AwardObject, self).drop())

	def replace(self, *args):
		self.free(super(AwardObject, self).replace(*args))

	# 获取本地最新开奖记录
	def get_last_award(self):
		cursor = self.select_all('*', order_by='period DESC')
		last_award = cursor.fetchone()
		while last_award:
			if last_award[1]:  # 过滤空数据(未开奖)
				break
			else:
				last_award = cursor.fetchone()
		self.free(cursor)
		if not last_award:
			print('error : 本地服务中没有开奖记录， 请检查路径：%s 是否存在' % os.path.abspath("./resouce/ssc.db"))
		return {'no': last_award[0], 'number': last_award[1], 'id': last_award[2]}

	# 获取本地某期后的开奖记录
	def get_new_award(self, no, end_no=None, order_by='asc'):
		if end_no:
			cursor = self.read('select * from award where period >= ? and period <= ? order by period %s' % order_by, [no, end_no])
		else:
			cursor = self.read('select * from award where period >= ? order by period %s' % order_by, [no])

		award = cursor.fetchone()
		while award:
			yield {'no': award[0], 'number': award[1], 'id': award[2]}
			award = cursor.fetchone()
		self.free(cursor)

	def diff_no(self, last_no, current_no):
		cursor = self.read("select count(*) as count from award where period > ? and period < ? and number <> ''",
		                   [last_no, current_no])
		diff_no = cursor.fetchone()
		self.free(cursor)
		return diff_no[0]

	def get_total(self):
		cursor = self.read("select count(*) as count from award where number <> ''")
		count = cursor.fetchone()
		self.free(cursor)
		return count[0]


class TwoStarObject(sqlite_db.Table):
	def __init__(self):
		super(TwoStarObject, self).__init__(
			"./resouce/ssc.db", "TwoStar", ["id TEXT PRIMARY KEY", "max_omit_number NUMERIC", "last_no TEXT", "last_id NUMERIC"])
		self.cache = {}

	def insert(self, *args):
		self.free(super(TwoStarObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(TwoStarObject, self).update(set_args, **kwargs))

	def update_cache(self, id, two_star):
		self.cache.setdefault(id, two_star)

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
			yield {'id': two_star[0], 'max_omit_number': two_star[1], 'last_no': two_star[2], 'last_id': two_star[3]}
			two_star = cursor.fetchone()
		self.free(cursor)

	def get_all_by_position(self, position):
		if not position:
			return self.get_all()
		cursor = self.read("select * from twostar where id like ?", [position])
		two_star = cursor.fetchone()
		while two_star:
			yield {'id': two_star[0], 'max_omit_number': two_star[1], 'last_no': two_star[2], 'last_id': two_star[3]}
			two_star = cursor.fetchone()
		self.free(cursor)

	def get_one_by_id(self, id):
		cursor = self.select('*', order_by=None, id=id)
		two_star = cursor.fetchone()
		self.free(cursor)
		if two_star:
			two_star = {'id': two_star[0], 'max_omit_number': two_star[1], 'last_no': two_star[2], 'last_id': two_star[3]}
		return two_star

	def get_one_by_id_cache(self, id):
		two_star = self.cache.get(id)
		if not two_star:
			two_star = self.get_one_by_id(id)
		if two_star:
			self.update_cache(id, two_star)
		return two_star

	def commit_cache(self):
		for value in self.cache.values():
			self.replace(value['id'], value['max_omit_number'], value['last_no'], value['last_id'])
		self.commit()


class OmitLogObject(sqlite_db.Table):
	def __init__(self):
		super(OmitLogObject, self).__init__(
			"./resouce/ssc.db", "OmitLog", ["no TEXT", "omit_number NUMERIC", "award_no TEXT", "award_id NUMERIC"])
		self.cache = []

	def insert(self, *args):
		self.free(super(OmitLogObject, self).insert(*args))

	def update(self, set_args, **kwargs):
		self.free(super(OmitLogObject, self).update(set_args, **kwargs))

	def delete(self, **kwargs):
		self.free(super(OmitLogObject, self).delete(**kwargs))

	def delete_all(self, **kwargs):
		self.free(super(OmitLogObject, self).delete_all())

	def drop(self):
		self.free(super(OmitLogObject, self).drop())

	def replace(self, *args):
		self.free(super(OmitLogObject, self).replace(*args))

	def insert_cache(self, omit_log):
		self.cache.append(omit_log)

	def commit_cache(self):
		for value in self.cache:
			self.insert(value['no'], value['omit_number'], value['award_no'], value['award_id'])
		self.commit()

	def get_avg_omit(self):
		cursor = self.read("select AVG(omit_number), COUNT(*), no from omitlog group by no")
		omit_log = cursor.fetchone()
		while omit_log:
			yield {'avg': omit_log[0], 'count': omit_log[1], 'no': omit_log[2]}
			omit_log = cursor.fetchone()
		self.free(cursor)

	def get_by_period(self, period):
		cursor = self.read("select * from omitlog where award_id = ?", [period])
		omit_log = cursor.fetchone()
		self.free(cursor)
		return {'no': omit_log[0], 'omit_number': omit_log[1], 'award_no': omit_log[2], 'award_id': omit_log[3]}

	def get_all_by_position(self, position, start_award_id=0, end_award_id=None):
		if not position:
			return None
		if end_award_id:
			cursor = self.read(
				"select no, count(*) from omitlog where no like ? and award_id > ? and award_id < ? group by no order by count(*) asc",
				[position, start_award_id, end_award_id])
		else:
			cursor = self.read(
				"select no, count(*) from omitlog where no like ? group by no order by count(*) asc",
				[position])
		result = []
		omit = cursor.fetchone()
		while omit:
			result.append({'no': omit[0], 'count': omit[1]})
			omit = cursor.fetchone()
		self.free(cursor)
		return result

	def get_omit_by_position(self, position, period):
		if not position:
			return None

		cursor = self.read(
			"select no, max(award_id) from omitlog where no like ? and award_id < ? group by no order by award_id",
			[position, period])

		result = []
		omit = cursor.fetchone()
		while omit:
			result.append({'no': omit[0], 'award_id': omit[1]})
			omit = cursor.fetchone()
		self.free(cursor)
		return result

	def get_no_count(self, end_award_id, no_array, start_award_id=0):
		if not no_array:
			return None
		params = "','".join(no_array)
		if end_award_id:
			cursor = self.read(
				"select no, count(*) from omitlog where no in ('%s') and award_id > ? and award_id < ? group by no order by count(*) asc" % params,
				[start_award_id, end_award_id])
		else:
			cursor = self.read(
				"select no, count(*) from omitlog where no in ('%s') group by no order by count(*) asc" % params,
				None)
		result = []
		omit = cursor.fetchone()
		while omit:
			result.append({'no': omit[0], 'count': omit[1]})
			omit = cursor.fetchone()
		self.free(cursor)
		return result


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
