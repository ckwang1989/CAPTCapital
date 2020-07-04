import requests
# import pandas as pd
from bs4 import BeautifulSoup
# import time
# import os
# import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
# import re

class sum():
    def bollinger_bands(self,df,DTE,lookback, numsd):
        row=len(df)-1
        df_C = df['Close'].iloc[row-(lookback-2+DTE):row+1] # only get lookback array
        df_H=df['High'].iloc[row-(lookback-2+DTE):row+1] .iloc[-DTE:] #.max()
        df_L=df['Low'].iloc[row-(lookback-2+DTE):row+1] .iloc[-DTE:] #.min()
        #df = df['Close']
        rolling_mean = df_C.rolling(window=lookback).mean() #,center=False
        rolling_std = df_C.rolling(window=lookback).std() #,center=False
        upper_band = rolling_mean + numsd*rolling_std
        lower_band = rolling_mean - numsd*rolling_std
        upper_in=round(upper_band[row],2)
        lower_in=round(lower_band[row],2)
        upper_band=upper_band.iloc[-DTE:]
        lower_band=lower_band.iloc[-DTE:]
        # max_P=df['High'].iloc[10:] #.max()
        # min_P=df['Low'].iloc[10:] #.min()
        i=row
        while 1>0:
            if upper_band[i]<df_H[i] or lower_band[i]>df_L[i]:
                numsd=numsd+0.05
                upper_band = rolling_mean + numsd*rolling_std
                lower_band = rolling_mean - numsd*rolling_std
            else:
                i=i-1
            if i==row-(DTE-1):
                break

        upper_out=round(upper_band[row],2)
        lower_out=round(lower_band[row],2)
        out_BB=round(numsd,2)
        #=======build dict from list
        list_input=['upper_in','lower_in','upper_out','lower_out','out_BB']
        dict_input={}
        for name in list_input:
            dict_input[name]=locals()[name]
        dict_sum=dict_input

        return dict_sum

#     def Stock_single_no_data(self, stock_TW):

#         filepath=os.getcwd() + '\\stock_temp'
#         if not os.path.isdir(filepath):
#             os.mkdir(filepath)
#         stock = yf.Ticker(stock_TW)
#         df =stock.history(period="max")
#         df=df.reset_index()
#         df.to_csv(os.getcwd() + '\\stock_temp' + '\\file_%s.csv' %stock_TW,index='Date')
#         return df
# if __name__ == '__main__':

#     df= sum().Stock_single_no_data('SPY')
#     upper_in,lower_in,upper_out,lower_out,out_BB=sum().bollinger_bands(df, DTE=60, lookback=20, numsd=2) # price,DTE,BB中心均線(fix),內BB標準差
#     temp=1