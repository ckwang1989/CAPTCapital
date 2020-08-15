import copy
import os
import glob

def sort_by_value(d): 
    items=d.items() 
    backitems=[[v[1],v[0]] for v in items] 
    backitems.sort(reverse=True)
    d_out = {}
    for i in range(0,len(backitems)):
        d_out[backitems[i][1]] = d[backitems[i][1]]
    return d_out


def multiply_close_interval(sup_pnt_dict_final, close_interval, interval_value_point, valid_percentage_pnt_threthod):
    d = {}
    first_flag = True
    for sup_dict_key in sup_pnt_dict_final.keys():
        if first_flag:
            value_max = sup_pnt_dict_final[sup_dict_key]
            first_flag = False
        if (sup_pnt_dict_final[sup_dict_key] / (value_max+0.0001)) > valid_percentage_pnt_threthod:
            d[round(sup_dict_key*close_interval, interval_value_point)] = round(sup_pnt_dict_final[sup_dict_key] / value_max, 2)
        #d[round(sup_dict_key*close_interval, interval_value_point)] = sup_pnt_dict_final[sup_dict_key]
    return d

def process_pnt_list_to_interval(support_list, sup_pnt_close_interval, close_interval, interval_value_point, valid_percentage_pnt_threthod):
    sup_pnt_dict_final = {}
    for sup_pnt in support_list:
        sup_pnt_interval_num = sup_pnt['Close']//close_interval if sup_pnt['Close']//close_interval < sup_pnt_close_interval else sup_pnt_close_interval
#        print (sup_pnt_interval_num, sup_pnt['Close']//close_interval, sup_pnt['Close'], close_interval, sup_pnt_close_interval)
#        input('w')
        if sup_pnt_interval_num in sup_pnt_dict_final.keys():
            sup_pnt_dict_final[sup_pnt_interval_num] += sup_pnt['Volume_sum']
        else:
            sup_pnt_dict_final[sup_pnt_interval_num] = sup_pnt['Volume_sum']
    sup_pnt_dict_final = sort_by_value(sup_pnt_dict_final)
    sup_pnt_dict_final = multiply_close_interval(sup_pnt_dict_final, close_interval, interval_value_point, valid_percentage_pnt_threthod)
    return sup_pnt_dict_final

def get_interval_volume_sum2(close_list, volume_list, idx, max_pass, max_next, stock_date_list):
    #Input:
    #	temp_list: the close_list from 5 days ago ~ 5 days next
    #	idx: main idx(today's idx)
    #	max & min: the max & min close from 5 days ago ~ 5 days next
    #Output:
    #	max & min idx
    
    stock_volume_sum = 0
    start = 0
    end = len(close_list)
    for index in range(start, end):
        stock_volume_sum+=volume_list[index]
    return stock_volume_sum

def get_supported_point(file_path, sup_pnt_close_interval=100, valid_percentage_sup_pnt_threthod=0.2, m=100*1):
    # step1 先跑5年，記錄最大累積成交量支撐點（sup_pnt_max）
    # step2 從第6年的第一開始，繼續找支撐點，一旦支撐點形成，先看該支撐點的價格跟其他支撐點的價格距離近不近，如果近就合併(update sup_pnt_dict)
    # sup_pnt_dict = {					sup_pnt_dict = {
    #	'23.5': volume1    -> 			'23.5': volume1,
    # }									'27.5': volume2
    #		 							}
    # step3 找到目前的close_max，並算區間
    # step4 將sup_pnt_dict的volume轉換成百分比 if 有新的支撐點
    # sup_pnt_percentage_dict = {				sup_pnt_percentage_dict = {
    #	'23.5_24.5': 80%	 			->			'23.5_24.5': 80%,
    # }												'26.5_27.5': 74%
    #		 									}
    # step5 將sup_pnt_dict的百分比情況update到stock_tech_idx_dict
    # stock_tech_idx_dict = {									sup_pnt_percentage_dict = {
    #	'2002-11-16': {'sup_pnt': {'23.5_24.5': 80%}}	 ->			'2002-11-16': {'sup_pnt': {'23.5_24.5': 80%}},
    # }																'2004-11-16': {'sup_pnt': {'26.5_27.5': 74%}}
    #		 													}


    all = []
    stock_dict_sum = {'topk_vol':[],'supported_point':{},'pressed_point':{},\
                        'moving_average':{}, 'MA_state_dict':{}, 'KD':{}}
    #stock_dict_sum = {'moving_average':{}}
    stock_dict = {}
    press_list = []
    count = 0

    interval_value_point = 3
    period_days = 5
    sup_pnt_dict_final_all = {}
    Open_last, High_last, Low_last, Close_last, Volume_last = 0, 0, 0, 0, 0
    stock_close_list_temp = []
    stock_volume_list_temp = []
    stock_date_list_temp = []
    sup_pnt_dict_final_all = {}
    with open(file_path, 'r') as file_read:
        for line in file_read.readlines():
            line = line.split(',')
            if line[1] == 'Date':
                continue
            Date, Open, High, Low, Close, Volume = line[1], line[2], line[3], line[4], line[5], line[6]
            if Open == 'null' or High == 'null' or Low == 'null' or Close == 'null' or Volume == 'null'\
                or Open == '' or High == '' or Low == '' or Close == '' or Volume == '':
                Open, High, Low, Close, Volume = Open_last, High_last, Low_last, Close_last, Volume_last
            stock_close_list_temp.append(float(Close))
            stock_volume_list_temp.append(float(Volume))
            stock_date_list_temp.append(Date)
            Open_last, High_last, Low_last, Close_last, Volume_last = Open, High, Low, Close, Volume

    pass_drop_rate = 0.05
    next_drop_rate = 0.05
    close_max = -1
    stock_close_list_temp = ((stock_close_list_temp[-m:]))
    for idx_temp, Close_temp in enumerate(stock_close_list_temp):

