import os
import sys
sys.path.insert(0, 'module')

from module.Strategy_option import strategy_option
from module.common import to_excel

# 市場 / 進or出 / 策略 / 進場觸發觸發指標(key) / 股票名稱 / ETF名稱 / 履約價 / 履約日期 / 相似天數 / 觸發進場策略 / 觸發出場策略
def main():
    stocks_num = 'stock_num.txt'
    outputs = []
    for stock_name in open(stocks_num, 'r').readlines():
        stock_name = stock_name.strip()
        print (f'{stock_name}')
        output = strategy_option(stock_name)
        if output:
            print (f'{output}')
            outputs.append(output)
    to_excel(outputs)
if __name__ == '__main__':
    main()