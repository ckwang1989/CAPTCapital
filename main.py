import Stock_history
import Technical_index
import IV_HV
from condition import Condition

import finviz
import json 
import copy

import Stock_back_test

import os
import pickle

import datetime
from datetime import timedelta
from datetime import date as dt
import yfinance as yf

import BB

C = Condition()

# 市場 / 策略 / 進場觸發觸發指標(key) / 股票名稱 / ETF名稱 / 履約價 / 履約日期 / 相似天數 / 觸發進場策略 / 觸發出場策略

def get_date_diff(date1, date2):
    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
    date1 = '{} 10:01:28.585'.format(date1)
    date2 = '{} 09:56:28.067'.format(date2)
    diff = datetime.datetime.strptime(date1, datetimeFormat) - datetime.datetime.strptime(date2, datetimeFormat)
    return diff.days

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


def Strategy_excecute(tech_idx_all, key, condition):
    '''
    transfer the tech_idx_condition to result_flag, e.g.:

    tech_idx_condition: {'BC': {'inBC': [['f40up80']], 
                                'outBC': [['f40godown', 'S80up', 'M80up'], ['f40down80']]}
    result_flag: {'BC': {'inBC': [[[{'f40up80': True}]], True], 
                         'outBC': [[[{'f40godown': True}, {'S80up': True}, {'M80up': True}], [{'f40down80': True}]], True]}
    '''
    L = []
    global_trigger = False
    def excecute(t1):
        local_list = []
        if type(t1) == type([]):
            local_trigger = True
            for t in t1:
                func = getattr(C, t)
                tmp = func(condition)
                local_trigger = tmp and local_trigger
                local_list.append({f'{t}': tmp})
        else:
            func = getattr(C, t)
            local_list.append({f'{t}': func(condition)})
        return local_list, local_trigger

    for t_one_type in tech_idx_all:
        r, local_trigger = excecute(t_one_type)
        L.append(r)
        global_trigger = global_trigger or local_trigger
    return [L, global_trigger]

def Strategy_trigger(tech_idx, config_p='strategy.json'):
    '''
    trigging a specific strategy by tech_idx
    input:
        tech_idx: {'MA5_val_sum': [54.39, 54.25, 54.0, 54.58], 
                    'MA4_val_sum': [54.31, 54.45, 54.55, 54.68], 
                    'MA40_val_sum': [53.97, 53.95, 53.95, 53.92], 
                    'MA80_val_sum': [51.43, 51.34, 51.24, 51.14], 
                    'latest_data_MA': ['P2', 'N3', 'P3', 'P3', 'Bull-Big'], 
                    'OSC_result': [-0.044322812710095305, -0.03365069505980517, 0.0002454249408569975, -0.0030353458753185625], 
                    'EMA13_result': [54.18530694506531, 54.17785817887014, 54.20083438942727, 54.14264024815506], 
                    'D_per_a': [31.91, 33.24, 36.99, 34.55, 'N2'], 
                    'RSI_result': [54.44332661680736, 54.13657128306894, 52.397387033603, 54.098459021013774], 
                    'RSI_result_F': 'P2', 
                    'ATR_avg_sum': [2.21, 2.18, 2.22, 2.28], 
                    'ATR_avg_F': 'P1', 
                    'precent_Vol': 52790500.0, 
                    'V_MA5_val_sum': [49168740.0, 52829940.0, 60502080.0, 67244340.0], 
                    'trigger': {'trigger': '21/Qa/Ma,13/Qa/Ma,'}}
    output:
        trig: {'trend': Bull-Big,
                'in': {'pcs':{'DTE': 3M up, 'strike_buy': xx, 'strike_sell': xx, ''}}
                'out': ['ccs']
    
        }
    '''
    with open(config_p) as json_file: 
        condition = json.load(json_file)

    market = tech_idx['latest_data_MA'][-1].split('_')[0]
    condition = condition[market]
    condition_result = copy.deepcopy(condition)
    for strategy in condition.keys():
        # combination contract
        if len(strategy) > 2:
            strategy_n=strategy.split('_')[0] # Dary: for more strategy
            keys = [f'in{strategy_n[:2]}', f'in{strategy_n[2:]}', f'out{strategy_n[:2]}', f'out{strategy_n[2:]}']
        # single contract
        else:
            strategy_n = strategy
            keys = [f'in{strategy_n[:2]}', f'out{strategy_n[:2]}']
        for k in keys:
            tech_idxes = condition[strategy][k]
            condition_result[strategy][k] = Strategy_excecute(tech_idxes, k, tech_idx)
    return condition_result 

# 市場 / 進or出 / 策略 / 進場觸發觸發指標(key) / 股票名稱 / ETF名稱 / 履約價 / 履約日期 / 相似天數 / 觸發進場策略 / 觸發出場策略
def main():
   #     Stock_name='AMD'
   keys = ['market', 'inout', 'strategy', 'tech_id', 'stock_symbol', 'etf_symbol', 'strike', 'DTE', 'correlation', 'trigging_tech_idx', 'IV_p/IV_c/HV', 'BBlower_Close', 'BBupper_Close', 'last_close']
   for stock_name in open('stock_num.txt', 'r').readlines():
        stock_name = stock_name.strip()
        print (stock_name)
        output = {i:'' for i in keys}
        output['correlation'] = '-'.join(stock_name.split('-')[2:])
        Stock_name = stock_name.split('-')[0]
        A=Stock_history.sum()
        B=Technical_index.sum()
        G=IV_HV.sum()
        df=A.Stock_price(Stock_name)
        last_close = df[:][-1:]['Close'].values[0]
        output['last_close'] = last_close

        # daily_dict=B.MACD_weekly_check(df,Stock_name, 26, 570, period=1, back_ornot=0) # get daily data_570days
        # weekly_dict=B.MACD_weekly_check(df,Stock_name, 26, 570, period=5, back_ornot=0) # get weekly data_570Weeks
        weekly_dict, _ = B.MACD_weekly_check(df,Stock_name, 26, 570*1, period=5, back_ornot=0, weekly_BT=0) # get weekly data_570Weeks
        daily_dict, _ = B.MACD_weekly_check(df,Stock_name, 26, 570*1, period=1, back_ornot=0, weekly_BT=weekly_dict['weekly_BT']) # get daily data_570days

        condition_result =  Strategy_trigger(daily_dict)
        output['market'] = daily_dict['latest_data_MA'][-1].split('_')[0]
        for k in condition_result.keys():
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
            continue

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
#        print ('best_ombination_option: ', best_ombination_option)
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
        F = BB.sum()
        BB_dict=F.bollinger_bands(df, DTE=60, lookback=20, numsd=2) # price,DTE,BB中心均線(fix),內BB標準差
        print (BB_dict)
        output['BBupper_Close'] = (BB_dict['upper_in'] - last_close) / last_close
        output['BBlower_Close'] = (last_close - BB_dict['lower_in']) / last_close
        print ('output: ', output)

if __name__ == '__main__':
    main()
