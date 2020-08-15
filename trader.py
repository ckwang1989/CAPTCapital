import os
import sys
import copy
sys.path.insert(0, 'module')

from module.Strategy_option import strategy_option
from module.common import to_excel

import multiprocessing
from multiprocessing import Process
from multiprocessing import queues

result_all = []

class Trader(object):
    def call(self, process_id, symbol_queues):
        while not symbol_queues.empty():
            symbol = symbol_queues.get()
            print (f'process_id: {process_id}, symbol: {symbol}')
            output = strategy_option(symbol)
            if output:
                result_all.append(output)
            print (symbol, len(result_all))
            to_excel(result_all)

class Boss(object):
    def __init__(self, symbols):
        self.num_worker = 4
        self.stock_queues = queues.Queue(len(symbols), ctx=multiprocessing)
        for symbol in symbols:
            self.stock_queues.put(symbol)
        self.workers = []

    def hire_worker(self):
        """
        using multiprocess to process .csv, we will enable self.num_worker thread to process data
        """
        for i in range(self.num_worker):
            trader = copy.deepcopy(Trader())
            print ('worker {}'.format(i))
            self.workers.append(trader)

    def assign_task(self):
        for i in range(self.num_worker):
            p = Process(target=self.workers[i].call, args=(i, self.stock_queues,))
            p.start()
            p.join(timeout=0.1)
        #self.workers[0].analysis_document(0, self.stock_queues)

        print ('assign task finish!')

def main():
    boss = Boss(get_stock_name_list('stock_num.txt'))
    boss.hire_worker()
    boss.assign_task()
    print ('completed!')

def get_stock_name_list(stocks_num):
    symbols = []
    for symbol in open(stocks_num, 'r').readlines():
        symbols.append(symbol.strip())
    return symbols

'''
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
    '''
if __name__ == '__main__':
    main()
    to_excel(result_all)