#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json

from db.ssc_dao import AnswerObject

answer_json = open('../../WinStarScrapy/answer.json', 'r', -1, 'utf-8').read()
answer_json = json.loads(answer_json)

answer_db = AnswerObject()
for answer in answer_json:
	answer_db.insert(answer['no'], answer['number'], answer['day_no'])
answer_db.commit()


