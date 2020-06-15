import requests
# import pandas as pd
from datetime import datetime
import time
import os
import yfinance as yf # option https://aroussi.com/post/python-yahoo-finance
import pandas as pd

class sum():
    def MACD_weekly_check(self, df, stock_name, MA_day, EMA_day, period, back_ornot):
        # back_ornot=1
        # if back_ornot==1:
        #     EMA_day=EMA_day*10  # 20 year  
    #==dim array
        MA5_val_sum=[0, 0, 0, 0]
        MA4_val_sum=[0, 0, 0, 0]
        MA40_val_sum=[0, 0, 0, 0]
        MA80_val_sum=[0, 0, 0, 0]
        latest_data_MA=[0, 0, 0, 0, 0]

        OSC_result=[0, 0, 0, 0]
        DIF_result=[0, 0, 0, 0]
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
        row_n =int(len(df))-1
        a = MA_day
        b = EMA_day

        #===RSI
        RSI_gain=0
        RSI_loss=0
        RSI_result=[0, 0, 0, 0]
        RSI_days=13
        RSI_days_flasg=RSI_days
        change_dict={}
        RSI_dict={}

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
    #===loop start
        flag_error=0

        if back_ornot==0:
            EMA5_Volum_criteria=(10)*period
            MA5_base_criteria=(10)*period
            MA40_base_criteria=(121)*period
            sto_criteria=(12+3+1+(b-100))*period
            ATR_criteria=(17)*period
        else:
            EMA5_Volum_criteria=9999999999
            MA5_base_criteria=9999999999
            MA40_base_criteria=9999999999
            sto_criteria=9999999999
            ATR_criteria=9999999999

        while Start<=row_n:
            flag_error=flag_error+1
            if flag_error>row_n+100: # avoid infiniti loop, then lost worker
                print('tek error')
                break
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
                    DIF_result[0]=DIF

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
                                K_per_a[flag_KD_loop]=round((df['Close'][int(Start)]-low)/(high-low)*100,2)
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

                #========backtesting
                    back_en=1 # 
                    if back_ornot==back_en or Start>=row_n-3:  #Start==row_n: latest days check trigger event
                        stop_per=3 #停損+/-2%
                        back_close=df['Close'][int(Start)]
                        Date_precent=df['Date'][int(Start-1)].date() #datetime.strptime(df['Date'][int(Start)], "%Y-%m-%d").date()
                        
                        for Qa in range(0,2): #season
                            if back_ornot==0: # no backtest don't check month and Q 
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
                            for Ma in range(0,2): #Month
                                if back_ornot==0: # no backtest don't check month and Q 
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

                        #===dev trigger check 背離
                                if len(D_dev_result)>=1:                       
                                    D_dev_result_Date=datetime.strptime(D_dev_result[len(D_dev_result)-1].split('/')[0], "%Y-%m-%d %H:%M:%S").date()
                                    D_dev_result_gain=D_dev_result[len(D_dev_result)-1].split('/')[1]
                                    D_dev_result_per_dev=float(D_dev_result[len(D_dev_result)-1].split('/')[2]) # percent of dev
                                    D_dev_result_per_price=float(D_dev_result[len(D_dev_result)-1].split('/')[3]) # percent of price
                                    D_dev_trggered=(Date_precent-D_dev_result_Date).days # used for dec trigger
                                    first_close_back=float(D_dev_result[len(D_dev_result)-1].split('/')[4])
                                #==1. D%空頭背離, bull
                                    if  D_dev_trggered==0 and D_dev_result_gain=='bear_dev' :
                                        num=str('1%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==2. D%空頭背離+D%<=30, bull
                                    if  D_per_a[1]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev': #
                                        num=str('2%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==3. D%空頭背離+D%<=30+delta_price_dec>=4, bull
                                    if  D_per_a[1]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev' and D_dev_result_per_dev>=4 and D_dev_result_per_price>=4: #
                                        num=str('3%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==4. D%空頭背離+D%<=30+delta_price_dec>=8, bull
                                    if  D_per_a[1]<=30 and D_dev_trggered==0 and D_dev_result_gain=='bear_dev' and D_dev_result_per_dev>=8 and D_dev_result_per_price>=8: #
                                        num=str('4%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==5. D%多頭背離, bear
                                    if  D_dev_trggered==0 and D_dev_result_gain=='bull_dev': #
                                        num=str('5%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==6. D%多頭背離+D%>=70, bear
                                    if  D_per_a[1]>=70 and D_dev_trggered==0 and D_dev_result_gain=='bull_dev': #
                                        num=str('6%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==7. D%多頭背離+D%>=70+delta_price_dec>=4, bear
                                    if  D_per_a[1]>=70 and D_dev_trggered==0 and D_dev_result_gain=='bull_dev' and D_dev_result_per_dev>=4 and D_dev_result_per_price>=4: #
                                        num=str('7%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==8. D%多頭背離+D%>=70+delta_price_dec>=8, bear
                                    if  D_per_a[1]>=70 and D_dev_trggered==0 and D_dev_result_gain=='bull_dev' and D_dev_result_per_dev>=8 and D_dev_result_per_price>=8: #
                                        num=str('8%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                if len(OSC_dev_result)>=1:                       
                                    OSC_dev_result_Date=datetime.strptime(OSC_dev_result[len(OSC_dev_result)-1].split('/')[0], "%Y-%m-%d %H:%M:%S").date()
                                    OSC_dev_result_gain=OSC_dev_result[len(OSC_dev_result)-1].split('/')[1]
                                    OSC_dev_result_per_dev=float(OSC_dev_result[len(OSC_dev_result)-1].split('/')[2]) # percent of dev
                                    OSC_dev_result_per_price=float(OSC_dev_result[len(OSC_dev_result)-1].split('/')[3]) # percent of price
                                    OSC_dev_trggered=(Date_precent-OSC_dev_result_Date).days # used for dec trigger
                                    first_close_back=float(OSC_dev_result[len(OSC_dev_result)-1].split('/')[4])
                                #==9. OSC空頭背離, bull
                                    if  OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' :
                                        num=str('9%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==10. OSC空頭背離+RSI<=30, bull
                                    if  RSI_result[1]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev': #
                                        num=str('10%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==11. OSC空頭背離+RSI<=30+delta_price_dec>=4, bull
                                    if  RSI_result[1]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' and OSC_dev_result_per_dev>=4 and OSC_dev_result_per_price>=4: #
                                        num=str('11%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==12. OSC空頭背離+RSI<=30+delta_price_dec>=8, bull
                                    if  RSI_result[1]<=30 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bear_dev' and OSC_dev_result_per_dev>=8 and OSC_dev_result_per_price>=8: #
                                        num=str('12%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==13. OSC多頭背離, bear
                                    if OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev': #
                                        num=str('13%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==14. OSC多頭背離+RSI>=70, bear
                                    if  RSI_result[1]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev': #
                                        num=str('14%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==15. OSC多頭背離+RSI>=70+delta_price_dec>=4, bear
                                    if  RSI_result[1]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev' and OSC_dev_result_per_dev>=4 and OSC_dev_result_per_price>=4: #
                                        num=str('15%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==16. OSC多頭背離+RSI>=70+delta_price_dec>=8, bear
                                    if  RSI_result[1]>=70 and OSC_dev_trggered==0 and OSC_dev_result_gain=='bull_dev' and OSC_dev_result_per_dev>=8 and OSC_dev_result_per_price>=8: #
                                        num=str('16%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                if len(RSI_dev_result)>=1:                       
                                    RSI_dev_result_Date=datetime.strptime(RSI_dev_result[len(RSI_dev_result)-1].split('/')[0], "%Y-%m-%d %H:%M:%S").date()
                                    RSI_dev_result_gain=RSI_dev_result[len(RSI_dev_result)-1].split('/')[1]
                                    RSI_dev_result_per_dev=float(RSI_dev_result[len(RSI_dev_result)-1].split('/')[2]) # percent of dev
                                    RSI_dev_result_per_price=float(RSI_dev_result[len(RSI_dev_result)-1].split('/')[3]) # percent of price
                                    RSI_dev_trggered=(Date_precent-RSI_dev_result_Date).days # used for dec trigger
                                    first_close_back=float(RSI_dev_result[len(RSI_dev_result)-1].split('/')[4])
                                #==17. RSI空頭背離, bull
                                    if  RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev' :
                                        num=str('17%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==18. RSI空頭背離+RSI<=30, bull
                                    if  RSI_result[1]<=30 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev': #
                                        num=str('18%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==19. RSI空頭背離+RSI<=30+delta_price_dec>=4, bull
                                    if  RSI_result[1]<=30 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev' and RSI_dev_result_per_dev>=4 and RSI_dev_result_per_price>=4: #
                                        num=str('19%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==20. RSI空頭背離+RSI<=30+delta_price_dec>=8, bull
                                    if  RSI_result[1]<=30 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bear_dev' and RSI_dev_result_per_dev>=8 and RSI_dev_result_per_price>=8: #
                                        num=str('20%s'%sum_check) 
                                        bull_bear_check='bull'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==21. RSI多頭背離, bear
                                    if  RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev': #
                                        num=str('21%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==22. RSI多頭背離+RSI>=70, bear
                                    if  RSI_result[1]>=70 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev': #
                                        num=str('22%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==23. RSI多頭背離+RSI>=70+delta_price_dec>=4, bear
                                    if  RSI_result[1]>=70 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev' and RSI_dev_result_per_dev>=4 and RSI_dev_result_per_price>=4: #
                                        num=str('23%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==24. RSI多頭背離+RSI>=70+delta_price_dec>=8, bear
                                    if  RSI_result[1]>=70 and RSI_dev_trggered==0 and RSI_dev_result_gain=='bull_dev' and RSI_dev_result_per_dev>=8 and RSI_dev_result_per_price>=8: #
                                        num=str('24%s'%sum_check) 
                                        bull_bear_check='bear'
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==25. 1~24 背離5天內 + 量>=1.2 MA5test
                                    if '/Qa/Ma' in sum_check and flag_V_EMA5>=5:
                                        for vol_dev in range(0,24):
                                            try:
                                                if precent_Vol >=precent_V_EMA5*1.5 and globals()['count_day_%s/Qa/Ma'%(vol_dev+1)]>0 and globals()['count_day_%s/Qa/Ma'%(vol_dev+1)]<=5: #
                                                    num=str('25%s'%sum_check + '/Vol-%s'%(vol_dev+1)) 
                                                    bull_bear_check=globals()['bear_bull_%s/Qa/Ma'%(vol_dev+1)]
                                                    dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                            except:
                                                pass # do not trigger yet.                      
                                # =====非背離
                                try: 
                                #==26. FAvg40 cross Favg80 up, bull
                                    if  MA40_val_sum[0]>MA80_val_sum[0] and MA40_val_sum[1]<MA80_val_sum[1]: #
                                        num=str('26%s'%sum_check) 
                                        bull_bear_check='bull'
                                        first_close_back=back_close # 非背離 紀錄當下 close
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                #==27. FAvg40 cross Favg80 down, bear
                                    if  MA40_val_sum[0]<MA80_val_sum[0] and MA40_val_sum[1]>MA80_val_sum[1]: #
                                        num=str('27%s'%sum_check) 
                                        bull_bear_check='bear'
                                        first_close_back=back_close # 非背離 紀錄當下 close
                                        dict_back_all=self.bact_trigger(dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back)
                                except:
                                    pass

                        if back_ornot==back_en:
                            for back_i in dict_flag_all:
                                if int(globals()[back_i])>0: #@@
                                    num=back_i.split('_')[2]
                                    # self.debug=Start
                                    globals()['count_day_%s'%num]=globals()['count_day_%s'%num]+1 #@@
                                    # if '26/Q2/M5' in back_i:
                                    #     temp=1
                                    dict_back_all[num],globals()['flag_lookup_%s'%num],globals()['record_per_%s'%num],globals()['count_day_%s'%num]=self.back_check(num,dict_back_all[num],globals()['first_close_back_%s'%num],back_close,stop_per,globals()['count_day_%s'%num],globals()['record_per_%s'%num],globals()['bear_bull_%s'%num]) #@                     
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
            except:
                self.debug=Start
                temp='MACD_week error'
        dict_back_all=self.dict_rename(dict_back_all)  # Throw away one sample record
        trigger=""
        for key in dict_back_all:
            trigger= trigger  +  key + ','
        trigger={'trigger':trigger}
        dict_back_all_obereved=self.dict_find(dict_back_all,26, 'Qa/Ma') # 不指定QM, 輸入/
        #=======================================check end record
        if back_ornot==back_en:
            #========save backtest result to csv================
            filepath=os.getcwd() + '\\stock_temp'
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
            dict_back_all = pd.DataFrame.from_dict(dict_back_all, orient="index")
            dict_back_all.to_csv(filepath + '\\%s_%s.csv'%(stock_name,'BT')) # Throw away one sample record
            #========save backtest result to csv================
            back_j=0
            for back_i in dict_flag_all:
                temp=int(globals()['count_day_%s'%back_i.split('_')[2]])
                if int(globals()[back_i])!=0 and int(globals()['count_day_%s'%back_i.split('_')[2]])<5:
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
        x=EMA_12
        
    #===========================================Sum===================================================		
        # DIF_last=EMA_12[i-1]
        # x=EMA_12
        temp=EMA_12[i]
        # show rank
        y={key: rank for rank, key in enumerate(sorted(x, key=x.get, reverse=False),1)}
        per_DIF[0]=round(y[i]/i*100,2)  #latest DIF%
        per_DIF[1]=round(y[i-1]/i*100,2)
        per_DIF[2]=round(y[i-2]/i*100,2)
        per_DIF[3]=round(y[i-3]/i*100,2)
        DIF_per_last_status=self.status_analysis(per_DIF)

        #KD
        temp=self.status_analysis(D_per_a) #daily_ok
        D_per_a.append(temp)

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
        MACD_12_26=self.status_analysis(EMA13_result) #daily_ok
        # final_result=self.operation_analysis(OSC_result_F,MACD_12_26) #daily_ok

        RSI_result_F=self.status_analysis(RSI_result) #daily_ok

        ATR_avg_sum=[list_ATR[len(list_ATR)-1], list_ATR[len(list_ATR)-2], list_ATR[len(list_ATR)-3], list_ATR[len(list_ATR)-4]] #daily_ok
        ATR_avg_F=self.status_analysis(ATR_avg_sum) #daily_ok

        V_MA5_val_sum
        precent_Vol

        #=======build dict from list
        list_input=['MA5_val_sum','MA4_val_sum','MA40_val_sum','MA80_val_sum','latest_data_MA','OSC_result','EMA13_result','D_per_a','RSI_result','RSI_result_F','ATR_avg_sum','ATR_avg_F','precent_Vol','V_MA5_val_sum','trigger']
        dict_input={}
        for name in list_input:
            dict_input[name]=locals()[name]
        dict_sum=dict_input

        return dict_sum

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

    def bact_trigger(self,dict_back_all,dict_flag_all,num,bull_bear_check,first_close_back):

        if 'flag_lookup_%s'%num not in  dict_flag_all: # initial dict
            dict_flag_all.append('flag_lookup_%s'%num)
            dict_back_all,globals()['flag_lookup_%s'%num]=self.dict_initial(num,dict_back_all)
        dict_back_all[num],globals()['flag_lookup_%s'%num],globals()['bear_bull_%s'%num],globals()['count_day_%s'%num],globals()['record_per_%s'%num],globals()['first_close_back_%s'%num]=self.back_base_add_2(dict_back_all[num],num,bull_bear_check,first_close_back)
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
        dict_back_all[str(flag_lookup)]={'5S_%s'%flag_lookup:dict_5S, '10S_%s'%flag_lookup:dict_10S, '15S_%s'%flag_lookup:dict_15S, '20S_%s'%flag_lookup:dict_20S, '30S_%s'%flag_lookup:dict_30S, '40S_%s'%flag_lookup:dict_40S}

        return dict_back_all,'0'

    def back_base_add_2(self,dict_back_all,flag_lookup,bull_bear_check,first_close_back):

        bear_bull=bull_bear_check #@@
        count_day=0 #@@
        record_per=0 #@@                         
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
        return dict_back_all,'1',bear_bull,count_day,record_per,first_close_back

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
            if record_per>0:
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
            if record_per<0:
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
            elif record_per<temp5 :
                temp5=round(record_per,2)
        else:
            temp1='bear'
            if temp5==0:
                temp5=round(record_per,2)
            elif record_per>temp5 :
                temp5=round(record_per,2)
        temp2=temp2+1
        # if '%s_%s'%(per,flag_lookup)=='0_1' and key_day=="5S_1": # debug
        #     print(self.debug)
        temp4=round(temp2/temp3*100,2)

        dict_back_all[key_day]['%s_%s'%(per,flag_lookup)]='%s/%s/%s/%s/%s'%(temp1,temp2,temp3,round(temp4,2),temp5)
        return dict_back_all

    def back_check(self,flag_lookup,dict_back,first_close,close,stop_per,delta_day,record_per,bear_bull_1):

        delta=close-first_close
        delta_per=(delta/first_close)*100

        if bear_bull_1=='bull': # 'bull'
            gain=1
            if delta_per>-stop_per:
                fail=0
            else:
                fail=1
        else: # 'bear'
            gain=0
            if delta_per<stop_per:
                fail=0
            else:
                fail=1

        if fail==0:
            if delta_per>record_per and gain==1:
                record_per=delta_per 
            elif delta_per<record_per and gain==0:
                record_per=delta_per

            if delta_day==5:
                key_day='5S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
            elif delta_day==10:
                key_day='10S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
            elif delta_day==15:
                key_day='15S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
            elif delta_day==20:
                key_day='20S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
            elif delta_day==30:
                key_day='30S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
            elif delta_day==40:
                key_day='40S_%s'%flag_lookup
                dict_back=self.record_in_1(dict_back,key_day,flag_lookup,record_per,gain)
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

    def dict_rename(self,dict_back_all):
        ket_delete=0
        record_remove=[]
        # for i in range(0, len(dict_back_all)):
        for key in dict_back_all:           
            try:
                j=key
                L=0
                for k in range(0, 6):
                    if ket_delete==1: # key has been deleted
                        ket_delete=0
                        break
                    if L==20 or L==30:
                        L=L+10
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
            result ='Bull-Big'
        elif MA_5 < MA_4 and MA_4 < MA_40 and MA_40 < MA_80:# 	
            result ='Bear-Big'
        elif MA_40 > MA_80 and MA_5 < MA_40:# 
            result ='Bull-small_5<40'
        elif MA_40 < MA_80 and MA_5 > MA_40:# 	
            result ='Bear-small_5>40'
        elif MA_40 > MA_80:# 
            result ='Bull-small'
        elif MA_40 < MA_80:# 	
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

        filepath=os.getcwd() + '\\stock_temp'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        stock = yf.Ticker(stock_TW)
        df =stock.history(period="max")
        df=df.reset_index()
        df.to_csv(os.getcwd() + '\\stock_temp' + '\\file_%s.csv' %stock_TW,index='Date')
        return df


# if __name__ == '__main__':
#     df= sum().Stock_single_no_data('AMD')
#     sum().MACD_weekly_check(df,'AMD', 26, 570*1, period=1, back_ornot=0) # get daily data_570days
#     sum().MACD_weekly_check(df,'AMD', 26, 570, period=5, back_ornot=0) # get weekly data_570Weeks