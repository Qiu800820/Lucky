#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

from PyQt5.QtWidgets import QApplication

from db.ssc_dao import AwardObject, AwardObject
from ui.ui import UI


def run():
	# 加载窗口
	app = QApplication(sys.argv)
	ui = UI()
	ui.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	run()
