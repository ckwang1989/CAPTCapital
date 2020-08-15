from datetime import datetime
from datetime import date as dt

class Condition:
#====================================MA===============================
    def bbupper(self, tech_idxes):
        if 0.995 * tech_idxes['upper'] < tech_idxes['last_close']:
            return True
        else:
            return False
    def bblower(self, tech_idxes):
        if 1.005 * tech_idxes['lower'] > tech_idxes['last_close']:
            return True
        else:
            return False

    def f40up80(self, tech_idxes):
        # FAvg40 cross Favg80 up, bull
        if  tech_idxes['MA40_val_sum'][0]>tech_idxes['MA80_val_sum'][0] and tech_idxes['MA40_val_sum'][1]<tech_idxes['MA80_val_sum'][1]:
            return True
        else:
            return False
    def f40down80(self, tech_idxes):
        # FAvg40 cross Favg80 down, bear
        if   tech_idxes['MA40_val_sum'][0]<tech_idxes['MA80_val_sum'][0] and  tech_idxes['MA40_val_sum'][1]>tech_idxes['MA80_val_sum'][1]:
            return True
        else:
            return False
    def f40godown(self, tech_idxes):
        # FAvg40=n 白下彎
        if   tech_idxes['MA40_val_sum'][0]<tech_idxes['MA40_val_sum'][1] and  tech_idxes['MA40_val_sum'][2]<tech_idxes['MA40_val_sum'][1]:
            return True
        else:
            return False
    def f40goup(self, tech_idxes):  # add new Dary
        # FAvg40=n 白上彎
        if   tech_idxes['MA40_val_sum'][0]>tech_idxes['MA40_val_sum'][1] and  tech_idxes['MA40_val_sum'][2]>tech_idxes['MA40_val_sum'][1]:
            return True
        else:
            return False
    def f40bigger80_D(self, tech_idxes):  # add new Dary
        # FAvg40 cross Favg80 down, bear
        if  tech_idxes['MA40_val_sum'][0]>tech_idxes['MA80_val_sum'][0]:
            return True
        else:
            return False
    def f40smaller80_D(self, tech_idxes): # add new Dary
        # FAvg40 cross Favg80 down, bear
        if  tech_idxes['MA40_val_sum'][0]<tech_idxes['MA80_val_sum'][0]:
            return True
        else:
            return False
    def f40bigger80_W(self, tech_idxes):  # add new Dary
        # FAvg40 cross Favg80 down, bear
        if  tech_idxes['M40_weekly_value'][0]>tech_idxes['M80_weekly_value'][0]:
            return True
        else:
            return False
    def f40smaller80_W(self, tech_idxes): # add new Dary
        # FAvg40 cross Favg80 down, bear
        if  tech_idxes['M40_weekly_value'][0]<tech_idxes['M80_weekly_value'][0]:
            return True
        else:
            return False
    def f5up4(self, tech_idxes):
        if tech_idxes['MA5_val_sum'][0]>tech_idxes['MA4_val_sum'][0] and tech_idxes['MA5_val_sum'][1]<tech_idxes['MA4_val_sum'][1]:
            return True
        else:
            return False
    def f5down4(self, tech_idxes):
        if tech_idxes['MA5_val_sum'][0]<tech_idxes['MA4_val_sum'][0] and tech_idxes['MA5_val_sum'][1]>tech_idxes['MA4_val_sum'][1]:
            return True
        else:
            return False
