import requests
# import pandas as pd
from datetime import datetime
import time
import os
import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
import pandas as pd
#import pygsheets
#https://medium.com/@yanweiliu/%E5%A6%82%E4%BD%95%E9%80%8F%E9%81%8Epython%E5%BB%BA%E7%AB%8Bgoogle%E8%A1%A8%E5%96%AE-%E4%BD%BF%E7%94%A8google-sheet-api-314927f7a601
#https://pypi.org/project/gspreadsheet/
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import pickle
import Technical_index


class sum():

    def BT(self, df, name ):
        B=Technical_index.sum()
        test_stock=name
        BT_sum={}
        temp=0
        #filepath=os.getcwd() + os.sep + 'obj' + os.sep + name + '.pkl'
        filepath = os.path.join(os.getcwd(), 'obj', f'{name}.pkl')
        # if not os.path.isfile(filepath):
        for i in [3,10]:
            dict_r, temp=B.MACD_weekly_check(df,test_stock, 26, 570*i, period=5, back_ornot=1, weekly_BT=0) # get weekly data_570Weeks
            dict_r, BT_sum[i]=B.MACD_weekly_check(df,test_stock, 26, 570*i, period=1, back_ornot=1, weekly_BT=dict_r['weekly_BT']) # get daily data_570days
        self.save_obj(BT_sum,test_stock)
        BT=self.load_obj(test_stock)
        sum().BT_combination(BT,70,test_stock) # 卡顯是勝率70以上
        print('%s BT done.'%test_stock)

    def save_obj(self, obj, name ):
        filepath=os.getcwd() + os.sep + 'obj'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        with open(os.path.join('obj', f'{name}.pkl'), 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    def load_obj(self, name ):
        with open(os.path.join('obj', f'{name}.pkl'), 'rb') as f:
            return pickle.load(f)

    def BT_combination(self, BT, T_per,stock):
        dict_r={}
        dict_F={}
        key_1st=BT[3]
        key_2nd=BT[10]
        gain_1st=int(570*3/240+1)
        gain_2nd=int(570*10/240+1)
        for key_type in key_2nd:
            dict_r_T={}
            dict_F_flag=0
            for day in ['5S','10S','15S','20S','30S','40S','60S','80S','100S','120S','140S']:
                for percent in ['0','5','10','15','20']:
                    S_1st_T=0
                    try:
                        W_1st_T=float(key_1st[key_type][day][percent].split('/')[3])
                        P_1st_T=float(key_1st[key_type][day][percent].split('/')[4])
                        S_1st_T=int(key_1st[key_type][day][percent].split('/')[2]) # sample
                        if percent=='0':
                            W_1st=W_1st_T
                            P_1st=P_1st_T
                        if W_1st_T>=T_per:
                            W_1st=W_1st_T
                            P_1st=P_1st_T
                        else:
                            break
                    except:
                        W_1st=0
                        P_1st=0  
                        break               
                for percent in ['0','5','10','15','20']:
                    W_2nd_T=float(key_2nd[key_type][day][percent].split('/')[3])
                    P_2nd_T=float(key_2nd[key_type][day][percent].split('/')[4])
                    S_2nd_T=int(key_2nd[key_type][day][percent].split('/')[2]) # sample
                    if percent=='0':
                        W_2nd=W_2nd_T
                        P_2nd=P_2nd_T
                    if W_2nd_T>=T_per:
                        W_2nd=W_2nd_T
                        P_2nd=P_2nd_T
                    else:
                        break
                if S_2nd_T>1: # only collect >1 sample data
                    if W_1st==0 and P_1st==0:
                        W_r=round(W_2nd*0.9,2) # 只有24年資料打9折
                        P_r=P_2nd
                    else:
                        W_r=round(W_1st*(gain_2nd)/(gain_1st+gain_2nd)+W_2nd*(gain_1st)/(gain_1st+gain_2nd),2)
                        P_r=round(P_1st*(gain_2nd)/(gain_1st+gain_2nd)+P_2nd*(gain_1st)/(gain_1st+gain_2nd),2)          
                    dict_r_T[day]='%s/%s/%s'%(W_r,P_r,(S_2nd_T+S_1st_T))
                    dict_r[key_type]=dict_r_T
                    if W_r>=T_per:
                        dict_F_flag=1
                        dict_F[key_type]='%s,%s,%s,%s'%(W_r,P_r,day,(S_2nd_T+S_1st_T)) # win rate, percent, DTE
                    if day=="140S" and dict_F_flag==1:
                        if '8/Q4/Ma'in key_type:
                            temp=1
                        hex_sum=self.add_Hex(dict_r[key_type],T_per)
                        dict_F[key_type]='%s,%s'%(dict_F[key_type],hex_sum) # add hex show win rate curve
            self.save_obj(dict_r,'%s_r'%stock)
            self.save_obj(dict_F,'%s_F'%stock)
        # dict_back_all_obereved44=self.dict_find(dict_F,'44', '/Ma')
        # dict_back_all_obereved441=self.dict_find(dict_r,'44', 'Qa/Ma')
        # dict_back_all_obereved46=self.dict_find(dict_F,'46', '/Ma')
        # dict_back_all_obereved461=self.dict_find(dict_r,'46', 'Qa/Ma')
        # dict_back_all_obereved34=self.dict_find(dict_r,'9', 'Qa/Ma')

        # dict_back_all_obereved461=self.dict_find(key_1st,'34', '/')
        # dict_back_all_obereved462=self.dict_find(key_2nd,'34', '/')
        return dict_r, dict_F

    def add_Hex(self,R,T_per):

        bin_sum=""
        for day in R:
            win_r=float(R[day].split('/')[0])
            if win_r>=T_per:
                bin_r=1
            else:
                bin_r=0
            bin_sum=bin_sum+str(bin_r)
        hex_sum=hex(int(bin_sum, 2))

        return hex_sum

    def dict_find(self,dict_back_all, key_find, QM_find):
        ket_delete=0
        record_remove=[]
        collect={}
        # for i in range(0, len(dict_back_all)):
        for key in dict_back_all:
            if str(key_find) in key and str(QM_find) in key:
                collect[key]=dict_back_all[key]

        return collect

    