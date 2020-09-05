import os
import sys
sys.path.insert(0, 'module')
import Stock_history
import statistics

import datetime
from datetime import timedelta
from datetime import date as dt

import numpy as np

import copy
import pandas as pd

def get_date_diff(date1, date2):
    try:
        datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
        date1 = '{} 10:01:28.585'.format(date1)
        date2 = '{} 09:56:28.067'.format(date2)
        diff = datetime.datetime.strptime(date1, datetimeFormat) - datetime.datetime.strptime(date2, datetimeFormat)
        return diff.days
    except:
        return -1

def get_stock_name_list(stocks_num):
    symbols = []
    for symbol in open(stocks_num, 'r').readlines():
        symbols.append(symbol.strip())
    return symbols

class sum():
    def bollinger_bands(self, df, period, lookback, numsd):
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

#        #=======build dict from list
#        list_input=['upper_in','lower_in']
#        dict_input={}
#        for name in list_input:
#            dict_input[name]=locals()[name]
#        dict_sum=dict_input

        return upper_in, lower_in

    def ma(self, df, period, lookback):
        row=len(df)
        df_C = df['Close'].iloc[row-(lookback+period):row-lookback]

        if period == 40:
            weights = []
            for v in range(1, 41):
                weights.append(v/float((1+40)*20))
            weights = np.asarray(weights)

            sum_weights = np.sum(weights)
            rolling_mean = df_C.rolling(window=period, center=False).apply(lambda x: np.sum(weights*x) / sum_weights, raw=False)

        else:
            rolling_mean = df_C.rolling(window=period).mean()

        return round(rolling_mean[row-1-lookback],2)

    def s(self, df, RSVs, period, lookback):
        row=len(df)
        close = df['Close'].iloc[row-lookback-1]
        higher = df['High'].iloc[row-(lookback+period):row-lookback].max()
        lower = df['Low'].iloc[row-(lookback+period):row-lookback].min()
        if len(RSVs) >= 3:
            RSVs.pop(0)
        RSV = 100.0 * ((close-lower)/(higher-lower+0.00000001))
        RSVs.append(RSV)
        return RSVs

    def d(self, df, RSV, period, lookback, K_old, D_old):
        row=len(df)
        close = df['Close'].iloc[row-lookback-1]
        higher = df['High'].iloc[row-(lookback+period):row-lookback].max()
        lower = df['Low'].iloc[row-(lookback+period):row-lookback].min()
#        RSV = 100.0 * ((close-lower)/(higher-lower+0.00000001))
        K_new = (2 * K_old / 3) + (RSV / 3)
        D_new = (2 * D_old / 3) + (K_new / 3)
        return K_new, D_new

def check(upper_band, lower_in, ma5, close, date):
#    if (upper_band + ma5) / 2.0 < close:
    if (2.0*upper_band + ma5) / 3.0 < close:
        return True
    else:
        return False


def save(p, d):
    with open(p, 'wb') as handle:
        pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load(p):
    with open(p, 'rb') as handle:
        b = pickle.load(handle)
    return b

def list_positive(values, i, num, slope=1):
    result = True
    for n in range(num):
        result = result and ((values[i-n]/values[i-1-n]) > slope)
    return result


def main():
    '''
        {'20190101': ['AMD', 'EBAY'],
        '20190102': ['AMD', 'FB'],
        ...
        ...
        ...}
    ''' 
    stocks = get_stock_name_list('/Users/Wiz/Desktop/wang_fund/CAPTCapital0823Bug/stock_num.txt')
#    stocks = ['JNJ-VTI-0-18-60', 'PG-VTI-0-18-57']
#    Stock_name = 'EBAY'
    A=Stock_history.sum()
    F=sum()
    period=20
    all = {}
    rates = {}
#    '''
    for k, Stock_name in enumerate(stocks):
        rates[Stock_name] = 0
#        print (Stock_name)
        try:
