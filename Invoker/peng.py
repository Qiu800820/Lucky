from Invoker.core.fetch import Fetch
from Invoker.db.ssc_dao import AwardObject, TwoStarObject, Config, OmitLogObject
import math


award = AwardObject()


def get_numbers(last_number):
	if not last_number:
		return None
	no_array = []
	number = (int(last_number[0]) + int(last_number[3])) % 10
	for i in range(1, 9):
		for j in range(1, 9):
			if number != ((i + j) % 10):
				no_array.append('%sXX%s' % (i, j))
	return no_array


def refresh_data():
	print('获取最新开奖数据...')
	fetch = Fetch()
	fetch.refresh_answer()


def main_v1(step=10):
	print('============= 时时彩助手v1 =============\n\n')
	max = award.get_max()
	refresh_data()
	complete = False
	while not complete:
		py_no = int(input('请输入开始模拟期号: 当前最大期数:%s' % max))
		py_end_no = int(input('请输入结束模拟期号: 当前最大期数:%s' % max))
		if py_no and py_end_no:
			money_count = 0
			start_period = py_no
			loop = int(math.ceil((py_end_no - py_no) / step))
			for i in range(loop):
				if start_period >= max:
					print('模拟结束 --- 超出当前号码期数！！！')
					break

				end_period = start_period + step
				bingo_count, bingo_money, number_count = award.count_bingo(end_period, get_numbers, start_period - 1, 1)
				money = (bingo_money - number_count) * 50
				money_count += money
				print("%s - %s期盈利数据 --- 成本：%s, 中奖次数：%s, 盈利：%s, 总盈利：%s" % (
					start_period, end_period, number_count * 50, bingo_count, money, money_count
				))  # 盈利数据
				start_period = end_period
			print("总盈利：%s" % money_count)
			return None

		else:
			print('输入格式有误')


if __name__ == '__main__':
	main_v1(10)
