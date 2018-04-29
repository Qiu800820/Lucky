#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

from PyQt5.QtWidgets import QApplication

from core.core import Core
from db.ssc_dao import AwardObject, AwardObject
from Invoker.ui import UI


def run():
	# 加载窗口
	app = QApplication(sys.argv)
	ui = UI()
	ui.show()
	sys.exit(app.exec_())


def test():
	core = Core()
	# no_array = ['34XXX', '66XXX', '78XXX', '87XXX', '57XXX', '93XXX', '97XXX', '67XXX', '12XXX', '74XXX', '08XXX', '69XXX', '56XXX', '18XXX', '91XXX', '27XXX', '01XXX', '72XXX', '52XXX', '41XXX', '10XXX', '28XXX', '31XXX', '95XXX', '68XXX', '39XXX', '33XXX', '24XXX', '90XXX', '16XXX', '20XXX', '64XXX', '30XXX', '94XXX', '07XXX', '76XXX', '29XXX', '58XXX', '23XXX', '83XXX', '19XXX', '11XXX', '61XXX', '46XXX', '65XXX', '51XXX', '63XXX', '17XXX', '89XXX', '79XXX']
	# for i in range(100):
	# 	period = 258000 + i * 120
	# 	core.get_regression_cycle_v2(period, 50, no_array)
	# core.get_regression_cycle(50000)
	# core.get_regression_cycle(10000, 10000, 50000, 20)
	core.get_max_drop_regression(270000, 50)

if __name__ == '__main__':
	run()
	# test()
