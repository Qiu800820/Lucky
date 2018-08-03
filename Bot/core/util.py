#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import time

import requests


def prepare_message_params(msg):
	if msg.get('isAt'):
		content = msg['Content'].split('\u2005')
		if len(content) > 1:
			content = content[1]
	else:
		content = msg['Content']
	create_time = msg['CreateTime']
	if msg.get('ActualNickName'):
		nick_name = actual_nick_name = None
	elif msg.get('User'):
		nick_name = msg['User']['RemarkName']
		actual_nick_name = msg['User']['NickName']
	else:
		nick_name = actual_nick_name = None
	msg_id = msg['MsgId']
	return content, create_time, actual_nick_name, nick_name, msg_id


def format_history_message(number_array):
	message = []
	for item in number_array:
		number = item['number']
		if ' ' in number:
			number = number.replace(' ', '  ')
		elif len(number) >= 5:
			number = '%s  %s  %s  %s  %s' % (number[0], number[1], number[2], number[3], number[4])

		message.append('%s.. %s' % (item['no'], number))
	message = '\n\n'.join(message)
	return message


def display_simple_numbers(number_array):
	numbers = []
	for number in number_array:
		numbers.append(number['number'])
	if len(numbers) < 11:
		return ','.join(numbers)
	return '%s .... %s' % (','.join(numbers[0:5]), ','.join(numbers[-5:]))


def get_superior_site(urls):
	superior_site = None
	superior_time = 100000
	for url in urls:
		start_time = time.time()
		response = None
		try:
			response = requests.get(url, timeout=1)
		except Exception:
			pass
		if response and response.status_code == 200:
			consuming_time = (time.time() - start_time) * 1000
		else:
			consuming_time = 100000
		print('%s 耗时 %s' % (url, consuming_time))
		if consuming_time < superior_time:
			superior_time = consuming_time
			superior_site = url
	if superior_site:
		match = re.search(r'(?P<value>[\w:]+//.*?)/', superior_site)
		superior_site = match.group('value')

	return superior_site


def test():
	number_array = [
		{'no': '20180613001', 'number': '0 1 2 3 4'}, {'no': '20180613002', 'number': '0 1 2 3 4'},
		{'no': '20180613003', 'number': '01234'}, {'no': '20180613004', 'number': '01234'}
	]
	print(format_history_message(number_array))


if __name__ == '__main__':
	test()
