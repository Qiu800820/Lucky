#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json

from Invoker.db.ssc_dao import AwardObject


def run(file_name):
	print('数据库文件缺失， 重新生成中...')
	answer_json = open(file_name, 'r', -1, 'utf-8').read()
	answer_json = json.loads(answer_json)

	answer_db = AwardObject()
	for answer in answer_json:
		answer_db.insert(answer['no'], answer['number'], None)
	answer_db.commit()