#        if (len(stock_close_list_temp) - idx_temp) > m:
#            continue
        support_list = []
        sup_pnt_dict = {}
        stock_close_list = stock_close_list_temp[0:idx_temp+1]
        stock_date_list = stock_date_list_temp[0:idx_temp+1]
        stock_volume_list = stock_volume_list_temp[0:idx_temp+1]
        for idx, Close in enumerate(stock_close_list):
            Volume_sum = 0
            with_sup_pnt = True
            with_pression_pnt = True
            
            close_max = Close if Close > close_max else close_max
            close_interval = round((close_max / sup_pnt_close_interval), interval_value_point)
            if idx < period_days or idx+period_days > len(stock_close_list):
                continue


            Close_five_days_pass_min = min(stock_close_list[idx-period_days:idx])
            if Close >= Close_five_days_pass_min:
                with_sup_pnt = False
            Close_five_days_pass_max = max(stock_close_list[idx-period_days:idx])
            if Close > Close_five_days_pass_max*(1-pass_drop_rate):
                with_sup_pnt = False
            Close_five_days_next_max = max(stock_close_list[idx+1:idx+1+period_days])
            if Close > Close_five_days_next_max*(1-next_drop_rate):
                with_sup_pnt = False
            Close_five_days_next_min = min(stock_close_list[idx+1:idx+1+period_days])
            if Close >= Close_five_days_next_min:
                with_sup_pnt = False


            Close_five_days_pass_max = max(stock_close_list[idx-period_days:idx])
            if Close <= Close_five_days_pass_max:
                with_pression_pnt = False
            Close_five_days_pass_min = min(stock_close_list[idx-period_days:idx])
            if Close < Close_five_days_pass_min*(1+pass_drop_rate):
                with_pression_pnt = False
            Close_five_days_next_min = min(stock_close_list[idx+1:idx+1+period_days])
            if Close < Close_five_days_next_min*(1+next_drop_rate):
                with_pression_pnt = False
            Close_five_days_next_max = max(stock_close_list[idx+1:idx+1+period_days])
            if Close < Close_five_days_next_max:
                with_pression_pnt = False

            if not(with_sup_pnt or with_pression_pnt):
                continue
            Volume_sum = get_interval_volume_sum2(stock_close_list[idx-period_days:idx+1+period_days], \
                                            stock_volume_list[idx-period_days:idx+1+period_days], \
                                            idx, Close_five_days_pass_max, Close_five_days_next_max, \
                                            stock_date_list)

            support_dict = {'Date': stock_date_list[idx],
                            'Volume_sum': Volume_sum,
                            'Close': Close,
                            #'Close_list': stock_close_list[idx-self.period_days:idx+1+self.period_days],
                            #'Close_five_days_pass_max': Close_five_days_pass_max,
                            #'Close_five_days_next_max': Close_five_days_next_max,
                            }
            #Volume_Value_max = Close*stock_dict[stock_date_list[idx]]['Volume'] if Close*stock_dict[stock_date_list[idx]]['Volume'] > Volume_Value_max else Volume_Value_max
            #Volume_max = stock_dict[stock_date_list[idx]]['Volume'] if stock_dict[stock_date_list[idx]]['Volume'] > Volume_max else Volume_max
            support_list.append(support_dict)

        sup_pnt_dict_final = process_pnt_list_to_interval(support_list, sup_pnt_close_interval, close_interval, interval_value_point, valid_percentage_sup_pnt_threthod)
    return sup_pnt_dict_final
#        sup_pnt_dict_final_all[stock_date_list_temp[idx_temp]] = copy.deepcopy(sup_pnt_dict_final)
#    return sup_pnt_dict_final_all

def main():
    base_p = '/Users/Wiz/Desktop/wang_fund/CAPTCapital0802/CAPTCapital/stock_temp'
    for p in glob.glob(os.path.join(base_p, '*.csv')):
        if 'EBAY' not in p:
            continue
        print (p)
        result = get_supported_point(p)
        print (result)
if __name__ == '__main__':
    main()