#====================================stochastics===============================
    def S20up3per(self, tech_idxes): # add new Dary
        # D%3 range <40, current> min+3%
        # 取n天內min比較, n越大，觸發機率越高，但也犧牲進場時機
        if  min(tech_idxes['D_per_a'])<=20 and tech_idxes['D_per_a'][0]<40 and tech_idxes['D_per_a'][0]>min(tech_idxes['D_per_a'])*1.03:
            return True
        else:
            return False
    def S80down3per(self, tech_idxes): # add new Dary
        # D%3 range >60, current> min+3%
        # 取n天內max比較, n越大，觸發機率越高，但也犧牲進場時機
        if  max(tech_idxes['D_per_a'])>=80 and tech_idxes['D_per_a'][0]>60 and tech_idxes['D_per_a'][0]<max(tech_idxes['D_per_a'])*0.97:
            return True
        else:
            return False
    def S80near(self, tech_idxes): # add new Dary
        # 接近超買，並連三天正斜率(確保接近超買強勁)
        if tech_idxes['D_per_a'][0]>=70 and tech_idxes['D_per_a'][0]>tech_idxes['D_per_a'][1] and tech_idxes['D_per_a'][1]>tech_idxes['D_per_a'][2]:
            return True
        else:
            return False
    def S80up(self, tech_idxes):
        if tech_idxes['D_per_a'][0]>=60 and max(tech_idxes['D_per_a']) >= 80:
            return True
        else:
            return False
    def S70up(self, tech_idxes):
        if tech_idxes['D_per_a'][0]>=70:
            return True
        else:
            return False
    def S60up(self, tech_idxes):
        if tech_idxes['D_per_a'][0]>=60:
            return True
        else:
            return False
    def S20near(self, tech_idxes): # add new Dary
        # 接近超賣，並連三天負斜率(確保接近超賣強勁)
        if tech_idxes['D_per_a'][0]<=30 and tech_idxes['D_per_a'][0]<tech_idxes['D_per_a'][1] and tech_idxes['D_per_a'][1]<tech_idxes['D_per_a'][2]:
            return True
        else:
            return False
    def S40down(self, tech_idxes):
        if tech_idxes['D_per_a'][0]<=40:
            return True
        else:
            return False
    def S30down(self, tech_idxes):
        if tech_idxes['D_per_a'][0]<=30:
            return True
        else:
            return False
    def S20down(self, tech_idxes): # add new Dary
        if tech_idxes['D_per_a'][0]<=20:
            return True
        else:
            return False
    def Sgodown(self, tech_idxes):
        # S=n 下彎
        if   tech_idxes['D_per_a'][0]<tech_idxes['D_per_a'][1] and  tech_idxes['D_per_a'][2]<tech_idxes['D_per_a'][1]:
            return True
        else:
            return False
    def Sgoup(self, tech_idxes):
        # S=V 上彎
        if   tech_idxes['D_per_a'][0]>tech_idxes['D_per_a'][1] and  tech_idxes['D_per_a'][2]>tech_idxes['D_per_a'][1]:
            return True
        else:
            return False
    def Sneg(self, tech_idxes):
        # S負斜率
        if   tech_idxes['D_per_a'][0]<tech_idxes['D_per_a'][1]:
            return True
        else:
            return False
    def Spos(self, tech_idxes):
        # S負斜率
        if   tech_idxes['D_per_a'][0]>tech_idxes['D_per_a'][1]:
            return True
        else:
            return False
