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

from datetime import datetime, date

def get_stock_name_list(stocks_num):
    symbols = []
    for symbol in open(stocks_num, 'r').readlines():
        symbols.append(symbol.strip())
    return symbols

class sum():
    def bollinger_bands(self, df, period, lookback, numsd, return_close=False):
        row=len(df)
        df_C = df['Close'].iloc[row-(lookback+period):row-lookback+1] # only get lookback array
        df_H=df['High'].iloc[row-(lookback+period):row-lookback+1] #.max()
        df_L=df['Low'].iloc[row-(lookback+period):row-lookback+1] #.min()
        df_Date=df['Date'].iloc[row-(lookback+period):row-lookback+1]
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

        if return_close:
             return upper_in, lower_in, round(df_C[row-1-lookback],2), df_Date[row-1-lookback]
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
    stocks = get_stock_name_list('/Users/Wiz/Desktop/wang_fund/Shield_1014/Shield/stock_num.txt')
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
    r_new = load('/Users/Wiz/Desktop/wang_fund/Shield_1011/Shield/fizviz_screener.pkl')
    print (r_new)
    assert False
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

def main3():
    process_num = int(sys.argv[1])#.startswith('--')
    process_num_all = int(sys.argv[2])#.startswith('--')
    stock_history = Stock_history.sum()
    outputs = {}
    finviz_screener_page = load('/Users/Wiz/Desktop/wang_fund/Shield_1011/Shield/fizviz_screener.pkl')
    for i_row, row in enumerate(finviz_screener_page):
        if i_row % 100 == 0: print('i_row: ', i_row)
        try:
            if i_row % process_num_all == process_num:
                symbol = row['Ticker']
                df = stock_history.Stock_price(symbol, from_yf=False)
                max_close = -1
                outputs[symbol] = []
                for i in range(len(df)):
                    if '19' in df['Date'][i][:2] or '-' not in df['Date'][i]: continue
                    if float(df['Close'][i]) > max_close:
                        max_close = float(df['Close'][i])
                        max_close_date = df['Date'][i]
                        outputs[symbol].append(copy.deepcopy({max_close_date: max_close}))                    
        except:
            print (f'{symbol} is fail')
    save('history_highest.pkl', outputs)
#    print (outputs)
# bb
# bb and Country
# bb and Diagnostics & Research
# bb and Sector
# bb and Price

def main4():
    process_num = int(sys.argv[1])#.startswith('--')
#    outputs = load(f'{process_num}.pkl')
    outputs = load('all.pkl')
    index_date_map = {}
    results = {'all': []}
    period = 20
    stock_history = Stock_history.sum()
    bollinger_bands = sum()
    df = stock_history.Stock_price('AMD', from_yf=False)
    for i in range(len(df)-period):
        if i > 350*1:
            break
        upper_in, lower_in, close, date = bollinger_bands.bollinger_bands(df, period=period, lookback=i, numsd=2, return_close=True)
        index_date_map[i] = date

    for i, output in enumerate(outputs):
        if output['Country'] != 'USA': continue
        if float(output['Price']) > 300: continue
        if '2019' not in output['Date'] and '2020' not in output['Date']: continue

        if output['Ticker'] not in results['all']:
            results['all'] += [output['Ticker']]
        
        if output['Date'] not in results.keys():
            results[output['Date']] = [output['Ticker']]
        else:
            results[output['Date']] += [output['Ticker']]
#    print (sorted(results.keys()))
    for i, date in enumerate(sorted(results.keys())):
        if '2019' not in date and '2020' not in date: continue
        if i < 3: continue
        symbol_pool_previous = set([vvv for ii in range(1, 4) for vvv in results[index_date_map[i-ii]]])
        symbol_pool_now = set(results[date])
#        print (date, len(symbol_pool_previous), len(symbol_pool_now), len(list(symbol_pool_now.intersection(symbol_pool_previous))))
#        print (len(results[date]))
#        input('w')
#        print (date, len(results[date]), int(len(results['all'])))
        #if len(results[date])>int(len(results['all'])*0.4):
        if len(list(symbol_pool_now.intersection(symbol_pool_previous)))>int(len(results['all'])*0.2):
#            print (results[date], date)
#            input('w')
            print (date, len(results['all']), len(list(symbol_pool_now.intersection(symbol_pool_previous))))
        date_last = date

