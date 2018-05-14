#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

mock_data = """{
	'MsgId': '8862234331128478280',
	'AppMsgType': 0,
	'ImgStatus': 1,
	'EncryFileName': '',
	'SubMsgType': 0,
	'FileSize': '',
	'StatusNotifyCode': 0,
	'Status': 3,
	'ActualUserName': '@5b282b03a5aede2d8e6fb02618b68aef7edb110bf9f1dd303fdabe2b10d3c0ce',
	'Content': '今天去哪玩',
	'Url': '',
	'MsgType': 1,
	'RecommendInfo': {
		'Province': '',
		'City': '',
		'Content': '',
		'NickName': '',
		'QQNum': 0,
		'AttrStatus': 0,
		'Sex': 0,
		'Signature': '',
		'Ticket': '',
		'Alias': '',
		'Scene': 0,
		'VerifyFlag': 0,
		'UserName': '',
		'OpCode': 0
	},
	'FromUserName': '@@c2184ae9b596f9ba28c4999f6dccca0d2a639409fda18c1808dc86536ddeef4c',
	'ForwardFlag': 0,
	'PlayLength': 0,
	'ToUserName': '@da0669e1c33a4b1ee7afee29197b139a',
	'HasProductId': 0,
	'StatusNotifyUserName': '',
	'ImgHeight': 0,
	'AppInfo': {
		'Type': 0,
		'AppID': ''
	},
	'FileName': '',
	'ActualNickName': 'sum',
	'Text': '今天去哪玩',
	'NewMsgId': 8862234331128478280,
	'ImgWidth': 0,
	'Type': 'Text',
	'CreateTime': 1526278352,
	'OriContent': '',
	'isAt': False,
	'MediaId': '',
	'VoiceLength': 0,
	'Ticket': ''
}"""


class itchat():

	def auto_login(self, hotReload):
		print('账号登陆')

	def search_chatrooms(self):
		return [{'UserName': 'SSC'}]

	def send(self, msg, toUserName):
		print('msg: %s, userName: %s' % msg, toUserName)

	def send_image(self, msg, toUserName):
		print('image, userName: %s' % msg, toUserName)

	def search_friends(self, name):
		return [{'UserName': 'Boss'}]

	def mock_run(self, received, command):
		while True:
			time.sleep(10)
