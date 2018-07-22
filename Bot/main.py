#!/usr/bin/python
# -*- coding: UTF-8 -*-


def balance():
	from Bot.core.config import Config
	from Bot.core.db.bot_dao import BotDao
	from Bot.core.log import Log
	config = Config()
	log = Log()
	botDao = BotDao(config.odds, log)
	botDao.accounting('180722080', '19304', True)
	pass


def run():
	from Bot.core.core import run
	run()

if __name__ == '__main__':
	run()
	# balance()
