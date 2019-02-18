import time
import tkinter.messagebox

from Bet.core.config import Config
from Bet.core.fetch import Fetch
from Bet.core.follow import Follow
from Bet.core.log import Log
from Bet.core.translate import Translate, AuthError

log = Log()
# 重要配置
config = Config()
# 译码服务
translate = Translate(config, log)

fetch = Fetch()

Odds = [0, 9, 99, 999, 9990, 99900]


def run():
	count_money = 0
	settle_no = '1'
	spacing = 60
	follow = None
	get_numbers = None
	#  选择策略
	while not get_numbers:
		no_id = input('请选择打码策略：\n1：头尾1-8, 除上期头尾合分\n2：头尾除9, 除上期头尾合分, 除上期第5球\n3：跟投')
		if no_id == '1':
			get_numbers = get_numbers1
			print('=== 正在监听最新开奖号码， 上次投注:%s期 ===' % config.last_no.get(no_id))
		elif no_id == '2':
			get_numbers = get_numbers2
			print('=== 正在监听最新开奖号码， 上次投注:%s期 ===' % config.last_no.get(no_id))
		elif no_id == '3':
			spacing = config.follow_spacing
			follow = Follow(config.agent_url, log)
			print('=== 上期跟投至:%s ===' % config.last_order_id)
			get_numbers = get_numbers1
		else:
			print('输入格式错误,请数据策略对应数字')
	# 输出账户余额
	status, current_money = inventory_v2()
	if status:
		print('=== 账户余额:%s ===' % current_money)
	else:
		print('=== 获取账户余额失败 ===')
	while config.max_shu < count_money < config.max_ying:
		try:
			current_no, last_answer = get_answer()
			if settle_no == last_answer.get('no') and last_answer.get('number'):
				status, money = inventory_v2()
				if status:
					settle_money = money - current_money
					settle_no = '1'
					count_money += settle_money
					log.info('=== %s期开奖结果%s, 本期盈利%s 总盈利%s===' % (last_answer.get('no'), last_answer.get('number'), settle_money, count_money))
					current_money = money
			elif follow:
				if current_no != '0':
					no_array = follow.follow(current_no, config.last_order_id)
					if no_array and len(no_array) > 0:
						info_array = []
						for no in no_array:
							info_array.append('%s|%s' % (no.get('bet_number'), no.get('bet_money')))
						info = ','.join(info_array)
						log.info('=== 跟码%s ===' % info)
						if len(info_array) > 6000:
							log.warning('=== 一次性打码超过6000组容易失败或者漏码，请注意检查 ===')
						validity, message, order_id = translate.post_number(info)
						if validity and order_id:
							config.last_order_id = no_array[0]['order_id']
							settle_no = current_no
							config.save_config()
							log.info('=== 跟码成功 ===')
						else:
							log.error('=== 跟码失败, 失败原因:%s ===' % message)
							translate.raise_login()
					else:
						log.info('=== 暂无新号码 ===')
				time.sleep(spacing)

			elif config.last_no.get(no_id) != current_no and last_answer.get('number'):
				no_array = get_numbers(last_answer.get('number'))
				log.info('=== %s期开奖结果%s, 本期打码%s ===' % (last_answer.get('no'), last_answer.get('number'), no_array))
				if no_array and len(no_array) > 0:
					info_array = []
					for number in no_array:
						info_array.append('%s|%s' % (number, config.bet))
					info = ','.join(info_array)
					validity, message, order_id = translate.post_number(info)
					if validity and order_id:
						config.last_no[no_id] = current_no
						settle_no = current_no
						config.save_config()
						log.info('=== %s期下单成功 ===' % settle_no)
					else:
						log.error('=== 下单失败, 失败原因:%s ===' % message)
						translate.raise_login()
			else:
				time.sleep(spacing)
		except Exception as e:
			log.error('程序发生未知错误,请联系开发人员进行调整', e)
			translate.relogin()

	print('=== 总盈利%s 超出止损止盈范围 ===' % count_money)
	input('请按回车键退出程序!!!')


def inventory(last_answer, no_array):
	money = 0
	for number in no_array:
		money = check_bingo(last_answer.get('number'), number)
		if money > 0:
			break
	principal = len(no_array) * config.bet
	money -= principal
	return True, money


def inventory_v2():
	money, statue = 0, False
	try:
		result = translate.get_my_money()
		my_info = result.split('#')[1]
		money = float(my_info.split('$')[5])
		statue = True
	except Exception as e:
		pass
	return statue, money


def get_numbers1(last_number):
	if not last_number:
		return None
	no_array = []
	number = (int(last_number[0]) + int(last_number[3])) % 10
	for i in range(1, 9):
		for j in range(1, 9):
			if number != ((i + j) % 10):
				no_array.append(config.position % (i, j))
	return no_array


def get_numbers2(last_number):
	if not last_number:
		return None
	no_array = []
	number = (int(last_number[0]) + int(last_number[3])) % 10
	numbers = [i for i in range(0, 9)]
	numbers.remove(int(last_number[4]))  # 除第5球
	for i in numbers:  # 除上期合码
		for j in numbers:
			if number != ((i + j) % 10):
				no_array.append(config.position % (i, j))
	return no_array


def get_answer():
	current_no, last_answer = translate.query_answer()
	if not current_no:
		current_no = '0'
	if not last_answer:
		last_answer = {'no': '0', 'number': ''}
	return current_no, last_answer


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