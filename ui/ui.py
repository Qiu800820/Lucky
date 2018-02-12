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
		self.two_star_list = []

	def setupUi(self, Lucky):
		super(UI, self).setupUi(Lucky=Lucky)
		self.strategySlider.valueChanged.connect(self.lcdNumber.display)
		self.refresh.clicked.connect(self.refresh_answer)
		self.statistics.clicked.connect(self.statistics_two_star)
		self.lucky.clicked.connect(self.lucky_lucky)

		self.checkBox.stateChanged.connect(self.check_other)
		self.checkBox_2.stateChanged.connect(self.check_other)
		self.checkBox_3.stateChanged.connect(self.check_other)
		self.checkBox_4.stateChanged.connect(self.check_other)
		self.checkBox_5.stateChanged.connect(self.check_other)
		self.checkBox_6.stateChanged.connect(self.check_other)
		self.checkBox_7.stateChanged.connect(self.check_other)
		self.checkBox_8.stateChanged.connect(self.check_other)
		self.checkBox_9.stateChanged.connect(self.check_other)
		self.checkBox_10.stateChanged.connect(self.check_other)
		self.checkBox_11.stateChanged.connect(self.check_all)

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
			strategy = self.get_strategy()
			self.show_two_star_result(percent, strategy['sort_type'], strategy['position_list'])
		except Exception as e:
			self.show_toast(message=e)
			traceback.print_exc(file=open('log.txt', 'a+'))
		finally:
			button_status_chang(self.statistics, disabled=False)

	def get_strategy(self):
		position_list = []
		if self.checkBox_11.isChecked():
			position_list.append(None)
		else:
			if self.checkBox.isChecked():
				position_list.append('__XXX')
			if self.checkBox_2.isChecked():
				position_list.append('_X_XX')
			if self.checkBox_3.isChecked():
				position_list.append('_XX_X')
			if self.checkBox_4.isChecked():
				position_list.append('_XXX_')
			if self.checkBox_5.isChecked():
				position_list.append('X__XX')
			if self.checkBox_6.isChecked():
				position_list.append('X_X_X')
			if self.checkBox_7.isChecked():
				position_list.append('X_XX_')
			if self.checkBox_8.isChecked():
				position_list.append('XX__X')
			if self.checkBox_9.isChecked():
				position_list.append('XX_X_')
			if self.checkBox_10.isChecked():
				position_list.append('XXX__')
		if self.radioButton.isChecked():
			sort_type = 'max_omit_weight'
		else:
			sort_type = 'avg_omit_weight'
		return {"sort_type": sort_type, "position_list": position_list}

	def show_toast(self, message):
		QMessageBox.information(self, "Lucky", str(message), QMessageBox.Yes)

	def show(self):
		super(UI, self).show()
		self.show_answer()

	def show_two_star_result(self, sort_percent, sort_type, position_list):
		self.result_table.clearContents()
		self.two_star_list = self.core.get_two_star_by_strategy(sort_percent, sort_type, position_list)

		row = 0
		size = len(self.two_star_list)
		self.result_table.setRowCount(size)
		self.label_3.setText(str(size))
		for two_star in self.two_star_list:
			self.result_table.setItem(row, 0, QtWidgets.QTableWidgetItem(two_star['id']))
			self.result_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(two_star[sort_type])))
			self.result_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(two_star['avg_omit_number'])))
			self.result_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(two_star['current_omit_number'])))
			self.result_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(two_star['max_omit_number'])))
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

	def check_all(self):
		if self.checkBox_11.isChecked():
			self.checkBox.setChecked(False)
			self.checkBox_2.setChecked(False)
			self.checkBox_3.setChecked(False)
			self.checkBox_4.setChecked(False)
			self.checkBox_5.setChecked(False)
			self.checkBox_6.setChecked(False)
			self.checkBox_7.setChecked(False)
			self.checkBox_8.setChecked(False)
			self.checkBox_9.setChecked(False)
			self.checkBox_10.setChecked(False)

	def check_other(self, state):
		if state == QtCore.Qt.Checked:
			self.checkBox_11.setChecked(False)

	def lucky_lucky(self):
		# self.result_table.currentItem().row()
		number_list = []
		for two_star in self.two_star_list:
			number_list.append(two_star['id'])
		self.result_edit.setText(','.join(number_list))


def button_status_chang(button, disabled):
	button.setDisabled(disabled)
