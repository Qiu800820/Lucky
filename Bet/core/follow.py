#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import time

import requests.sessions

from Bet.core.log import Log
from Bot.core.encrypted import Encryption


class Follow:

	def __init__(self, agent_url, log):
		self.user_name = None
		self.pwd = None
		self.gt_user = None
		self.encryption = None
		self.service = agent_url
		self.log = log
		self.session = requests.Session()
		self.input_params()

	def input_params(self):

		url = "%s/Default.aspx" % self.service
		response = self.session.get(url)  # 初始化Cookie
		key = re.search('new RSAKeyPair\("010001", "", "(?P<key>[0-9A-Z]*)"\);', response.text).group('key')
		self.encryption = Encryption(key)

		login_status = False
		while not login_status:
			proxy_user = input('请输入代理用户名:')
			proxy_psw = input('请输入代理密码:')
			gt_user = input('请输入跟投用户名:')
			if proxy_user and proxy_psw and gt_user:
				proxy_psw = self.encryption.encrypted(proxy_psw)
				message, login_status = self.login(proxy_user, proxy_psw)
				self.gt_user = gt_user
			else:
				message = '账号密码不能为空！'
			if not login_status:
				print(message)

	# 登录
	def login(self, proxy_user, proxy_psw):
		url = "%s/ResellerLogin.aspx" % self.service
		data = {
			"User": proxy_user, "Pwd": proxy_psw,
		}
		self.log.debug('--> url:%s, data:%s' % (url, data))
		response = self.session.post(url, data=data, timeout=20)
		login_status = False
		self.log.debug(response.text)
		if response.status_code == 200 and 'ResellerTop.aspx' in response.text:
			self.user_name = proxy_user
			self.pwd = proxy_psw
			message = '登陆成功'
			login_status = True
		else:
			message = '登陆失败：%s' % response.text
		return message, login_status

	def follow(self, current_no, last_order_id):
		orders = []
		index = 1
		result = self.get_user_bet_detail(self.gt_user, current_no, index, last_order_id)
		orders.extend(result)
		while len(result) >= 50:
			index += 1
			result = self.get_user_bet_detail(self.gt_user, current_no, index, last_order_id)
			orders.extend(result)
		return orders

	def get_user_bet_detail(self, follow_user_name, current_no, index, last_order_id):
		result = []
		url = "%s/BraComUserBetDetail.aspx" % self.service
		data = {
			"Commd": "InitData", "BetType": "", "BallNo": "",
			"txtTerm": current_no, "txtPoint1": "", "txtPoint2": "",
			"UserID": follow_user_name, "HitType": "",
			"PageIndex": index, "PageSize": "50"
		}
		self.log.debug('--> url:%s, data:%s' % (url, data))
		response = self.session.post(url, data=data)
		self.log.debug(response.text)
		if response.status_code == 200 and 'Succeeded' in response.text:
			html_result = re.search(r"Succeeded@(?P<result>.*?)\$", response.text).group('result')
			for order in html_result.split('#'):
				items = order.split("|")
				if int(items[0]) > int(last_order_id):
					result.append({
						"order_id": items[0], "bet_number": items[6], "bet_money": items[9]
					})
		return result


if __name__ == '__main__':
	last_order_id = '0'
	log = Log()
	follow = Follow('http://pu.yy2bt.com', log)
	while follow:
		no_array = follow.follow("20190218035", last_order_id)
		if no_array and len(no_array) > 0:
			info_array = []
			for no in no_array:
				info_array.append('%s|%s' % (no.get('bet_number'), no.get('bet_money')))
			info = ','.join(info_array)
			log.info('=== 跟码%s ===' % info)
			last_order_id = no_array[0]['order_id']
		time.sleep(10)

