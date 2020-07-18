import requests
# import pandas as pd
from datetime import datetime
import time
import os
import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
import pandas as pd

class sum():
    def Stock_price(self, stock_TW):
        folderpath = os.path.join(os.getcwd(), 'stock_temp')
        filepath = os.path.join(folderpath, f'file_{stock_TW}.csv')
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
        stock = yf.Ticker(stock_TW)
        df =stock.history(period="max")
        df=df.reset_index()
        df.to_csv(filepath, index='Date')
        return df

if __name__ == '__main__':
	df= sum().Stock_single_no_data('AMD')