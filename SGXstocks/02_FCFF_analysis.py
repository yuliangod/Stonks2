import sys
sys.path.append('./')

from Stonks import Stonks
from sgxscraper import sgx_scraper
import pandas as pd
from currency_converter import CurrencyConverter

def main(stock, csv, year, timeframe=100, corrected_beta=0.5):
    a = Stonks(csv=csv, timeframe=timeframe)
    #get financial statements of stock
    IS, BS, CF, currency = sgx_scraper(stock)
    print(f"{stock} reports its financial statements in {currency}")

    #set up dataframe
    fcff_df = pd.DataFrame()
    fcff_df['Ticker'] = stock
    fcff_df = fcff_df.set_index(['Ticker'])

    #get revenue
    revenue = float(IS.loc['Revenue', year])
    fcff_df.loc[(stock),'Revenue'] = revenue

    #get net income
    net_income = float(IS.loc['Net Income', year])
    fcff_df.loc[(stock),'Net Income'] = net_income

    #get total equity
    total_equity = float(BS.loc['Total Equity', year])
    fcff_df.loc[(stock),'Total Equity'] = total_equity

    #get total debt
    total_debt = float(BS.loc['Total Debt', year])
    fcff_df.loc[(stock),'Total debt'] = total_debt

    #get leveled beta
    beta = a.Beta(stock, index="^STI")
    if beta < 0:    #change beta to a positive number if it is negative
        beta = corrected_beta

    BL = a.BL(beta, total_debt, total_equity)
    fcff_df.loc[(stock),'BL'] = BL

    #get cost of equity
    cost_of_equity = a.cost_of_equity(BL)
    fcff_df.loc[(stock),'Cost of equity'] = cost_of_equity

    #get market value of equity
    shares_outstanding = float(BS.loc['Total Common Shares Outstanding', year])
    latest_price = list(a.pricehistory(stock))[-1]
    market_value_of_equity = shares_outstanding * latest_price

    #get CDS
    IE = float(IS.loc['Interest Inc.(Exp.),Net-Non-Op., Total', year])  * -1
    if IE == 0:
        IE = 0.00001
    EBIT = float(IS.loc['Operating Income', year])
    stock_ICR = EBIT/IE     #interest coverage ratio
    CDS = a.CDS(market_value_of_equity*(10**6), stock_ICR)     
    fcff_df.loc[(stock),'Company Default Spread'] = CDS

    CC = CurrencyConverter()
    cap = CC.convert(market_value_of_equity, 'SGD', currency)  #convert market cap to currency financials are reported in
    fcff_df.loc[(stock),'Market value of equity'] = market_value_of_equity

    #get cost of debt
    cost_of_debt = a.cost_of_debt(CDS)
    fcff_df.loc[(stock),'Cost of debt'] = cost_of_debt 

    #get market value of debt
    market_value_of_debt = total_debt + IE
    fcff_df.loc[(stock),'Market value of debt'] = market_value_of_debt

    #get corporate tax rate
    Tc = float(IS.loc['Provision for Income Taxes', year])/float(IS.loc['Net Income Before Taxes', year])
    fcff_df.loc[(stock),'Corporate tax rate'] = Tc

    #calculate wacc
    wacc = a.wacc(cost_of_equity, cost_of_debt, market_value_of_equity, market_value_of_debt, Tc)
    fcff_df.loc[(stock),'WACC'] = wacc

    #calculate averaged fcff
    fcff_list = pd.Series([], dtype='float64')

    for year in list(IS.columns):  
        EBIT = float(IS.loc['Operating Income', year])
        CapEx = float(CF.loc['Capital Expenditures', year])
        Depreciation = float(CF.loc['Depreciation/Depletion', year])
        non_cashItems = float(CF.loc['Non-Cash Items', year])
        workingCapital = float(CF.loc['Changes in Working Capital', year])
        fcff = pd.Series([a.fcff(EBIT,Tc, CapEx, Depreciation, non_cashItems, workingCapital)])
        fcff_list = fcff_list.append(fcff)

    fcff_avg = fcff_list.mean()
    fcff_df.loc[(stock),'FCFF'] = fcff_avg

    #calculate expected growth rate
    expected_growth_rate_list = pd.Series([], dtype='float64')

    for year in list(IS.columns)[1:]:  
        #calculate reinvestment rate with data from previous year
        CapEx_prev = float(CF.loc['Capital Expenditures', str(round(float(year)) - 1)])
        Depreciation_prev = float(CF.loc['Depreciation/Depletion', str(round(float(year)) - 1)])
        non_cashItems_prev = float(CF.loc['Non-Cash Items', str(round(float(year)) - 1)])

        NetCapEx_prev = CapEx_prev + Depreciation_prev + non_cashItems_prev
        workingCapital_prev = float(CF.loc['Changes in Working Capital', str(round(float(year)) - 1)])
        EBIT_prev = float(IS.loc['Operating Income', str(round(float(year)) - 1)])
        Tc_prev = float(IS.loc['Provision for Income Taxes', str(round(float(year)) - 1)])/float(IS.loc['Net Income Before Taxes', str(round(float(year)) - 1)])

        reinvestment_rate = (NetCapEx_prev - workingCapital_prev)/(EBIT_prev*(1-Tc_prev))

        #calculate return on capital
        cash = float(BS.loc['Cash', year])
        ROC = (EBIT*(1 - Tc))/(total_equity + total_debt - cash)

        #calculate expected growth rate
        expected_growth_rate = pd.Series([reinvestment_rate * ROC])
        expected_growth_rate_list = expected_growth_rate_list.append(expected_growth_rate)

    expected_growth_rate_avg = expected_growth_rate_list.mean()
    fcff_df.loc[(stock),'Expected growth rate'] = expected_growth_rate_avg

    #calculate terminal value
    
    EBIT_avg = IS.loc['Operating Income',:].astype("float64").mean()
    EBIT_t5 = EBIT_avg*(1 + expected_growth_rate)**5

    v0 = float((EBIT_t5*(1-Tc)*(1-(0.01559/ROC)))/(wacc - 0.01559))
    fcff_df.loc[(stock),'Terminal value'] = v0

    #project FCFF
    projected_FCFF = v0
    for i in range(1,5):
        FCFF_t = (fcff*(1 + expected_growth_rate)**i)/((1+wacc)**i)
        projected_FCFF += float(FCFF_t)
    fcff_df.loc[(stock),'Present value of FCFF'] = projected_FCFF 

    #calculate fair value
    shares_outstanding = float(BS.loc['Total Common Shares Outstanding', year])
    fcff_df.loc[(stock),'Shares outstanding'] = shares_outstanding
    fair_value = projected_FCFF/shares_outstanding

    fair_value = CC.convert(fair_value, currency, 'SGD')  #convert fair value back to sgd
    fcff_df.loc[(stock),'Fair value'] = fair_value

    #calculate percentage undervalued
    latest_price = list(a.pricehistory(stock))[-1]
    percentage_undervalued = (1 - (latest_price/fair_value))*100
    fcff_df.loc[stock,'Percentage undervalued'] = percentage_undervalued

    #create index again to include percentage undervalued as an index
    fcff_df['Ticker'] = stock
    fcff_df = fcff_df.set_index(['Ticker', 'Percentage undervalued', 'Fair value'])

    print(fcff_df)
    return fcff_df

