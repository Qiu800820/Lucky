#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from enum import Enum

from core.fetch import Fetch
from db.ssc_dao import AnswerObject, TwoStarObject, Config, OmitLogObject


class Core:
	def __init__(self):
		self.fetch = Fetch()
		self.answer = AnswerObject()
		self.two_star = TwoStarObject()
		self.omit_log = OmitLogObject()
		self.config = Config()
		self.index = [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
		print('init done')

	def refresh_answer(self):
		last_answer = self.answer.get_last_answer()
		print('获取上期开奖数据', last_answer)
		if last_answer:
			self.fetch.refresh_answer(last_answer['no'])
			self.statistics()
		else:
			raise Exception('数据库文件缺失')

	def statistics(self):
		# 获取上次分析期号
		last_no = self.config.read("last_statistics_no")
		print('获取上次分析期号', last_no)
		# 加载新开奖数据
		new_answer_data = self.answer.get_new_answer(last_no)
		# 开始分析并写入two_star表中
		if new_answer_data:
			last_answer_no = None
			for answer in new_answer_data:
				print('正在分析', answer)
				answer_no = answer['no']
				answer_number = answer['number'].replace(' ', '')
				self.update_two_star(answer_no, answer_number)
				last_answer_no = answer_no
			self.omit_log.commit_cache()
			self.two_star.commit_cache()
			if last_answer_no:
				self.config.write('last_statistics_no', last_answer_no)

	# 根据开奖数据更新双星数据
	def update_two_star(self, answer_no, answer_number):
		if len(answer_number) < 5:
			return
		for index in self.index:
			number_format = "XXXXX"
			two_star_id = number_format[:index[0]] + answer_number[index[0]] + number_format[index[0] + 1:index[1]] + \
			              answer_number[index[1]] + number_format[index[1] + 1:]  # 得到two_star id
			two_star = self.two_star.get_one_by_id_cache(two_star_id)  # 根据ID 取出本地双星数据
			if two_star:
				omit_number = self.answer.diff_no(two_star['last_no'], answer_no)  # 算出遗漏期数
				two_star['max_omit_number'] = max(two_star['max_omit_number'], omit_number)  # 计算最大遗漏期数
				two_star['last_no'] = answer_no
				self.add_omit_log(two_star_id, omit_number)
				self.two_star.update_cache(two_star['id'], two_star)  # 更新双星数据
			else:
				self.two_star.update_cache(two_star_id, {'id': two_star_id, 'max_omit_number': 0, 'last_no': answer_no})  # 本地无该数据  直接插入

	def add_omit_log(self, no, omit_number):
		if omit_number > 0:
			self.omit_log.insert_cache({'no': no, 'omit_number': omit_number})

	def get_two_star_by_strategy(self, sort_percent, sort_type, position_list=[None]):
		two_star_dist = {}
		for position in position_list:
			result = self.two_star.get_all_by_position(position)
			for item in result:
				answer = self.answer.get_last_answer()
				current_omit_number = self.answer.diff_no(item['last_no'], answer['no'])
				item['current_omit_number'] = current_omit_number
				item['max_omit_weight'] = 0
				if not item['max_omit_number'] == 0:
					item['max_omit_weight'] = current_omit_number / item['max_omit_number']
				two_star_dist.setdefault(item['id'], item)
		# 补齐平均遗漏数
		result = self.omit_log.get_avg_omit()
		for item in result:
			two_star = two_star_dist.get(item['no'])
			if two_star:
				two_star.setdefault('avg_omit_number', item['avg'])
				avg_omit_weight = two_star['current_omit_number'] / (200 - item['avg'])
				two_star.setdefault("avg_omit_weight", avg_omit_weight)
				two_star.setdefault("bingo_count", item['count'])

		two_star_list = sorted(two_star_dist.values(), key=lambda key: key[sort_type], reverse=True)

		size = 0
		if 1 > sort_percent > 0:
			size = int(len(two_star_list) * sort_percent)

		return two_star_list[:size]

	def get_today_answer(self):
		no = time.strftime('%y%m%d', time.localtime(time.time()))
		no += "000"
		return self.answer.get_new_answer(no, order_by='desc')



