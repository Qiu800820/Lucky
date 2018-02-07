#!/usr/bin/python
# -*- coding: UTF-8 -*-
import traceback

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
		self.two_star_list = []

	def setupUi(self, Lucky):
		super(UI, self).setupUi(Lucky=Lucky)
		self.strategySlider.valueChanged.connect(self.lcdNumber.display)
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
		percent = self.lcdNumber.value() / 100
		button_status_chang(self.statistics, disabled=True)  # 按钮防抖
		try:
			self.get_strategy()
			self.show_two_star_result(percent)
		except Exception as e:
			self.show_toast(message=e)
			traceback.print_exc(file=open('log.txt', 'a+'))
		finally:
			button_status_chang(self.statistics, disabled=False)

	def get_strategy(self):
		# todo
		return {}

	def show_toast(self, message):
		QMessageBox.information(self, "Lucky", str(message), QMessageBox.Yes)

	def show(self):
		super(UI, self).show()
		self.show_answer()

	def show_two_star_result(self, strategy):
		self.result_table.clearContents()
		self.two_star_list = self.core.get_two_star_by_strategy(strategy)

		row = 0
		size = len(self.two_star_list)
		self.result_table.setRowCount(size)
		self.label_3.setText(str(size))
		for two_star in self.two_star_list:
			self.result_table.setItem(row, 0, QtWidgets.QTableWidgetItem(two_star['id']))
			self.result_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(two_star['weight'])))
			self.result_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(two_star['avg_omit_number'])))
			self.result_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(two_star['max_omit_number'])))
			self.result_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(two_star['current_omit_number'])))
			row += 1

	def show_answer(self):
		self.answer_table.clearContents()
		answer_list = self.core.get_today_answer()
		new_answer_list = []
		for answer in answer_list:
			new_answer_list.append(answer)

		self.answer_table.setRowCount(len(new_answer_list))
		row = 0
		for answer in new_answer_list:
			self.answer_table.setItem(row, 0, QtWidgets.QTableWidgetItem(answer['no']))
			self.answer_table.setItem(row, 1, QtWidgets.QTableWidgetItem(answer['number']))
			row += 1

	def lucky_lucky(self):
		number_list = []
		for two_star in self.two_star_list:
			number_list.append(two_star['id'])
		self.result_edit.setText(','.join(number_list))


def button_status_chang(button, disabled):
	button.setDisabled(disabled)
