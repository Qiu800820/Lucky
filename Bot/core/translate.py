#!/usr/bin/python
# -*- coding: UTF-8 -*-
from requests import Session


class Translate:

	def __init__(self, service):
		self.service = service
		self.session = Session()
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
		}

	def login(self, params):
		url = "%s/Default.aspx" % self.service  # 初始化Cookie
		response = self.session.get(url, headers=self.headers)
		url = "%s/MemberLogin.aspx?%s" % (self.service, params)
		response = self.session.post(url)
		print(response.text)

	def prepare(self, info):
		url = "%s/weixinImport.aspx" % self.service
		data = {
			'action': 'CreateData',
			'info': info
		}
		response = self.session.post(url, data)
		return response.text





