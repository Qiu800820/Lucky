#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Tkinter import Tk

from core.core import Core


class UI:
	def __init__(self):
		# 窗口初始化配置
		self.core = Core()
		self.window = Tk()

	# 刷新开奖结果
	def refresh_answer(self):
		self.button_status_chang(clickable=False)  # 按钮防抖
		is_complete, message = self.core.refresh_answer()
		self.button_status_chang(clickable=True)
		if not is_complete:
			self.show_toast(message=message)

	def button_status_chang(self, clickable):
		print('刷新按钮点击状体%s' % clickable)

	def show_toast(self, message):
		print('显示信息 %s', message)

	def show(self):
		self.window.mainloop()
		print('显示窗口')
