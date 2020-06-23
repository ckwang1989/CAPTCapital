import Stock_history
import Technical_index
import IV_HV

import finviz
import json 
'''
def big_bull_bc(tech_idx):
    status_in = {'in': {'MA'}}
    for i in range(len(tech_idx['MA40_val_sum'])-1):
        if tech_idx['MA40_val_sum'][i] > tech_idx['MA80_val_sum'][i] and \
        tech_idx['MA40_val_sum'][i+1] <= tech_idx['MA80_val_sum'][i+1]:
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
    assert False
#    # BC進場白上跨藍
#    if latest_data_MA[-1] == 'Bull-Big':
#        if 


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
