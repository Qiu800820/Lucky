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


def mock(no, count):
	if len(no) < 7:
		print('期号输入错误, 正确格式181010001')
		return None
	print('开始模拟数据...')

	day_no = no[6:]
	second = int(time.mktime(time.strptime(no[0:6], '%y%m%d')))
	second += int(int(day_no) + int(count) / 120) * 86400
	end_no = time.strftime('%y%m%d', time.localtime(second)) + str(int(day_no) + int(count) % 120)

	award_db = AwardObject()
	return award_db.get_new_award(no, end_no)


def output_csv(mock_data, file_name):
	if not mock_data:
		print('模拟数据为空，生成失败')
		return
	print('开始生成数据...')
	familiar_map = {'myriad': [], 'thousand': [], 'hundred': [], 'ten': [], 'one': []}
	with open(file_name, 'w+') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(['期号', '万', '千', '百', '十', '个', '万熟组', '千熟组', '百熟组', '十熟组', '个熟组', '万生', '千生', '百生', '十生', '个生'])
		for item in mock_data:
			writer.writerow(update_familiar(familiar_map, item))


def update_familiar(familiar_map, item):
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
			elif key == 'thousand':
				sort_familiar(thousand, value)
			elif key == 'hundred':
				sort_familiar(hundred, value)
			elif key == 'ten':
				sort_familiar(ten, value)
			elif key == 'one':
				sort_familiar(one, value)
		return [
			item['no'], myriad, thousand, hundred, ten, one, familiar_map.get('myriad'), familiar_map.get('thousand'),
			familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'),
			if_myriad, is_thousand, is_hundred, is_ten, is_one
		]
	else:
		return [
			item['no'], '', '', '', '', '', familiar_map.get('myriad'), familiar_map.get('thousand'),
			familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one'), familiar_map.get('myriad'),
			familiar_map.get('thousand'), familiar_map.get('hundred'), familiar_map.get('ten'), familiar_map.get('one')
		]


def sort_familiar(number, value):
	if number in value:
		if value.index(number) != (len(value) - 1):
			value.remove(number)
			value.append(number)
	else:
		value.append(number)


def is_unfamiliar(number, value):
	return len(value) > 0 and number == value[0]


if __name__ == '__main__':
	print('============= 时时彩助手v1 =============\n\n')

	init_data()
	refresh_data()
	complete = False
	while not complete:
		py_no = input('请输入开始模拟期号: 如181010120')
		py_count = input('请输入模拟期数: 如500')
		if py_no and py_count:
			data = mock(py_no, py_count)
			if data:
				output_csv(data, '%s-%s.csv' % (py_no, py_count))
				complete = True
		else:
			print('输入格式有误')
