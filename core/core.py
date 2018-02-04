#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

from core.fetch import Fetch
from db.ssc_dao import AnswerObject, TwoStarObject, Config


class Core:
	def __init__(self):
		self.fetch = Fetch()
		self.answer = AnswerObject()
		self.two_star = TwoStarObject()
		self.config = Config()
		self.index = [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
		print('init done')

	def refresh(self):
		self.refresh_answer()
		self.statistics()

	def refresh_answer(self):
		last_answer = self.answer.get_last_answer()
		if last_answer:
			self.fetch.refresh_answer(last_answer['no'])
		else:
			raise Exception('数据库文件缺失')

	def statistics(self):
		# 获取上次分析期号
		last_no = self.config.read("last_statistics_no")
		# 加载新开奖数据
		new_answer_data = self.answer.get_new_answer(last_no)
		# 开始分析并写入two_star表中
		if new_answer_data:
			last_answer_no = None
			for answer in new_answer_data:
				answer_no = answer['no']
				answer_number = answer['number'].replace(' ', '')
				self.update_two_star(answer_no, answer_number)
				last_answer_no = answer_no
			self.two_star.commit()
			if last_answer_no:
				self.config.write('last_statistics_no', last_answer_no)

	# 根据开奖数据更新双星数据
	def update_two_star(self, answer_no, answer_number):
		for index in self.index:
			number_format = "XXXXX"
			two_star_id = number_format[:index[0]] + answer_number[index[0]] + number_format[index[0] + 1:index[1]] + \
			              answer_number[index[1]] + number_format[index[1] + 1:]  # 得到two_star id
			two_star = self.two_star.get_one_by_id(two_star_id)  # 根据ID 取出本地双星数据
			if two_star:
				omit_number = self.answer.diff_no(two_star['last_no'], answer_no)  # 算出遗漏期数
				if two_star['history_omit_number']:
					two_star['history_omit_number'] += ("|" + str(omit_number))  # 叠加历史遗漏期数
				else:
					two_star['history_omit_number'] = str(omit_number)
				two_star['max_omit_number'] = max(two_star['max_omit_number'], omit_number)  # 计算最大遗漏期数
				two_star['last_no'] = answer_no
				self.two_star.update(two_star, id=two_star_id)  # 更新双星数据
			else:
				self.two_star.insert(two_star_id, '0', 0, answer_no)  # 本地无该数据  直接插入

	def get_two_star_by_strategy(self, strategy):
		result = self.two_star.get_all()
		two_star_list = []
		for item in result:
			answer = self.answer.get_last_answer()
			current_omit_number = self.answer.diff_no(item['last_no'], answer['no'])
			item['weight'] = 0
			if not item['max_omit_number'] == 0:
				item['weight'] = current_omit_number / item['max_omit_number']
			two_star_list.append(item)
		two_star_list = sorted(two_star_list, key=lambda key: key['weight'], reverse=True)

		size = 0
		if 1 > strategy > 0:
			size = int(len(two_star_list) * strategy)

		return two_star_list[:size]

	def get_today_answer(self):
		day = time.strftime('%y%m%d', time.localtime(time.time()))
		today_answer = self.answer.get


