'''
def frogPosition(n, edges, time, target):
    T = collections.defaultdict(set)
    for u, v in edges:
        T[u].add(v)
        T[v].add(u)

    def dfs(x, y, t, p):
        if t < 0:
            return 0
        zs = [z for z in T[y] if z != x]
        if y == target:
            return 0 if (d and zs) else p
        q = 1 / len(zs)
        return sum(dfs(y, z, t-1, p*q) for z in zs)

    return dfs(-1, 1, time, 1)
    '''

#t_all = [[t1, t2], [t3]]
def Strategy_excecute(t_all):
    print (f'{t_all}')
    D = {}
    global_trigger = False
    def dfs(t1):
        tmp = []
        print (f'{t1}')
        if type(t1) == type([]):
            local_trigger = True
            for t in t1:
                local_trigger = getattr(F, t)() and local_trigger
                tmp.append({f'{t}': getattr(F, t)()})
        else:
            local_trigger = getattr(F, t1)()
            tmp.append({f'{t1}': local_trigger})
        return tmp, local_trigger

    for t in t_all:
        D[t], local_trigger = dfs(t)
        global_trigger = global_trigger or local_trigger
    return D
    
class F():
    def f40up80():
        return True

    def S80up():
        return True

    def M80up():
        return True

    def f40down80():
        return True

    def f40godown():
        return True

    def Sgodown():
        return True

    def S30down():
        return True

    def f5up4():
        return True

    def S70up():
        return True

    def M70up():
        return True

    def f5up4():
        return True

import Stock_history
import Technical_index
import IV_HV

import finviz
import json 
import copy

'''
def Strategy_excecute(tech_idxes):
    res = {}
    if len(tech_idxes) > 1:
        return Strategy_excecute()
    else:
        return
        '''

def Strategy_trigger(tech_idx, config_p='configure_file.json'):
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
    print (condition)

    in_strategies = []
    out_strategies = []
    if True: #'Bull-Big' in tech_idx['latest_data_MA'][-1]:
        condition = condition['big_bull']
        condition_result = copy.deepcopy(condition)
        for strategy in condition.keys():
            if len(strategy) > 2:
                in_sell_tech_idxes = condition[strategy][f'in{strategy[:2]}']                
                in_buy_tech_idxes = condition[strategy][f'in{strategy[2:]}']
                out_sell_tech_idxes = condition[strategy][f'out{strategy[:2]}']                
                out_buy_tech_idxes = condition[strategy][f'out{strategy[2:]}']
                condition_result[strategy][f'in{strategy[:2]}'] = Strategy_excecute(in_sell_tech_idxes)
                print (f'in{strategy[:2]}')
    print (condition_result)

def main():
    Stock_name='AMD'
    A=Stock_history.sum()
    B=Technical_index.sum()
#    G=IV_HV.sum()
    df=A.Stock_price(Stock_name)

    daily_dict=B.MACD_weekly_check(df,Stock_name, 26, 570, period=1, back_ornot=0) # get daily data_570days
    weekly_dict=B.MACD_weekly_check(df,Stock_name, 26, 570, period=5, back_ornot=0) # get weekly data_570Weeks

    print (daily_dict)

    Strategy_trigger(daily_dict)
#    IV_HV_dict=G.IV_HV(Stock_name)


if __name__ == '__main__':
    #print (finviz.get_stock('AMD'))
    main()
