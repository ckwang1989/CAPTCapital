from yahoo_earnings_calendar import YahooEarningsCalendar

class sum():
    def earning_get(self,stock_name):
        #===================================================get earning date
        try:
            yec = YahooEarningsCalendar()
            try:
                sec_earning=yec.get_next_earnings_date(stock_name)
                ear=datetime.fromtimestamp(sec_earning).strftime("%b %d %Y")
                ear_year=ear.split(' ')[2]
            except:
                ear=finviz.get_stock(stock_name)['Earnings']
                

            ear_mon=ear.split(' ')[0]
            ear_day=ear.split(' ')[1]
            
            # ear_status=ear.split(' ')[2]
            ear_mon=list(calendar.month_abbr).index(ear_mon) # Eng to number of month
        except:
            ear_year='NA'
            ear_mon='NA'
            ear_day='NA'
            ear_status='NA'
        #===================================================get earning date
        sum_earning='%s %s %s'%(ear_year,ear_mon,ear_day)
        return sum_earning