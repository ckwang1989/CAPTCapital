import finviz
import json 
import copy

import requests
from datetime import datetime
import time
import os
import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
import pandas as pd

def get_symbols(csv_p):
    csv = pd.read_csv(csv_p, header=0)
    symbols = csv.to_dict('list')['Ticker']
    return symbols

def Stock_price(stock_TW, interval):
    folderpath = os.path.join(os.getcwd(), 'stock_temp')
    filepath = os.path.join(folderpath, f'file_{stock_TW}.csv')
    if not os.path.isdir(folderpath):
        os.mkdir(folderpath)
    stock = yf.Ticker(stock_TW)
    df = stock.history(period="max", auto_adjust=False, interval=interval)
    df = df.reset_index()
    df.to_csv(filepath, index='Date')
    return df

def get_grownth_list(symbol, acc_num=12):
    grownth_list = []
    df = Stock_price(symbol, interval='1mo')
    i  = 1
    data_last, close_last = -1, -1
    if len(df.to_dict('list')['Adj Close']) < acc_num+4+1:
        return None
    while len(grownth_list) < acc_num:
        close = df.to_dict('list')['Adj Close'][-i]
        date = df.to_dict('list')['Date'][-i].date()
        if str(close) == 'nan':
            i += 1
            continue
        if close_last != -1:
            grownth_list.append(close_last/float(close))
#        print (date, close)
        i += 1
        data_last, close_last = date, close
    return grownth_list

def compare(a, b):
    # a: target
    # b: spy
    return [a[i] > b[i] for i in range(len(a))]

def main():
    symbols = get_symbols(csv_p='result.csv')
    spy_grownth_list = get_grownth_list('spy')
    for symbol in symbols:
        print (symbol)
        if symbol[:1] not in ['T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            continue
        target_grownth_list = get_grownth_list(symbol)
        if not target_grownth_list:
            continue
        grown_acc = sum(compare(target_grownth_list, spy_grownth_list))
        if grown_acc >= 10:
            print ('symbol: ', symbol, grown_acc)
#        input('w')
if __name__ == '__main__':
    main()
