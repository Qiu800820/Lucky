#!/usr/bin/python
# -*- coding: UTF-8 -*-
from core.fetch import Fetch
from db.ssc_dao import AnswerObject, TwoStarObject


class Core:

	def __init__(self):
		self.fetch = Fetch()
		self.answer = AnswerObject()
		self.two_star = TwoStarObject()
		print('init done')

	def refresh_answer(self):
		last_answer = self.answer.get_last_answer()
		if last_answer:
			self.fetch.refresh_answer(last_answer['no'])
			run_result = (True, "refresh complete")
		else:
			run_result = (False, "数据库文件缺失")
		return run_result
