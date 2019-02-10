import math
import time

from Bet.core.config import Config
from Bet.core.log import Log
from Bet.core.translate import Translate
from Bet.core.fetch import Fetch

log = Log()
# 重要配置
config = Config()
# 译码服务
translate = Translate(config, log)

fetch = Fetch()

Odds = [0, 9, 99, 999, 9990, 99900]


def run():
	count_money = 0
	bet_no = '0'
	settle_no = '1'
	no_array = []
	while math.fabs(count_money) < config.max:
		answer = get_answer()
		if settle_no == answer.get('no'):
			money = 0
			for number in no_array:
				money = check_bingo(answer.get('number'), number)
				if money > 0:
					break
			count_money += money
			log.info('=== %s期开奖结果%s, 本期盈利%s 总盈利%s===' % (answer.get('no'), answer.get('number'), money, count_money))
		elif bet_no != answer.get('no'):
			no_array = get_numbers(answer.get('number'))
			log.info('=== %s期开奖结果%s, 本期打码%s ===' % (answer.get('no'), answer.get('number'), no_array))
			if no_array and len(no_array) > 0:
				info_array = []
				for number in no_array:
					info_array.append('%s|%s' % (number, config.bet))
				info = ','.join(info_array)
				validity, message, order_id = translate.post_number(info)
				if validity and order_id:
					bet_no = answer.get('no')
					settle_no = next_no(bet_no)
					log.info('=== %s期下单成功 ===' % settle_no)
				else:
					log.error('=== 下单失败, 失败原因:%s ===' % message)
		else:
			time.sleep(30)
	print('=== 总盈利%s 超出止损止盈范围 ===' % count_money)


def get_numbers(last_number):
	if not last_number:
		return None
	no_array = []
	number = (int(last_number[0]) + int(last_number[3])) % 10
	for i in range(1, 9):
		for j in range(1, 9):
			if number != ((i + j) % 10):
				no_array.append(config.position % (i, j))
	return no_array


def get_answer():
	item, history = fetch.query_answer()
	return item or {'no': '0', 'number': ''}


def next_no(no):
	day_sec = int(time.mktime(time.strptime(no[:6], '%y%m%d')))
	day_no = int(no[6:]) + 1
	if day_no > 120:
		day_sec += 86400
		day_no -= 120
	return '%s%s' % (time.strftime('%y%m%d', time.localtime(day_sec)), day_no)


def check_bingo(award, no):
	bingo_number_count = 0
	for i in range(len(no)):
		if no[i] == 'X':
			continue
		if no[i] != award[i]:
			bingo_number_count = 0
			break
		else:
			bingo_number_count += 1
	money = Odds[bingo_number_count]
	return money
