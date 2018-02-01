#!/usr/bin/python
# -*- coding: UTF-8 -*-
from db import sqlite_db


class AnswerObject(sqlite_db.Table):
	def __init__(self):
		super(AnswerObject, self).__init__("../resouce/ssc.db", "answer", ['no TEXT PRIMARY KEY', 'number TEXT', 'day_no TEXT'])

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


class TwoStarObject(sqlite_db.Table):
	def __int__(self):
		super(TwoStarObject, self).__init__("../resouce/ssc.db", "two_star", ["id TEXT PRIMARY KEY", "history_omit_number TEXT", "current_omit_number NUMERIC", "last_no TEXT"])

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
