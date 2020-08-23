import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
import matplotlib as mpl

import math

#from pandas.plotting import register_matplotlib_converters
#register_matplotlib_converters()

def check_folder(p):
    if not os.path.exists(p):
        os.makedirs(p)

def to_excel(outputs, excel_p='result.xlsx'):
#        input:
#            outputs: [{'k1': v1, 'k2': v2....}, {'k1': v1, 'k2': v2....} ...]
#        output:
#            excel_file

    df = pd.DataFrame(outputs)
    df.to_excel(excel_p)

# https://blog.csdn.net/funnyPython/article/details/83925573?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task
def plot(x, y, symbol, x_axis_interval):
#    the param of plot
    print (x)
#    mpl.rcParams['lines.linewidth'] = 10
#    mpl.rcParams['figure.figsize'] = (15, 15)
#    plt.gcf().set_size_inches(20, 20)
    ax=plt.gca()
    a = list(range(len(x)))
    plt.xticks(a, x, rotation=90, fontsize=10)
    for label in ax.get_xticklabels():
#        label.set_visible(False)
#    for label in ax.get_xticklabels()[::x_axis_interval]:
        label.set_visible(True)
    plt.plot(x, y)
    plt.savefig(f'plot/{symbol}.png')
    plt.close()

def ma_40(df, period, lookback):
    row=len(df)
    df_C = df['Close'].iloc[row-(lookback+period):row-lookback+1]
    rolling_mean = df_C.rolling(window=period).mean()
    return round(rolling_mean[row-1-lookback],2)

def bollinger_bands(df, period, lookback, numsd):
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

    return upper_in, lower_in

def draw_tech(df, daily_dict, symbol):
    row=len(df)

    lookback = 250
    numsd = 2
    x_axis_interval = 30
    bbuppers = []
    bblowers = []
    ma40s = []
    ma5s = daily_dict['MA5_val_sum']
    ma4s = daily_dict['MA4_val_sum']
    ma80s = daily_dict['MA80_val_sum']
    closes = []
    dates = []
    dates2 = []

    df_C = df['Close'].iloc[row-(lookback):row+1]
    rolling_min = df_C.rolling(window=lookback).min()
    bottom = math.floor(rolling_min[row-1]) / 2

    for l in range(lookback):
        date = str(df['Date'][len(df)-l-1-1]).split(' ')[0]
        close = df['Close'][len(df)-l-1-1]
        for typ in ['ma40', 'bb', 'ma5', 'ma4', 'ma80']:
            if typ == 'ma40':
                ma40 = ma_40(df, period=40, lookback=l)
                ma40s.append(ma40)
            if typ == 'bb':
                upper_in, lower_in = bollinger_bands(df, period=20, lookback=l, numsd=2)
                bbuppers.append(upper_in)
                bblowers.append(lower_in)
            if typ == 'ma5':
                if l >= len(ma5s):
                    ma5s.append(bottom)
            if typ == 'ma4':
                if l >= len(ma4s):
                    ma4s.append(bottom)
            if typ == 'ma80':
                if l >= len(ma80s):
                    ma80s.append(bottom)
        date = date + '          ' * (l % x_axis_interval)
        dates.append(date)
        closes.append(close)
    
    plot(np.asarray(dates[: :-1]), np.asarray([closes[: :-1], ma5s[: :-1], ma4s[: :-1], ma40s[: :-1], ma80s[: :-1], bbuppers[: :-1], bblowers[: :-1]]).T, symbol, x_axis_interval=x_axis_interval)

if __name__ == '__main__':
    daily_dict = {'MA5_val_sum': [], 'MA4_val_sum': [], 'MA80_val_sum': []}
    df = pd.read_csv(f"stock_temp/file_A.csv")
    check_folder('plot')
    symbol = 'A'
    draw_tech(df, daily_dict, symbol)
