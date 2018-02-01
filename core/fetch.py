#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import time
from lxml import etree

from db.ssc_dao import AnswerObject


class Fetch:
	def __init__(self):
		self.url = 'http://caipiao.163.com/t/awardlist.html'
		self.answer_db = AnswerObject()
		self.has_change = True

	# 刷新历史开奖数据
	# last_no ：本地最新开奖期
	def refresh_answer(self, last_no):
		page_no = 1
		data_list = self.query_answer(no=page_no)
		for data in data_list:
			if int(data['period']) > int(last_no):
				self.answer_db.insert(data['period'], data['number'], data['period'][-3:])
		if self.has_change:
			self.answer_db.commit()

	def query_answer(self, no):
		params = {'gameEn': 'ssc', 'pageNums': '30', 'pageNo': no, 'cache': int(time.time() * 1000)}
		response = requests.get(self.url, params)
		data_list = response.json()['list']
		return data_list


def time_difference(no):
	if len(no) > 6:
		no = no[0:6]
	second = int(time.mktime(time.strptime(no, '%y%m%d')))
	print('本地最新开奖结果时间：%s, millisecond: %s' % (no, second))

time_difference('180201001')
