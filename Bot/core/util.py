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
	else:
		nick_name = msg['User']['RemarkName']
		actual_nick_name = msg['User']['NickName']
	msg_id = msg['MsgId']
	return content, create_time, actual_nick_name, nick_name, msg_id
