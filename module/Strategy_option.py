import os
import sys
import pickle
import yfinance as yf
import datetime
from datetime import timedelta
from datetime import date as dt

import Stock_history, Technical_index, Stock_back_test, IV_HV, earning
from Strategy_trigger import strategy_trigger
from condition import Condition
import BB
import time

# 市場 / 策略 / 進場觸發觸發指標(key) / 股票名稱 / ETF名稱 / 履約價 / 履約日期 / 相似天數 / 觸發進場策略 / 觸發出場策略

def get_date_diff(date1, date2):
    try:
        datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
        date1 = '{} 10:01:28.585'.format(date1)
        date2 = '{} 09:56:28.067'.format(date2)
        diff = datetime.datetime.strptime(date1, datetimeFormat) - datetime.datetime.strptime(date2, datetimeFormat)
        return diff.days
    except:
        return -1

def get_combination_option(options_file_path, last_close, day, return_on_inves_thre=0.02):
    stock_name = options_file_path.split('/')[-1][:-4]
    try:
        stock_ticker = yf.Ticker(stock_name)
        tmp = stock_ticker.options
    except:
        print ('fail in {}'.format(stock_name))
        return {}, False

    d = {'call': {'bid':-1, 'ask':-1,'bid_strike':-1, 'ask_strike':-1, 'return':0, 'date':0}, \
        'put': {'bid':-1, 'ask':-1,'bid_strike':-1, 'ask_strike':-1, 'return':0, 'date':0}}
    flag_sc = False
    flag_sp = False
    for date in stock_ticker.options:
        delta_d = get_date_diff(date, dt.today().strftime("%Y-%m-%d"))
        if delta_d < day:
            continue
        #print (stock_ticker.option_chain(date))
        for index, opts in enumerate(stock_ticker.option_chain(date)):
            typ = 'call' if index == 0 else 'put'
            if flag_sp and typ == 'put':
                continue
            if flag_sc and typ == 'call':
                continue
            opts_dict = opts.to_dict()
            for idx in opts_dict['contractSymbol'].keys():
                #opt = opts_dict[key][idx]
                #print (opts_dict['bid'][idx], opts_dict['ask'][idx])
                if (not '.' in str(opts_dict['bid'][idx])) or (not '.' in str(opts_dict['ask'][idx])):
                    continue
                if int(opts_dict['bid'][idx]) == 0 or int(opts_dict['ask'][idx]) == 0:
                    continue
                if index: # SP
                    if float(opts_dict['strike'][idx]) < last_close:
                        min_ask = opts_dict['ask'][0]
                        return_on_inves = float((opts_dict['bid'][idx]-min_ask)/opts_dict['strike'][idx])
                        if return_on_inves > return_on_inves_thre:
                            if return_on_inves > d[typ]['return']:
                                d[typ]['return'] = return_on_inves
                                d[typ]['bid'] = opts_dict['bid'][idx]
                                d[typ]['ask'] = min_ask
                                d[typ]['bid_strike'] = opts_dict['strike'][idx]
                                d[typ]['ask_strike'] = opts_dict['strike'][0]
                                d[typ]['date'] = date
                                flag_sp = True

                else: # SC
                    if float(opts_dict['strike'][idx]) > last_close:
                        min_ask = opts_dict['ask'][opts_dict['ask'].__len__()-1]
                        return_on_inves = float((opts_dict['bid'][idx]-min_ask)/opts_dict['strike'][idx])
                        if return_on_inves > return_on_inves_thre:
                            if return_on_inves > d[typ]['return']:
                                d[typ]['return'] = return_on_inves
                                d[typ]['bid'] = opts_dict['bid'][idx]
                                d[typ]['ask'] = min_ask
                                d[typ]['bid_strike'] = opts_dict['strike'][idx]
                                d[typ]['ask_strike'] = opts_dict['strike'][opts_dict['ask'].__len__()-1]
                                d[typ]['date'] = date
                                flag_sc = True
    return d

def check_fail(bt_result_str):
    bt_result_str = bt_result_str[2:]
    days = [5, 10, 15, 20, 30, 40, 60, 80, 100, 120, 140]
    flag = 1
    for k, v in enumerate(days):
        flag = flag and (int(bt_result_str[k]))
        if not flag:
            if not k:
                return 0
            else:
                return days[k-1]
    return days[-1]

