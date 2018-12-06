#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

import requests
from lxml import etree

from Invoker.db.ssc_dao import AwardObject


class Fetch:
	def __init__(self):
		self.award_db = AwardObject()
		self.has_change = False  # 是否需要提交事务

	# 刷新历史开奖数据
	# last_no ：本地最新开奖期
	def refresh_answer(self, last_no=None):
		if not last_no:
			last_award = self.award_db.get_last_award()
			last_no = last_award and last_award['no']
		day_list = time_difference(last_no)
		for day in day_list:
			data_list = self.__query_answer(day=day)
			for data in data_list:
				if data and data['no'] and int(data['no']) > int(last_no):  # 排除未开奖结果 and 本地已有数据
					self.award_db.insert(data['no'], data['number'], None)
					print(data)
					self.has_change = True
			if self.has_change:
				self.award_db.commit()
				self.has_change = False

	def __query_answer(self, day):
		result = []
		has_data = False
		items = self.__query_answer_163(day=day)
		for item in items:
			result.append(item)
			has_data = True
		if not has_data:
			items = self.__query_award_360(day=day)
			for item in items:
				result.append(item)
				has_data = True
		if has_data:
			result = sorted(result, key=lambda key: key['no'], reverse=False)
		return result

	#  加载某一天开奖结果
	def __query_answer_163(self, day):
		print('加载%s内容' % day)
		response = requests.get('http://caipiao.163.com/award/cqssc/%s.html' % day)
		response = etree.HTML(response.text)
		td_list = response.xpath("//table/tr/td[contains(@class, 'start')]")
		for td in td_list:
			number = td.xpath("@data-win-number")
			if number and len(number) > 0 and len(number[0]) > 1:
				yield {'number': number[0], 'no': td.xpath("@data-period")[0], 'day_no': td.xpath("text()")[0]}

	def __query_award_360(self, day):
		print('加载%s内容' % day)
		format_day = '%s-%s-%s' % (day[:4], day[4:6], day[6:8])
		response = requests.get('http://chart.cp.360.cn/kaijiang/kaijiang?lotId=255401&spanType=2&span=%s_%s' % (format_day, format_day))
		response = etree.HTML(response.text)
		td_list = response.xpath("//td[contains(@class, 'red big')]")
		for td in td_list:
			day_no = td.xpath("../td")[0].xpath("text()")[0]
			no = day[2:] + day_no
			number = td.xpath("text()")[0]
			if number:
				yield {'number': number, 'no': no, 'day_no': day_no}


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
