#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

import requests
from lxml import etree


class Fetch:

	# 获取最新开奖记录
	def query_answer(self, no=None, size=10):
		result = None
		if not no:
			no = str(self.get_day_no())
		if not no:
			return result

		day = self.get_format_day()[:2] + no[:6]
		items = self.__query_answer_163(day=day)
		for item in items:
			if item['no'] == no:
				return item, items[-size:]

		items = self.__query_award_360(day=day)
		for item in items:
			if item['no'] == no:
				return item, items[-size:]
		return None, None

	#  加载某一天开奖结果
	def __query_answer_163(self, day):
		items = []
		response = requests.get('http://caipiao.163.com/award/cqssc/%s.html' % day)
		response = etree.HTML(response.text)
		td_list = response.xpath("//table/tr/td[contains(@class, 'start')]")
		for td in td_list:
			number = td.xpath("@data-win-number")
			if number and len(number) > 0 and len(number[0]) > 1:
				items.append({'number': number[0], 'no': td.xpath("@data-period")[0], 'day_no': td.xpath("text()")[0]})
		if len(items) > 0:
			items = sorted(items, key=lambda item: item['day_no'])
		return items

	def __query_award_360(self, day):
		items = []
		format_day = '%s-%s-%s' % (day[:4], day[4:6], day[6:8])
		response = requests.get('http://chart.cp.360.cn/kaijiang/kaijiang?lotId=255401&spanType=2&span=%s_%s' % (format_day, format_day))
		response = etree.HTML(response.text)
		td_list = response.xpath("//td[contains(@class, 'red big')]")
		for td in td_list:
			day_no = td.xpath("../td")[0].xpath("text()")[0]
			no = day[2:] + day_no
			number = td.xpath("text()")[0]
			if number:
				items.append({'number': number, 'no': no, 'day_no': day_no})
		if len(items) > 0:
			items = sorted(items, key=lambda item: item['day_no'])
		return items

	def get_format_day(self):
		current_second = int(time.time())
		return time.strftime('%Y%m%d', time.localtime(current_second))

	# 计算需要加载的期数
	def get_day_no(self, extra_time=0, current_second=None):
		if not current_second:
			current_second = time.time()
		current_second = int(current_second) + extra_time  # 提前时间
		second = current_second % 86400

		if (2 * 3600) <= second <= (14 * 3600):  # 10:00 - 22:00 -> 24-96
			no = 24 + int((second - 2 * 3600) / 600)
		elif (14 * 3600) < second < (18 * 3600):  # 22:00 - 02:00 -> 97-120-23
			no = 96 + int((second - 14 * 3600) / 300)
		else:
			no = 23
		if no > 120:
			no -= 120
		no += int(time.strftime('%y%m%d', time.localtime(current_second - 300))) * 1000
		return no


def test():
	fetch = Fetch()
	for i in range(200):
		second = int(1528816025) + (i * 30)
		print(fetch.get_day_no(60, second), time.asctime(time.localtime(second)))


if __name__ == '__main__':
	test()
