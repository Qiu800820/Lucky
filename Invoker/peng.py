import math

from Invoker.core.config import Config
from Invoker.core.fetch import Fetch
from Invoker.db.ssc_dao import AwardObject

config = Config()
award = AwardObject()


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


def refresh_data():
	print('获取最新开奖数据...')
	fetch = Fetch()
	fetch.refresh_answer()


def main_v1(step=10):
	print('============= 时时彩助手v1 =============\n\n')
	max = award.get_max()
	refresh_data()
	count_money = 0
	get_numbers = None
	while not get_numbers:
		no_id = input('请选择打码策略：\n1：头尾1-8, 除上期头尾合分\n2：头尾除9, 除上期头尾合分, 除上期第5球\n')
		if no_id == '1':
			get_numbers = get_numbers1
		elif no_id == '2':
			get_numbers = get_numbers2
		else:
			print('输入格式错误,请数据策略对应数字')
	while True:
		py_no = int(input('请输入开始模拟期号: 当前最大期数:%s' % max))
		py_end_no = int(input('请输入结束模拟期号: 当前最大期数:%s' % max))
		if py_no and py_end_no:
			money_count = 0
			start_period = py_no
			loop = int(math.ceil((py_end_no - py_no) / step))
			for i in range(loop):
				if config.max_shu > money_count or config.max_ying < money_count:
					print('模拟结束 --- 超出止损止盈！！！')
					break
				if start_period >= max:
					print('模拟结束 --- 超出当前号码期数！！！')
					break

				end_period = start_period + step
				bingo_count, bingo_money, number_count = award.count_bingo(end_period, get_numbers, start_period - 1, 1)
				money = (bingo_money - number_count) * config.bet
				money_count += money
				print("%s - %s期盈利数据 --- 成本：%s, 中奖次数：%s, 盈利：%s, 总盈利：%s" % (
					start_period, end_period, number_count * config.bet, bingo_count, money, money_count
				))  # 盈利数据
				start_period = end_period
			print("总盈利：%s" % money_count)
			input("请按回车键退出程序")
			return None

		else:
			print('输入格式有误')


if __name__ == '__main__':
	main_v1(10)
