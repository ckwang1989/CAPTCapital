import Stock_history
import Technical_index
import IV_HV
import BB

def main():  
    A=Stock_history.sum()
    B=Technical_index.sum()
    F=BB.sum()
    G=IV_HV.sum()

    Stock_name='SPY'
    df=A.Stock_price(Stock_name)

    weekly_dict=B.MACD_weekly_check(df,Stock_name, 26, 570*1, period=5, back_ornot=0, weekly_BT=0) # get weekly data_570Weeks
    daily_dict=B.MACD_weekly_check(df,Stock_name, 26, 570*1, period=1, back_ornot=0, weekly_BT=weekly_dict['weekly_BT']) # get daily data_570days

    # input DTE, output: std_Dev of out_BB, which include all High/Low price(DTE)
    BB_dict=F.bollinger_bands(df, DTE=60, lookback=20, numsd=2) # price,DTE,BB中心均線(fix),內BB標準差

    IV_HV_dict=G.IV_HV(Stock_name)

    pass

if __name__ == '__main__':
    main()
