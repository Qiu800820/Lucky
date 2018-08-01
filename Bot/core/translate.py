#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests

from Bot.core.encrypted import Encryption


class Translate:
	def __init__(self, config, log):
		self.service = 'https://bc.exsba.com'
		self.config = config
		self.token = config.token
		self.log = log
		self.encryption = Encryption()
		self.check_login()

	def login(self, py_user, py_psw, ssc_user, ssc_psw):
		url = "%s/user/sign/in" % self.service
		data = {
			"username": py_user, "password": py_psw,
			"ssc_username": ssc_user, "ssc_password": ssc_psw
		}
		self.log.debug('--> url:%s, data:%s' % (url, data))
		response = requests.post(url, data=data)
		login_status = False
		self.log.debug(response.text)
		if response.status_code == 200:
			self.token = response.json()['token']
			self.config.token = self.token
			message = '登陆成功'
			login_status = True
		else:
			message = '登陆失败：%s' % response.text
		return message, login_status

	def prepare(self, info):
		url = "%s/decode/order" % self.service
		headers = {
			'Authorization': self.token
		}
		data = {
			'info': info
		}
		self.log.debug('--> url:%s, data:%s, headers:%s' % (url, data, headers))
		response = requests.post(url, data, headers=headers)
		self.check_response(response)
		result = response.json()['data']
		number_array = []
		message = ''
		validity = True
		if response.status_code != 200 or len(result) == 0 or 'html' in result:
			message = '译码错误'
			validity = False
		else:
			for item in result.split(','):
				item = item.split('=')
				if len(item) > 1:
					money = float(item[1])
					number_array.append({'number': item[0], 'money': money})
				else:
					message = '未配置金额'
					validity = False
					break
			if len(number_array) == 0:
				message = result
				validity = False
		return validity, number_array, message

	def post_number(self, number_array):
		info_array = []
		for number in number_array:
			info_array.append('%s|%s' % (number['number'], number['money']))
		info = ','.join(info_array)
		url = "%s/make/order" % self.service
		headers = {
			'Authorization': self.token
		}
		data = {
			'info': info
		}
		self.log.debug('--> url:%s, data:%s, headers:%s' % (url, data, headers))
		message = ''
		validity = False
		response = requests.post(url, data, headers=headers)
		self.check_response(response)
		if response.status_code != 200:
			message = response.text
		else:
			validity = True
		return validity, message

	def check_login(self):

		print('============= 群助手v1 =============\n')
		print('               登陆                 \n')
		login_status = False
		while not login_status:
			py_user = input('请输入软件用户名:')
			py_psw = input('请输入软件密码:')
			ssc_user = input('请输入平台用户名:')
			ssc_psw = input('请输入平台密码:')
			if py_user and py_psw and ssc_user and ssc_psw:
				ssc_psw = self.encryption.encrypted(ssc_psw)
				message, login_status = self.login(py_user, py_psw, ssc_user, ssc_psw)
			else:
				message = '账号密码不能为空！'
			if not login_status:
				print(message)
		self.config.save_config()

	def check_response(self, response):
		self.log.debug(response.text)
		if response.status_code == 401:
			self.config.token = ""
			self.config.save_config()
			print('警告：登陆过期，请重启程序！！！！')
