#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sched


class TimeRunning:

	def __init__(self):
		self.schedule = sched.scheduler()

	def running(self, delay_time, func, *args):
		self.schedule.enter(delay_time, 0, self.running, (delay_time, func, *args))
		self.schedule.enter(0, 0, func, *args)

	def delay_run(self, delay_time, func, *args):
		self.schedule.enter(delay_time, 0, self.running, (delay_time, func, *args))
		self.schedule.run()