#====================================MACD===============================
    def M50up(self, tech_idxes): # add new Dary
        # 'per_DIF' 是考量90交易日的DIF百分比, 目前沒有具體百分比化的時間長度，因此以50當做多空分水嶺
        if tech_idxes['per_DIF'][0]>=50:
            return True
        else:
            return False
    def M50down(self, tech_idxes): # add new Dary
        # 'per_DIF' 是考量90交易日的DIF百分比, 目前沒有具體百分比化的時間長度，因此以50當做多空分水嶺
        if tech_idxes['per_DIF'][0]<=50:
            return True
        else:
            return False
    def M60up(self, tech_idxes):
        if tech_idxes['per_DIF'][0]>=60:
            return True
        else:
            return False
    def M80up(self, tech_idxes):
        if tech_idxes['per_DIF'][0]>=80:
            return True
        else:
            return False
    def M40down(self, tech_idxes): # add new Dary
        if tech_idxes['per_DIF'][0]<=40:
            return True
        else:
            return False
    def M20down(self, tech_idxes): # add new Dary
        if tech_idxes['per_DIF'][0]<=20:
            return True
        else:
            return False
    def Mgodown(self, tech_idxes): # add new Dary
        # M=n 下彎
        if   tech_idxes['per_DIF'][0]<tech_idxes['per_DIF'][1] and  tech_idxes['per_DIF'][2]<tech_idxes['per_DIF'][1]:
            return True
        else:
            return False
    def Mgoup(self, tech_idxes): # add new Dary
        # M=V 上彎
        if   tech_idxes['per_DIF'][0]>tech_idxes['per_DIF'][1] and  tech_idxes['per_DIF'][2]>tech_idxes['per_DIF'][1]:
            return True
        else:
            return False
    def Mneg(self, tech_idxes): # add new Dary
        # M負斜率
        if   tech_idxes['per_DIF'][0]<tech_idxes['per_DIF'][1]:
            return True
        else:
            return False
    def Mpos(self, tech_idxes): # add new Dary
        # M正斜率
        if   tech_idxes['per_DIF'][0]>tech_idxes['per_DIF'][1]:
            return True
        else:
            return False
#====================================RSI===============================
    def R30down(self, tech_idxes): # add new Dary
        # RSI<=30
        # 配合背離使用
        if tech_idxes['RSI_result'][0]<=30:
            return True
        else:
            return False
    def R70up(self, tech_idxes): # add new Dary
        # RSI>=70
        # 配合背離使用
        if tech_idxes['RSI_result'][0]>=70:
            return True
        else:
            return False
#====================================vol===============================
    def Vol2MA5(self, tech_idxes): # add new Dary
        if tech_idxes['precent_Vol']>=tech_idxes['V_MA5_val_sum'][0]*2: #V_MA5_val_sum
            return True
        else:
            return False
