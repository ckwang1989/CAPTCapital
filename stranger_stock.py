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

def main():
    symbols = get_symbols(csv_p='result.csv')
    for symbol in symbols:
        print ('symbol: ', symbol)
        df = Stock_price(symbol, interval='1mo')
        i  = 1
        while i < 24:
            close = df.to_dict('list')['Adj Close'][-i]
            date = df.to_dict('list')['Date'][-i].date()
            if str(close) == 'nan':
                i += 1
                continue
            print (date, close)
            i += 1
        input('w')
if __name__ == '__main__':
    main()
