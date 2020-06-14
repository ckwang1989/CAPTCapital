import Stock_history
import Technical_index
import IV_HV

def main():  
    A=Stock_history.sum()
    B=Technical_index.sum()
    G=IV_HV.sum()

    Stock_name='AMD'
    df=A.Stock_price(Stock_name)
    
    daily_dict=B.MACD_weekly_check(df,Stock_name, 26, 570, period=1, back_ornot=0) # get daily data_570days
    daily_dict=B.MACD_weekly_check(df,Stock_name, 26, 570, period=5, back_ornot=0) # get weekly data_570Weeks

    IV_HV_dict=G.IV_HV(Stock_name)

    pass

if __name__ == '__main__':
    main()
