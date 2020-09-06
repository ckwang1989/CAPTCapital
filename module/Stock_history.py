import requests
# import pandas as pd
from datetime import datetime
from datetime import date
import time
import os
import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
import pandas as pd


def get_weekday(d):
    return date(d.split('-')[0], d.split('-')[1], d.split('-')[2]).weekday()+1

class sum():
    def Stock_price(self, stock_TW, interval='1d'):
        folderpath = os.path.join(os.getcwd(), 'stock_temp')
        filepath = os.path.join(folderpath, f'file_{stock_TW}.csv')
        filepath_tmp = os.path.join(folderpath, f'file_tmp.csv')
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
        stock = yf.Ticker(stock_TW)
        df = stock.history(period="max", auto_adjust=False, interval=interval)
#        print (df)
        df=df.reset_index()
        df.to_csv(filepath_tmp, index='Date')
        with open(filepath, 'w') as f_w:
            for line in open(filepath_tmp, 'r').readlines():
                if ',,,' in line:
                    continue
                else:
                    f_w.write(line)
        df = pd.read_csv(filepath)  
        # remove 
        removes = []
        for i in range(len(df['Date'])):
            d = df['Date'][i]
            if (date(int(d.split('-')[0]), int(d.split('-')[1]), int(d.split('-')[2])).weekday()+1) != 4:
                removes.append(i)
        df.drop(removes , inplace=True)
        return df.reset_index(drop=True)

if __name__ == '__main__':
	df= sum().Stock_single_no_data('AMD')