def fcff_analysis(csv, year, timeframe=100, corrected_beta=0.5):
    #set up dataframes before processing
    priceHist_df = pd.read_csv(csv)
    tickers_list = list(priceHist_df.columns)

    df = pd.DataFrame()     #empty dataframe to append to 
    failed_tickers = []     #list to display which tickers failed
    successful_tickers = [] #list to show succesful tickers

    #loop main function through tickers in csv file
    for ticker in tickers_list[1:]:   
      try:
        print(f"Analysing {ticker}")
        fcff_df = main(ticker, csv, year, timeframe=timeframe, corrected_beta=corrected_beta)
        df = df.append(fcff_df)
        print(f"Done analysing {ticker}, index is {tickers_list.index(ticker)}\n")
        successful_tickers.append(ticker)   

      except Exception: 
        failed_tickers.append(ticker)
        print(f"The program could not analyse these tickers: {failed_tickers}")
        continue

    df = df.sort_index(level='Percentage undervalued', ascending=False)
    df.to_excel('SGXstocks/FCFF_analysis.xlsx')
    print(f"The program could not analyse these tickers: {failed_tickers}")

def filter(fcff_csv, fcff=True, expected_growth_rate=False):
    df = pd.read_excel(fcff_csv)

    #filter out stocks with negative fair value or no fair value
    for index, row in df.iterrows():
        if row["Fair value"] < 0 or pd.isnull(row['Fair value']):
            df = df.drop(index=index)

    #option to filter out tickers with negative fcff
    if fcff==True:
        for index, row in df.iterrows():
            if row["FCFF"] < 0:
                df = df.drop(index=index)

    #option to filter out tickers with negative expected growth rate
    if fcff==True:
        for index, row in df.iterrows():
            if row["Expected growth rate"] < 0:
                df = df.drop(index=index)

    df.to_excel("SGXstocks/FCFF_analysis_filtered.xlsx", index=False)

if __name__ == "__main__":
    stock = "BN2.SI"
    csv = "SGXstocks/PriceHistory/SGX-priceHist.csv"
    #main(stock, csv, "2020", timeframe=250)

    #fcff_analysis(csv, "2020")

    fcff_csv = "SGXstocks/FCFF_analysis.xlsx"
    filter(fcff_csv, fcff=True)


