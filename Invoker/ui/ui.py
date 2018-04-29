#!/usr/bin/python
# -*- coding: UTF-8 -*-
import traceback

import sys
from PyQt5 import QtCore

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox


from core.core import Core
from Invoker.ui import Ui_Lucky


class UI(QtWidgets.QMainWindow, Ui_Lucky):
	def __init__(self):
		# 窗口初始化配置
		super(UI, self).__init__()
		self.setupUi(self)
		self.core = Core()
		self.two_star_team_list = []

	def setupUi(self, Lucky):
		super(UI, self).setupUi(Lucky=Lucky)
		self.refresh.clicked.connect(self.refresh_answer)
		self.statistics.clicked.connect(self.statistics_two_star)
		self.lucky.clicked.connect(self.lucky_lucky)
		self.lucky_2.clicked.connect(self.mock_lucky)
		self.horizontalSlider.valueChanged.connect(self.lcdNumber.display)

		# sys.stdout = EmittingStream(textWritten=self.normal_output_written)
		# sys.stderr = EmittingStream(textWritten=self.normal_output_written)

	# 刷新开奖结果
	def refresh_answer(self):
		button_status_chang(self.refresh, disabled=True)  # 按钮防抖
		try:
			self.core.refresh_answer()
			self.show_answer()
			self.lineEdit.setText(str(self.core.get_award_total()))
		except Exception as e:
			self.show_toast(message=e)
			traceback.print_exc(file=open('log.txt', 'a+'))
		finally:
			button_status_chang(self.refresh, disabled=False)

	# 重新计算结果
	def statistics_two_star(self):

		button_status_chang(self.statistics, disabled=True)
		try:
			strategy = self.get_strategy()
			self.show_two_star_result(**strategy)

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
		group_size = int(self.lcdNumber.value())
		step = self.spinBox.value()
		loop = self.spinBox_2.value()
		mock_step = self.spinBox_3.value()
		mock_loop = self.spinBox_4.value()
		try:
			start_period = int(self.lineEdit.text())
		except Exception as e:
			self.show_toast('数据量输入无效， 只能填写数字！')
			traceback.print_exc(file=open('log.txt', 'a+'))
			self.lineEdit.setText('50000')
			start_period = 50000
		return {
			"position_list": position_list, 'group_size': group_size, 'step': step, 'loop': loop, 'mock_step': mock_step,
			'mock_loop': mock_loop, 'start_period': start_period
		}

	def show_toast(self, message):
		QMessageBox.information(self, "Lucky", str(message), QMessageBox.Yes)

	def show(self):
		super(UI, self).show()
		self.show_answer()

	def show_two_star_result(self, **statistics):
		self.result_table.clearContents()
		self.two_star_team_list = self.core.get_two_star_by_strategy_v3(
			statistics['group_size'], statistics['step'], statistics['loop'], statistics['position_list'], statistics['start_period'])

		row = 0
		size = len(self.two_star_team_list)
		self.result_table.setRowCount(size)
		self.label_3.setText(str(size))
		for two_star in self.two_star_team_list:
			self.result_table.setItem(row, 0, QtWidgets.QTableWidgetItem(two_star['position']))  # 位置
			self.result_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(two_star['group_size'])))  # 组合数
			self.result_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(two_star['regression_count'])))  # 偏差下降数
			self.result_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(two_star['regression_percent'])))  # 偏差下降率
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

	def mock_lucky(self):
		# UI 缺少期数参数
		strategy = self.get_strategy()
		text = self.result_edit.toPlainText()
		no_array = None
		if text:
			no_array = text.split(',')
		if no_array:
			result = self.core.mock_lucky(strategy['start_period'], no_array, strategy['mock_step'], strategy['mock_loop'])
			self.textEdit.setText(result)

		else:
			self.show_toast('生成号码组为空， 不能模拟盈利数据')

	def lucky_lucky(self):
		index = self.result_table.currentItem().row()
		two_star_team = self.two_star_team_list[index]
		two_star_list = two_star_team.get('regression_array')
		self.result_edit.setText(','.join(two_star_list))

	def __del__(self):
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__


class EmittingStream(QtCore.QObject):

	textWritten = QtCore.pyqtSignal(str)

	def write(self, text):
		self.textWritten.emit(str(text))


def button_status_chang(button, disabled):
	button.setDisabled(disabled)