#====================================deviate===============================
    def dev_split(self, dev,dev_pre): # add new Dary
        '''
        'precent':
        'OSC':'2020-06-17 00:00:00/bull_dev/99.88/4.97/56.07'
        'RSI':'2020-06-22 00:00:00/bull_dev/8.9/2.04/55.82'
        'Sto':'2020-05-28 00:00:00/bear_dev/53.14/0.0/49.09'
        '''
        Date_precent=dev_pre
        split=dev.split('/')
        dev_result_Date=datetime.strptime(split[0], "%Y-%m-%d %H:%M:%S").date()
        dev_result_gain=split[1]
        dev_result_per_dev=float(split[2]) # percent of dev
        dev_result_per_price=float(split[3]) # percent of price
        dev_trggered=(Date_precent-dev_result_Date).days # used for dec trigger
        return [dev_trggered,dev_result_gain,dev_result_per_dev,dev_result_per_price]

    def OSCbeardev(self, tech_idxes): # add new Dary
        # OSC空頭背離, 看bull
        # OSC[0]<=3 當天背離
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'],tech_idxes['dev_dict']['precent'])
        if  OSC[0]<=3 and OSC[1]=='bear_dev' :
            return True
        else:
            return False
    def OSCbulldev(self, tech_idxes): # add new Dary
        # OSC多頭背離, 看bear
        # OSC[0]<=3 當天背離
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'],tech_idxes['dev_dict']['precent'])
        if  OSC[0]<=3 and OSC[1]=='bull_dev' :
            return True
        else:
            return False
    def RSIbeardev(self, tech_idxes): # add new Dary
        # RSI空頭背離, 看bull
        # RSI[0]<=3 當天背離
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'],tech_idxes['dev_dict']['precent'])
        if  RSI[0]<=3 and RSI[1]=='bear_dev' :
            return True
        else:
            return False
    def RSIbulldev(self, tech_idxes): # add new Dary
        # RSI多頭背離, 看bear
        # RSI[0]<=3 當天背離
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'],tech_idxes['dev_dict']['precent'])
        if  RSI[0]<=3 and RSI[1]=='bull_dev' :
            return True
        else:
            return False
    def Sbeardev(self, tech_idxes): # add new Dary
        # sto空頭背離, 看bull
        # sto[0]<=3 當天背離
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'],tech_idxes['dev_dict']['precent'])
        if  Sto[0]<=3 and Sto[1]=='bear_dev' :
            return True
        else:
            return False
    def Sbulldev(self, tech_idxes): # add new Dary
        # sto多頭背離, 看bear
        # sto[0]<=3 當天背離
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'],tech_idxes['dev_dict']['precent'])
        if  Sto[0]<=3 and Sto[1]=='bull_dev' :
            return True
        else:
            return False
    #===============dev percent================
    def OSCdevper4(self, tech_idxes): # add new Dary
        # 背離指數差4%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'],tech_idxes['dev_dict']['precent'])
        if  OSC[2]>=4:
            return True
        else:
            return False
    def RSIdevper4(self, tech_idxes): # add new Dary
        # 背離指數差4%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'],tech_idxes['dev_dict']['precent'])
        if  RSI[2]>=4:
            return True
        else:
            return False
    def Sdevper4(self, tech_idxes): # add new Dary
        # 背離指數差4%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'],tech_idxes['dev_dict']['precent'])
        if  Sto[2]>=4:
            return True
        else:
            return False
    def OSCdevper8(self, tech_idxes): # add new Dary
        # 背離指數差8%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'],tech_idxes['dev_dict']['precent'])
        if  OSC[2]>=8:
            return True
        else:
            return False
    def RSIdevper8(self, tech_idxes): # add new Dary
        # 背離指數差8%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'],tech_idxes['dev_dict']['precent'])
        if  RSI[2]>=8:
            return True
        else:
            return False
    def Sdevper8(self, tech_idxes): # add new Dary
        # 背離指數差8%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'],tech_idxes['dev_dict']['precent'])
        if  Sto[2]>=8:
            return True
        else:
            return False
    #===============dev-price percent================
    def OSCdevprice4(self, tech_idxes): # add new Dary
        # 背離價錢差4%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'],tech_idxes['dev_dict']['precent'])
        if  OSC[3]>=4:
            return True
        else:
            return False
    def RSIdevprice4(self, tech_idxes): # add new Dary
        # 背離價錢差4%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'],tech_idxes['dev_dict']['precent'])
        if  RSI[3]>=4:
            return True
        else:
            return False
    def Sdevprice4(self, tech_idxes): # add new Dary
        # 背離價錢差4%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'],tech_idxes['dev_dict']['precent'])
        if  Sto[3]>=4:
            return True
        else:
            return False
    def OSCdevprice8(self, tech_idxes): # add new Dary
        # 背離價錢差8%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'],tech_idxes['dev_dict']['precent'])
        if  OSC[3]>=8:
            return True
        else:
            return False
    def RSIdevprice8(self, tech_idxes): # add new Dary
        # 背離價錢差8%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'],tech_idxes['dev_dict']['precent'])
        if  RSI[3]>=8:
            return True
        else:
            return False
    def Sdevprice8(self, tech_idxes): # add new Dary
        # 背離價錢差8%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'],tech_idxes['dev_dict']['precent'])
        if  Sto[3]>=8:
            return True
        else:
            return False