def get_weekday(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").weekday()+1

def get_datetime_diff(date1_string, date2_string):
    return (datetime.strptime(date1_string, "%Y-%m-%d") - datetime.strptime(date2_string, "%Y-%m-%d")).days

def get_dayshift_string(date_string, shift_days):
    import datetime
    from datetime import datetime as dt
    return str(dt.strptime(date_string, "%Y-%m-%d") + datetime.timedelta(days = shift_days))[:len('2020-10-10')]

def get_history_data(df, date, typ):
    for i in range(len(df)):
        if '-' not in df['Date'][i]: continue
        if get_datetime_diff(date, df['Date'][i]) < 0: return df[typ][i]
        if date == df['Date'][i]:
            return df[typ][i]


def main5():
    stock_history = Stock_history.sum()
    stop_business_dates = ['2019-01-01', '2019-01-21', '2019-02-18', '2019-04-19', '2019-05-27', '2019-07-04', '2019-09-02', '2019-11-28', '2019-12-25', \
                            '2020-01-01', '2020-01-20', '2020-02-17', '2020-04-09', '2020-04-10', '2020-05-22', '2020-05-25', '2020-07-03', '2020-07-04', '2020-09-07', '2020-10-12', '2020-11-11', '2020-11-26', '2020-11-27', '2020-12-24', '2020-12-25', '2020-12-31']
    p = '/Users/Wiz/Desktop/wang_fund/CAPTCapital_1016/CAPTCapital/history_highest.pkl'
    hhs = load(p)
    hh_symbol_dates = {}
    for hh_symbol in hhs.keys():
        hh_symbol_dates[hh_symbol] = []
        for hh_sybol_dict in hhs[hh_symbol]:
            hh_symbol_dates[hh_symbol].append(copy.deepcopy(list(hh_sybol_dict.keys())[0]))
#    print (hh_symbol_dates)


    p = '/Users/Wiz/Desktop/wang_fund/CAPTCapital_1016/CAPTCapital/bb.pkl'
    bbs = load(p) 
    bb_symbol_dates = {}
    
    for bb in bbs: 
        if bb['Ticker'] in bb_symbol_dates.keys():
            bb_symbol_dates[bb['Ticker']].append(copy.deepcopy(bb['Date']))
        else:
            bb_symbol_dates[bb['Ticker']] = []
#    print (bb_symbol_dates)

    hottests_all = []

    for symbol in hh_symbol_dates.keys():
        if symbol in hh_symbol_dates.keys() and symbol in bb_symbol_dates.keys():
            # hh_symbol_dates = [{'symbol1': [date1, date2, ..]}, {'symbol2': [date1, ...]}]
            # bb_symbol_dates = same as hh_symbol_dates
            hottests = sorted(list(set(hh_symbol_dates[symbol]) & set(bb_symbol_dates[symbol])))
            if len(hottests) > 0:
                hottests_all.extend(copy.deepcopy(hottests))
#                print (symbol, hottests)
#                input('w')

    for hottests_date in sorted(list(set(hottests_all))):
        if hottests_all.count(hottests_date) > 230:
            print (f'{hottests_date}: {hottests_all.count(hottests_date)}')

#    for i_row, row in enumerate(finviz_screener_page):
#        symbol = row['Ticker']

    for symbol in ['AMD', 'AAPL', 'NIO', 'TWOU', 'TDOC', 'INFO', 'FB', 'XLNX', 'RVLV', 'ISRG']:
#    finviz_screener_page = load('/Users/Wiz/Desktop/wang_fund/Shield_1011/Shield/fizviz_screener.pkl')
#    for i_row, row in enumerate(finviz_screener_page):
#        symbol = row['Ticker']

        df = stock_history.Stock_price(symbol, from_yf=False)

        if symbol not in hh_symbol_dates.keys() or symbol not in bb_symbol_dates.keys(): continue
        merge_dates = sorted(list(set(hh_symbol_dates[symbol])&set(bb_symbol_dates[symbol])))
#        if '2020-11-12' in merge_dates or '2020-11-13' in merge_dates:
#            print (symbol, get_datetime_diff('2020-11-14', '2020-11-12'))
#            print ('hh_symbol_dates: ', sorted(hh_symbol_dates[symbol]))
#            print ('bb_symbol_dates: ', sorted(bb_symbol_dates[symbol]))
#            print ('hh_symbol_dates & bb_symbol_dates: ', sorted(merge_dates))
#            print ('\n\n')
#            input('wait')

#        dates = [2020-10-11, 2020-10-12, 2020-10-15, 2020-10-16, 2020-10-17, 2020-10-26, 2020-10-27, 2020-10-31]
        dates = merge_dates
        shift_days = 2
        group = []
        for i_date, date in enumerate(dates):
#            print ('i_date: ', i_date)
            # first element in groups
            start_date = date
            if i_date == 0:
                while True:
                    start_date = get_dayshift_string(start_date, 1)
#                    print (get_weekday(start_date))
                    if get_weekday(start_date) not in [6, 7] or get_datetime_diff(start_date, date): break
                start_price = get_history_data(df, start_date, typ='Close')
                group.append(copy.deepcopy({'start_date': start_date, 'start_price': start_price}))
#                print (group)
#                input('w')
                continue 
                
            # second... element in groups
            #                    2020-10-05(2)  2020-10-01(5)
            shift_days_plus = 2 if get_weekday(dates[i_date]) < get_weekday(dates[i_date-1]) else 0
            if get_datetime_diff(dates[i_date], dates[i_date-1]) > shift_days+shift_days_plus: # if so far between last element -> end the group
                end_date = get_dayshift_string(dates[i_date-1], shift_days+1)
                end_price = get_history_data(df, end_date, typ='Open')
                group[-1]['end_date'] = end_date
                group[-1]['end_price'] = end_price

                while True:
                    start_date = get_dayshift_string(start_date, 1)
#                    print (get_weekday(start_date))
                    if get_weekday(start_date) not in [6, 7]: break
                start_price = get_history_data(df, start_date, typ='Close')
                group.append(copy.deepcopy({'start_date': start_date, 'start_price': start_price}))
            else:  # if close
                pass
            
            # last element in group
            if i_date == len(dates)-1:
                if get_datetime_diff('2020-11-13', date) < 3:
                    group.pop()
                else:
                    end_date = get_dayshift_string(date, shift_days+1)
                    end_price = get_history_data(df, end_date, typ='Open')
                    group[-1]['end'] = end_date
                    group[-1]['end_open'] = end_price
#            print ('group: ', group, dates[i_date], dates[i_date-1], get_datetime_diff(dates[i_date], dates[i_date-1]))
#            input('w')
        print ('symbol: ', symbol, group)

if __name__ == '__main__':
#    main3()
#    main4()
    main5()