import requests
# import pandas as pd
from datetime import datetime
import time
import os
import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
import pandas as pd

class sum():
    def Stock_price(self, stock_TW):

        filepath=os.getcwd() + '\\stock_temp'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        stock = yf.Ticker(stock_TW)
        df =stock.history(period="max")
        df=df.reset_index()
        df.to_csv(os.getcwd() + '\\stock_temp' + '\\file_%s.csv' %stock_TW,index='Date')
        return df


# if __name__ == '__main__':
#     df= sum().Stock_single_no_data('AMD')