def strategy_option(stock_name):
    keys = ['market', 'inout', 'strategy', 'tech_id', 'stock_symbol', 'etf_symbol', 'strike', 'DTE', 'correlation', 'trigging_tech_idx', 'IV_p/IV_c/HV', 'BBlower_Close%', 'BBupper_Close%', 'last_close', 'earning']
    output = {i:'' for i in keys}
    output['correlation'] = '-'.join(stock_name.split('-')[2:])
    Stock_name = stock_name.split('-')[0]
    ETF_name = stock_name.split('-')[1]
    output['stock_symbol'] = Stock_name
    output['etf_symbol'] = ETF_name
    A=Stock_history.sum()
    B=Technical_index.sum()
    G=IV_HV.sum()
    N=earning.sum()
    while True:
        df=A.Stock_price(Stock_name)
        if len(df[:]) < 4:
            print (f'wrong in {stock_name}.csv')
            time.sleep(60)
        else:
            break

    last_close = df[:][-1:]['Close'].values[0]
    output['last_close'] = last_close

    weekly_dict, _ = B.MACD_weekly_check(df,Stock_name, 26, 570*1, period=5, back_ornot=0, weekly_BT=0) # get weekly data_570Weeks
    daily_dict, _ = B.MACD_weekly_check(df,Stock_name, 26, 570*1, period=1, back_ornot=0, weekly_BT=weekly_dict['weekly_BT']) # get daily data_570days
    print (daily_dict)
    condition_result =  strategy_trigger(daily_dict)
#    print ('condition_result: ', condition_result)
    output['market'] = daily_dict['latest_data_MA'][-1].split('_')[0]
    for k in condition_result.keys():
#        print ('k: ', k)
        if condition_result[k][f'in{k[:2]}'][1]:
            output['strategy'] = k[:2]
            output['inout'] = 'in'
            output['trigging_tech_idx'] = condition_result[k][f'in{k[:2]}']
            break
        if condition_result[k][f'out{k[:2]}'][1]:
            output['strategy'] = k[:2]
            output['inout'] = 'out'
            output['trigging_tech_idx'] = condition_result[k][f'out{k[:2]}']
            break
#            if len(k) > 2:
#                assert False, 'do not support combination contract'
#                print ('in', condition_result[k][f'in{k[:2]}'][1])
#                print ('out', condition_result[k][f'out{k[:2]}'][1])
#                print ('in', condition_result[k][f'in{k[2:]}'][1])
#                print ('out', condition_result[k][f'out{k[2:]}'][1])
#            else:
#                print ('in', condition_result[k][f'in{k[:2]}'][1])
#                print ('out', condition_result[k][f'out{k[:2]}'][1])


    if output['strategy'] == '' or output['inout'] == 'out':
        return None

    '''
    L=Stock_back_test.sum()
    L.BT(df, Stock_name)

    with open(os.path.join('obj', Stock_name+'_F.pkl'), 'rb') as f:
        p = pickle.load(f)
    # p['26/Qa/M2'] = 90.0,39.0,140S,2,0x7ff 90%, 漲跌39%, 140天
    # [5.10.15 20.30.40.60 80.100.120.140]
    #  1  1  0  0  0  0  0 0    0  0   0
    #  都不會跌破lower or 漲過upper
    if output['inout'] == 'in':
        if 'BC' in output['strategy']:
            tech_id = 28
        elif 'BP' in output['strategy']:
            tech_id = 29
        elif 'SP' in output['strategy']:
            tech_id = 32
        elif 'SC' in output['strategy']:
            tech_id = 33
        else:
            assert False, 'error in tech_id'
        bt_result = p[f'{tech_id}/Qa/Ma'].split(',')[-1]
        output['tech_id'] = f'{tech_id}/Qa/Ma'
    # BC 28
    # BP 29
    # PCS 32 週日牛正合一
    # CCS 33 週日牛反合一
    # CCS 37 週no日牛反三合一
    
    # d = 勝率超過70%的最近天數
    d = check_fail(str(bin(int(bt_result, 16))))

    options_file_path = os.path.join('option', f'{Stock_name}.csv')
    best_ombination_option = get_combination_option(options_file_path, last_close, d)
    IV = G.IV_HV(Stock_name)
    output['IV_p/IV_c/HV'] = f"{IV['IV']['put']}/{IV['IV']['call']}/{IV['HV']['30day']}"


    if 'C' in output['strategy']:
        date = best_ombination_option['call']['date']
    elif 'P' in output['strategy']:
        date = best_ombination_option['put']['date']
    else:
        assert False


    detla_d = get_date_diff(date, dt.today().strftime("%Y-%m-%d"))
    iv_delta_price = (pow(float(detla_d)/365, 0.5)) * last_close * float(IV['HV']['30day'])
    if 'B' in output['strategy']:
        iv_new_price = 'NAN'
        DTE = 'NAN'
    elif 'S' in output['strategy']:
        DTE = date
        if 'C' in output['strategy']:
            iv_new_price = last_close - iv_delta_price
        elif 'P' in output['strategy']:
            iv_new_price = last_close + iv_delta_price
        else:
            assert False
    else:
        assert False
    output['DTE'] = DTE
    output['strike'] = iv_new_price
    '''
    F = BB.sum()
    BB_dict=F.bollinger_bands(df, DTE=60, lookback=20, numsd=2) # price,DTE,BB中心均線(fix),內BB標準差
    output['BBupper_Close'] = BB_dict['upper_in']
    output['BBlower_Close'] = BB_dict['lower_in']
    output['BBupper_Close%'] = 100 * (BB_dict['upper_in'] - last_close) / last_close
    output['BBlower_Close%'] = 100 * (last_close - BB_dict['lower_in']) / last_close
    output['earning'] = N.earning_get(Stock_name)
    return output
