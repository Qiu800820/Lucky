#!/usr/bin/python
# -*- coding: UTF-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from core.core import Core
from ui.window import Ui_Lucky


class UI(QtWidgets.QMainWindow, Ui_Lucky):
	def __init__(self):
		# 窗口初始化配置
		super(UI, self).__init__()
		self.setupUi(self)
		self.core = Core()

	# 刷新开奖结果
	def refresh_answer(self):
		self.button_status_chang(clickable=False)  # 按钮防抖
		try:
			self.core.refresh()
		except Exception as e:
			self.show_toast(message=e)
		finally:
			self.button_status_chang(clickable=True)

	def button_status_chang(self, clickable):
		print('刷新按钮点击状体%s' % clickable)

	def show_toast(self, message):
		print('显示信息 %s', message)

	def show(self):
		super(UI, self).show()
		self.show_answer()

	def show_answer(self):
		print('asd')
