#!/usr/bin/python
# -*- coding: UTF-8 -*-
import csv
import os

import xlrd

from Invoker.core.fetch import Fetch
from Invoker.db.json2db import run
from Invoker.db.ssc_dao import AwardObject


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
	combo_map = {'myriad': [], 'thousand': [], 'hundred': [], 'ten': [], 'one': []}
	with open(file_name, 'w+') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow([
			'期号', '万', '千', '百', '十', '个',
			'万熟组', '千熟组', '百熟组', '十熟组', '个熟组',
			'万生', '千生', '百生', '十生', '个生',
			'万031', '千031', '百031', '十031', '个031',
			'万顺序', '千顺序', '百顺序', '十顺序', '个顺序',
			'万码组', '千码组', '百码组', '十码组', '个码组'
		])
		for item in mock_data:
			writer.writerow(update_familiar(familiar_map, count_map, item, combo_map))


def update_familiar(familiar_map, count_map, item, combo_map):
	award = item['number'].replace(' ', '')
	if award and len(award) == 5:
		myriad, thousand, hundred, ten, one = (award[0], award[1], award[2], award[3], award[4])
		myriad_index, thousand_index, hundred_index, ten_index, one_index = (0, 0, 0, 0, 0)
		if_myriad, is_thousand, is_hundred, is_ten, is_one = (
			is_unfamiliar(myriad, familiar_map.get('myriad')), is_unfamiliar(thousand, familiar_map.get('thousand')),
			is_unfamiliar(hundred, familiar_map.get('hundred')), is_unfamiliar(ten, familiar_map.get('ten')),
			is_unfamiliar(one, familiar_map.get('one'))
		)
		for (key, value) in familiar_map.items():
			if key == 'myriad':
				myriad_index = sort_familiar(myriad, value)
				count(myriad, count_map[key])
			elif key == 'thousand':
				thousand_index = sort_familiar(thousand, value)
				count(thousand, count_map[key])
			elif key == 'hundred':
				hundred_index = sort_familiar(hundred, value)
				count(hundred, count_map[key])
			elif key == 'ten':
				ten_index = sort_familiar(ten, value)
				count(ten, count_map[key])
			elif key == 'one':
				one_index = sort_familiar(one, value)
				count(one, count_map[key])
		return [
			item['no'], myriad, thousand, hundred, ten, one, familiar_map.get('myriad'), familiar_map.get('thousand'),
			familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'),
			if_myriad, is_thousand, is_hundred, is_ten, is_one,
			is_combo(myriad, combo_map.get('myriad')), is_combo(thousand, combo_map.get('thousand')),
			is_combo(hundred, combo_map.get('hundred')), is_combo(ten, combo_map.get('ten')),
			is_combo(one, combo_map.get('one')),
			myriad_index, thousand_index, hundred_index, ten_index, one_index,
			count_map.get('myriad'), count_map.get('thousand'), count_map.get('hundred'), count_map.get('ten'), count_map.get('one')
		]
	else:
		return [
			item['no'], '', '', '', '', '', familiar_map.get('myriad'), familiar_map.get('thousand'),
			familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'),
			False, False, False, False, False,
			False, False, False, False, False,
			1, 1, 1, 1, 1,
			count_map.get('myriad'), count_map.get('thousand'), count_map.get('hundred'),
			count_map.get('ten'), count_map.get('one')
		]


def sort_familiar(number, value):
	index = 0
	if number in value:
		index = value.index(number)
		if index != (len(value) - 1):
			value.remove(number)
			value.append(number)
		index = (len(value) - index) % 10
	else:
		value.append(number)
	return index


def count(number, value):
	count_number = value.get(number, 0)
	value[number] = count_number + 1


def is_unfamiliar(number, value):
	return len(value) > 0 and number == value[0]


def is_combo(number, combo_array):
	if number == '0' and len(combo_array) == 0:
		combo_array.append(number)
	elif number == '3' and len(combo_array) == 1:
		combo_array.append(number)
	elif number == '1' and len(combo_array) == 2:
		combo_array.clear()
		return True
	else:
		combo_array.clear()
	return False


def main_v1():
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


def main_v2():
	mock_data = load_xls()
	output_csv(mock_data, 'zund.csv')


def load_xls():
	workbook = xlrd.open_workbook('zund.xls')
	for sheet in workbook.sheets():
		last_day = ''
		for i in range(sheet.nrows):
			row = sheet.row_values(i)
			if row[0]:
				last_day = row[0]
			if row[2]:
				number = '%d%d%d%d%d' % (row[2], row[3], row[4], row[5], row[6])
			else:
				number = ''
			yield {
				'no': '%s%02d%02d' % (sheet.name, last_day, row[1]), 'number': number
			}


if __name__ == '__main__':
	main_v1()
	# main_v2()
