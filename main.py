#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

from PyQt5.QtWidgets import QApplication

from core.core import Core
from db.ssc_dao import AwardObject, AwardObject
from ui.ui import UI


def run():
	# 加载窗口
	app = QApplication(sys.argv)
	ui = UI()
	ui.show()
	sys.exit(app.exec_())


def test():
	core = Core()

	for i in range(100):
		core.get_regression_cycle(70000 + i * 2000)

if __name__ == '__main__':
	# run()
	test()
