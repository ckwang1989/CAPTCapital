import os
import datetime
import requests
import Stock_history

def check_folder(path):
	if not os.path.exists(path):
		os.makedirs(path)

def load_close(stock_symbol):
	Open_last, High_last, Low_last, Close_last, Volume_last = 0, 0, 0, 0, 0
	stock_tech_idx_dict = {}
	closes = []
	with open(f'stock_temp/file_{stock_symbol}.csv', 'r') as file_read:
		for line in reversed(file_read.readlines()[-180:]):
			line = line.split(',')
			if 'Date' in line:
				continue
			Date, Open, High, Low, Close, Adj_Close, Volume = line[0+1], line[1+1], line[2+1], line[3+1], line[4+1], line[5+1], (line[6+1].strip('\n'))
			if Open == 'null' or High == 'null' or Low == 'null' or Close == 'null' or Volume == 'null':
				Open, High, Low, Close, Volume = Open_last, High_last, Low_last, Close_last, Volume_last
			closes.append(Close)
		return closes
#			stock_tech_idx_dict[Date] = {'Close': float(Close)}
#			Open_last, High_last, Low_last, Close_last, Volume_last = Open, High, Low, Close, Volume
#		return stock_tech_idx_dict

def correlation_day(s1, s2):
	A = Stock_history.sum()
	A.Stock_price(s1)
	A.Stock_price(s2)
	c1 = load_close(s1)
	c2 = load_close(s2)
	count = 0
	for i in range(len(c1)-1):
		stock = c1[i] > c1[i+1]
		etf = c2[i] > c2[i+1]
		if stock == etf:
			count += 1
		else:
			break
	print (count)


if __name__ == '__main__':
	correlation_day('AMD', 'SPY')