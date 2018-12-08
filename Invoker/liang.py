#!/usr/bin/python
# -*- coding: UTF-8 -*-
import csv
import os
import time

from Invoker.db.json2db import run
from Invoker.db.ssc_dao import AwardObject
from Invoker.core.fetch import Fetch


def init_data():
	print('正在检测数据库文件是否存在...')
	if not os.path.exists('./resouce/ssc.db'):
		run('./resouce/answer.json')


def refresh_data():
	print('获取最新开奖数据...')
	fetch = Fetch()
	fetch.refresh_answer()


def mock(no, end_no):
	if len(no) < 7 or len(end_no) < 7:
		print('期号输入错误, 正确格式181010001')
		return None
	print('开始模拟数据...')

	award_db = AwardObject()
	return award_db.get_new_award(no, end_no)


def output_csv(mock_data, file_name):
	if not mock_data:
		print('模拟数据为空，生成失败')
		return
	print('开始生成数据...')
	familiar_map = {'myriad': [], 'thousand': [], 'hundred': [], 'ten': [], 'one': []}
	count_map = {'myriad': {}, 'thousand': {}, 'hundred': {}, 'ten': {}, 'one': {}}
	with open(file_name, 'w+') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow([
			'期号', '万', '千', '百', '十', '个',
			'万熟组', '千熟组', '百熟组', '十熟组', '个熟组',
			'万生', '千生', '百生', '十生', '个生',
			'万码组', '千码组', '百码组', '十码组', '个码组'
		])
		for item in mock_data:
			writer.writerow(update_familiar(familiar_map, count_map, item))


def update_familiar(familiar_map, count_map, item):
	award = item['number'].replace(' ', '')
	if award and len(award) == 5:
		myriad, thousand, hundred, ten, one = (award[0], award[1], award[2], award[3], award[4])
		if_myriad, is_thousand, is_hundred, is_ten, is_one = (
			is_unfamiliar(myriad, familiar_map.get('myriad')), is_unfamiliar(thousand, familiar_map.get('thousand')),
			is_unfamiliar(hundred, familiar_map.get('hundred')), is_unfamiliar(ten, familiar_map.get('ten')),
			is_unfamiliar(one, familiar_map.get('one'))
		)
		for (key, value) in familiar_map.items():
			if key == 'myriad':
				sort_familiar(myriad, value)
				count(myriad, count_map[key])
			elif key == 'thousand':
				sort_familiar(thousand, value)
				count(thousand, count_map[key])
			elif key == 'hundred':
				sort_familiar(hundred, value)
				count(hundred, count_map[key])
			elif key == 'ten':
				sort_familiar(ten, value)
				count(ten, count_map[key])
			elif key == 'one':
				sort_familiar(one, value)
				count(one, count_map[key])
		return [
			item['no'], myriad, thousand, hundred, ten, one, familiar_map.get('myriad'), familiar_map.get('thousand'),
			familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'),
			if_myriad, is_thousand, is_hundred, is_ten, is_one, count_map.get('myriad'), count_map.get('thousand'),
			count_map.get('hundred'), count_map.get('ten'), count_map.get('one')
		]
	else:
		return [
			item['no'], '', '', '', '', '', familiar_map.get('myriad'), familiar_map.get('thousand'),
			familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'), familiar_map.get('myriad'),
			familiar_map.get('thousand'), familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'),
			count_map.get('myriad'), count_map.get('thousand'), count_map.get('hundred'),
			count_map.get('ten'), count_map.get('one')
		]


def sort_familiar(number, value):
	if number in value:
		if value.index(number) != (len(value) - 1):
			value.remove(number)
			value.append(number)
	else:
		value.append(number)


def count(number, value):
	count_number = value.get(number, 0)
	value[number] = count_number + 1


def is_unfamiliar(number, value):
	return len(value) > 0 and number == value[0]


if __name__ == '__main__':
	print('============= 时时彩助手v1 =============\n\n')

	init_data()
	refresh_data()
	complete = False
	while not complete:
		py_no = input('请输入开始模拟期号: 如181010120')
		py_end_no = input('请输入结束模拟期号: 如181030120')
		if py_no and py_end_no:
			data = mock(py_no, py_end_no)
			if data:
				output_csv(data, '%s-%s.csv' % (py_no, py_end_no))
				complete = True
		else:
			print('输入格式有误')
