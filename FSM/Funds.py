import sys
sys.path.append('./')

from Stonks import Stonks
import pandas as pd
import math

class Funds(Stonks):
    def __init__(self, csv, fundstable_csv, timeframe=56):
        super().__init__(csv, timeframe)
        self.fundstable_csv = fundstable_csv

    #daily dividend yield of funds
    def daily_fund_dividends(self, stock):
        #clean up funds table          
        fundstable_csv = self.fundstable_csv
        fundstable_csv = pd.read_csv(fundstable_csv)
        fundstable_csv = fundstable_csv.fillna('0%')
        fundstable_csv['Fund Name'] = fundstable_csv['Fund Name'].str.strip()
        fundstable_csv = fundstable_csv.set_index('Fund Name')
        annual_dividend = fundstable_csv.loc[stock,'Indicated Gross <br\/> Dividend Yield* (%)']

        #convert annual yield value to daily float
        annual_dividend = float(annual_dividend.replace("%",""))
        daily_dividend = float(annual_dividend)/253
        return daily_dividend

    #calculate risk and returns of a stock but with an option to include dividends from funds
    def riskreturn(self, stock1, include_dividends=False):
        timeframe = self.timeframe
        stock = self.pricehistory(stock1)
        series = pd.Series([], dtype='float64')
        returns_list = pd.Series([], dtype='float64')

        #calculations
        if len(stock) == timeframe:
            # loop through prices 
            for i in range(int(timeframe - 1)):
                n = int(i + 1)
                Cn1 = stock[n]  
                Cn = stock[i]
                returns_ratio = pd.Series([(Cn1-Cn)/Cn])
                returns_list = returns_list.append(returns_ratio)
                ln_returns = pd.Series([math.log(Cn1/Cn)])
                series = series.append(ln_returns)
                average_returns1 = returns_list.mean()
                volatiliity1 = series.std()

            if include_dividends == True:
                dividend = self.daily_fund_dividends(stock1)/100
                average_returns1 = average_returns1 + dividend

            return stock1,average_returns1,volatiliity1
        else:
            average_returns1, volatiliity1 = 0,0
            return stock1,average_returns1,volatiliity1
    

if __name__ == "__main__":
    b = Funds("FSM/PriceHistory/fsm-pricehistory-2021-05-23.csv", "FSM/FundsTable/export(1622864030092).csv")
    fund = "JPMorgan Investment Funds - Global Income A (div) SGD-H"

    #test daily_fund_dividends function
    daily_dividends = b.daily_fund_dividends(fund)
    print(f"Daily dividend yield of {fund} is {daily_dividends}%\n")

    #test riskreturn function without dividends included
    fund, returns, risk = b.riskreturn(fund)
    print(f"Risk of {fund} without dividends included is {risk}")
    print(f"Return of {fund} without dividends included is {returns}\n")

    #test risk return function with dividends included
    fund, returns, risk = b.riskreturn(fund, include_dividends=True)
    print(f"Risk of {fund} with dividends included is {risk}")
    print(f"Return of {fund} with dividends included is {returns}\n")