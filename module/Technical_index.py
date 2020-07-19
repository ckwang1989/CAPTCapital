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


class sum():

    def dict_search(self, key_T,weekly_BT): # 二分法搜尋

        flag_check=int(weekly_BT[0].split(',')[2])
        dict_0={0:0,1:0,2:0,3:0}
        if flag_check >key_T:
            return dict_0, dict_0

        M40_weekly_value={}
        M80_weekly_value={}
        sto_weekly_value={}
        temp=[]
        low=0
        middle=int((len(weekly_BT)-1)/2)
        high=len(weekly_BT)-1
        while len(weekly_BT)>=4:
            flag_check=int(weekly_BT[middle].split(',')[2])
            if flag_check >=key_T:
                high=middle
                middle=int((middle+low)/2) # find middle                
            if flag_check <key_T:
                low=middle
                middle=int((high+middle)/2) # find middle
            if middle-low==1:
                flag_check=int(weekly_BT[middle].split(',')[2])
                if flag_check >= key_T:
                    if low>3:
                        flag=4
                    else:
                        flag=1 # if low=0, weekly[low] will be error
                    for i in range(0,flag):
                        M40_weekly_value[i]=float(weekly_BT[low-i].split(',')[0])
                        M80_weekly_value[i]=float(weekly_BT[low-i].split(',')[1])
                        sto_weekly_value[i]=float(weekly_BT[low-i].split(',')[3])
                    break
            if high-middle==1:
                flag_check=int(weekly_BT[middle].split(',')[2])
                if flag_check <= key_T:
                    if middle>3:
                        flag=4
                    else:
                        flag=1 # if low=0, weekly[low] will be error
                    for i in range(0,flag):
                        M40_weekly_value[i]=float(weekly_BT[middle-i].split(',')[0])
                        M80_weekly_value[i]=float(weekly_BT[middle-i].split(',')[1])
                        sto_weekly_value[i]=float(weekly_BT[middle-i].split(',')[3])      
                    break              

        return M40_weekly_value, M80_weekly_value, sto_weekly_value

    def bollinger_bands(self, df,row,lookback, numsd):
        df = df['Close'].iloc[row-(lookback-1):row+1] # only get lookback array
        #df = df['Close']
        rolling_mean = df.rolling(window=lookback).mean() #,center=False
        rolling_mean = df.rolling(window=lookback).mean() #,center=False
        rolling_std = df.rolling(window=lookback).std() #,center=False
        upper_band = rolling_mean + numsd*rolling_std
        lower_band = rolling_mean - numsd*rolling_std

        close=df[row]
        mean=round(rolling_mean[row],2)
        upper=round(upper_band[row],2)
        lower=round(lower_band[row],2)

        upper_per=round((upper-close)/close*100,2)
        lower_per=round((close-lower)/close*100,2)

        return upper_per,lower_per,mean,upper,lower

    def option_out_price(self, period, lower, upper, first_close_back):
        if period==1:
            try:
                first_close_back_L="%s,%s"%(lower,first_close_back)#[lower,first_close_back] #OTM
                first_close_back_R="%s,%s"%(upper,first_close_back)#[upper,first_close_back] #OTM
            except:
                first_close_back_L="%s,%s"%(first_close_back,first_close_back)#
                first_close_back_R="%s,%s"%(first_close_back,first_close_back)#
        else:
            first_close_back_L="%s,%s"%(first_close_back,first_close_back)#[first_close_back,first_close_back]#lower #OTM
            first_close_back_R="%s,%s"%(first_close_back,first_close_back)#[first_close_back,first_close_back]#upper #OTM 
        
        return first_close_back_L,first_close_back_R

    def slew_rate_check(self, list,percent,day):
        flag1=0
        for i in range(0,day):
            if abs((list[1-i]-list[2-i])/list[2-i])*100<=percent:
                flag1=flag1+1
        if flag1>=2:
            result=1
        else:
            result=0
        return result

    def MACD_weekly_check(self, df, stock_name, MA_day, EMA_day, period, back_ornot, weekly_BT):
        back_en=1 # 
        # upper_per,lower_per,mean,upper,lower=self.bollinger_bands(df,9000,20,2)
        # back_ornot=1
    #==dim array
        MA5_val_sum=[0, 0, 0, 0]
        MA4_val_sum=[0, 0, 0, 0]
        MA40_val_sum=[0, 0, 0, 0]
        MA80_val_sum=[0, 0, 0, 0]
        latest_data_MA=[0, 0, 0, 0, 0]

        OSC_result=[0, 0, 0, 0]
        DIF_result=[0, 0, 0, 0]
        DIF_result_dict={}
        EMA13_result=[0, 0, 0, 0]
        per_DIF=[0, 0, 0, 0]
        latest_data_MACD=[0, 0, 0, 0, 0] #'DIF': 0,'DEM': 0,'OSC': 0,'MACD%': 0,'MACD%_s': 0
        K_per_a=[0, 0, 0, 0, 0, 0]
        D_per_a=[0, 0, 0, 0 ]#,0
        max_dict={}
        min_dict={}
        MA5_AVG_dict={}
        MA4_AVG_dict={}
        MA40_AVG_dict={}
        MA80_AVG_dict={}
        MA40_Weekly_BT={}
        MA80_Weekly_BT={}
        BB={}
        upper_list=[0, 0, 0, 0, 0, 0]#,0
        lower_list=[0, 0, 0, 0, 0, 0]#,0
        MA_40_80_Weekly_BT={}

        row_n =int(len(df))-1
        a = MA_day
        b = EMA_day

        pre_Start=0
        sum_MA = 0
        Start_MA = row_n - (b + 1) * period
        if Start_MA<0:
            Start_MA=50
        #==============check Week=5?
        if period>1:
            Start_MA = self.Week_check(df, Start_MA,row_n)
        #==============check Week=5?
        for i in range(0,a):
            temp=df['Close'][int(Start_MA)]
            sum_MA=sum_MA+df['Close'][int(Start_MA)]
            Start_MA=Start_MA-1
        sum_MA=sum_MA/a
        Start = Start_MA+a+period
        #==============check Week=5?
        if period>1:
            Start_MA = self.Week_check(df, Start,row_n)
    #===RSI
        RSI_gain=0
        RSI_loss=0
        RSI_result=[0, 0, 0, 0]
        RSI_days=13
        RSI_days_flasg=RSI_days
        change_dict={}
        RSI_dict={}
    #==============check Week=5?		
        EMA_n_1_12=0
        EMA_n_1_13=0
        EMA_n_1_26=0
        DIF_n_1_9=0
        i=1
        EMA_12={}
        flag_max_min=0
        flag_KD_loop=5
        max_min_F=0
        period_high=0
        period_low=0

        flag_MA45=0
        flag_MA48=0
        flag_MA5=0
        flag_MA4=0
        flag_MA40=0
        flag_MA80=0
        MA5=0
        MA4=0
        MA40=0
        MA40_minus=0
        MA80=0
        MA80_minus=0

        n40=39 # weight MA40
        n80=79 # weight MA80
    #========================Volume
        V_EMA5=0
        flag_V_EA5=0
        flag_V_EMA5=0

        Start_flag5_V=0 # for MA5
        V_EMA5_minus_f=0 # for ma5
        temp_V_MA5_d={}
        temp_V_MA5=0

        V_EMA5_AVG_dict={}
    #=======================record value of minus MA5
        Start_flag5=0 # for MA5
        MA5_minus_f=0 # for ma5
        temp_0={}
        temp_1=0
    #=======================record value of minus: MA40
        Start_flag40=0 # for MA40
        MA40_minus_f=0 # for ma40
        temp_3={}
        temp_4=0	
        # =============deviate use
    #=============OSC_dec
        OSC_dev={} # record V
        OSC_dev_result={}
        OSC_Backtest=0
        price_OSC_dev={} # record V of price
        price_OSC_dev_result={}
    #=============%D_dec
        D_dev={} # record V
        D_dev_result={}
        D_Backtest=0
        price_D_dev={} # record V of price
        price_D_dev_result={}
    #=============RSI_dec
        RSI_dev={} # record V
        RSI_dev_result={}
        RSI_Backtest=0
        price_RSI_dev={} # record V of price
        price_RSI_dev_result={} 
    #======ATR===
        list_TR=[]
        TR_F=0
        TR_sum=0
        list_ATR=[]
        ATR_avg=0

    #=====backtesting
        total_lookup=25
        dict_back_all={}
        dict_flag_end_record_buy={} # for last one record
        dict_flag_end_record_sell={} # for last one record
        dict_flag_all=[]
        # if back_ornot==1 and period==1:
            # MA40_AVG_dict_weekly=weekly_BT[0]
            # MA80_AVG_dict_weekly=weekly_BT[1]
            # start=10150
            # M40_weekly_value, M80_weekly_value=self.dict_search(start,weekly_BT)

    #===loop start
        flag_error=0

        if back_ornot==0:
            DIF_criteria=90
            EMA5_Volum_criteria=(10)*period
            MA5_base_criteria=(10)*period
            MA40_base_criteria=(121)*period
            sto_criteria=(12+3+1+(b-100))*period
            ATR_criteria=(17)*period
        else:
            DIF_criteria=9999999999
            EMA5_Volum_criteria=9999999999
            MA5_base_criteria=9999999999
            MA40_base_criteria=9999999999
            sto_criteria=9999999999
            ATR_criteria=9999999999
        minus_dif=0
        self.out_check=0 # backtest use
        while Start<=row_n:
            flag_error=flag_error+1
            if flag_error>row_n+100: # avoid infiniti loop, then lost worker
                print('tek error')
                break
            if back_ornot==1 and period==1: # get weekly MA40 & MA80
                M40_weekly_value, M80_weekly_value, sto_weekly_value=self.dict_search(Start,weekly_BT)
            else:
                if Start>=row_n-5 and period==1:
                    M40_weekly_value={}
                    M80_weekly_value={}
                    sto_weekly_value={}
                    for M4080 in range(0,4):
                        M40_weekly_value[M4080]=float(weekly_BT[len(weekly_BT)-1-M4080].split(',')[0])
                        M80_weekly_value[M4080]=float(weekly_BT[len(weekly_BT)-1-M4080].split(',')[1])
                        sto_weekly_value[M4080]=float(weekly_BT[len(weekly_BT)-1-M4080].split(',')[3])
                elif  period==5:
                        M40_weekly_value=""
                        M80_weekly_value=""
                        sto_weekly_value=""
            try:
                nan_check=df['Close'][int(Start)]
                if nan_check==nan_check:
                #===MACD
                    if i==1:
                        sum_EMA_12=sum_MA+2/(12+1)*(df['Close'][int(Start)]-sum_MA)
                        sum_EMA_13=sum_MA+2/(13+1)*(df['Close'][int(Start)]-sum_MA)
                        sum_EMA_26=sum_MA+2/(26+1)*(df['Close'][int(Start)]-sum_MA)
                        DIF=sum_EMA_12-sum_EMA_26
                        sum_DEM_9=0+2/(9+1)*(DIF-0)
                    else:
                        #MACD
                        sum_EMA_12=EMA_n_1_12+2/(12+1)*(df['Close'][int(Start)]-EMA_n_1_12)
                        sum_EMA_13=EMA_n_1_13+2/(13+1)*(df['Close'][int(Start)]-EMA_n_1_13)
                        sum_EMA_26=EMA_n_1_26+2/(26+1)*(df['Close'][int(Start)]-EMA_n_1_26)
                        DIF=sum_EMA_12-sum_EMA_26
                        sum_DEM_9=DIF_n_1_9+2/(9+1)*(DIF-DIF_n_1_9)

                    EMA_n_1_12=sum_EMA_12
                    EMA_n_1_13=sum_EMA_13
                    EMA_n_1_26=sum_EMA_26
                    DIF_n_1_9=sum_DEM_9
                    DEM=sum_DEM_9
                    OSC=DIF-DEM

                    #=====put adata into array for record
                    DIF_result[3]=DIF_result[2]
                    DIF_result[2]=DIF_result[1]
                    DIF_result[1]=DIF_result[0]
                    DIF_result[0]=round(DIF,2)

                    #=======DIF percentage  90交易日的DIF百分比
                    if row_n-Start<=DIF_criteria:
                        DIF_result_dict[len(DIF_result_dict)+minus_dif]=round(DIF,2)
                        if len(DIF_result_dict)>=90:                       
                            y={key: rank for rank, key in enumerate(sorted(DIF_result_dict, key=DIF_result_dict.get, reverse=False),1)}
                            y_L=90+minus_dif-1
                            per_DIF[0]=round(y[y_L]/90*100,2)  #latest DIF%
                            per_DIF[1]=round(y[y_L-1]/90*100,2)
                            per_DIF[2]=round(y[y_L-2]/90*100,2)
                            per_DIF[3]=round(y[y_L-3]/90*100,2)

                            del DIF_result_dict[minus_dif]
                            minus_dif=minus_dif+1
                            if minus_dif==87:
                                temp=1

                    EMA_12[i]=DIF # record DIF for % caculation

                    OSC_result[3]=OSC_result[2]
                    OSC_result[2]=OSC_result[1]
                    OSC_result[1]=OSC_result[0]
                    OSC_result[0]=OSC

                    EMA13_result[3]=EMA13_result[2]
                    EMA13_result[2]=EMA13_result[1]
                    EMA13_result[1]=EMA13_result[0]
                    EMA13_result[0]=sum_EMA_13	
                    #=====put adata into array for record

                #===sto %K
                    if row_n-Start<=sto_criteria: #(12+3+1+(b-100))*period: #+(b-100)
                        #there are 16 keys in dict for record highest/lowest
                        if period==1:
                            max_dict[flag_max_min]=df['High'][int(Start)]
                            min_dict[flag_max_min]=df['Low'][int(Start)]
                        else:
                            max_dict[flag_max_min]=period_high
                            min_dict[flag_max_min]=period_low						
                        flag_max_min=flag_max_min+1		# initial: flag_max_min=0	
                        try:	
                            if max_dict[11]>=0: #row_n-Start==flag_KD_loop*period: # record the latest 5 K%     max_dict[11]>=0: #
                                high=max_dict[max(max_dict,key=max_dict.get)]
                                low=min_dict[min(min_dict,key=min_dict.get)]
                                temp=df['Close'][int(Start)]
                                # if high-low==0:
                                #     temp=1
                                if flag_KD_loop==-1:
                                    K_per_a[5]=K_per_a[4]
                                    K_per_a[4]=K_per_a[3]
                                    K_per_a[3]=K_per_a[2]
                                    K_per_a[2]=K_per_a[1]
                                    K_per_a[1]=K_per_a[0]

                                    D_per_a[3]=D_per_a[2]
                                    D_per_a[2]=D_per_a[1]
                                    D_per_a[1]=D_per_a[0]
                                    flag_KD_loop=0
                                if (high-low)!=0:
                                    K_per_a[flag_KD_loop]=round((df['Close'][int(Start)]-low)/(high-low)*100,2)
                                else:
                                    K_per_a[flag_KD_loop]=pow(10,-6)
                                if flag_KD_loop<=3:
                                    D_per_a[flag_KD_loop]=round((K_per_a[flag_KD_loop]+K_per_a[flag_KD_loop+1]+K_per_a[flag_KD_loop+2])/3,2)
                                max_dict[max_min_F]=0 # clear oldest of record
                                min_dict[max_min_F]=9000 # clear oldest of record
                                max_min_F=max_min_F+1 # new data put into next key
                                flag_KD_loop=flag_KD_loop-1
                            #====deviate check
                        except:
                            pass

                #===RSI # https://zhuanlan.zhihu.com/p/95748397           
                    if pre_Start>0: #Start>=1
                        # calculate avg for RS
                        change_dict[len(change_dict)]=float(df['Close'][int(Start)])-float(df['Close'][int(pre_Start)]) #Start-1
                        change=float(change_dict[len(change_dict)-1])
                        if change >=0: #sum
                            RSI_gain=RSI_gain+change
                        else:
                            RSI_loss=RSI_loss+abs(change)
                        RSI_days_flasg=RSI_days_flasg-1                      
                        try:	
                            if RSI_days_flasg<=0: #calculate AVG gain/loss
                                if (RSI_loss/RSI_days)==0:
                                    RSI=100
                                else:
                                    RSI_RS=(RSI_gain/RSI_days)/(RSI_loss/RSI_days)
                                    RSI=100-(100/(1+RSI_RS))

                                #========minus 1st avg_tiem for next avg
                                change_pre=change_dict[len(change_dict)-13]    #float(df['Close'][int(Start-(RSI_days-1))])-float(df['Close'][int(Start-1-(RSI_days-1))])
                                if change_pre >=0:
                                    RSI_gain=RSI_gain-abs(change_pre)
                                else:
                                    RSI_loss=RSI_loss-abs(change_pre)
                                #========minus 1st avg_tiem for next avg

                                #==================================AVG5
                                RSI_dict[len(RSI_dict)]=RSI
                                if len(RSI_dict)>=5:
                                    RSI_Avg=(RSI_dict[len(RSI_dict)-1]+RSI_dict[len(RSI_dict)-2]+RSI_dict[len(RSI_dict)-3]+RSI_dict[len(RSI_dict)-4]+RSI_dict[len(RSI_dict)-5])/5

                                RSI_result[3]=RSI_result[2]
                                RSI_result[2]=RSI_result[1]
                                RSI_result[1]=RSI_result[0]
                                RSI_result[0]=RSI_Avg
                        except:
                            pass

                #===EMA5-Volume	/ sample	
                    if row_n-Start<=EMA5_Volum_criteria: #(10)*period:	
                        
                        temp_V_MA5_d[temp_V_MA5]='%s,%s'%(str(df['Volume'][int(Start)]),str(Start))
                        precent_Vol=float(temp_V_MA5_d[len(temp_V_MA5_d)-1].split(',',2)[0])  # use for backtest
                        temp_V_MA5=temp_V_MA5+1

                        V_EMA5 = float(V_EMA5) + df['Volume'][int(Start)]
                        flag_V_EMA5=flag_V_EMA5+1
                        if flag_V_EMA5>=5:
                            V_EMA5_minus_f=int(temp_V_MA5_d[Start_flag5_V].split(',',2)[1])
                            V_EMA5_AVG_dict[flag_V_EA5]=round(float(V_EMA5)/(5),2) #(Start-V_EMA5_minus_f+1)=分母		
                            precent_V_EMA5=V_EMA5_AVG_dict[len(V_EMA5_AVG_dict)-1]			
                            V_EMA5=float(V_EMA5)-df['Volume'][int(V_EMA5_minus_f)] # Start-(4)
                            Start_flag5_V=Start_flag5_V+1 #用來扣掉四個以前(不一定是四個，遇到假日))
                            flag_V_EA5=flag_V_EA5+1

                        try:
                            V_MA5_val_len=len(V_EMA5_AVG_dict)
                            V_MA5_val_sum=[V_EMA5_AVG_dict[V_MA5_val_len-1], V_EMA5_AVG_dict[V_MA5_val_len-2], V_EMA5_AVG_dict[V_MA5_val_len-3], V_EMA5_AVG_dict[V_MA5_val_len-4]] #daily_ok
                        except:
                            V_MA5_val_sum=[0, 0, 0, 0]      

                #===MA5-base close			
                    if row_n-Start<=MA5_base_criteria: #(10)*period:	
                        
                        temp_0[temp_1]='%s,%s'%(str(df['Close'][int(Start)]),str(Start))
                        temp_1=temp_1+1
                        # if int(Start)==12513:
                        # 	stop=1
                        MA5 = float(MA5) + df['Close'][int(Start)]
                        flag_MA45=flag_MA45+1
                        if flag_MA45>=5:
                            MA5_minus_f=int(temp_0[Start_flag5].split(',',2)[1])
                            MA5_AVG_dict[flag_MA5]=round(float(MA5)/(5),2) #(Start-MA5_minus_f+1)=分母					
                            MA5=float(MA5)-df['Close'][int(MA5_minus_f)] # Start-(4)
                            Start_flag5=Start_flag5+1 #用來扣掉四個以前(不一定是四個，遇到假日))
                            MA4=MA4+MA5_AVG_dict[flag_MA5]
                            flag_MA5=flag_MA5+1
                            #===MA4-base MA5
                            if len(MA5_AVG_dict)>=4:
                                MA4_AVG_dict[flag_MA4]=round(float(MA4)/4,2)
                                MA4=float(MA4)-MA5_AVG_dict[flag_MA5-1-3]
                                flag_MA4=flag_MA4+1
                        # if Start==10139:
                        #     temp=1
                        try:
                            MA5_val_len=len(MA5_AVG_dict)
                            MA5_val_sum=[MA5_AVG_dict[MA5_val_len-1], MA5_AVG_dict[MA5_val_len-2], MA5_AVG_dict[MA5_val_len-3], MA5_AVG_dict[MA5_val_len-4]] #daily_ok
                        except:
                            MA5_val_sum=[0, 0, 0, 0]      
                        try:                  
                            MA4_val_len=len(MA4_AVG_dict)
                            MA4_val_sum=[MA4_AVG_dict[MA4_val_len-1], MA4_AVG_dict[MA4_val_len-2], MA4_AVG_dict[MA4_val_len-3], MA4_AVG_dict[MA4_val_len-4]] #daily_ok
                        except:
                            MA4_val_sum=[0, 0, 0, 0]  

                    # if Start==8677:
                    #     temp=1
                    #     temp_close=df['Close'][int(Start)]
                    #     temp_2=temp_3[Start_flag40]
                    #     temp_3=MA40_AVG_dict[len_40-1]
                    
                #===MA40-base close		

                    if row_n-Start<=MA40_base_criteria:#(121)*period:   
                        temp_3[temp_4]='%s,%s'%(str(df['Close'][int(Start)]),str(Start))
                        temp_4=temp_4+1
                        # MA40 = float(MA40) + df['Close'][int(Start)]
                        MA40=float(MA40)+float(df['Close'][int(Start)])*(40-n40)/(40*(40+1)/2)
                        if MA40!=MA40: # check nan
                            temp=1
                        MA40_minus = float(MA40_minus) + float(df['Close'][int(Start)])
                        if n40!=0: #weighting
                            n40=n40-1
                        flag_MA48=flag_MA48+1
                        if flag_MA48>=40:
                            # MA40_minus_f=int(temp_3[Start_flag40].split(',',2)[1])
                            # MA40_AVG_dict[flag_MA40]=round(float(MA40)/40,2)
                            MA40_AVG_dict[flag_MA40]=round(MA40,2)
                            # if period==5:
                            #     MA40_Weekly_BT[flag_MA40]=str(round(MA40,2)) + ',' +  str(Start) # used for weekly backtest        
                            # MA40=float(MA40)-df['Close'][int(Start-39)]
                            MA40=float(MA40)-MA40_minus/(40*(40+1)/2)
                            # temp_1234=df['Close'][int(MA40_minus_f)] 
                            MA40_minus=float(MA40_minus)-float(temp_3[Start_flag40].split(',',2)[0])#Start-39*period
                            Start_flag40=Start_flag40+1 #用來扣掉四個以前(不一定是四個，遇到假日))
                            # MA80=MA80+MA40_AVG_dict[flag_MA40]
                            MA80=MA80+MA40_AVG_dict[flag_MA40]*(80-n80)/(80*(80+1)/2)
                            MA80_minus = float(MA80_minus) + MA40_AVG_dict[flag_MA40]
                            if n80!=0: #weighting
                                n80=n80-1
                            flag_MA40=flag_MA40+1
                            #===MA80-base MA40
                            if len(MA40_AVG_dict)>=80:
                                # MA80_AVG_dict[flag_MA80]=round(float(MA80)/80,2)
                                MA80_AVG_dict[flag_MA80]=round(MA80,2)
                                # MA80=float(MA80)-MA40_AVG_dict[flag_MA40-1-79
                                MA80=float(MA80)-MA80_minus/(80*(80+1)/2)
                                MA80_minus=float(MA80_minus)-MA40_AVG_dict[flag_MA40-1-79]
                                flag_MA80=flag_MA80+1
                        
                        try:
                            len_40=len(MA40_AVG_dict)
                            MA40_val_sum=[MA40_AVG_dict[len_40-1], MA40_AVG_dict[len_40-2], MA40_AVG_dict[len_40-3], MA40_AVG_dict[len_40-4]] #daily_ok
                        except:
                            MA40_val_sum=[0, 0, 0, 0] #daily_ok
                        try:
                            len_80=len(MA80_AVG_dict)
                            MA80_val_sum=[MA80_AVG_dict[len_80-1], MA80_AVG_dict[len_80-2], MA80_AVG_dict[len_80-3], MA80_AVG_dict[len_80-4]] #daily_ok
                        except:
                            MA80_val_sum=[0, 0, 0, 0] #daily_ok

                        if period==5: # for backtest, record weekly data into daily
                            MA_40_80_Weekly_BT[flag_MA80]=str(round(MA40_val_sum[0],2)) + ',' + str(round(MA80_val_sum[0],2)) + ',' +  str(Start) + ',' + str(D_per_a[0]) # used for weekly backtest
                            # temp1=MA_40_80_Weekly_BT[len(MA_40_80_Weekly_BT)-1].split(',')[2]
                            # temp1=MA_40_80_Weekly_BT[len(MA_40_80_Weekly_BT)-1].split(',')[1]
                            # temp1=MA_40_80_Weekly_BT[len(MA_40_80_Weekly_BT)-1].split(',')[0]

                #====deviate check
                    try:                  
                        # price_dev={} # record V of price
                        # price_dev_result={}
                        RSI_Backtest,price_RSI_dev,price_RSI_dev_result,RSI_dev, RSI_dev_result=self.deviate_check(df,Start,RSI_Backtest,price_RSI_dev,price_RSI_dev_result, RSI_dev,RSI_dev_result, RSI_result,0,50)
                        OSC_Backtest,price_OSC_dev,price_OSC_dev_result,OSC_dev, OSC_dev_result=self.deviate_check(df,Start,OSC_Backtest,price_OSC_dev,price_OSC_dev_result, OSC_dev,OSC_dev_result, OSC_result,0,0)
                        D_Backtest,price_D_dev,price_D_dev_result,D_dev, D_dev_result=self.deviate_check(df,Start,D_Backtest,price_D_dev,price_D_dev_result, D_dev,D_dev_result, D_per_a,0,50)
                        # dev_n_date,'bear_dev',per_dev,per_price,dev_n_price
                    except:
                        pass

                #====ATR====
                    if row_n-Start<ATR_criteria: #(17)*period:
                        close_n_1_ATR=df['Close'][int(pre_Start)]
                        # TR=MAX(high-low,ABS(high-close_n-1),ABS(close_n-1-low))
                        high_ATR=df['High'][int(Start)]
                        low_ATR=df['Low'][int(Start)]
                        for check_HL in range(0,(Start-pre_Start)): # for weekly to find highest/lowest price during a week
                            if df['High'][int(Start-check_HL)]>high_ATR and period>1:
                                high_ATR=df['High'][int(Start-check_HL)]
                            if df['Low'][int(Start-check_HL)]<low_ATR and period>1:
                                low_ATR=df['Low'][int(Start-check_HL)]
                        close_n_ATR=df['Close'][int(Start)]
                        # close_n_1_ATR=df['Close'][int(Start-1*period)]
                        TR=max(high_ATR-low_ATR,abs(high_ATR-close_n_1_ATR),abs(close_n_1_ATR-low_ATR))
                        TR_sum=TR_sum+TR
                        list_TR.append(TR_F)
                        list_TR[TR_F]=TR
                        TR_F=TR_F+1
                        if TR_F>=14: # (ATR14)
                            # AVERAGE(TR_1:TR_14)    
                            list_ATR.append(ATR_avg)                    
                            list_ATR[ATR_avg]=round(TR_sum/14,2)
                            TR_sum=TR_sum-list_TR[TR_F-14]
                            ATR_avg=ATR_avg+1

                #======BB=====
                    if period==1:
                        if back_ornot==back_en or back_ornot==1: 
                            upper_per,lower_per,mean,upper,lower=self.bollinger_bands(df,Start,20,2)
                            upper_list[5]=upper_list[4]
                            upper_list[4]=upper_list[3]
                            upper_list[3]=upper_list[2]
                            upper_list[2]=upper_list[1]
                            upper_list[1]=upper_list[0]
                            upper_list[0]=upper
                            lower_list[5]=lower_list[4]
                            lower_list[4]=lower_list[3]
                            lower_list[3]=lower_list[2]
                            lower_list[2]=lower_list[1]
                            lower_list[1]=lower_list[0]
                            lower_list[0]=lower
                        if Start>=row_n-5:
                            upper_per,lower_per,mean,upper,lower=self.bollinger_bands(df,Start,20,2)
                            upper_list[5]=upper_list[4]
                            upper_list[4]=upper_list[3]
                            upper_list[3]=upper_list[2]
                            upper_list[2]=upper_list[1]
                            upper_list[1]=upper_list[0]
                            upper_list[0]=upper
                            lower_list[5]=lower_list[4]
                            lower_list[4]=lower_list[3]
                            lower_list[3]=lower_list[2]
                            lower_list[2]=lower_list[1]
                            lower_list[1]=lower_list[0]
                            BB['upper']=upper 
                            BB['lower']=lower 
                    else:
                        BB=''
                        upper=0   
                        lower=0                      

                #========backtesting
                    if Start==5447:
                        temp=1
                    
                    if back_ornot==back_en or Start>=row_n-5:  #Start==row_n: latest days check trigger event
                        stop_per_default=0.2 #停損+/-2%  改用當時的BB
                        Date_precent=df['Date'][int(Start-1)].date() #datetime.strptime(df['Date'][int(Start)], "%Y-%m-%d").date()
                        if back_ornot==0: # no backtest only run once loop 
                            loop_QM=1
                        else:
                            loop_QM=2
                        for Qa in range(0,loop_QM): #season
                            if back_ornot==2: # no backtest don't check month and Q 
                                Qa=1
                            if Qa==0: # 分開統計
                                if Date_precent.month>=1 and Date_precent.month<=3:
                                    Q_n='Q1'
                                elif Date_precent.month>=4 and Date_precent.month<=6:
                                    Q_n='Q2'
                                elif Date_precent.month>=7 and Date_precent.month<=9:
                                    Q_n='Q3'
                                elif Date_precent.month>=10 and Date_precent.month<=12:
                                    Q_n='Q4'
                            else: # total
                                Q_n='Qa'
                            for Ma in range(0,loop_QM): #Month
                                if back_ornot==2: # no backtest don't check month and Q   # back_ornot==1 for development@@@@
                                    Ma=1
                                if Ma==0: # 分開統計
                                    M_n='M%s'%Date_precent.month
                                else: # total
                                    M_n='Ma' 
                                for Va in range(0,0): #Month  precent_V_EMA5   precent_Vol   先disable
                                    if Va==1: # total
                                        V_n='Va'
                                    else: # 分開統計
                                        if flag_V_EMA5>=5: # EMA5>5
                                            if precent_Vol >=precent_V_EMA5*2:
                                                V_n='V%s'%2 # 當前量>=5日均量*2
                                            else:
                                                continue 
                                        else:
                                            continue                                    
                                    sum_check='/%s/%s/%s'%(Q_n,M_n,V_n) #技術指標項目/季/月/量
                                sum_check='/%s/%s'%(Q_n,M_n) #技術指標項目/季/月/量

                        #=======out condition=========    3_R                            
                            #白下彎(n) & S靠近80: 1_L
                                if MA40_val_sum[0]<MA40_val_sum[1] and MA40_val_sum[1]>MA40_val_sum[2] and D_per_a[0]>=60: # 白下彎(n) & S靠近80
                                    self.out_check='1_L'
                            #白上彎(V) & S靠近20: 1_R
                                if MA40_val_sum[0]>MA80_val_sum[1] and MA40_val_sum[1]<MA40_val_sum[2] and D_per_a[0]<=40: # 白上彎(V) & S靠近20
                                    self.out_check='1_R'
                            #白下跨藍: 2_L
                                if MA40_val_sum[0]<MA80_val_sum[0] and MA40_val_sum[1]>MA80_val_sum[1]: # 白下跨藍
                                    self.out_check='2_L'
                            #白上跨藍: 2_R
                                if MA40_val_sum[0]>MA80_val_sum[0] and MA40_val_sum[1]<MA80_val_sum[1]: # 白上跨藍
                                    self.out_check='2_R'
                            #綠下跨紅: 3_L
                                if MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1]: # 
                                    self.out_check='3_L'
                            #綠上跨紅: 3_R
                                if MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1]: # 
                                    self.out_check='3_R'
                            #S下彎(n) & M負斜率: 4_L
                                if D_per_a[0]<D_per_a[1] and D_per_a[1]>D_per_a[2] and per_DIF[0]<per_DIF[1]: # 
                                    self.out_check='4_L'
                            #S上彎(V) & M正斜率: 4_R
                                if D_per_a[0]>D_per_a[1] and D_per_a[1]<D_per_a[2] and per_DIF[0]>per_DIF[1]: # 
                                    self.out_check='4_R'
                            #M下彎(n) & S負斜率: 5_L
                                if per_DIF[0]<per_DIF[1] and per_DIF[1]>per_DIF[2] and D_per_a[0]<D_per_a[1]: # 
                                    self.out_check='5_L'
                            #M上彎(V) & S正斜率: 5_R
                                if per_DIF[0]>per_DIF[1] and per_DIF[1]<per_DIF[2] and D_per_a[0]>D_per_a[1]: # 
                                    self.out_check='5_R'
                            #綠下跨紅 & S/M靠近80: 6_L
                                if MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1] and D_per_a[0]>=60 and per_DIF[0]>=60: # 
                                    self.out_check='6_L'
                            #綠上跨紅 & S/M靠近20: 6_R
                                if MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1] and D_per_a[0]<=40 and per_DIF[0]<=40: # 
                                    self.out_check='6_R'
                            #綠下跨紅 & S/M下彎: 7_L
                                if MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1] and D_per_a[0]<max(D_per_a) and per_DIF[0]<max(per_DIF): # 
                                    self.out_check='7_L'
                            #M%<20 & M上勾3%: 8_R
                                if per_DIF[0]<=20 and DIF_result[0]>min(DIF_result)*1.03: # 
                                    self.out_check='8_R'
                            #向下跳空: 9_L
                                if df['Open'][int(Start)]<df['Close'][int(Start-1)]*(1-1.2): # 
                                    self.out_check='9_L'
                            #白下彎(n): 10_L
                                if MA40_val_sum[0]<MA40_val_sum[1] and MA40_val_sum[1]>MA40_val_sum[2]: # 白下彎(n)
                                    self.out_check='10_L'
                            #>=上BB: 11_L
                                if close_n_ATR>=upper: 
                                    self.out_check='11_L'
                            #<=下BB: 11_R
                                if close_n_ATR<=lower: 
                                    self.out_check='11_R'
                            #sto破50向下: 12_L
                                if D_per_a[0]<50 and D_per_a[1]>50: 
                                    self.out_check='12_L'
                            #sto破50向上: 12_R
                                if D_per_a[0]>50 and D_per_a[1]<50: 
                                    self.out_check='12_R'
                        #===trigger condition
                        # dict_sum
                            #====背離
                                # if Start>=1601:
                                #     temp=1
                                if len(D_dev_result)>=1:                       
                                    D_dev_result_Date=datetime.strptime(D_dev_result[len(D_dev_result)-1].split('/')[0], "%Y-%m-%d %H:%M:%S").date()
                                    D_dev_result_gain=D_dev_result[len(D_dev_result)-1].split('/')[1]
                                    D_dev_result_per_dev=float(D_dev_result[len(D_dev_result)-1].split('/')[2]) # percent of dev
                                    D_dev_result_per_price=float(D_dev_result[len(D_dev_result)-1].split('/')[3]) # percent of price
                                    D_dev_trggered=(Date_precent-D_dev_result_Date).days # used for dec trigger
                                    #strike
                                    first_close_back=float(D_dev_result[len(D_dev_result)-1].split('/')[4]) # ATM
                                    first_close_back_L,first_close_back_R=self.option_out_price(period,lower,upper,first_close_back) 
                                #==1. D%空頭背離, bull
                                    if  D_dev_trggered==0 and D_dev_result_gain=='bear_dev' :
                                        num=str('1%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==2. D%空頭背離+D%<=30, bull
                                    if  D_per_a[0]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev': #
                                        num=str('2%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==3. D%空頭背離+D%<=30+delta_price_dec>=4, bull
                                    if  D_per_a[0]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev' and D_dev_result_per_dev>=4 and D_dev_result_per_price>=4: #
                                        num=str('3%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==4. D%空頭背離+D%<=30+delta_price_dec>=8, bull
                                    if  D_per_a[0]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev' and D_dev_result_per_dev>=8 and D_dev_result_per_price>=8: #
                                        num=str('4%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==40. D%空頭背離+D%<=30+W:白>藍 D:白(NA斜率)>藍, bull
                                    if len(M40_weekly_value)>0:
                                        if  D_per_a[0]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev' and MA40_val_sum[0]>MA80_val_sum[0] and M40_weekly_value[0]>M80_weekly_value[0]: #
                                            num=str('40%s'%sum_check) 
                                            bull_bear_check='bull'
                                            out=['3_L','4_L','5_L'] # 出場機制
                                            dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)

                                #==5. D%多頭背離, bear
                                    if  D_dev_trggered==0 and D_dev_result_gain=='bull_dev': #
                                        num=str('5%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==6. D%多頭背離+D%>=70, bear
                                    if  D_per_a[0]>=70 and D_dev_trggered==0 and D_dev_result_gain=='bull_dev': #
                                        num=str('6%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==7. D%多頭背離+D%>=70+delta_price_dec>=4, bear
                                    if  D_per_a[0]>=70 and D_dev_trggered==0 and D_dev_result_gain=='bull_dev' and D_dev_result_per_dev>=4 and D_dev_result_per_price>=4: #
                                        num=str('7%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==8. D%多頭背離+D%>=70+delta_price_dec>=8, bear
                                    if  D_per_a[0]>=70 and D_dev_trggered==0 and D_dev_result_gain=='bull_dev' and D_dev_result_per_dev>=8 and D_dev_result_per_price>=8: #
                                        num=str('8%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                if len(OSC_dev_result)>=1:                       
                                    OSC_dev_result_Date=datetime.strptime(OSC_dev_result[len(OSC_dev_result)-1].split('/')[0], "%Y-%m-%d %H:%M:%S").date()
                                    OSC_dev_result_gain=OSC_dev_result[len(OSC_dev_result)-1].split('/')[1]
                                    OSC_dev_result_per_dev=float(OSC_dev_result[len(OSC_dev_result)-1].split('/')[2]) # percent of dev
                                    OSC_dev_result_per_price=float(OSC_dev_result[len(OSC_dev_result)-1].split('/')[3]) # percent of price
                                    OSC_dev_trggered=(Date_precent-OSC_dev_result_Date).days # used for dec trigger
                                    # strike
                                    first_close_back=float(OSC_dev_result[len(OSC_dev_result)-1].split('/')[4]) #ATM
                                    first_close_back_L,first_close_back_R=self.option_out_price(period,lower,upper,first_close_back)                                        
                                #==9. OSC空頭背離, bull
                                    if  OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' :
                                        num=str('9%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==10. OSC空頭背離+RSI<=30, bull
                                    if  RSI_result[0]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev': #
                                        num=str('10%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==11. OSC空頭背離+RSI<=30+delta_price_dec>=4, bull
                                    if  RSI_result[0]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' and OSC_dev_result_per_dev>=4 and OSC_dev_result_per_price>=4: #
                                        num=str('11%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==12. OSC空頭背離+RSI<=30+delta_price_dec>=8, bull
                                    if  RSI_result[0]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' and OSC_dev_result_per_dev>=8 and OSC_dev_result_per_price>=8: #
                                        num=str('12%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==41. OSC空頭背離+RSI<=30+W:白>藍 D:白(NA斜率)>藍, bull
                                    if len(M40_weekly_value)>0:
                                        if  RSI_result[0]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' and MA40_val_sum[0]>MA80_val_sum[0] and M40_weekly_value[0]>M80_weekly_value[0]: #
                                            num=str('41%s'%sum_check) 
                                            bull_bear_check='bull'
                                            out=['3_L','4_L','5_L'] # 出場機制
                                            dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)

                                #==13. OSC多頭背離, bear
                                    if OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev': #
                                        num=str('13%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==14. OSC多頭背離+RSI>=70, bear
                                    if  RSI_result[0]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev': #
                                        num=str('14%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==15. OSC多頭背離+RSI>=70+delta_price_dec>=4, bear
                                    if  RSI_result[0]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev' and OSC_dev_result_per_dev>=4 and OSC_dev_result_per_price>=4: #
                                        num=str('15%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==16. OSC多頭背離+RSI>=70+delta_price_dec>=8, bear
                                    if  RSI_result[0]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev' and OSC_dev_result_per_dev>=8 and OSC_dev_result_per_price>=8: #
                                        num=str('16%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==42. OSC多頭背離+RSI>=70+W:白<藍 D:白(NA斜率)<藍, bear
                                    if len(M40_weekly_value)>0:
                                        if  RSI_result[0]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev' and MA40_val_sum[0]<MA80_val_sum[0] and M40_weekly_value[0]<M80_weekly_value[0]: #
                                            num=str('42%s'%sum_check) 
                                            bull_bear_check='bear'
                                            out=['3_R','4_R','5_R'] # 出場機制
                                            dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)

                                if len(RSI_dev_result)>=1:                       
                                    RSI_dev_result_Date=datetime.strptime(RSI_dev_result[len(RSI_dev_result)-1].split('/')[0], "%Y-%m-%d %H:%M:%S").date()
                                    RSI_dev_result_gain=RSI_dev_result[len(RSI_dev_result)-1].split('/')[1]
                                    RSI_dev_result_per_dev=float(RSI_dev_result[len(RSI_dev_result)-1].split('/')[2]) # percent of dev
                                    RSI_dev_result_per_price=float(RSI_dev_result[len(RSI_dev_result)-1].split('/')[3]) # percent of price
                                    RSI_dev_trggered=(Date_precent-RSI_dev_result_Date).days # used for dec trigger
                                    # 合約價
                                    first_close_back=float(RSI_dev_result[len(RSI_dev_result)-1].split('/')[4]) #ATM
                                    first_close_back_L,first_close_back_R=self.option_out_price(period,lower,upper,first_close_back)                                       
                                #==17. RSI空頭背離, bull
                                    if  RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev' :
                                        num=str('17%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==18. RSI空頭背離+RSI<=30, bull
                                    if  RSI_result[0]<=30 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev': #
                                        num=str('18%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==19. RSI空頭背離+RSI<=30+delta_price_dec>=4, bull
                                    if  RSI_result[0]<=30 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev' and RSI_dev_result_per_dev>=4 and RSI_dev_result_per_price>=4: #
                                        num=str('19%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==20. RSI空頭背離+RSI<=30+delta_price_dec>=8, bull
                                    if  RSI_result[0]<=30 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev' and RSI_dev_result_per_dev>=8 and RSI_dev_result_per_price>=8: #
                                        num=str('20%s'%sum_check) 
                                        bull_bear_check='bull'
                                        out=['3_L','4_L','5_L'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_L,out)
                                #==21. RSI多頭背離, bear
                                    if  RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev': #
                                        num=str('21%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==22. RSI多頭背離+RSI>=70, bear
                                    if  RSI_result[0]>=70 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev': #
                                        num=str('22%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==23. RSI多頭背離+RSI>=70+delta_price_dec>=4, bear
                                    if  RSI_result[0]>=70 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev' and RSI_dev_result_per_dev>=4 and RSI_dev_result_per_price>=4: #
                                        num=str('23%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==24. RSI多頭背離+RSI>=70+delta_price_dec>=8, bear
                                    if  RSI_result[0]>=70 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev' and RSI_dev_result_per_dev>=8 and RSI_dev_result_per_price>=8: #
                                        num=str('24%s'%sum_check) 
                                        bull_bear_check='bear'
                                        out=['3_R','4_R','5_R'] # 出場機制
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back_R,out)
                                #==25. 1~24 背離5天內 + 量>=1.2 MA5test
                                    if '/Qa/Ma' in sum_check and flag_V_EMA5>=5:
                                        for vol_dev in range(0,24):
                                            try:
                                                if precent_Vol >=precent_V_EMA5*2 and globals()['count_day_%s/Qa/Ma'%(vol_dev+1)]>0 and globals()['count_day_%s/Qa/Ma'%(vol_dev+1)]<=5: #
                                                    num=str('25%s'%sum_check + '/Vol-%s'%(vol_dev+1)) 
                                                    bull_bear_check=globals()['bear_bull_%s/Qa/Ma'%(vol_dev+1)]
                                                    if bull_bear_check=='bear':
                                                        first_close_back=first_close_back_R
                                                    else:
                                                        first_close_back=first_close_back_L
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,globals()['out_%s/Qa/Ma'%(vol_dev+1)])
                                            except:
                                                pass # do not trigger yet.                      
                            # =====非背離
                                try: 
                                # 合約價
                                        back_close=df['Close'][int(Start)]
                                        back_close_L,back_close_R=self.option_out_price(period,lower,upper,back_close) 
                                        if len(M40_weekly_value)>0:                                       
                                        #==26. FAvg40 cross Favg80 up, bull
                                            if  MA40_val_sum[0]>MA80_val_sum[0] and MA40_val_sum[1]<MA80_val_sum[1]: #
                                                num=str('26%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['1_L','2_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==27. FAvg40 cross Favg80 down, bear
                                            if  MA40_val_sum[0]<MA80_val_sum[0] and MA40_val_sum[1]>MA80_val_sum[1]: #
                                                num=str('27%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['1_R','2_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==28. FAvg40 cross Favg80 up and weekly_MA40>weekly_MA80, bull
                                            if  MA40_val_sum[0]>MA80_val_sum[0] and MA40_val_sum[1]<MA80_val_sum[1] and M40_weekly_value[0]>M80_weekly_value[0]: #
                                                num=str('28%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['1_L','2_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==29. FAvg40 cross Favg80 down and weekly_MA40<weekly_MA80, bear
                                            if  MA40_val_sum[0]<MA80_val_sum[0] and MA40_val_sum[1]>MA80_val_sum[1] and M40_weekly_value[0]<M80_weekly_value[0]: #
                                                num=str('29%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['1_R','2_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==30. 不分市場&正三合一(min(S)<=30 and S<40 and S>min(4days)*1.03 and M% <=20 and M:positive and G cross R up),W:白>藍 D:白(NA斜率)>藍, bull  and per_DIF[0]>per_DIF[1]
                                            if  min(D_per_a)<=20 and D_per_a[0]<40 and D_per_a[0]>min(D_per_a)*1.03 and \
                                                per_DIF[0]<=50  and MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1]: # and MA40_val_sum[0]>MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('30%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['6_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==31. 不分市場&反三合一(max(S)>=80 and S>60 and S<max(4days)*0.97 and M% >=80 and M:negative and G cross R down),W:白>藍 D:白(NA斜率)>藍, bear  and per_DIF[0]<per_DIF[1]
                                            if  max(D_per_a)>=80 and D_per_a[0]>60 and D_per_a[0]<max(D_per_a)*0.97 and per_DIF[0]>=50  and MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1]: # and MA40_val_sum[0]<MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('31%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['6_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==32. W/D牛市&正三合一(min(S)<=30 and S<40 and S>min(4days)*1.03 and M% <=20 and M:positive and G cross R up),W:白>藍 D:白(NA斜率)>藍, bull  and per_DIF[0]>per_DIF[1]
                                            if  min(D_per_a)<=20 and D_per_a[0]<40 and D_per_a[0]>min(D_per_a)*1.03 and per_DIF[0]<=50  and MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1] and MA40_val_sum[0]>MA80_val_sum[0] and M40_weekly_value[0]>M80_weekly_value[0]: # and MA40_val_sum[0]>MA40_val_sum[3]
                                                num=str('32%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['6_L','3_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==33. W/D牛市&反三合一(max(S)>=80 and S>60 and S<max(4days)*0.97 and M% >=80 and M:negative and G cross R down),W:白>藍 D:白(NA斜率)>藍, bear  and per_DIF[0]<per_DIF[1]
                                            if  max(D_per_a)>=80 and D_per_a[0]>60 and D_per_a[0]<max(D_per_a)*0.97 and per_DIF[0]>=50  and MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1] and MA40_val_sum[0]>MA80_val_sum[0] and M40_weekly_value[0]>M80_weekly_value[0]: # and MA40_val_sum[0]<MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('33%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['6_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==34. W/D熊市&正三合一(min(S)<=30 and S<40 and S>min(4days)*1.03 and M% <=20 and M:positive and G cross R up),W:白<藍 D:白(NA斜率)<藍, bull  and per_DIF[0]>per_DIF[1]
                                            if  min(D_per_a)<=20 and D_per_a[0]<40 and D_per_a[0]>min(D_per_a)*1.03 and per_DIF[0]<=50  and MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1] and MA40_val_sum[0]<MA80_val_sum[0] and M40_weekly_value[0]<M80_weekly_value[0]: # and MA40_val_sum[0]>MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('34%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['6_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==35. W/D熊市&反三合一(max(S)>=80 and S>60 and S<max(4days)*0.97 and M% >=80 and M:negative and G cross R down),W:白<藍 D:白(NA斜率)<藍, bear  and per_DIF[0]<per_DIF[1]
                                            if  max(D_per_a)>=80 and D_per_a[0]>60 and D_per_a[0]<max(D_per_a)*0.97 and per_DIF[0]>=50  and MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1] and MA40_val_sum[0]<MA80_val_sum[0] and M40_weekly_value[0]<M80_weekly_value[0]: # and MA40_val_sum[0]<MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('35%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['6_R','3_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==36. D牛市&正三合一(min(S)<=30 and S<40 and S>min(4days)*1.03 and M% <=20 and M:positive and G cross R up),D:白(NA斜率)>藍, bull
                                            if  min(D_per_a)<=20 and D_per_a[0]<40 and D_per_a[0]>min(D_per_a)*1.03 and per_DIF[0]<=50  and MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1] and MA40_val_sum[0]>MA80_val_sum[0]: # and MA40_val_sum[0]>MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('36%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['6_L','3_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==37. D牛市&反三合一(max(S)>=80 and S>60 and S<max(4days)*0.97 and M% >=80 and M:negative and G cross R down),D:白(NA斜率)>藍, bear
                                            if  max(D_per_a)>=80 and D_per_a[0]>60 and D_per_a[0]<max(D_per_a)*0.97 and per_DIF[0]>=50  and MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1] and MA40_val_sum[0]>MA80_val_sum[0]: # and MA40_val_sum[0]<MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('37%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['6_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==38. D熊市&正三合一(min(S)<=30 and S<40 and S>min(4days)*1.03 and M% <=20 and M:positive and G cross R up),D:白(NA斜率)<藍, bull
                                            if  min(D_per_a)<=20 and D_per_a[0]<40 and D_per_a[0]>min(D_per_a)*1.03 and per_DIF[0]<=50  and MA5_val_sum[0]>MA4_val_sum[0] and MA5_val_sum[1]<MA4_val_sum[1] and MA40_val_sum[0]<MA80_val_sum[0]: # and MA40_val_sum[0]>MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('38%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['6_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==39. D熊市&反三合一(max(S)>=80 and S>60 and S<max(4days)*0.97 and M% >=80 and M:negative and G cross R down),D:白(NA斜率)<藍, bear
                                            if  max(D_per_a)>=80 and D_per_a[0]>60 and D_per_a[0]<max(D_per_a)*0.97 and per_DIF[0]>=50  and MA5_val_sum[0]<MA4_val_sum[0] and MA5_val_sum[1]>MA4_val_sum[1] and MA40_val_sum[0]<MA80_val_sum[0]: # and MA40_val_sum[0]<MA40_val_sum[3]
                                                if Start>=9700:
                                                    temp=1
                                                num=str('39%s'%sum_check) 
                                                bull_bear_check='bear'
                                                out=['6_R'] # 出場機制
                                                first_close_back=back_close_R # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==43. W/D牛市&S正斜率&M>50 (S/M近80), bull
                                            if D_per_a[0]>=70 and D_per_a[0]>D_per_a[2] and per_DIF[0]>=50 and MA40_val_sum[0]>MA80_val_sum[0] and M40_weekly_value[0]>M80_weekly_value[0]:
                                                num=str('43%s'%sum_check) 
                                                bull_bear_check='bull'
                                                out=['7_L','4_L'] # 出場機制
                                                first_close_back=back_close_L # 非背離 紀錄當下 close
                                                dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==
                                            if lower_list[5]>0:
                                                self.debug=Start
                                                back_close_1=df['Close'][int(Start-1)]
                                                back_close_2=df['Close'][int(Start-2)]
                                                back_close_3=df['Close'][int(Start-3)]
                                                slew_R_BB=self.slew_rate_check(lower_list,0.5,3) # check slew (list,in percent,days)
                                                slew_L_BB=self.slew_rate_check(upper_list,0.1,3) # check slew (list,in percent,days)
                                        #==44. 不分市場/close>前一天BB_upper(前三天沒跌破BB) & 白下彎或走平(白[0][1]漲幅不超過0.1%) & BB下都平(連續維持在0.5%內), bull
                                                if  slew_R_BB==1 and slew_L_BB==1 and back_close>upper_list[1] and back_close_1<upper_list[1] and back_close_2<upper_list[2] and back_close_3<upper_list[3]:# and ((MA40_val_sum[0]-MA40_val_sum[1])/MA40_val_sum[1])*100>=0.1:  
                                                    num=str('44%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['10_L'] # 出場機制
                                                    first_close_back='%s,%s'%((upper+lower)/2,back_close) # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==45. 不分市場/close<前一天BB_lower(前三天沒跌破BB) & 白下彎或走平(白[0][1]漲幅不超過0.1%) & BB下都平(連續維持在0.5%內), bear
                                                if  slew_R_BB==1 and slew_L_BB==1 and back_close<lower_list[1] and back_close_1>lower_list[1] and back_close_2>lower_list[2] and back_close_3>lower_list[3]:# and ((MA40_val_sum[0]-MA40_val_sum[1])/MA40_val_sum[1])*100<=0.1:  
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('45%s'%sum_check) 
                                                    bull_bear_check='bear'
                                                    out=['8_R','9_L'] # 出場機制
                                                    first_close_back=back_close_R # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==46. 不分市場/close<前一天BB_lower(前三天沒跌破BB) & 白下彎或走平(白[0][1]漲幅不超過0.1%) & BB下都平(連續維持在0.5%內), bull
                                                if  slew_R_BB==1 and slew_L_BB==1 and back_close<lower_list[1] and back_close_1>lower_list[1] and back_close_2>lower_list[2] and back_close_3>lower_list[3]:# and ((MA40_val_sum[0]-MA40_val_sum[1])/MA40_val_sum[1])*100<=0.1:  
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('46%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['10_L'] # 出場機制
                                                    first_close_back=back_close_L # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==47. 不分市場/close>當天BB_upper + 爆量(量>=1.2 MA5), bear
                                                if  back_close>upper_list[1] and back_close_1<upper_list[1] and back_close_2<upper_list[2] and back_close_3<upper_list[3] and precent_Vol >=precent_V_EMA5*1.2: 
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('47%s'%sum_check) 
                                                    bull_bear_check='bear'
                                                    out=['11_R'] # 出場機制
                                                    first_close_back=back_close_R # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==48. 不分市場/close<當天BB_lower + 爆量(量>=1.2 MA5), bull
                                                if  back_close<lower_list[1] and back_close_1>lower_list[1] and back_close_2>lower_list[2] and back_close_3>lower_list[3] and precent_Vol >=precent_V_EMA5*1.2: 
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('48%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['11_L'] # 出場機制
                                                    first_close_back=back_close_L # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==49. 不分市場/close>當天BB_upper + 爆量(量>=1.2 MA5), bull
                                                if  back_close>upper_list[1] and back_close_1<upper_list[1] and back_close_2<upper_list[2] and back_close_3<upper_list[3] and precent_Vol >=precent_V_EMA5*1.2: 
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('49%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['11_L'] # 出場機制
                                                    first_close_back=back_close_L # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==50. 不分市場/close<當天BB_lower + 爆量(量>=1.2 MA5), bear
                                                if  back_close<lower_list[1] and back_close_1>lower_list[1] and back_close_2>lower_list[2] and back_close_3>lower_list[3] and precent_Vol >=precent_V_EMA5*1.2:  
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('50%s'%sum_check) 
                                                    bull_bear_check='bear'
                                                    out=['11_R'] # 出場機制
                                                    first_close_back=back_close_R # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==51. 週S>50 & 日S剛突破50向上, bull
                                                if  D_per_a[0]>50 and D_per_a[1]<50 and sto_weekly_value[0]>50:
                                                    if Start>4600:
                                                        temp=1
                                                    num=str('51%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['6_L'] # 出場機制
                                                    first_close_back=back_close_L # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==52. 週S<50 & 日S剛突破50向下, bear
                                                if  D_per_a[0]<50 and D_per_a[1]>50 and sto_weekly_value[0]<50:
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('52%s'%sum_check) 
                                                    bull_bear_check='bear'
                                                    out=['6_R'] # 出場機制
                                                    first_close_back=back_close_R # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==53. 週S>50 & 日S剛突破50向上(連續正斜率), bull
                                                if  D_per_a[0]>50 and D_per_a[1]<50 and sto_weekly_value[0]>50 and sto_weekly_value[0]>sto_weekly_value[1] and sto_weekly_value[1]>sto_weekly_value[2] :
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('53%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['6_L'] # 出場機制
                                                    first_close_back=back_close_L # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==54. 週S<50 & 日S剛突破50向下(連續負斜率), bear
                                                if  D_per_a[0]<50 and D_per_a[1]>50 and sto_weekly_value[0]<50 and sto_weekly_value[0]<sto_weekly_value[1] and sto_weekly_value[1]<sto_weekly_value[2]:
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('54%s'%sum_check) 
                                                    bull_bear_check='bear'
                                                    out=['6_R'] # 出場機制
                                                    first_close_back=back_close_R # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==53. W/D牛, 日S>50 & 週S剛突破50向上, bull
                                                if  D_per_a[0]>50 and D_per_a[1]<50 and sto_weekly_value[0]>50 and MA40_val_sum[0]>MA80_val_sum[0] and M40_weekly_value[0]>M80_weekly_value[0]:
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('55%s'%sum_check) 
                                                    bull_bear_check='bull'
                                                    out=['6_L'] # 出場機制
                                                    first_close_back=back_close_L # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                        #==54. W/D熊, 週S<50 & 日S剛突破50向下, bear
                                                if  D_per_a[0]<50 and D_per_a[1]>50 and sto_weekly_value[0]<50 and D_per_a[0]<50 and MA40_val_sum[0]<MA80_val_sum[0] and M40_weekly_value[0]<M80_weekly_value[0]:
                                                    if Start>5507:
                                                        temp=1
                                                    num=str('56%s'%sum_check) 
                                                    bull_bear_check='bear'
                                                    out=['6_R'] # 出場機制
                                                    first_close_back=back_close_R # 非背離 紀錄當下 close
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out)
                                except:
                                    pass

                        if back_ornot==back_en:
                            for back_i in dict_flag_all:
                                if int(globals()[back_i])>0: #@@
                                    num=back_i.split('_')[2]
                                    # self.debug=Start
                                    globals()['count_day_%s'%num]=globals()['count_day_%s'%num]+1 #@@
                                    #============================================BB set 停損=====
                                    if period==1:
                                        if globals()['bear_bull_%s'%num]=='bear':
                                            if upper_per<0:
                                                stop_per=stop_per_default
                                            elif upper_per>=15:
                                                stop_per=10
                                            else:
                                                stop_per=upper_per
                                        else:
                                            if lower_per<0:
                                                stop_per=stop_per_default
                                            elif lower_per>=15:
                                                stop_per=10
                                            else:
                                                stop_per=lower_per  
                                    else: # weekly don't care BB
                                        stop_per=stop_per_default                                    
                                    #============================================BB set 停損=====
                                    dict_back_all[num],globals()['flag_lookup_%s'%num],globals()['record_per_%s'%num],globals()['count_day_%s'%num]=self.back_check(num,dict_back_all[num],globals()['first_close_back_%s'%num],back_close,stop_per,globals()['count_day_%s'%num],globals()['record_per_%s'%num],globals()['bear_bull_%s'%num],globals()['out_%s'%num]) #@                     
                            # back_i=0

            #===loop step
                #====for ATE
                pre_Start=Start # for sto
                if Start==row_n:
                    break
                elif row_n-Start<period:
                    Start=row_n
                else:
                    Start=Start+period
                    #==============check Week=5?
                    if period>1:
                        Start = self.Week_check(df, Start,row_n)
                    #==============check Week=5?

                #== for KD% persiod>1 to find period high/low
                if row_n-Start<=(12+3+1+(b-100))*period and period>1: #+(b-100)
                    period_high=0
                    period_low=9000
                    for j in range(0,Start-pre_Start):
                        if period_high<df['High'][int(Start-j)]:
                            period_high=df['High'][int(Start-j)]
                        if period_low>df['Low'][int(Start-j)]:
                            period_low=df['Low'][int(Start-j)]

                i=i+1
                self.debug=Start
            except:
                self.debug=Start
                temp='MACD_week error'
        dict_back_all=self.dict_rename(dict_back_all,back_ornot)  # Throw away one sample record
        trigger=[]
        for key in dict_back_all:
            count_get=globals()['count_day_%s'%key]
            if back_ornot==1:
                if count_get<=5 and count_get!=0:
                    trigger.append('%s_%s'%(count_get,key))
            else:
                if count_get<=5:
                    trigger.append('%s_%s'%(count_get,key))

        # dict_back_all_obereved51=self.dict_find(dict_back_all,51, '/')
        # dict_back_all_obereved52=self.dict_find(dict_back_all,52, '/')
        # dict_back_all_obereved53=self.dict_find(dict_back_all,53, '/')
        # dict_back_all_obereved54=self.dict_find(dict_back_all,54, '/')

        # dict_back_all_obereved44=self.dict_find(dict_back_all,44, '/')
        # dict_back_all_obereved45=self.dict_find(dict_back_all,45, '/')
        # dict_back_all_obereved46=self.dict_find(dict_back_all,46, '/')
        # 不指定QM, 輸入/  ,Qa/Ma
        # dict_back_all_obereved26=self.dict_find(dict_back_all,26, 'Qa/Ma') # FAvg40 cross Favg80 up, bull
        # dict_back_all_obereved27=self.dict_find(dict_back_all,27, 'Qa/Ma') # FAvg40 cross Favg80 down, bear
        # dict_back_all_obereved28=self.dict_find(dict_back_all,28, 'Qa/Ma') # FAvg40 cross Favg80 up and weekly_MA40>weekly_MA80, bull
        # dict_back_all_obereved29=self.dict_find(dict_back_all,29, 'Qa/Ma') # FAvg40 cross Favg80 down and weekly_MA40<weekly_MA80, bear

        # dict_back_all_obereved2=self.dict_find(dict_back_all,2, 'Qa/Ma') # D%空頭背離+D%<=30, bull
        # dict_back_all_obereved4=self.dict_find(dict_back_all,4, 'Qa/Ma') # D%空頭背離+D%<=30+delta_price_dec>=8, bull
        # dict_back_all_obereved6=self.dict_find(dict_back_all,6, 'Qa/Ma') # D%多頭背離+D%>=70, bear
        # dict_back_all_obereved7=self.dict_find(dict_back_all,7, 'Qa/Ma') # D%多頭背離+D%>=70+delta_price_dec>=4, bear
        # dict_back_all_obereved40=self.dict_find(dict_back_all,40, 'Qa/Ma') # D%空頭背離+D%<=30+W:白>藍 D:白(NA斜率)>藍, bull

        # dict_back_all_obereved9=self.dict_find(dict_back_all,9, 'Qa/Ma') # OSC空頭背離, bull
        # dict_back_all_obereved10=self.dict_find(dict_back_all,10, 'Qa/Ma') # OSC空頭背離+RSI<=30, bull
        # dict_back_all_obereved12=self.dict_find(dict_back_all,12, 'Qa/Ma') # OSC空頭背離+RSI<=30+delta_price_dec>=8, bull
        # dict_back_all_obereved41=self.dict_find(dict_back_all,41, 'Qa/Ma') # OSC空頭背離+RSI<=30+W:白>藍 D:白(NA斜率)>藍, bull

        # dict_back_all_obereved13=self.dict_find(dict_back_all,13, 'Qa/Ma') # OSC多頭背離, bear
        # dict_back_all_obereved14=self.dict_find(dict_back_all,14, 'Qa/Ma') # OSC多頭背離+RSI>=70, bear
        # dict_back_all_obereved16=self.dict_find(dict_back_all,16, 'Qa/Ma') # OSC多頭背離+RSI>=70+delta_price_dec>=8, bear
        # dict_back_all_obereved42=self.dict_find(dict_back_all,42, 'Qa/Ma') # OSC多頭背離+RSI>=70+W:白<藍 D:白(NA斜率)<藍, bear

        # dict_back_all_obereved17=self.dict_find(dict_back_all,17, 'Qa/Ma') # RSI空頭背離, bull
        # dict_back_all_obereved20=self.dict_find(dict_back_all,20, 'Qa/Ma') # RSI空頭背離+RSI<=30+delta_price_dec>=8, bull

        # dict_back_all_obereved21=self.dict_find(dict_back_all,21, 'Qa/Ma') # RSI多頭背離, bear
        # dict_back_all_obereved24=self.dict_find(dict_back_all,24, 'Qa/Ma') # RSI多頭背離+RSI>=70+delta_price_dec>=8, bear

        # dict_back_all_obereved43=self.dict_find(dict_back_all,43, 'Qa/Ma') # W/D牛市&S正斜率&M>50 (S/M近80), bull
        # dict_back_all_obereved44=self.dict_find(dict_back_all,44, 'Qa/Ma') # 不分市場/close>前一天BB_lower(前三天沒跌破BB) & BB下都平(連續維持在0.5%內), bull
        # dict_back_all_obereved45=self.dict_find(dict_back_all,45, 'Qa/Ma') # 不分市場/close<前一天BB_lower(前三天沒跌破BB) & BB下都平(連續維持在0.5%內), bear
        # dict_back_all_obereved46=self.dict_find(dict_back_all,46, 'Qa/Ma') # 不分市場/close<前一天BB_lower(前三天沒跌破BB) & BB下都平(連續維持在0.5%內), bull

        # #===不分市場
        # dict_back_all_obereved30=self.dict_find(dict_back_all,30, '/') # 正三
        # dict_back_all_obereved31=self.dict_find(dict_back_all,31, '/') # 反三
        # #===W/D牛市
        # dict_back_all_obereved32=self.dict_find(dict_back_all,32, '/') # 正三
        # dict_back_all_obereved33=self.dict_find(dict_back_all,33, '/') # 反三
        # #===W/D熊市
        # dict_back_all_obereved34=self.dict_find(dict_back_all,34, 'Qa/Ma') # 正三
        # dict_back_all_obereved35=self.dict_find(dict_back_all,35, 'Qa/Ma') # 反三
        # #===D牛市
        # dict_back_all_obereved36=self.dict_find(dict_back_all,36, '/') # 正三
        # dict_back_all_obereved37=self.dict_find(dict_back_all,37, '/') # 反三
        # #===D熊市
        # dict_back_all_obereved38=self.dict_find(dict_back_all,38, 'Qa/Ma') # 正三
        # dict_back_all_obereved39=self.dict_find(dict_back_all,39, 'Qa/Ma') # 反三
        #=======================================check end record
        if back_ornot==back_en:
            #========save backtest result to csv================
            if period==1:
                filepath=os.getcwd() + os.sep +'stock_temp'
                if not os.path.isdir(filepath):
                    os.mkdir(filepath)
                dict_back_all_pd = pd.DataFrame.from_dict(dict_back_all, orient="index")
                dict_back_all_pd.to_csv(filepath + os.sep + '%s_%s.csv'%(stock_name,'BT')) # Throw away one sample record
                #update to googlesheet
                # sheet=self.initial_google_API_sheet()
                # self.csv_to_google_sheet(test_stock,sheet)
            #========save backtest result to csv================
            back_j=0
            for back_i in dict_flag_all:
                temp=int(globals()['count_day_%s'%back_i.split('_')[2]])
                N=1000 # 找< N天內觸發
                if int(globals()[back_i])!=0 and int(globals()['count_day_%s'%back_i.split('_')[2]])<N: 
                    try:
                        win_rate_5S=float(dict_back_all[back_i.split('_')[2]]['5S']['0'].split('/')[3])
                        Win_per_5S=abs(float(dict_back_all[back_i.split('_')[2]]['5S']['0'].split('/')[4]))
                        win_rate_10S=float(dict_back_all[back_i.split('_')[2]]['10S']['0'].split('/')[3])
                        Win_per_10S=abs(float(dict_back_all[back_i.split('_')[2]]['10S']['0'].split('/')[4]))
                        win_rate_20S=float(dict_back_all[back_i.split('_')[2]]['20S']['0'].split('/')[3])
                        win_rate_30S=float(dict_back_all[back_i.split('_')[2]]['30S']['0'].split('/')[3])
                        win_rate_40S=float(dict_back_all[back_i.split('_')[2]]['40S']['0'].split('/')[3])
                        if win_rate_10S>=70 or win_rate_5S>=70:
                            if Win_per_5S>=1 or Win_per_10S>=1:               
                                dict_flag_end_record_buy[back_i.split('_')[2]]=dict_back_all[back_i.split('_')[2]]
                        elif win_rate_20S>=55 or win_rate_30S>=55 or win_rate_40S>=55:
                                dict_flag_end_record_sell[back_i.split('_')[2]]=dict_back_all[back_i.split('_')[2]]
                    except:
                        pass
                    back_j=back_j+1
        #=======================================check end record
        #加入指數 幾天內顯示在 "dict_flag_end_record"
        # 公布財報前一天的行為 機率
        # 篩選出漲幅最大支個股作buy合約
        # 月份1~12 done
        # 季 Q1~Q4 done
        # 爆量(當天量>MA5*2) + 近期指數背離   @@@
        # 25. 用迴圈跑所有背離指標+2倍大量+count<=5
        # 40 天內沒有停損 考慮做sell
        
    #===========================================Sum===================================================		
        DIF_per_last_status=self.status_analysis(per_DIF)

        #KD
        # temp=self.status_analysis(D_per_a) #daily_ok
        # D_per_a.append(temp)

        # latest_data=[0, 0, 0, 0, 0] #'DIF': 0,'DEM': 0,'OSC': 0,'MACD%': 0,'MACD%_s': 0 #daily_ok
        latest_data_MACD[0]=DIF
        latest_data_MACD[1]=DEM
        latest_data_MACD[2]=OSC
        latest_data_MACD[3]=per_DIF[0]#latest DIF%
        latest_data_MACD[4]=DIF_per_last_status

        MA5_analy=self.status_analysis(MA5_val_sum)
        MA4_analy=self.status_analysis(MA4_val_sum)
        MA40_analy=self.status_analysis(MA40_val_sum)
        MA80_analy=self.status_analysis(MA80_val_sum)
        latest_data_MA=[MA5_analy, MA4_analy, MA40_analy, MA80_analy, self.MA_analysis(MA5_val_sum[0],MA4_val_sum[0],MA40_val_sum[0],MA80_val_sum[0])]

        OSC_result_F=self.status_analysis(OSC_result) #daily_ok
        MACD_12_26=self.status_analysis(DIF_result) #daily_ok
        # final_result=self.operation_analysis(OSC_result_F,MACD_12_26) #daily_ok

        RSI_result_F=self.status_analysis(RSI_result) #daily_ok

        ATR_avg_sum=[list_ATR[len(list_ATR)-1], list_ATR[len(list_ATR)-2], list_ATR[len(list_ATR)-3], list_ATR[len(list_ATR)-4]] #daily_ok
        ATR_avg_F=self.status_analysis(ATR_avg_sum) #daily_ok
        try:
            dev_dict={'precent':Date_precent,'OSC':OSC_dev_result[len(OSC_dev_result)-1],'RSI':RSI_dev_result[len(RSI_dev_result)-1],'Sto':D_dev_result[len(D_dev_result)-1]}
        except:
            dev_dict={}
        V_MA5_val_sum
        precent_Vol
        weekly_BT=MA_40_80_Weekly_BT
        M40_weekly_value
        M80_weekly_value

        #=======build dict from list
        list_input=['MA5_val_sum','MA4_val_sum','MA40_val_sum','MA80_val_sum','latest_data_MA','OSC_result','DIF_result','per_DIF','D_per_a','RSI_result','RSI_result_F','ATR_avg_sum','ATR_avg_F','precent_Vol','V_MA5_val_sum','dev_dict','trigger','weekly_BT','M40_weekly_value','M80_weekly_value','BB']
        dict_input={}
        for name in list_input:
            dict_input[name]=locals()[name]
        dict_sum=dict_input


        return dict_sum, dict_back_all

        # return trigger, Switch_p, OSC_result_F, EMA13_result_F, final_result, latest_data_MACD, D_per_a, latest_data_MA, OSC_dev_result, D_dev_result, RSI_dev_result, dict_back_all

    def deviate_check(self,df, n,Backtest, price_dev,price_dev_result, dev, dev_result, A, inverse,helf): # df['Close'][int(Start)]
        # B=A
        if inverse==1:
            B=A[::-1]
        else:
            B=A
        # dim B is indicator, C is pre peak/deep (P1 or N1)
        # 1. check B is V or n
        # 2. V: if B_n>B_n-1 and price_n<price_n-1 and C=n: bear deviate
        # 3. n: if B_n<B_n-1 and price_n>price_n-1 and C=V: bull deviate
        #1. 
        V=len(dev)
        if float(B[2])!=0: #(V/n, indicator value, price, Date)
            # deta_temp=str(df['Date'][int(n-1)])
            # if '2017-08-03' in str(df['Date'][int(n-1)]):
            #     temp=1

            #===========helf check
            #MACD_Histog
            if B[1]<helf:
                helf_check='N'
            elif B[1]>helf:
                helf_check='P'
            else:
                helf_check=''

            if B[0]>B[1] and B[2]>B[1] and helf_check=='N': #find V   
                V_price=min(float(df['Low'][int(n-4)]),float(df['Low'][int(n-3)]),float(df['Low'][int(n-2)]),float(df['Low'][int(n-1)])) # indicator is lowest, but each price Not certainly is lowest, find near 3 days lowest
                if V==0: #1st
                    dev[V]='%s/%s/%s/%s'%('V',str(B[1]),str(V_price),str(df['Date'][int(n-1)]))
                if len(dev)>=1 and B[1]<float(dev[V-1].split('/')[1]) and dev[V-1].split('/')[0]=='V': # if pre dev is also V, and current value smaller then last one, replace it(ignore multi 'V' in dict)
                    dev[V-1]='%s/%s/%s/%s'%('V',str(B[1]),str(V_price),str(df['Date'][int(n-1)]))
                elif dev[V-1].split('/')[0]=='n': # cross over n to V,  maybe dev happend
                    dev[V]='%s/%s/%s/%s'%('V',str(B[1]),str(V_price),str(df['Date'][int(n-1)]))

            if B[0]<B[1] and B[2]<B[1] and helf_check=='P': #find n  
                n_price=max(float(df['High'][int(n-4)]),float(df['High'][int(n-3)]),float(df['High'][int(n-2)]),float(df['High'][int(n-1)])) # indicator is peak, but each price Not certainly is peak, find near 3 days peak
                if V==0: #1st
                    dev[V]='%s/%s/%s/%s'%('n',str(B[1]),str(n_price),str(df['Date'][int(n-1)]))
                if len(dev)>=1 and B[1]>float(dev[V-1].split('/')[1]) and dev[V-1].split('/')[0]=='n': # if pre dev is also n, and current value bigger then last one, replace it(ignore multi 'n' in dict)
                    dev[V-1]='%s/%s/%s/%s'%('n',str(B[1]),str(n_price),str(df['Date'][int(n-1)]))
                elif dev[V-1].split('/')[0]=='V': # cross over V to n,  maybe dev happend
                    dev[V]='%s/%s/%s/%s'%('n',str(B[1]),str(n_price),str(df['Date'][int(n-1)]))

        #2.
        if V>=3:
            #deviate happend, v:
            R=len(dev_result)
            dev_n_date=dev[len(dev)-1].split('/')[3]
            if R!=0:
                dev_result_date_L=dev_result[R-1].split('/')[0]
            dev_n_sign=dev[len(dev)-1].split('/')[0]
            dev_n_1_sign=dev[len(dev)-2].split('/')[0]
            dev_n_2_sign=dev[len(dev)-3].split('/')[0]
            dev_n_value=float(dev[len(dev)-1].split('/')[1])
            dev_n_1_value=float(dev[len(dev)-2].split('/')[1])
            dev_n_2_value=float(dev[len(dev)-3].split('/')[1])
            per_dev=round(abs(abs(dev_n_value)-abs(dev_n_2_value))/max(abs(dev_n_value),abs(dev_n_2_value))*100,2)
            dev_n_price=float(dev[len(dev)-1].split('/')[2])
            dev_n_1_price=float(dev[len(dev)-2].split('/')[2])
            dev_n_2_price=float(dev[len(dev)-3].split('/')[2])
            per_price=round(abs(abs(dev_n_price)-abs(dev_n_2_price))/max(dev_n_price,dev_n_2_price)*100,2)
            # if '2020-02-12' in dev_result_date_L:
            #     temp=1
            if R==0: #1st
                if dev_n_sign=='V' and dev_n_1_sign=='n' and dev_n_2_sign=='V' and dev_n_value>dev_n_2_value and dev_n_price<dev_n_2_price: # price n<n-1
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bear_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
                if dev_n_sign=='V' and dev_n_1_sign=='n' and dev_n_2_sign=='V' and dev_n_value>dev_n_2_value and per_price<=1: # price almost same in 5%
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bear_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
                if dev_n_sign=='n' and dev_n_1_sign=='V' and dev_n_2_sign=='n' and dev_n_value<dev_n_2_value and dev_n_price>dev_n_2_price: # price n<n-1
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bull_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
                if dev_n_sign=='n' and dev_n_1_sign=='V' and dev_n_2_sign=='n' and dev_n_value<dev_n_2_value and per_price<=5: # price almost same in 5%
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bull_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
            else:
                # if '2020-02-12' in dev_result_date_L:
                #     temp=1
                if dev_result_date_L!=dev_n_date and dev_n_sign=='V' and dev_n_1_sign=='n' and dev_n_2_sign=='V' and dev_n_value>dev_n_2_value and dev_n_price<dev_n_2_price: # price n<n-1
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bear_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
                if dev_result_date_L!=dev_n_date and dev_n_sign=='V' and dev_n_1_sign=='n' and dev_n_2_sign=='V' and dev_n_value>dev_n_2_value and per_price<=1: # price almost same in 5%
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bear_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
                if dev_result_date_L!=dev_n_date and dev_n_sign=='n' and dev_n_1_sign=='V' and dev_n_2_sign=='n' and dev_n_value<dev_n_2_value and dev_n_price>dev_n_2_price: # price n<n-1
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bull_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
                if dev_result_date_L!=dev_n_date and dev_n_sign=='n' and dev_n_1_sign=='V' and dev_n_2_sign=='n' and dev_n_value<dev_n_2_value and per_price<=5: # price almost same in 5%
                    dev_result[R]='%s/%s/%s/%s/%s'%(dev_n_date,'bull_dev',per_dev,per_price,dev_n_price)
                    Backtest=1 # start to backtest
        
        #========check history of dev happend.
        if Backtest==3:
            p=len(price_dev)
            # dev_n_price
            date_now=df['Date'][int(n)]
            price_now=df['Close'][int(n)]
            price_n1=df['Close'][int(n-1)]
            price_n2=df['Close'][int(n-2)]
            price_p1=df['Close'][int(n+1)]
            price_p2=df['Close'][int(n+2)]
            dev_date=dev_result[len(dev_result)-1].split('/')[0]
            dev_sign=dev_result[len(dev_result)-1].split('/')[1]
            dev_price=float(dev_result[len(dev_result)-1].split('/')[3])
            
            # find price's 'n', [price_dev]: record all V and n
            if price_now>price_n1 and price_now>price_n2 and price_now>price_p1 and price_now>price_p2: #and price_now>dev_price 
                # temp_backtest='%s/%s'%(date_now,price_now)
                price_dev[p]='%s/%s/%s'%('n',price_now,date_now)
            #find price's 'V'
            elif price_now<price_n1 and price_now<price_n2 and price_now<price_p1 and price_now<price_p2: #and price_now>dev_price 
                # temp_backtest='%s/%s'%(date_now,price_now)
                price_dev[p]='%s/%s/%s'%('V',price_now,date_now)

            flag_check=0
            if len(price_dev)>0:
                price_tran_sign_n=price_dev[len(price_dev)-1].split('/')[0]
                if dev_sign=='bull_dev' and price_tran_sign_n=='V':
                    flag_check=1
                if dev_sign=='bear_dev' and price_tran_sign_n=='n':
                    flag_check=1

            v_n_not_enough=0
            #check n > n or V < V
            if p>=3 and flag_check==1:
                #==============find pre v or n, which same as surrent
                find_pre=2
                while 1>0:
                    if price_dev[len(price_dev)-find_pre].split('/')[0]==price_tran_sign_n:
                        break
                    find_pre=find_pre+1
                    if find_pre>len(price_dev): # V/n are not enough
                        v_n_not_enough=1
                        break  
                if v_n_not_enough==0: # V/n are enough for checking        
                    price_tran_value_n=float(price_dev[len(price_dev)-1].split('/')[1])
                    # price_tran_date_n=price_dev[len(price_dev)-1].split('/')[2]
                    price_tran_value_n_1=float(price_dev[len(price_dev)-find_pre].split('/')[1])
                    price_tran_date_n_1=price_dev[len(price_dev)-find_pre].split('/')[2]
                    #==============find pre v or n, which same as surrent
                    temp=len(price_dev_result)
                    if price_tran_sign_n=='n' and dev_sign=='bear_dev':
                        if price_tran_value_n>dev_price: # not sure whehter more hifger/lower price.
                            price_dev_result[0]=price_tran_value_n # record next V/n for 
                        elif price_tran_value_n<price_tran_value_n_1 and len(price_dev_result)>0:
                            temp_price=round(abs(price_tran_value_n_1-dev_price)/dev_price*100,2)
                            price_tran_date_n_1=datetime.strptime(price_tran_date_n_1.split(' ')[0], "%Y-%m-%d").date() # %H:%M:%S
                            dev_date=datetime.strptime(dev_date.split(' ')[0], "%Y-%m-%d").date() # %H:%M:%S
                            delta_day=(price_tran_date_n_1-dev_date).days
                            temp='/%s/%s'%(delta_day,temp_price) #delta,price%
                            dev_result[len(dev_result)-1]=dev_result[len(dev_result)-1] + temp
                            Backtest=0 #confirm
                            price_dev={} #reset V/n record 
                            price_dev_result={}
                        elif price_tran_value_n<price_tran_value_n_1 and len(price_dev_result)==0:
                            #dev fail
                            dev_result[len(dev_result)-1]=dev_result[len(dev_result)-1]+ '/'+'Fail'
                            Backtest=0 #confirm
                            price_dev={} #reset V/n record 
                            price_dev_result={}
                    elif price_tran_sign_n=='V' and dev_sign=='bull_dev':
                        if price_tran_value_n<dev_price: # not sure whehter more hifger/lower price.
                            price_dev_result[0]=price_tran_value_n # record next V/n for 
                        elif price_tran_value_n>price_tran_value_n_1 and len(price_dev_result)>0:
                            temp_price=round(abs(price_tran_value_n_1-dev_price)/dev_price*100,2)
                            price_tran_date_n_1=datetime.strptime(price_tran_date_n_1.split(' ')[0], "%Y-%m-%d").date() # %H:%M:%S
                            dev_date=datetime.strptime(dev_date.split(' ')[0], "%Y-%m-%d").date() # %H:%M:%S
                            delta_day=(price_tran_date_n_1-dev_date).days
                            temp='/%s/%s'%(delta_day,temp_price) #delta,price%
                            dev_result[len(dev_result)-1]=dev_result[len(dev_result)-1] + temp
                            Backtest=0 #confirm
                            price_dev={} #reset V/n record 
                            price_dev_result={}
                        elif price_tran_value_n>price_tran_value_n_1 and len(price_dev_result)==0:
                            #dev fail
                            dev_result[len(dev_result)-1]=dev_result[len(dev_result)-1]+ '/'+'Fail'
                            Backtest=0 #confirm
                            price_dev={} #reset V/n record 
                            price_dev_result={}
                    else: # 1st V or n over/under dev's price
                        #dev fail
                        dev_result[len(dev_result)-1]=dev_result[len(dev_result)-1]+ '/'+'Fail'
                        Backtest=0 #confirm
                        price_dev={} #reset V/n record 
                        price_dev_result={}
                    
        return Backtest,price_dev, price_dev_result, dev, dev_result

    def bact_trigger(self,dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back,out):

        if 'flag_lookup_%s'%num not in  dict_flag_all: # initial dict
            dict_flag_all.append('flag_lookup_%s'%num)
            dict_back_all,globals()['flag_lookup_%s'%num]=self.dict_initial(num,dict_back_all)
        dict_back_all[num],globals()['flag_lookup_%s'%num],globals()['bear_bull_%s'%num],globals()['count_day_%s'%num],globals()['record_per_%s'%num],globals()['first_close_back_%s'%num],globals()['out_%s'%num]=self.back_base_add_2(dict_back_all[num],num,bull_bear_check,first_close_back,out)
        return dict_back_all

    def dict_find(self,dict_back_all, key_find, QM_find):
        ket_delete=0
        record_remove=[]
        collect={}
        # for i in range(0, len(dict_back_all)):
        for key in dict_back_all:
            if str(key_find) in key and str(QM_find) in key:
                collect[key]=dict_back_all[key]

        return collect

    def dict_initial(self,flag_lookup,dict_back_all):

        dict_5S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'} #bear/bull, 分子,分母,勝率,漲幅
        dict_10S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_15S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_20S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_30S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_40S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_60S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'} #bear/bull, 分子,分母,勝率,漲幅
        dict_80S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_100S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_120S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_140S={'0_%s'%flag_lookup:'0/0/0/0/0', '5_%s'%flag_lookup:'0/0/0/0/0', '10_%s'%flag_lookup:'0/0/0/0/0', '15_%s'%flag_lookup:'0/0/0/0/0', '20_%s'%flag_lookup:'0/0/0/0/0'}
        dict_back_all[str(flag_lookup)]={'5S_%s'%flag_lookup:dict_5S, '10S_%s'%flag_lookup:dict_10S, '15S_%s'%flag_lookup:dict_15S, '20S_%s'%flag_lookup:dict_20S, '30S_%s'%flag_lookup:dict_30S, '40S_%s'%flag_lookup:dict_40S, '60S_%s'%flag_lookup:dict_60S, '80S_%s'%flag_lookup:dict_80S, '100S_%s'%flag_lookup:dict_100S, '120S_%s'%flag_lookup:dict_120S, '140S_%s'%flag_lookup:dict_140S}

        return dict_back_all,'0'

    def back_base_add_2(self,dict_back_all,flag_lookup,bull_bear_check,first_close_back,out):

        bear_bull=bull_bear_check #@@
        count_day=0 #@@
        record_per=0 #@@                         
        A=5
        per=0

        for i in range(0,11): #~140S
            for j in range(0,5):
                #bear/bull, 分子,分母,勝率,漲幅
                temp1=dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[0] #bear/bull
                temp2=int(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[1]) #分子
                temp3=int(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[2]) #分母
                temp4=float(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[3]) #勝率
                temp5=float(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[4]) #漲幅
                temp3=temp3+1
                temp4=round(temp2/temp3*100,2)
                dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)]='%s/%s/%s/%s/%s'%(temp1,temp2,temp3,temp4,temp5)
                per=per+5
            if A==20 or A==30:
                A=A+10
            elif A==40 or A==60 or A==80 or A==100 or A==120:
                A=A+20
            else:
                A=A+5
            per=0
        return dict_back_all,'1',bear_bull,count_day,record_per,first_close_back,out

    def back_base_add(self,dict_back_all,flag_lookup):
        A=5
        per=0
        for i in range(0,6):
            for j in range(0,5):
                #bear/bull, 分子,分母,勝率,漲幅
                temp1=dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[0] #bear/bull
                temp2=int(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[1]) #分子
                temp3=int(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[2]) #分母
                temp4=float(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[3]) #勝率
                temp5=float(dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)].split('/')[4]) #漲幅
                temp3=temp3+1
                temp4=round(temp2/temp3*100,2)
                dict_back_all['%sS_%s'%(A,flag_lookup)]['%s_%s'%(per,flag_lookup)]='%s/%s/%s/%s/%s'%(temp1,temp2,temp3,temp4,temp5)
                per=per+5
            if A==20 or A==30:
                A=A+10
            else:
                A=A+5
            per=0
        return dict_back_all

    def record_in_1(self,dict_back,key_day,flag_lookup,record_per,gain):
        if gain==1:
            if record_per>0 or record_per<0:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'0',record_per,gain)
            if record_per>5:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'5',record_per,gain)
            if record_per>10:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'10',record_per,gain)
            if record_per>15:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'15',record_per,gain)
            if record_per>20:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'20',record_per,gain)
        else:
            if record_per<0 or record_per>0:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'0',record_per,gain)
            if record_per<-5:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'5',record_per,gain)
            if record_per<-10:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'10',record_per,gain)
            if record_per<-15:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'15',record_per,gain)
            if record_per<-20:
                dict_back=self.record_in_2(dict_back,key_day,flag_lookup,'20',record_per,gain)
        return dict_back

    def record_in_2(self,dict_back_all,key_day,flag_lookup,per,record_per,gain):
        #bear/bull, 分子,分母,勝率,漲幅
        temp1=dict_back_all[key_day]['%s_%s'%(per,flag_lookup)].split('/')[0] #bear/bull
        temp2=int(dict_back_all[key_day]['%s_%s'%(per,flag_lookup)].split('/')[1]) #分子
        temp3=int(dict_back_all[key_day]['%s_%s'%(per,flag_lookup)].split('/')[2]) #分母
        temp4=float(dict_back_all[key_day]['%s_%s'%(per,flag_lookup)].split('/')[3]) #勝率
        temp5=float(dict_back_all[key_day]['%s_%s'%(per,flag_lookup)].split('/')[4]) #漲幅

        if gain==1:
            temp1='bull'
            if temp5==0:
                temp5=round(record_per,2)
            else:
                temp5=round((temp5*temp2+record_per)/(temp2+1),2) # average
            # elif record_per<temp5 : # record min
            #     temp5=round(record_per,2)
            temp2=temp2+1
        else:
            temp1='bear'
            if temp5==0:
                temp5=round(record_per,2)
            else:
                temp5=round((temp5*temp2+record_per)/(temp2+1),2) # average
            # elif record_per>temp5 : # record min
            #     temp5=round(record_per,2)
            temp2=temp2+1
        temp4=round(temp2/temp3*100,2)

        dict_back_all[key_day]['%s_%s'%(per,flag_lookup)]='%s/%s/%s/%s/%s'%(temp1,temp2,temp3,round(temp4,2),temp5)
        return dict_back_all

    def out_loop_check(self,out_F):
        
        result=0
        for i in out_F:
            if i==self.out_check: # 代表出場機制早已觸發，必須把這一次的統計資料列入
                result=1
                break
        return result

    def back_check(self,flag_lookup,dict_back,first_close,close,stop_per,delta_day,record_per,bear_bull_1,out_F):
        
        # if '13' in flag_lookup and close==2.66:
        #     temp=1
        first_close_BB=round(float(first_close.split(',')[0]),2)
        first_close=round(float(first_close.split(',')[1]),2)

        delta=close-first_close_BB # 合約價
        delta_per=(delta/first_close_BB)*100

        delta_st=close-first_close # 觸發時的市價
        delta_per_st=(delta_st/first_close)*100

        out_result_check=self.out_loop_check(out_F)
        if bear_bull_1=='bull': # 'bull'
            gain=1
            if delta_per>-stop_per or out_result_check==1: # out_result_check=1代表出場機制早已觸發，必須把這一次的統計資料列入
                fail=0
            else:
                fail=1
        else: # 'bear'
            gain=0
            if delta_per<stop_per or out_result_check==1: # out_result_check=1代表出場機制早已觸發，必須把這一次的統計資料列入
                fail=0
            else:
                fail=1

        if 0==0: # fail==0
            if delta_per>record_per and gain==1:
                record_per=delta_per_st
            elif delta_per<record_per and gain==0:
                record_per=delta_per_st
            # record_per=delta_per_st

            if delta_day==5 and fail==0:
                key_day='5S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==10 and fail==0:
                # if '31' in flag_lookup:
                #     print(self.debug)
                key_day='10S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==15 and fail==0:
                key_day='15S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==20 and fail==0:
                key_day='20S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==30 and fail==0:
                key_day='30S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==40 and fail==0:
                key_day='40S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==60 and fail==0:
                key_day='60S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==80 and fail==0:
                key_day='80S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==100 and fail==0:
                key_day='100S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==120 and fail==0:
                key_day='120S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin
            elif delta_day==140 and fail==0:
                key_day='140S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
                self.out_check=0 # 初始化for下一個bin

                flag_lookup='0' # stop to record
                delta_day=0
        else:
            # 停損
            flag_lookup='0'
            delta_day=0

        try:
            flag_lookup=flag_lookup.split('/')[0]
        except:
            pass

        return dict_back,flag_lookup,record_per,delta_day

    def Week_check(self, df, Start_MA,row_n):
        input_initial = Start_MA - 5	
        loop_minus = -1
        date_C=df['Date'][int(Start_MA)]
        # date_C=datetime.strptime(date_C, "%Y/%m/%d")#.date()
        w_i=date_C.weekday()+1
        w=date_C.weekday()+1 #0=mon, 1=Tus....6=sun
        for j in range (0,30):
 
            if w!=5:
                Start_MA=Start_MA+loop_minus
                # date_C=df['Date'][int(Start_MA)]
                # w=datetime.strptime(df['Date'][int(Start_MA)], "%Y/%m/%d").weekday()+1
                w=df['Date'][int(Start_MA)].weekday()+1
                if j==0 and w==5-w_i: # last Fir is holiday
                    break
            else:
                if j>1 and Start_MA==input_initial:
                    Start_MA=input_initial+5
                    # w=datetime.strptime(df['Date'][int(Start_MA)], "%Y/%m/%d").weekday()+1
                    w=df['Date'][int(Start_MA)].weekday()+1
                    loop_minus = 1
                else:
                    break
        return Start_MA

    def dict_rename(self,dict_back_all,back_ornot):
        ket_delete=0
        record_remove=[]
        # for i in range(0, len(dict_back_all)):
        for key in dict_back_all:           
            try:
                j=key
                L=0
                for k in range(0, 11):
                    if ket_delete==1: # key has been deleted
                        ket_delete=0
                        break
                    if L==20 or L==30: #A==20 or A==30 or A==40 or A==60 or A==80 or A==100 or A==120 or A==140   L==20 or L==30
                        L=L+10
                    elif L==40 or L==60 or L==80 or L==100 or L==120:
                        L=L+20
                    else:
                        L=L+5
                    str_2='%sS_%s'%(L,j)
                    str_1='%sS'%(L)
                    dict_back_all[j][str_1] = dict_back_all[j].pop(str_2)
                    H=0
                    for G in range(0, 5):
                        str_3='%s_%s'%(H,j)
                        str_4='%s'%(H)
                        if int(dict_back_all[j][str_1][str_3].split('/')[2])==1 and str_1=='5S' and str_4=='0': # check sample is 1 or not? 1: delete this repord of dict
                            # dict_back_all.pop(j)
                            record_remove.append(j)
                            # del dict_back_all[j]
                            ket_delete=1
                            break
                        else:
                            dict_back_all[j][str_1][str_4] = dict_back_all[j][str_1].pop(str_3)
                        H=H+5
            except:
                continue  # Lost this key
        if back_ornot==1:
            for list in record_remove:
                del dict_back_all[list]

        return dict_back_all

    def status_analysis(self, array):
        if array[0]==0 and array[1]==0 and array[2]==0 and array[3]==0:
            result="0"
        elif array[0]>=array[1] and array[1]>=array[2] and array[2]>=array[3]:
            result="P3"
        elif array[1]>=array[2] and array[2]>=array[3]:
            result="ing/P2"
        elif array[0]>=array[1] and array[1]>=array[2]:
            result="P2"
        elif array[0]>=array[1]:
            result="P1"
        elif array[0]<=array[1] and array[1]<=array[2] and array[2]<=array[3]:
            result="N3"
        elif array[1]<=array[2] and array[2]<=array[3]:
            result="ing/N2"
        elif array[0]<=array[1] and array[1]<=array[2]:
            result="N2"
        elif array[0]<=array[1]:
            result="N1"
        else:
            result="same"
        
        return result

    def MA_analysis(self, MA_5, MA_4, MA_40, MA_80):
        # Output:
        # 1=Bull_big: MA5 > MA4 > MA40 > MA80
        # 2=Bull_Samll: MA40 > MA80
        # 3=Bull_Samll_5<40: MA40 > MA80, MA40 > MA5
        # 4=kink_P: else & MA80 increase 3 days
        # 5=Bear_big: MA5 < MA4 < MA40 < MA80
        # 6=Bear_Samll: MA40 < MA80
        # 7=Bear_Samll_5>40: MA40 > MA80, MA40 > MA5
        # 8=kink_n: else & MA80 decrease 3 days
        # 9=kink: else
        
        if MA_5 > MA_4 and MA_4 > MA_40 and MA_40 > MA_80:# 	
            result ='Bull-Big' # 大牛
        elif MA_5 < MA_4 and MA_4 < MA_40 and MA_40 < MA_80:# 	
            result ='Bear-Big' # 大熊
        elif MA_40 > MA_80 and MA_5 < MA_40:# 
            result ='Bull-small_5<40' 
        elif MA_40 < MA_80 and MA_5 > MA_40:# 	
            result ='Bear-small_5>40'
        elif MA_40 > MA_80: # 小牛
            result ='Bull-small'
        elif MA_40 < MA_80: # 大熊
            result ='Bear-small'
        else:
            result ='NA'
        return result

    def operation_analysis(self, EMA, OSC):
        if 'P' in str(EMA) and 'P' in str(OSC):
            result="Long/watch" #can NOT short
        elif 'N' in str(EMA) and 'N' in str(OSC):
            result="Short/watch" #can NOT Long
        else:
            result="Long/Short" #observed 2nd filter
        return result

    def Stock_single_no_data(self, stock_TW):

        filepath=os.getcwd() + os.sep + 'stock_temp'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        stock = yf.Ticker(stock_TW)
        df =stock.history(period="max")
        df=df.reset_index()
        df.to_csv(os.getcwd() + os.sep + 'stock_temp' + os.sep + 'file_%s.csv' %stock_TW,index='Date')
        return df

    def csv_to_google_sheet(self,Stock_mame,sheet):
        # https://github.com/burnash/gspread
        # check worksheet esit or not
        # worksheet_list = sheet.worksheets()        
        try:
            worksheet = sheet.worksheet(Stock_mame)
        except:
            sheet.add_worksheet(title=Stock_mame, rows="100", cols="20")
        csvFile = os.getcwd() + os.sep + 'stock_temp%s%s_BT.csv'%(os.sep,Stock_mame)
        sheetName=Stock_mame
        sheet.values_update(
            sheetName,
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': list(csv.reader(open(csvFile)))}
        )
        
    def initial_google_API_sheet(self):
        auth_json_path = os.getcwd() + os.sep + 'google_API%squickstart-1588518768211-49f22d29c37c.json'%os.sep
        gss_scopes = ['https://spreadsheets.google.com/feeds']
        #連線
        credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)
        gss_client = gspread.authorize(credentials)
        #開啟 Google Sheet 資料表
        # https://docs.google.com/spreadsheets/d/1xmcbYs_ZGiZ3ccfQ68IqLo-Ybg9BSbzQ3T-yxXlc4Pc/edit#gid=1766151529
        
        spreadsheet_key = '1xmcbYs_ZGiZ3ccfQ68IqLo-Ybg9BSbzQ3T-yxXlc4Pc' 
        sheet = gss_client.open_by_key(spreadsheet_key)
        
        return sheet

    def google_API_sheet(self):
        # gc = pygsheets.authorize(service_file=os.getcwd() + '\\google_API\\quickstart-1588518768211-49f22d29c37c.json')
        # # https://docs.google.com/spreadsheets/d/1xmcbYs_ZGiZ3ccfQ68IqLo-Ybg9BSbzQ3T-yxXlc4Pc/edit?usp=sharing
        # sht = gc.create("Python測試用模板",parent_id="1xmcbYs_ZGiZ3ccfQ68IqLo-Ybg9BSbzQ3T-yxXlc4Pc")
        # # sh = gc.open('python_link')
        # wks_list = sht.worksheets()
        # print(wks_list)

        # refer web:  https://medium.com/@yanweiliu/%E5%A6%82%E4%BD%95%E9%80%8F%E9%81%8Epython%E5%BB%BA%E7%AB%8Bgoogle%E8%A1%A8%E5%96%AE-%E4%BD%BF%E7%94%A8google-sheet-api-314927f7a601
        auth_json_path = os.getcwd() + os.sep +'google_API%squickstart-1588518768211-49f22d29c37c.json'%os.sep
        gss_scopes = ['https://spreadsheets.google.com/feeds']

        #連線
        credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)
        gss_client = gspread.authorize(credentials)

        #開啟 Google Sheet 資料表
        spreadsheet_key = '1xmcbYs_ZGiZ3ccfQ68IqLo-Ybg9BSbzQ3T-yxXlc4Pc' 

        
        # step1: create 金鑰 https://console.cloud.google.com/iam-admin/serviceaccounts/details/105294018447533401887?folder=&organizationId=&project=quickstart-1588518768211&supportedpurview=project
        # step2: Enable it by visiting : https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=1054109961393
        # step3: 共享sheet 並將之道連結設定為編輯者

        #建立工作表1
        # sheet = gss_client.open_by_key(spreadsheet_key).sheet1
        #自定義工作表名稱

        #https://github.com/burnash/gspread
        sheet = gss_client.open_by_key(spreadsheet_key)#.worksheet('SPY_BT')

        # temp=sheet.get_all_values()
        # https://stackoverflow.com/questions/57264871/python-gspread-import-csv-to-specific-work-sheet
        csvFile = os.getcwd() + os.sep +'stock_temp%sSPY_BT.csv'%os.sep
        sheetName='SPY_BT'
        sheet.values_update(
            sheetName,
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': list(csv.reader(open(csvFile)))}
        )
        self.sheet=sheet

        # return 0

        #Google Sheet 資料表操作(20191224新版)
        sheet.update_acell('D2', 'ABC')  #D2加入ABC
        sheet.update_cell(2, 4, 'ABC')   #D2加入ABC(第2列第4行即D2)
        #寫入一整列(list型態的資料)
        values = ['A','B','C','D']
        sheet.insert_row(values, 1) #插入values到第1列

        dict = {'0':{'5':1,'10':2},'1':{'5':1,'10':2}}
        all=dict.items()
        key=dict.keys()
        value=dict.values()
        # sheet.frozen_col_count
        # sheet.set_basic_filter
        # sheet.sort
        # sheet.
        # 粗體
        # sheet.format('A1:B1', {'textFormat': {'bold': True}}) # copy the last row and append it back to the sheet
        sheet.batch_update([{
            'range': 'A1:B2',
            'values': [['A1', 'B1'], ['A2', 'B2']],
        }, {
            'range': 'J42:K43',
            'values': [[1, 2], [3, 4]],
        }])

        # sheet.insert_row(dict) #插入values到第1列

        #讀取儲存格
        temp=sheet.acell('A3').value
        sheet.cell(1, 2).value

        #讀取整欄或整列
        temp=sheet.row_values(1) #讀取第1列的一整列
        sheet.col_values(1) #讀取第1欄的一整欄
        #讀取整個表
        temp=sheet.get_all_values()
        
        temp=1

    def save_obj(self, obj, name ):
        filepath=os.getcwd() + os.sep +'obj'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        with open('obj/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    def load_obj(self, name ):
        with open('obj/' + name + '.pkl', 'rb') as f:
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
            for day in ['5S','10S','15S','20S','30S','40S','60S','80S','100S','120S','140S']:
                for percent in ['0','5','10','15','20']:
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
                    dict_r_T[day]='%s/%s/%s'%(W_r,P_r,S_2nd_T)
                    dict_r[key_type]=dict_r_T
                    if W_r>=T_per:
                        dict_F[key_type]='%s,%s,%s,%s'%(W_r,P_r,day,S_2nd_T) # win rate, percent, DTE
                        self.save_obj(dict_r,'%s_r'%stock)
                        self.save_obj(dict_F,'%s_F'%stock)
        # dict_back_all_obereved32=self.dict_find(dict_F,'32', '/Ma')
        # dict_back_all_obereved33=self.dict_find(dict_r,'34/', 'Q2/Ma')
        # dict_back_all_obereved34=self.dict_find(dict_r,'34/', 'Qa/Ma')

        # dict_back_all_obereved461=self.dict_find(key_1st,'34', '/')
        # dict_back_all_obereved462=self.dict_find(key_2nd,'34', '/')
        return dict_r, dict_F

if __name__ == '__main__':

    
    test_stock='QQQ'
    # sheet=sum().initial_google_API_sheet()
    # sum().csv_to_google_sheet(test_stock,sheet)

    df= sum().Stock_single_no_data(test_stock)
    
    BT_sum={}
    temp=0
    for i in [3,10]:
        dict_r, temp=sum().MACD_weekly_check(df,test_stock, 26, 570*i, period=5, back_ornot=1, weekly_BT=0) # get weekly data_570Weeks
        dict_r, BT_sum[i]=sum().MACD_weekly_check(df,test_stock, 26, 570*i, period=1, back_ornot=1, weekly_BT=dict_r['weekly_BT']) # get daily data_570days
    sum().save_obj(BT_sum,test_stock)
    BT=sum().load_obj(test_stock)
    sum().BT_combination(BT,70,test_stock)
    print('123')
    