#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import time
from lxml import etree

from db.ssc_dao import AnswerObject


class Fetch:
	def __init__(self):
		self.answer_db = AnswerObject()
		self.has_change = False  # 是否需要提交事务
		self.url = 'http://caipiao.163.com/award/cqssc/%s.html'

	# 刷新历史开奖数据
	# last_no ：本地最新开奖期
	def refresh_answer(self, last_no):
		day_list = time_difference(last_no)
		for day in day_list:
			data_list = self.__query_answer(day=day)
			for data in data_list:
				if data and data['no'] and int(data['no']) > int(last_no):  # 排除未开奖结果 and 本地已有数据
					self.answer_db.replace(data['no'], data['number'], data['day_no'])
					print(data)
					self.has_change = True
			if self.has_change:
				self.answer_db.commit()
				self.has_change = False

	#  加载某一天开奖结果
	def __query_answer(self, day):
		print('加载%s内容' % day)
		response = requests.get(self.url % day)
		response = etree.HTML(response.text)
		td_list = response.xpath("//table/tr/td[contains(@class, 'start')]")
		for td in td_list:
			number = td.xpath("@data-win-number")
			if number and len(number) > 0:
				yield {'number': number[0], 'no': td.xpath("@data-period")[0], 'day_no': td.xpath("text()")[0]}


# 计算需要加载的日期
def time_difference(no):
	day_no = '000'
	if len(no) > 6:
		no = no[0:6]
		day_no = no[6:]
	second = int(time.mktime(time.strptime(no, '%y%m%d')))
	current_second = int(time.time())
	print('本地最新开奖结果时间：%s-%s, second: %s' % (no, day_no, second))
	while second < current_second:
		day_str = time.strftime('%Y%m%d', time.localtime(second))
		yield day_str
		second += 86400

