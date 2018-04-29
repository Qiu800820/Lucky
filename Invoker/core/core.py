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

	# 当前遗漏数/平均遗漏数
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

	# 出现概率较低的号码组合
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

	# 周期内偏差数持续下跌号码组合
	def get_two_star_by_strategy_v3(self, group_size, step, loop, position_list=['__XXX'], start_period=None):
		two_star_team_array = []
		for position in position_list:
			print('正在分析位置:', position)
			regression_array, regression_count = self.get_max_drop_regression(position, group_size, step, loop, start_period)
			two_star_team_array.append({
				'regression_array': regression_array, 'regression_count': regression_count, 'position': position,
				'group_size': group_size, 'regression_percent': regression_count / (step * loop)
			})
		two_star_team_array = sorted(two_star_team_array, key=lambda key: key['regression_count'], reverse=True)
		return two_star_team_array

	# 组合遗漏数情况
	def get_omit_strategy(self, period, count=100, size=40):
		bingo_count = 0
		number_total = 0
		omit_number_array = []
		result = self.omit_log.get_omit_by_position('__XXX', period=period)
		for index in range(size):
			item = result[index]
			omit_number_array.append(item['no'])
		for i in range(count):
			number_size = len(omit_number_array)
			period += 1
			award_number = self.omit_log.get_by_period(period)
			if award_number['no'] in omit_number_array:
				bingo_count += 1
				print("中奖!!! 组合数:%s, 盈利:%s,  总盈利:%s" % (number_size, 100 - number_size, bingo_count * 100 - number_total))
			else:
				print("xxx 组合数:%s 未中奖 ,  总盈利:%s xxx" % (number_size, bingo_count * 100 - number_total))
			number_total += number_size
			omit_number_array = []
			result = self.omit_log.get_omit_by_position('__XXX', period=period)
			for index in range(size):
				item = result[index]
				omit_number_array.append(item['no'])

	# 获取周期内遗漏数下跌最大号码组合
	def get_max_drop_regression(self, position, group_size, step=120, loop=100, start_period=None):
		if not start_period:
			max_total = self.award.get_last_award()['id']
			start_period = max_total - step * loop

		current_result = self.omit_log.get_all_by_position('__XXX', start_award_id=0, end_award_id=start_period)
		regression_dist = {}
		regression_array = []
		diff_count = 0
		# [{'no':'00XXX', 'count':'120'}, {'no':'01XXX', 'count':'121'}] ==> {'01XXX':121, '00XXX':120}
		for item in current_result:
			regression_dist.setdefault(item['no'], item['count'])
		last_result = self.omit_log.get_all_by_position(position, start_award_id=0, end_award_id=start_period - step*loop)
		# [{'no':'00XXX', 'count':'110'}, {'no':'01XXX', 'count':'111'}] ===>
		# [{'no':'00XXX', 'count':'110', 'diff': 10}, {'no':'01XXX', 'count':'111', 'diff': 10}]
		for item in last_result:
			diff = regression_dist.get(item['no'], 0) - item['count']
			item.setdefault('diff', diff)
		last_result = sorted(last_result, key=lambda key: key['diff'], reverse=False)[:group_size]
		for item in last_result:
			regression_array.append(item['no'])
			diff_count += item['diff']
		regression_count = group_size*step*loop / 100 - diff_count
		print('最大下跌组合:%s, 下跌数:%s' % (regression_array, regression_count))
		return regression_array, regression_count

	# 模拟计算偏差数与偏差率变化
	def get_regression_cycle(self, start_period, loop_start_period, step=500, max_loop_count=20):
		money_count = 0
		max_total = self.award.get_last_award()['id']
		# for i in range(1000): # 计算1000次 得出平均概率
		# step1 计算最大偏差
		total = start_period
		avg_count = total / 100
		max_deviation_number_array = []
		max_deviation_count = 0
		# 根据位置取出号码出现次数 [{'no':'11XXX', 'count': 2888}]
		result = self.omit_log.get_all_by_position('__XXX', start_award_id=0, end_award_id=total)
		print('初始化参数: max_total:%s, total:%s, result_len:%s' % (max_total, total, len(result)))
		print('平均值:', avg_count, '号码组合出现概率:', result)
		for item in result:
			if item['count'] >= avg_count:
				break
			max_deviation_count += (avg_count - item['count'])
			max_deviation_number_array.append(item['no'])
		# step2 开始回补偏差
		size = len(max_deviation_number_array)
		loop = 0
		if loop_start_period:
			total = loop_start_period
		while max_deviation_count > 0 and total < max_total and loop < max_loop_count:
			loop += 1
			print('分析期数:%s,组合数:%s,偏差值:%s, 偏差率;%s' % (total, size, max_deviation_count, max_deviation_count/total))  # 回归过程
			# 动态调配
			# step = int(max_deviation_count * (100 / size))

			last_count = avg_count * size - max_deviation_count

			total += step
			result = self.omit_log.get_no_count(start_award_id=0, end_award_id=total, no_array=max_deviation_number_array)
			avg_count = math.ceil(total / 100)
			max_deviation_count = 0

			# print('平均值:', avg_count, '号码组合出现概率:', result)  # 详细信息

			for item in result:
				max_deviation_count += (avg_count - item['count'])

			count = avg_count * size - max_deviation_count
			money = 100 * (count - last_count) - step * size
			money_count += money
			print("%s期盈利数据 --- 成本：%s, 中奖次数：%s, 盈利：%s, 总盈利：%s" % (step, step * size, count - last_count, money, money_count))  # 盈利数据

		print('回补完成 ----> 分析期数:%s,组合数:%s,偏差值:%s' % (total, size, max_deviation_count))

	# 模拟计算组合号码周期内偏差数变化
	def get_regression_cycle_v2(self, start_period, group_size, no_array):
		result = self.omit_log.get_no_count(start_award_id=0, end_award_id=start_period, no_array=no_array)
		group = result[:group_size]
		avg_count = start_period / 100
		deviation_count = 0
		for item in group:
			deviation_count += (avg_count - item['count'])
		print('期数:%s, %s组最大偏差数:%s' % (start_period, group_size, deviation_count))

	def get_today_answer(self):
		no = time.strftime('%y%m%d', time.localtime(time.time()))
		no += "000"
		return self.award.get_new_award(no, order_by='desc')

	def mock_lucky(self, start_period, no_array, step, loop):
		total = self.award.get_total()
		money_count = 0
		size = len(no_array)
		for i in range(loop):
			if start_period >= total:
				print('模拟结束 --- 超出当前号码期数！！！')
				break

			end_period = start_period + step
			result = self.omit_log.get_no_count(start_award_id=start_period, end_award_id=end_period, no_array=no_array)
			bingo_count = 0
			for item in result:
				bingo_count += item['count']
			money = 100 * bingo_count - step * size
			money_count += money
			print("%s - %s期盈利数据 --- 成本：%s, 中奖次数：%s, 盈利：%s, 总盈利：%s" % (start_period, end_period, step * size, bingo_count, money, money_count))  # 盈利数据
			start_period = end_period
		return "总盈利：%s" % money_count

	def get_award_total(self):
		return self.award.get_total()