#====================================deviate_con===============================
    def Ddevbear_NA_1(self, tech_idxes): # D%空頭背離, bull
        # 
        if self.Sbeardev(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbear_NA_2(self, tech_idxes): # D%空頭背離+D%<=30, bull
        # 
        if self.Sbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbear_NA_3(self, tech_idxes): # D%空頭背離+D%<=30+delta_price_dec>=4, bull
        # 
        if self.Sbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.Sdevper4(tech_idxes)==True and self.Sdevprice4(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbear_NA_4(self, tech_idxes): # D%空頭背離+D%<=30+delta_price_dec>=8, bull
        # 
        if self.Sbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.Sdevper8(tech_idxes)==True and self.Sdevprice8(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbear_WDbull_40(self, tech_idxes): # D%空頭背離+D%<=30+W:白>藍 D:白(NA斜率)>藍, bull
        # 
        if self.Sbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.Sdevper8(tech_idxes)==True and self.Sdevprice8(tech_idxes)==True and self.f40bigger80_D(tech_idxes)==True and self.f40bigger80_W(tech_idxes)==True: 
            return True
        else:
            return False

    def Ddevbull_NA_5(self, tech_idxes): # D%多頭背離, bear
        # 
        if self.Sbulldev(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbull_NA_6(self, tech_idxes): # D%多頭背離+D%>=70, bear
        # 
        if self.Sbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbull_NA_7(self, tech_idxes): # D%多頭背離+D%>=70+delta_price_dec>=4, bear
        # 
        if self.Sbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.Sdevper4(tech_idxes)==True and self.Sdevprice4(tech_idxes)==True: 
            return True
        else:
            return False
    def Ddevbull_NA_8(self, tech_idxes): # D%多頭背離+D%>=70+delta_price_dec>=8, bear
        # 
        if self.Sbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.Sdevper8(tech_idxes)==True and self.Sdevprice8(tech_idxes)==True: 
            return True
        else:
            return False

    def OSCdevbear_NA_9(self, tech_idxes): # OSC空頭背離, bull
        # 
        if self.OSCbeardev(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbear_NA_10(self, tech_idxes): # OSC空頭背離+RSI<=30, bull
        # 
        if self.OSCbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbear_NA_11(self, tech_idxes): # OSC空頭背離+RSI<=30+delta_price_dec>=4, bull
        # 
        if self.OSCbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.OSCdevper4(tech_idxes)==True and self.OSCdevprice4(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbear_NA_12(self, tech_idxes): # OSC空頭背離+RSI<=30+delta_price_dec>=8, bull
        # 
        if self.OSCbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.OSCdevper8(tech_idxes)==True and self.OSCdevprice8(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbear_WDbull_41(self, tech_idxes): # OSC空頭背離+RSI<=30+W:白>藍 D:白(NA斜率)>藍, bull
        # 
        if self.OSCbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.OSCdevper8(tech_idxes)==True and self.OSCdevprice8(tech_idxes)==True and self.f40bigger80_D(tech_idxes)==True and self.f40bigger80_W(tech_idxes)==True: 
            return True
        else:
            return False

    def OSCdevbull_NA_13(self, tech_idxes): # OSC多頭背離, bear
        # 
        if self.OSCbulldev(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbull_NA_14(self, tech_idxes): # OSC多頭背離+RSI>=70, bear
        # 
        if self.OSCbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbull_NA_15(self, tech_idxes): # OSC多頭背離+RSI>=70+delta_price_dec>=4, bear
        # 
        if self.OSCbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.OSCdevper4(tech_idxes)==True and self.OSCdevprice4(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbull_NA_16(self, tech_idxes): # OSC多頭背離+RSI>=70+delta_price_dec>=8, bear
        # 
        if self.OSCbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.OSCdevper8(tech_idxes)==True and self.OSCdevprice8(tech_idxes)==True: 
            return True
        else:
            return False
    def OSCdevbull_WDbear_42(self, tech_idxes): # OSC多頭背離+RSI>=70+W:白<藍 D:白(NA斜率)<藍, bear
        # 
        if self.OSCbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.OSCdevper8(tech_idxes)==True and self.OSCdevprice8(tech_idxes)==True and self.f40smaller80_D(tech_idxes)==True and self.f40smaller80_W(tech_idxes)==True: 
            return True
        else:
            return False

    def RSIdevbear_NA_17(self, tech_idxes): # RSI空頭背離, bull
        # 
        if self.RSIbeardev(tech_idxes)==True: 
            return True
        else:
            return False
    def RSIdevbear_NA_18(self, tech_idxes): # RSI空頭背離+RSI<=30, bull
        # 
        if self.RSIbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True: 
            return True
        else:
            return False
    def RSIdevbear_NA_19(self, tech_idxes): # RSI空頭背離+RSI<=30+delta_price_dec>=4, bull
        # 
        if self.RSIbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.RSIdevper4(tech_idxes)==True and self.RSIdevprice4(tech_idxes)==True: 
            return True
        else:
            return False
    def RSIdevbear_NA20(self, tech_idxes): # RSI空頭背離+RSI<=30+delta_price_dec>=8, bull
        # 
        if self.RSIbeardev(tech_idxes)==True and self.S30down(tech_idxes)==True and self.RSIdevper8(tech_idxes)==True and self.RSIdevprice8(tech_idxes)==True: 
            return True
        else:
            return False

    def RSIdevbull_NA_21(self, tech_idxes): # OSC多頭背離, bear
        # 
        if self.RSIbulldev(tech_idxes)==True: 
            return True
        else:
            return False
    def RSIdevbull_NA_22(self, tech_idxes): # OSC多頭背離+RSI>=70, bear
        # 
        if self.RSIbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True: 
            return True
        else:
            return False
    def RSIdevbull_NA_23(self, tech_idxes): # OSC多頭背離+RSI>=70+delta_price_dec>=4, bear
        # 
        if self.RSIbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.RSIdevper4(tech_idxes)==True and self.RSIdevprice4(tech_idxes)==True: 
            return True
        else:
            return False
    def RSIdevbull_NA_24(self, tech_idxes): # OSC多頭背離+RSI>=70+delta_price_dec>=8, bear
        # 
        if self.RSIbulldev(tech_idxes)==True and self.S70up(tech_idxes)==True and self.RSIdevper8(tech_idxes)==True and self.RSIdevprice8(tech_idxes)==True: 
            return True
        else:
            return False

    def devbull_all(self, tech_idxes): # 任一多頭背離發生
        # 
        if self.Ddevbull_NA_5(tech_idxes)==True or self.Ddevbull_NA_6(tech_idxes)==True or self.Ddevbull_NA_7(tech_idxes)==True or self.Ddevbull_NA_8(tech_idxes)==True \
            or self.OSCdevbull_NA_13(tech_idxes)==True or self.OSCdevbull_NA_14(tech_idxes)==True or self.OSCdevbull_NA_15(tech_idxes)==True \
                or self.OSCdevbull_NA_16(tech_idxes)==True or self.OSCdevbull_WDbear_42(tech_idxes)==True or self.RSIdevbull_NA_21(tech_idxes)==True \
                     or self.RSIdevbull_NA_22(tech_idxes)==True or self.RSIdevbull_NA_23(tech_idxes)==True or self.RSIdevbull_NA_24(tech_idxes)==True: 
            return True
        else:
            return False
    def devbear_all(self, tech_idxes): # 任一空頭背離發生
        # 
        if self.Ddevbear_NA_1(tech_idxes)==True or self.Ddevbear_NA_2(tech_idxes)==True or self.Ddevbear_NA_3(tech_idxes)==True or self.Ddevbear_NA_4(tech_idxes)==True \
            or self.Ddevbear_WDbull_40(tech_idxes)==True or self.OSCdevbear_NA_9(tech_idxes)==True or self.OSCdevbear_NA_10(tech_idxes)==True \
                or self.OSCdevbear_NA_11(tech_idxes)==True or self.OSCdevbear_NA_12(tech_idxes)==True or self.RSIdevbear_NA_17(tech_idxes)==True \
                     or self.RSIdevbear_NA_18(tech_idxes)==True or self.RSIdevbear_NA_19(tech_idxes)==True or self.RSIdevbear_NA20(tech_idxes)==True: 
            return True
        else:
            return False

#====================================BT_items===============================   
    # ======反三合一         
    def Trin_NA_31(self, tech_idxes): # 不分市場&反三合一
        # ["S80down3per","M50up","f5down4"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True : 
            return True
        else:
            return False
    def Trin_WDBull_33(self, tech_idxes): # W/D牛市&反三合一
        # ["S80down3per","M50up","f5down4","f40bigger80_D","f40bigger80_W"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40bigger80_D(tech_idxes)==True and self.f40bigger80_W(tech_idxes)==True: 
            return True
        else:
            return False
    def Trin_WDBear_35(self, tech_idxes): # W/D熊市&反三合一
        # ["S80down3per","M50up","f5down4","f40smaller80_D","f40smaller80_W"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40smaller80_D(tech_idxes)==True and self.f40smaller80_W(tech_idxes)==True: 
            return True
        else:
            return False
    def Trin_DBull_37(self, tech_idxes): # D牛市&反三合一
        # ["S80down3per","M50up","f5down4","f40bigger80_D"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40bigger80_D(tech_idxes)==True: 
            return True
        else:
            return False
    def Trin_DBear_39(self, tech_idxes): # D熊市&反三合一
        # ["S80down3per","M50up","f5down4","f40bigger80_D"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40smaller80_D(tech_idxes)==True: 
            return True
        else:
            return False
    # ======正三合一         
    def TriV_NA_30(self, tech_idxes): # 不分市場&正三合一
        # ["S20up3per","M50down","f5up4"]
        if self.S20up3per(tech_idxes)==True and self.M50down(tech_idxes)==True and self.f5up4(tech_idxes)==True: 
            return True
        else:
            return False
    def TriV_WDBull_32(self, tech_idxes): # W/D牛市&正三合一
        # ["S20up3per","M50down","f5up4","f40bigger80_D","f40bigger80_W"]
        if self.S20up3per(tech_idxes)==True and self.M50down(tech_idxes)==True and self.f5up4(tech_idxes)==True and self.f40bigger80_D(tech_idxes)==True and self.f40bigger80_W(tech_idxes)==True: 
            return True
        else:
            return False
    def TriV_WDBear_34(self, tech_idxes): # W/D熊市&正三合一
        # ["S80down3per","M50up","f5down4","f40smaller80_D","f40smaller80_W"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40smaller80_D(tech_idxes)==True and self.f40smaller80_W(tech_idxes)==True: 
            return True
        else:
            return False
    def TriV_DBull_36(self, tech_idxes): # D牛市&正三合一
        # ["S80down3per","M50up","f5down4","f40bigger80_D"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40bigger80_D(tech_idxes)==True: 
            return True
        else:
            return False
    def TriV_DBear_38(self, tech_idxes): # D熊市&正三合一
        # ["S80down3per","M50up","f5down4","f40bigger80_D"]
        if self.S80down3per(tech_idxes)==True and self.M50up(tech_idxes)==True and self.f5down4(tech_idxes)==True and self.f40smaller80_D(tech_idxes)==True: 
            return True
        else:
            return False
    # ======白上跨藍        
    def WupB_NA_26(self, tech_idxes): # FAvg40 cross Favg80 up
        # ["f40up80"]
        if self.f40up80(tech_idxes)==True: 
            return True
        else:
            return False
    def WupB_W_28(self, tech_idxes): # FAvg40 cross Favg80 up and weekly_MA40>weekly_MA80
        # ["f40up80","f40bigger80_W"]
        if self.f40up80(tech_idxes)==True and self.f40bigger80_W(tech_idxes)==True: 
            return True
        else:
            return False
    # ======白下跨藍        
    def WdownB_NA_27(self, tech_idxes): # FAvg40 cross Favg80 down
        # ["f40down80"]
        if self.f40down80(tech_idxes)==True: 
            return True
        else:
            return False
    def WdownB_W_29(self, tech_idxes): # FAvg40 cross Favg80 down and weekly_MA40<weekly_MA80
        # ["f40down80","f40smaller80_W"]
        if self.f40down80(tech_idxes)==True and self.f40smaller80_W(tech_idxes)==True: 
            return True
        else:
            return False