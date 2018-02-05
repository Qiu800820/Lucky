#!/usr/bin/python
# -*- coding: UTF-8 -*-


class Log:

	def __init__(self, print_level):
		self.print_level = print_level

	def log(self, level=0, *args):
		if level > self.print_level:
			print(*args)


