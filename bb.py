import requests
# import pandas as pd
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, 'module')
import Stock_history
import pickle

import copy

sys.path.insert(0, 'module')
from module.common import to_excel

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

    def ma5(self, df, period, lookback):
        row=len(df)
        df_C = df['Close'].iloc[row-(lookback+period):row-lookback+1]
        rolling_mean = df_C.rolling(window=period).mean()
        ma5=round(rolling_mean[row-1-lookback],2)
        return ma5

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



def main():
    '''
        {'20190101': ['AMD', 'EBAY'],
        '20190102': ['AMD', 'FB'],
        ...
        ...
        ...}
    ''' 
    stocks = get_stock_name_list('/Users/Wiz/Desktop/wang_fund/Shield/stock_num.txt')
#    Stock_name = 'EBAY'
    A=Stock_history.sum()
    F=sum()
    period=20
    r = {}
    outputs = []
#    '''
    for k, Stock_name in enumerate(stocks):
        print (len(stocks) - k)
        symbol = Stock_name.split('-')[0]
        df=A.Stock_price(symbol)
        for i in range(len(df)-period):
            if i > 250*2:
                break
            upper_in, lower_in=F.bollinger_bands(df, period=period, lookback=i, numsd=2)
            ma5 = F.ma5(df, period=5, lookback=i)
            date = str(df['Date'][len(df)-i-1-1]).split(' ')[0]
            close = df['Close'][len(df)-i-1-1]
            volume = df['Volume'][len(df)-i-1-1]
            if Stock_name not in r.keys():
                r[Stock_name] = {}
            r[Stock_name][i] = {'upper': upper_in, 'lower': lower_in, 'volume': volume, 'ma5': ma5, 'close': close, 'date': date}

#            if check(upper_in, lower_in, ma5, close, date):
#                if date in r.keys():
#                    r[date].append(symbol)
#                else:
#                    r[date] = [symbol]
#            else:
#                pass

#                '''

    save('bb_all_spyg.pkl', r)
    r_new = load('bb_all_spyg.pkl')
    print (r_new)
    '''
    for k in r_new.keys():
        outputs.append({'len': len(r_new[k]), 'date': k, 'symbols': r_new[k]})
    print (outputs)
    to_excel(outputs, excel_p='bb.xlsx')
    '''

def main2():
    r_new = load('bb_all_spyg.pkl')
    print (r_new)
    max_num = 250*2
    output = {}
    queue_close = {}
    for k, symbol in enumerate(r_new.keys()):
        if len(r_new[symbol].keys()) < 500:
            continue
        print (len(r_new.keys()) - k)
        for i in range(1, max_num):
            if i not in output.keys():
                output[i] = {}
            if symbol not in queue_close.keys():
                queue_close[symbol] = []

            # growth
            if r_new[symbol][i]['close'] > r_new[symbol][i-1]['close']:
                growth = 1
            elif r_new[symbol][i]['close'] < r_new[symbol][i-1]['close']:
                growth = -1
            else:
                growth = 0
            output[i][symbol] = {'ad': {'up': 0, 'down': 0}, 'volume': {'up': 0, 'down': 0}, 'nhnl': 0}

            # volume
            if growth == 1:
               output[i][symbol]['volume']['up'] = r_new[symbol][i]['volume']
               output[i][symbol]['ad']['up'] = 1
            elif growth == -1:
                output[i][symbol]['volume']['down'] = r_new[symbol][i]['volume']
                output[i][symbol]['ad']['down'] = 1
            # nhnl
            if len(queue_close[symbol]) == 52*5:
                max_close = max(queue_close[symbol])
                min_close = min(queue_close[symbol])
                if r_new[symbol][i]['close'] > max_close:
                    nhnl = 1 
                elif r_new[symbol][i]['close'] < min_close:
                    nhnl = -1
                else:
                    nhnl = 0
                queue_close[symbol].pop(0)
                output[i][symbol]['nhnl'] = nhnl
            queue_close[symbol].append(copy.deepcopy(r_new[symbol][i]['close']))
    
    outputs = []
    ups = {}
    downs = {}
    ups_ma10 = 0
    downs_ma10 = 0
    print (output)
    for date in output.keys():
        ad_up = 0
        ad_down = 0
        nhnl = 0
        print ('date: ', date)
        for symbol in output[date].keys():
#            print ('symbol: ', symbol)
            if symbol not in ups.keys():
                ups[symbol] = []
                downs[symbol] = []
            # ad
            ad_up += output[date][symbol]['ad']['up']
            ad_down += output[date][symbol]['ad']['down']

            # volume
            if len(ups[symbol]) == 10:
                ups_sum = 0
                downs_sum = 0
                for i in range(len(ups[symbol])):
                    ups_sum += ups[symbol][i]
                    downs_sum += downs[symbol][i]
                ups_ma10 = ups_sum / 10.0
                downs_ma10 = downs_sum / 10.0

                ups[symbol].pop(0)
                downs[symbol].pop(0)
            ups[symbol].append(output[date][symbol]['volume']['up'])
            downs[symbol].append(output[date][symbol]['volume']['down'])

            nhnl += output[date][symbol]['nhnl']
        if len(ups[symbol]) == 10:
            outputs.append({'ad': ad_up-ad_down, 'volume': ups_ma10/(downs_ma10+0.0001), 'nhnl': nhnl})

    save('bb_all_spyg_marketindex.pkl', outputs)
    to_excel(outputs, excel_p='bb_all_spyg_marketindex.xlsx')

if __name__ == '__main__':
    main2()