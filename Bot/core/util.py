#!/usr/bin/python
# -*- coding: UTF-8 -*-


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


def display_simple_numbers(numbers):
	if len(numbers < 11):
		return ','.join(numbers)
	return '%s .... %s' % (','.join(numbers[0:5]), ','.join(numbers[-5:]))


def test():
	number_array = [
		{'no': '20180613001', 'number': '0 1 2 3 4'}, {'no': '20180613002', 'number': '0 1 2 3 4'},
		{'no': '20180613003', 'number': '01234'}, {'no': '20180613004', 'number': '01234'}
	]
	print(format_history_message(number_array))


if __name__ == '__main__':
	test()
