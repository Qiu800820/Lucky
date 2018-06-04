#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests


class Translate:

	def __init__(self):
		self.service = 'https://bc.exsba.com'
		self.token = None
		self.check_login()

	def login(self, user_name, password):
		url = "%s/user/sign/in" % self.service
		response = requests.post(url, data={"username": user_name, "password": password})
		print(response.text)
		login_status = False
		if response.status_code == 200:
			self.token = response.json()['token']
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
		response = requests.post(url, data, headers=headers)
		result = response.text
		check_response(result)
		number_array = []
		message = ''
		validity = True
		if response.status_code != 200 or '<html>' in result:
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

	def post_number(self):
		pass

	def check_login(self):
		print('============= 群助手v1 =============\n')
		print('               登陆                 \n')
		login_status = False
		while not login_status:
			user_name = input('请输入用户名:')
			password = input('请输入密码:')
			if user_name and password:
				message, login_status = self.login(user_name, password)
			else:
				message = '账号密码不能为空！'
			if not login_status:
				print(message)


def check_response(response):
	if response.status_code == 401:
		print('警告：登陆过期，请重启程序！！！！')
