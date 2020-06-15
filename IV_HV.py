import requests
# import pandas as pd
from bs4 import BeautifulSoup
import time
# import re

class sum():
    def IV_HV(self, stock_nam): #

        # ==============Exchange==============
        #  AMEX: NYSEAN
        # NASD: NASDAQ
        # NYSE: NYSE
        # https://oic.ivolatility.com/oic_options.j;jsessionid=bOxhYZXCIBEe?ticker=AMD%3ANASDAQ&R=1
        for password in ['a4aVeOaOsH97','bOxhYZXCIBEe','bnvKABxYIAee','asAaERwoziH4']:
            for exchange in ['NYSE','NYSEAN','NASDAQ','NYSEArca']:
                url = 'https://oic.ivolatility.com/oic_options.j;jsessionid=%s?ticker=%s3A%s&R=1'%(password,stock_nam+ '%',exchange)

                    # https://oic.ivolatility.com/oic_options.j;jsessionid=a4aVeOaOsH97?ticker=AMD%3ANASDAQ&R=1
                try:
                    response = requests.get(url)#, timeout=0.1)
                    # print(response)
                # DNS lookup failure
                except requests.exceptions.ConnectionError as e:
                    print('''%s-Webpage doesn't seem to exist!\n%s''' %(stock_nam,e) )
                    pass
                # Timeout failure
                except requests.exceptions.ConnectTimeout as e:
                    print('''%s-Slow connection!\n%s''' %(stock_nam,e))
                    pass
                # HTTP error
                except requests.exceptions.HTTPError as e:
                    print('''%s-HTTP error!\n%s''' %(stock_nam,e))
                    pass

                # Get webpage content
                try:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    check=soup.text
                    if "You may give each page an identifying name" in check :
                        pass # exchange is wrong
                    elif "Your session is expired, please continue here" in check:
                        break
                    else:
                        break
                except:
                    pass
                
        HV_days_10=soup.text.split('\n\n\n10 days')[1].split('\n\n\n20 days')[0]
        HV_days_10_curr=float(HV_days_10.split('%')[0])
        HV_days_10_W=float(HV_days_10.split('%')[1])
        HV_days_10_Hi=float(HV_days_10.split('%')[2])
        temp=HV_days_10.split('%')[3].split('-')[2].split('%')[0]
        HV_days_10_low=float(temp.replace(''.join([x for x in temp if x.isalpha()]),""))

        HV_days_20=soup.text.split('\n\n\n20 days')[1].split('\n\n\n30 days')[0] 
        HV_days_20_curr=float(HV_days_20.split('%')[0])
        HV_days_20_W=float(HV_days_20.split('%')[1])
        HV_days_20_Hi=float(HV_days_20.split('%')[2])
        temp=HV_days_20.split('%')[3].split('-')[2].split('%')[0]
        HV_days_20_low=float(temp.replace(''.join([x for x in temp if x.isalpha()]),""))
        
        HV_days_30=soup.text.split('\n\n\n30 days')[1].split('\n\n\n\xa0\xa0IMPLIED VOLATILITY')[0] 
        HV_days_30_curr=float(HV_days_30.split('%')[0])
        HV_days_30_W=float(HV_days_30.split('%')[1])
        HV_days_30_Hi=float(HV_days_30.split('%')[2])
        temp=HV_days_30.split('%')[3].split('-')[2].split('%')[0]
        HV_days_30_low=float(temp.replace(''.join([x for x in temp if x.isalpha()]),""))

        IV_call=soup.text.split('Index call\xa0')[1].split('Index put\xa0')[0]
        IV_call_curr=float(IV_call.split('%')[0])
        IV_call_W=float(IV_call.split('%')[1])
        IV_call_Hi=float(IV_call.split('%')[2])
        temp=IV_call.split('%')[3].split('-')[2].split('%')[0]
        IV_call_low=float(temp.replace(''.join([x for x in temp if x.isalpha()]),""))

        IV_put=soup.text.split('Index put\xa0')[1].split('Index mean\xa0')[0]
        IV_put_curr=float(IV_put.split('%')[0])
        IV_put_W=float(IV_put.split('%')[1])
        IV_put_Hi=float(IV_put.split('%')[2])
        temp=IV_put.split('%')[3].split('-')[2].split('%')[0]
        IV_put_low=float(temp.replace(''.join([x for x in temp if x.isalpha()]),""))

        IV_index_mean=soup.text.split('Index mean\xa0')[1].split('\n\n\nHISTORICAL 30-DAYS CORRELATION AGAINST')[0]
        IV_index_mean_curr=float(IV_index_mean.split('%')[0])
        IV_index_mean_W=float(IV_index_mean.split('%')[1])
        IV_index_mean_Hi=float(IV_index_mean.split('%')[2])
        temp=IV_index_mean.split('%')[3].split('-')[2].split('%')[0]
        IV_index_mean_low=float(temp.replace(''.join([x for x in temp if x.isalpha()]),""))

        #=====normalized: one year
        HV_10_n=round(HV_days_10_curr*50/((HV_days_10_Hi+HV_days_10_low)/2),2)
        HV_20_n=round(HV_days_20_curr*50/((HV_days_20_Hi+HV_days_20_low)/2),2)
        HV_30_n=round(HV_days_30_curr*50/((HV_days_30_Hi+HV_days_30_low)/2),2)
        # 10 days,20 days, 30days
        HV_n={'10day_n':HV_10_n,'20day_n':HV_20_n,'30day_n':HV_30_n}
        HV={'10day':HV_days_10_curr,'20day':HV_days_20_curr,'30day':HV_days_30_curr}
        # call,put,mean
        IV_call_n=round(IV_call_curr*50/((IV_call_Hi+IV_call_low)/2),2)
        IV_put_n=round(IV_put_curr*50/((IV_put_Hi+IV_put_low)/2),2)
        IV_index_mean_n=round(IV_index_mean_curr*50/((IV_index_mean_Hi+IV_index_mean_low)/2),2)
        IV_n={'call_n':IV_call_n,'put_n':IV_put_n,'mean_n':IV_index_mean_n}
        IV={'call':IV_call_curr,'put':IV_put_curr,'mean':IV_index_mean_curr}

        time.sleep(0.05)
        #=======build dict from list
        list_input=['HV','IV','HV_n','IV_n']
        dict_input={}
        for name in list_input:
            dict_input[name]=locals()[name]
        dict_sum=dict_input

        return dict_sum # HV/IV : current, HV_n/IV_n : normalized one year

# if __name__ == '__main__':
#     sum().IV_HV('TDOC')