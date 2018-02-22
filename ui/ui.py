#!/usr/bin/python
# -*- coding: UTF-8 -*-
import traceback
from PyQt5 import QtCore

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from core.core import Core
from ui.lucky import Ui_Lucky


class UI(QtWidgets.QMainWindow, Ui_Lucky):
	def __init__(self):
		# 窗口初始化配置
		super(UI, self).__init__()
		self.setupUi(self)
		self.core = Core()
		self.two_star_team_list = []
		self.two_star_result_dist = {}

	def setupUi(self, Lucky):
		super(UI, self).setupUi(Lucky=Lucky)
		self.refresh.clicked.connect(self.refresh_answer)
		self.statistics.clicked.connect(self.statistics_two_star)
		self.lucky.clicked.connect(self.lucky_lucky)

	# 刷新开奖结果
	def refresh_answer(self):
		button_status_chang(self.refresh, disabled=True)  # 按钮防抖
		try:
			self.core.refresh_answer()
			self.show_answer()
		except Exception as e:
			self.show_toast(message=e)
			traceback.print_exc(file=open('log.txt', 'a+'))
		finally:
			button_status_chang(self.refresh, disabled=False)

	# 重新计算结果
	def statistics_two_star(self):

		button_status_chang(self.statistics, disabled=True)  # 按钮防抖
		try:
			strategy = self.get_strategy()
			self.show_two_star_result(strategy['position_list'])

		except Exception as e:
			self.show_toast(message=e)
			traceback.print_exc(file=open('log.txt', 'a+'))
		finally:
			button_status_chang(self.statistics, disabled=False)

	def get_strategy(self):
		position_list = []
		if self.checkBox.isChecked():
			position_list.append('__XXX')
		if self.checkBox_2.isChecked():
			position_list.append('_X_XX')
		if self.checkBox_3.isChecked():
			position_list.append('_XX_X')
		if self.checkBox_6.isChecked():
			position_list.append('X_X_X')
		if self.checkBox_7.isChecked():
			position_list.append('X__XX')
		if self.checkBox_8.isChecked():
			position_list.append('XX__X')
		return {"position_list": position_list}

	def show_toast(self, message):
		QMessageBox.information(self, "Lucky", str(message), QMessageBox.Yes)

	def show(self):
		super(UI, self).show()
		self.show_answer()

	def show_two_star_result(self, position_list):
		self.result_table.clearContents()
		self.two_star_team_list, self.two_star_result_dist = self.core.get_two_star_by_strategy_v2(position_list)

		row = 0
		size = len(self.two_star_team_list)
		self.result_table.setRowCount(size)
		self.label_3.setText(str(size))
		for two_star in self.two_star_team_list:
			self.result_table.setItem(row, 0, QtWidgets.QTableWidgetItem(two_star['position']))  # 位置
			self.result_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(two_star['size'])))  # 组合数
			self.result_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(two_star['avg_percent'])))  # 组合平均概率
			self.result_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(two_star['perfect_percent'])))  # 组合理论概率
			self.result_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(two_star['weight'])))  # 权重
			row += 1

	def show_answer(self):
		self.answer_table.clearContents()
		answer_list = self.core.get_today_answer()
		new_answer_list = []
		for answer in answer_list:
			new_answer_list.append(answer)
		if len(new_answer_list) != 0:
			self.answer_table.setRowCount(len(new_answer_list))
			row = 0
			for answer in new_answer_list:
				self.answer_table.setItem(row, 0, QtWidgets.QTableWidgetItem(answer['no']))
				self.answer_table.setItem(row, 1, QtWidgets.QTableWidgetItem(answer['number']))
				row += 1
		else:
			self.show_toast('今日未开奖！')

	def lucky_lucky(self):
		index = self.result_table.currentItem().row()
		two_star_team = self.two_star_team_list[index]
		two_star_list = self.two_star_result_dist.get(two_star_team['position'])
		number_list = []
		for two_star in two_star_list:
			number_list.append(two_star['no'])
		self.result_edit.setText(','.join(number_list))


def button_status_chang(button, disabled):
	button.setDisabled(disabled)
