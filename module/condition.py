class Condition:
#====================================MA===============================
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
    def S20near(self, tech_idxes): # add new Dary
        # 接近超賣，並連三天負斜率(確保接近超賣強勁)
        if tech_idxes['D_per_a'][0]<=30 and tech_idxes['D_per_a'][0]<tech_idxes['D_per_a'][1] and tech_idxes['D_per_a'][1]<tech_idxes['D_per_a'][2]:
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
    def M70up(self, tech_idxes):
        if tech_idxes['per_DIF'][0]>=70:
            return True
        else:
            return False
    def M80up(self, tech_idxes):
        if tech_idxes['per_DIF'][0]>=80:
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
    def dev_split(self, dev): # add new Dary
        '''
        'OSC':'2020-06-17 00:00:00/bull_dev/99.88/4.97/56.07'
        'RSI':'2020-06-22 00:00:00/bull_dev/8.9/2.04/55.82'
        'Sto':'2020-05-28 00:00:00/bear_dev/53.14/0.0/49.09'
        '''
        split=dev.split('/')
        dev_result_Date=datetime.strptime(split[0], "%Y-%m-%d %H:%M:%S").date()
        dev_result_gain=split[1]
        dev_result_per_dev=float(split[2]) # percent of dev
        dev_result_per_price=float(split[3]) # percent of price
        dev_trggered=(Date_precent-dev_result_Date).days # used for dec trigger
        return [dev_trggered,dev_result_gain,dev_result_per_dev,dev_result_per_price]

    def OSCbeardev(self, tech_idxes): # add new Dary
        # OSC空頭背離, 看bull
        # OSC[0]==0 當天背離
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'])
        if  OSC[0]==0 and OSC[1]=='bear_dev' :
            return True
        else:
            return False
    def OSCbulldev(self, tech_idxes): # add new Dary
        # OSC多頭背離, 看bear
        # OSC[0]==0 當天背離
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'])
        if  OSC[0]==0 and OSC[1]=='bull_dev' :
            return True
        else:
            return False
    def Rbeardev(self, tech_idxes): # add new Dary
        # RSI空頭背離, 看bull
        # RSI[0]==0 當天背離
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'])
        if  RSI[0]==0 and RSI[1]=='bear_dev' :
            return True
        else:
            return False
    def Rbulldev(self, tech_idxes): # add new Dary
        # RSI多頭背離, 看bear
        # RSI[0]==0 當天背離
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'])
        if  RSI[0]==0 and RSI[1]=='bull_dev' :
            return True
        else:
            return False
    def Sbeardev(self, tech_idxes): # add new Dary
        # sto空頭背離, 看bull
        # sto[0]==0 當天背離
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'])
        if  Sto[0]==0 and Sto[1]=='bear_dev' :
            return True
        else:
            return False
    def Sbulldev(self, tech_idxes): # add new Dary
        # sto多頭背離, 看bear
        # sto[0]==0 當天背離
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'])
        if  Sto[0]==0 and Sto[1]=='bull_dev' :
            return True
        else:
            return False
    #===============dev percent================
    def OSCdevper4(self, tech_idxes): # add new Dary
        # 背離指數差4%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'])
        if  OSC[2]>=4:
            return True
        else:
            return False
    def RSIdevper4(self, tech_idxes): # add new Dary
        # 背離指數差4%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'])
        if  RSI[2]>=4:
            return True
        else:
            return False
    def Sdevper4(self, tech_idxes): # add new Dary
        # 背離指數差4%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'])
        if  Sto[2]>=4:
            return True
        else:
            return False
    def OSCdevper8(self, tech_idxes): # add new Dary
        # 背離指數差8%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'])
        if  OSC[2]>=8:
            return True
        else:
            return False
    def RSIdevper8(self, tech_idxes): # add new Dary
        # 背離指數差8%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'])
        if  RSI[2]>=8:
            return True
        else:
            return False
    def Sdevper8(self, tech_idxes): # add new Dary
        # 背離指數差8%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'])
        if  Sto[2]>=8:
            return True
        else:
            return False
    #===============dev-price percent================
    def OSCdevprice4(self, tech_idxes): # add new Dary
        # 背離價錢差4%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'])
        if  OSC[3]>=4:
            return True
        else:
            return False
    def RSIdevprice4(self, tech_idxes): # add new Dary
        # 背離價錢差4%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'])
        if  RSI[3]>=4:
            return True
        else:
            return False
    def Sdevprice4(self, tech_idxes): # add new Dary
        # 背離價錢差4%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'])
        if  Sto[3]>=4:
            return True
        else:
            return False
    def OSCdevprice8(self, tech_idxes): # add new Dary
        # 背離價錢差8%
        OSC=self.dev_split(tech_idxes['dev_dict']['OSC'])
        if  OSC[3]>=8:
            return True
        else:
            return False
    def RSIdevprice8(self, tech_idxes): # add new Dary
        # 背離價錢差8%
        RSI=self.dev_split(tech_idxes['dev_dict']['RSI'])
        if  RSI[3]>=8:
            return True
        else:
            return False
    def Sdevprice8(self, tech_idxes): # add new Dary
        # 背離價錢差8%
        Sto=self.dev_split(tech_idxes['dev_dict']['Sto'])
        if  Sto[3]>=8:
            return True
        else:
            return False