import requests
# import pandas as pd
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, 'module')
import Stock_history
# import time
# import os
# import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
# import re

# i r l
# 0 1 
# 1 2 1
# 2 3 2
# 3 4 3
# 4 5 4
# 3:5

class sum():
    def bollinger_bands(self,df,period,lookback, numsd):
        row=len(df)
        df_C = df['Close'].iloc[row-(lookback+period):row-lookback+1] # only get lookback array
        df_H=df['High'].iloc[row-(lookback+period):row-lookback+1] #.max()
        df_L=df['Low'].iloc[row-(lookback+period):row-lookback+1] #.min()
        rolling_mean = df_C.rolling(window=period).mean() #,center=False
        rolling_std = df_C.rolling(window=period).std() #,center=False
        upper_band = rolling_mean + numsd*rolling_std
        lower_band = rolling_mean - numsd*rolling_std
        upper_in=round(upper_band[row-1-lookback],2)
        lower_in=round(lower_band[row-1-lookback],2)

        #=======build dict from list
        list_input=['upper_in','lower_in']
        dict_input={}
        for name in list_input:
            dict_input[name]=locals()[name]
        dict_sum=dict_input

        return dict_sum

def main():
    Stock_name = 'EBAY'
    A=Stock_history.sum()
    df=A.Stock_price(Stock_name)
    #print (df)
    F=sum()
    period=20
    for i in range(len(df)-period):
        BB_dict=F.bollinger_bands(df, period=period, lookback=i, numsd=2) # price,DTE,BB中心均線(fix),內BB標準差
        print (i, BB_dict)

if __name__ == '__main__':
    main()