#        if 1:
            s = 0
            symbol = Stock_name.split('-')[0]
            df=A.Stock_price(symbol, interval='1wk')
            ma5s = []
            ma4s = []
            ma40s = []
            dates = []
            closes = []
            d = {}
            d2 = {}
            output = {}
            keep_day = 90
            K_old, D_old = 0.5, 0.5
            back_max = 350*2 if len(df) > 350*2 else len(df)-1-40
            RSVs = []
            Ds = []
            ma40_old = 0.0000001
            ma12_old = 0.0000001
            ma26_old = 0.0000001
            ma12_k = 1.0 / (1 + 12)
            ma26_k = 1.0 / (1 + 26)


            ### to determine the interval that can investment ###
            ok = {'yes':[], 'no':[]}
            up_down = []
            macd_fasts = []
            ma40_rise = []
            for i in range(back_max, 0, -1):
                ma40 = F.ma(df, period=40, lookback=i)
                if ma40 >= ma40_old:
                    up_down.append(1)
                else:
                    up_down.append(0)
                if len(up_down) > 4:
                    up_down.pop(1)
                
                ma40_rise.append(ma40 >= ma40_old)
                close = df['Close'][len(df)-i-1]
                ma12 = close*ma12_k + ma12_old*(1-ma12_k)
                ma26 = close*ma26_k + ma26_old*(1-ma26_k)
                macd_fast = ma12 - ma26
                macd_fasts.append(macd_fast)
                

                date = str(df['Date'][len(df)-i-1]).split(' ')[0]
    #            print (date, close, macd_fast, ma12, ma26)
                #input('www')
                #if ma40/ma40_old>=0.9998:
                if np.sum(up_down) > 3:
                    ok['yes'].append(date)
                else:
                    ok['no'].append(date)
                ma40_old = ma40
                ma12_old = ma12
                ma26_old = ma26

                ma5 = F.ma(df, period=5, lookback=i)
                ma40 = F.ma(df, period=40, lookback=i)
                RSVs = F.s(df, RSVs, period=9, lookback=i)
                RSV = statistics.mean(RSVs)
                K_new, D_new = F.d(df, RSV, period=9, lookback=i, K_old=K_old, D_old=D_old)

                date = str(df['Date'][len(df)-i-1]).split(' ')[0]
                
                close = df['Close'][len(df)-i-1]
                volume = df['Volume'][len(df)-i-1]
    #            print (date, close, ma5, ma40, RSV, K_new, D_new)
    #            input('w')

                ma5s.append(ma5)
                ma40s.append(ma40)
                closes.append(close)
                dates.append(date)
    #            ma5s.insert(0, ma5)
    #            ma40s.insert(0, ma40)
    #            closes.insert(0, close)
    #            dates.insert(0, date)

                if len(ma5s) >= 4:
                    ma4 = statistics.mean(ma5s[-4:len(ma5s)])
                    ma4s.append(ma4)
                else:
                    ma4s.append(0)
    #                ma4s.insert(0, ma4)

                K_old, D_old = K_new, D_new
                Ds.append(D_old)

    #        for i in range(len(ma5s)-len(ma4s)):
    #            ma4s.insert(0, 0)
            d2 = {'up': False, '5up4_date':'', '5up4_close':0}
            win = {'win': 0, 'loss': 0}
            close_std = []
            close_std2 = []
            for i in range(2, len(ma5s)):
                close_std.append(closes[i]-closes[i-1])
                close_std2.append(closes[i-1]-closes[i-1-1])
    #            print (closes[i]-closes[i-1], close_std, max(close_std))
    #            max_jump = (max(close_std) == closes[i]-closes[i-1])
                c_std = np.std(close_std)
                c_std2 = np.std(close_std2)
                if len(close_std) >= 4:
                    close_std.pop(0)
                    close_std2.pop(0)
                
    #            print (dates[i], closes[i])
    #            if ma5s[i] > ma4s[i] and ma5s[i-1] < ma4s[i-1] and not d2['up'] and ma40s[i]/ma40s[i-1]>0.9998 and Ds[i] < 70:
    #                d[i] = {'date': dates[i], 'close': closes[i], '5down4_date': 0, 'assign': False}

                date = dates[i]
                change_state_count = 0
                if i > 12:
                    for idx in range(i-12, i):
                        if ma4s[idx] >= ma4s[idx-1] and ma4s[idx-1-1] >= ma4s[idx-1]:
                            change_state_count += 1
                        if ma4s[idx] <= ma4s[idx-1] and ma4s[idx-1-1] <= ma4s[idx-1]:
                            change_state_count += 1
    #            print (date, change_state_count)
    #            if c_std > 0.8:
    #                print (date) 
    #            print ('date: ', date, ' ma5: ', ma5s[i], ma5s[i-1], ma5s[i-2], ' macd_fasts: ', macd_fasts[i]/macd_fasts[i-1])
    #            print (list_positive(ma5s, i, 2), list_positive(ma40s, i, 4, 1.004), list_positive(closes, i, 3))
    #            print (date, closes[i], closes[i]/closes[i-1])

                if int(date.split('-')[0])>2009 and list_positive(ma5s, i, 2) and list_positive(ma40s, i, 4, 1.004) and list_positive(closes, i, 3) and not d2['up']:
                    d2 = {'5up4_date': dates[i], '5up4_close': closes[i], '5down4_date': 0, '5down4_close': 0, 'up': True, 'D_new': Ds[i], 'max_jump': False, 'change_state_count': change_state_count}
    #                if ma4s[i]/(ma4s[i-1]+0.000000000001)<1.0003:
    #                    print ('in jump', date, ma4s[i]/(ma4s[i-1]+0.000000000001))
    #                    d2['max_jump'] = True
    #                print ('in', d2)
    #            if ma5s[i] < ma4s[i] and ma5s[i-1] > ma4s[i-1] and d2['up']:
    #            if d2['5up4_date'] != date and ((ma5s[i-1]<=ma5s[i-1-1] and ma5s[i]<=ma5s[i-1]) or (closes[i]/d2['5up4_close'])>1.1) and d2['up']:
                if d2['5up4_date'] != date and ((closes[i-1]< closes[i] and closes[i-1-1] < closes[i-1] and closes[i] < ma4s[i]) or (closes[i]/d2['5up4_close'])>1.1) and d2['up']:

                    d2['5down4_close'] = closes[i]
                    d2['5down4_date'] = dates[i]
                    d2['up'] = False
                    if 1:#not d2['change_state_count'] > 1:
                        print ('\t\t', d2['5down4_close']/d2['5up4_close'], d2)
    #                    print ('\n')
                        if d2['5up4_date'] in all.keys():
                            pass
                        else:
                            all[d2['5up4_date']] = []
                        all[d2['5up4_date']].append(copy.deepcopy({'Stock_name': Stock_name.split('/')[0], '5up4_date': d2['5up4_date'], '5down4_date': d2['5down4_date'], 'rate': d2['5down4_close']/d2['5up4_close'], 'rate_average': rates[Stock_name]}))

                        if d2['5down4_close']/d2['5up4_close'] >=1 :
                            s += d2['5down4_close']/d2['5up4_close']
                            win['win'] += 1
                        else:
                            s -= d2['5down4_close']/d2['5up4_close']
                            win['loss'] += 1
                    else:
                        print ('fail: ', d2['change_state_count'], d2['5down4_close']/d2['5up4_close'], d2)

    #            print (dates[i], i, i-keep_day, d.keys(), i-keep_day in d.keys())
                '''
                for k in d.keys():
                    index_5up4 = k
                    if d[index_5up4]['assign']:
                        continue
    #                delta_d = abs(get_date_diff(dates[index_5up4], dates[i]))
    #                print (delta_d)
                    
                    if delta_d >= 90:
                        d[index_5up4]['keep_day_close'] = closes[i]
                        d[index_5up4]['assign'] = True
                        print (dates[index_5up4], d[index_5up4]['close'], d[index_5up4]['keep_day_close'])
                        output[index_5up4] = {'date': dates[index_5up4], 'distance':  d[index_5up4]['keep_day_close'] / d[index_5up4]['close']}
                        #del(d[index_5up4])
                        break
                        '''
            print (Stock_name, s, (s-(win['win']-win['loss']))/(win['win']+win['loss']), win)
            rates[Stock_name] = {'rate_average': (s-(win['win']-win['loss']))/(win['win']+win['loss']), 'win': win['win'], 'loss':win['loss']}
            #print (all)
#            to_excel(all, rates, excel_p='result.xlsx')
    #        print (win)
    #        input ('w')

        except:
            print ('fail', Stock_name)
    to_excel(all, rates, excel_p='result.xlsx')

def to_excel(outputs, rates, excel_p='result.xlsx'):
#        input:
#            outputs: [{'k1': v1, 'k2': v2....}, {'k1': v1, 'k2': v2....} ...]
#        output:
#            excel_file
    o = []
    for k in outputs.keys():
        o += outputs[k]
    for v in o:
        v['rate_average'] = rates[v['Stock_name']]['rate_average']
        v['win'] = rates[v['Stock_name']]['win']
        v['loss'] = rates[v['Stock_name']]['loss']
    df = pd.DataFrame(o)
    df.to_excel(excel_p)

if __name__ == '__main__':
    main()