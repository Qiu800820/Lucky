#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

import requests
from lxml import etree


class Fetch:

	# 获取最新开奖记录
	def query_answer(self):
		result = None
		no = get_day_no()
		if not no:
			return result

		day = get_format_day()
		items = self.__query_answer_163(day=day)
		for item in items:
			if int(item['day_no']) == no:
				return item

		items = self.__query_award_360(day=day)
		for item in items:
			if int(item['day_no']) == no:
				return item
		return None

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


def get_format_day():
	current_second = int(time.time())
	return time.strftime('%Y%m%d', time.localtime(current_second))


# 计算需要加载的期数
def get_day_no(extra_time=0):
	no = None
	current_second = int(time.time()) + extra_time  # 提前时间
	current_second %= 86400

	if (2 * 3600) <= current_second <= (14 * 3600):  # 10:00 - 22:00 -> 24-96
		no = 24 + int((current_second - 2 * 3600) / 600)
	elif (14 * 3600) < current_second < (18 * 3600):  # 22:00 - 02:00 -> 97-120-23
		no = 97 + int((current_second - 14 * 3600) / 300)
	return no

