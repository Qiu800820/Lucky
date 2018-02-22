#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import math
from core.fetch import Fetch
from db.ssc_dao import AwardObject, TwoStarObject, Config, OmitLogObject


class Core:
	def __init__(self):
		self.fetch = Fetch()
		self.award = AwardObject()
		self.two_star = TwoStarObject()
		self.omit_log = OmitLogObject()
		self.config = Config()
		self.index = [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
		print('init done')

	def refresh_answer(self):
		last_award = self.award.get_last_award()
		print('获取上期开奖数据', last_award)
		if last_award:
			self.fetch.refresh_answer(last_award['no'])
			self.statistics()
		else:
			raise Exception('数据库文件缺失')

	def statistics(self):
		# 获取上次分析期号
		last_no = self.config.read("last_statistics_no")
		print('获取上次分析期号', last_no)
		# 加载新开奖数据
		new_award_data = self.award.get_new_award(last_no)
		# 开始分析并写入two_star表中
		if new_award_data:
			last_award_no = None
			for award in new_award_data:
				print('正在分析', award)
				award_no = award['no']
				award_number = award['number'].replace(' ', '')
				award_id = award['id']
				self.update_two_star(award_no, award_number, award_id)
				last_award_no = award_no
			self.omit_log.commit_cache()
			self.two_star.commit_cache()
			if last_award_no:
				self.config.write('last_statistics_no', last_award_no)
			print("全部分析完成")

	# 根据开奖数据更新双星数据
	def update_two_star(self, award_no, award_number, award_id):
		if len(award_number) < 5:
			return
		for index in self.index:
			number_format = "XXXXX"
			two_star_id = number_format[:index[0]] + award_number[index[0]] + number_format[index[0] + 1:index[1]] + \
			              award_number[index[1]] + number_format[index[1] + 1:]  # 得到two_star id
			two_star = self.two_star.get_one_by_id_cache(two_star_id)  # 根据ID 取出本地双星数据
			if two_star:
				# omit_number = self.award.diff_no(two_star['last_no'], award_no)  # 算出遗漏期数
				omit_number = award_id - two_star['last_id']
				two_star['max_omit_number'] = max(two_star['max_omit_number'], omit_number)  # 计算最大遗漏期数
				two_star['last_no'] = award_no
				two_star['last_id'] = award_id
				self.add_omit_log(two_star_id, omit_number, award_id, award_no)
				self.two_star.update_cache(two_star['id'], two_star)  # 更新双星数据
			else:
				self.two_star.update_cache(two_star_id, {'id': two_star_id, 'max_omit_number': 0, 'last_no': award_no, 'last_id': award_id})  # 本地无该数据  直接插入

	def add_omit_log(self, no, omit_number, award_id, award_no):
		if omit_number > 0:
			self.omit_log.insert_cache({'no': no, 'omit_number': omit_number, 'award_no': award_no, 'award_id': award_id})

	def get_two_star_by_strategy(self, sort_percent, sort_type, position_list=[None]):
		two_star_dist = {}
		for position in position_list:
			result = self.two_star.get_all_by_position(position)
			for item in result:
				answer = self.award.get_last_award() # 获取上期开奖号码
				current_omit_number = self.award.diff_no(item['last_no'], answer['no'])
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

	def get_two_star_by_strategy_v2(self, position_list=[None]):
		two_star_result_dist = {}
		two_star_team_array = []
		history_total = self.award.get_total()  # 历史开奖总数
		for position in position_list:  # 00XXX in [00XXX, 0X0XX]
			result = self.omit_log.get_all_by_position(position)  # 根据位置取出号码出现次数 [{'no':'11XXX', 'count': 2888}]
			i = 0
			two_star_result_dist.setdefault(position, result)
			team_show_total = 0
			for item in result:
				i += 1
				team_show_total += item['count']
				two_star_item = {}
				if 29 < i < 81:
					avg_percent = team_show_total / history_total
					perfect_percent = i / 100
					two_star_item = {'position': position, 'avg_percent': avg_percent,
					                       'perfect_percent': perfect_percent, 'size': i, 'weight': perfect_percent - avg_percent}
					two_star_team_array.append(two_star_item)
				if i > 81 or two_star_item.get('weight', 0) < 0:
					break
				two_star_team_array = sorted(two_star_team_array, key=lambda key: key['weight'], reverse=True)
		return two_star_team_array, two_star_result_dist

	def get_today_answer(self):
		no = time.strftime('%y%m%d', time.localtime(time.time()))
		no += "000"
		return self.award.get_new_award(no, order_by='desc')



