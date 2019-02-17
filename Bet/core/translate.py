#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
from lxml import etree

from Bot.core.encrypted import Encryption
from Bot.core.util import get_superior_site

mock_post = False


class AuthError(Exception):

	def __init__(self):
		pass


class Translate:

	def __init__(self, config, log):
		self.service = 'https://bc.exsba.com'
		self.user_name = None
		self.user_pwd = None
		self.platform_name = None
		self.platform_pwd = None
		self.config = config
		self.token = config.token
		self.log = log
		self.encryption = Encryption()
		self.check_login()
		self.fail_count = 0

	def relogin(self):
		return self.login(self.user_name, self.user_pwd, self.platform_name, self.platform_pwd)

	def login(self, py_user, py_psw, ssc_user, ssc_psw):
		url = "%s/user/sign/in" % self.service
		data = {
			"username": py_user, "password": py_psw,
			"ssc_username": ssc_user, "ssc_password": ssc_psw,
			"ssc_base_url": self.get_base_url()
		}
		self.log.debug('--> url:%s, data:%s' % (url, data))
		response = requests.post(url, data=data)
		login_status = False
		self.log.debug(response.text)
		if response.status_code == 200:
			self.token = response.json()['token']
			self.config.token = self.token
			self.user_name, self.user_pwd, self.platform_name, self.platform_pwd = py_user, py_psw, ssc_user, ssc_psw
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
			# todo 兼容关盘提示
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

	def post_number(self, number_array, money):
		info_array = []
		for number in number_array:
			info_array.append('%s|%s' % (number, money))
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
		order_id = ''
		validity = False
		if mock_post:
			return True, message, 'mock_order'
		response = requests.post(url, data, headers=headers)
		self.check_response(response)
		if response.status_code != 200:
			message = response.text
		else:
			validity = True
			result = response.json()
			order_id = result.get('order_id')
			message = result.get('data')
			if order_id:
				self.fail_count = 0
		return validity, message, order_id

	def revoke(self, order_id):
		url = '%s/cancel/order' % self.service
		headers = {
			'Authorization': self.token
		}
		data = {
			'id': order_id
		}
		validity = False
		self.log.debug('--> url:%s, data:%s, headers:%s' % (url, data, headers))
		response = requests.post(url, data, headers=headers)
		self.check_response(response)
		if response.status_code != 200:
			message = response.text
		else:
			message = '退码成功'
			validity = True
		return validity, message

	def check_login(self):

		print('============= Bet助手v1 =============\n')
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

	def get_base_url(self):
		response = requests.get(self.config.base_url)
		if response.status_code != 200:
			return self.config.base_url
		else:
			selector = etree.HTML(response.text)
			urls = selector.xpath("//a[@class='best']/@data-testurl")
			return get_superior_site(urls)

	def check_response(self, response):
		self.log.debug(response.text)
		if response.text in 'MemberLogin.aspx' or response.status_code == 401:
			self.raise_login()

	def raise_login(self):
		if self.fail_count > 5:
			raise Exception('账号异常')
		self.fail_count += 1
		self.config.token = ""
		self.config.save_config()
		print('警告：登陆过期，正在重启程序！！！！')
		raise AuthError()

	def query_answer(self):
		url = '%s/lot/ret' % self.service
		headers = {
			'Authorization': self.token
		}
		self.log.debug('--> url:%s, headers:%s' % (url, headers))
		response = requests.post(url, headers=headers)
		self.check_response(response)
		if response.status_code != 200:
			self.log.error(response.text)
		else:
			result = response.text
			answer_array = result.split('@')
			if len(answer_array) > 1:
				current_no = answer_array[0].split('=')[1]
				last_answer = answer_array[1].split('=')
				if last_answer[2] and last_answer[2].strip():
					last_number = '%s%s%s%s%s' % (last_answer[2], last_answer[3], last_answer[4], last_answer[5], last_answer[6])
					last_no = last_answer[1]
					return current_no, {"no": last_no, "number": last_number}
		return None, None
