import pandas as pd
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins
import math
import yfinance as yf

#extract price history of list of tickers to a csv
def tickers_to_csv(list_of_tickers, csv_name):
	' '.join(list_of_tickers)
	data = yf.download(list_of_tickers, period = '2y')
	print(data)
	data1 = data['Close']
	data1.to_csv(f'{csv_name}.csv')

class Stonks:

	def __init__(self, csv, timeframe=56):
		self.csv = csv
		self.timeframe = timeframe
	
	#get latest n number of daily prices for stock
	def pricehistory(self, stock):
		timeframe = self.timeframe
		df = pd.read_csv(self.csv, thousands=',')
		stock = df[stock].dropna()
		stock = stock.iloc[-timeframe:]
		stock = stock.reset_index(drop=True)
		return(stock)

	#get year end price of stock
	def year_end_price(self, stock, year):
		data = yf.download(stock, start=f'{year}-11-01', end=f'{year}-12-31')
		return data['Close'][-1]
	
	#calculate correlation between 2 stocks
	def correlation(self, stock1, stock2):
		#pull out data for stock 1 & 2 and store it in a dataframe
		stock1_price = self.pricehistory(stock1)
		stock2_price = self.pricehistory(stock2)

		#create new dataframe with values needed for correlation calculation
		df3 = pd.DataFrame()
		df3[stock1] = stock1_price
		df3[stock2] = stock2_price
		df3 = df3.dropna()

		stock1_mean = stock1_price.mean()
		stock2_mean = stock2_price.mean()
		df3['a'] = df3[stock1] - stock1_mean
		df3['b'] = df3[stock2] - stock2_mean
		df3['axb'] = df3['a'] * df3['b']
		df3['a_square'] = (df3['a'])**2
		df3['b_square'] = (df3['b'])**2

		#final calculation
		correlation = (df3['axb'].sum())/(math.sqrt(df3['a_square'].sum()*(df3['b_square'].sum())))

		return(correlation)

	def Beta(self, stock, index='SPY'):
		#variables
		index_correlation = self.correlation(stock, index)
		stock_volatility = (self.riskreturn(stock))[-1]
		index_volatility = (self.riskreturn(index))[-1]

		#calculation
		beta = index_correlation * (stock_volatility/index_volatility)
		return beta

	def expected_returns(self, stock, Rf = 0.017, Rm = 0.025, beta_index="SPY"):
		beta = self.Beta(stock,index=beta_index)
		Er = Rf + beta*(Rm - Rf)
		return(Er)

	#calculate risk and returns of a stock
	def riskreturn(self, stock):
		timeframe = self.timeframe
		pricehist_df = self.pricehistory(stock)
		series = pd.Series([], dtype='float64')
		returns_list = pd.Series([], dtype='float64')

		#calculations
		if len(pricehist_df) == timeframe:
			# loop through prices 
			for i in range(int(timeframe - 1)):
				n = int(i + 1)
				Cn1 = pricehist_df[n]  
				Cn = pricehist_df[i]
				returns_ratio = pd.Series([(Cn1-Cn)/Cn])
				returns_list = returns_list.append(returns_ratio)
				ln_returns = pd.Series([math.log(Cn1/Cn)])
				series = series.append(ln_returns)
			returns = returns_list.mean()
			risk = series.std()
		else: 
			print(f'{stock} has not enough price data for risk return data')
			returns, risk = 0,0
		return stock,returns,risk 
			
	#generate a plot of the risk return points of all stocks within the csv
	def riskreturn_graph(self, filename):
		df = pd.read_csv(self.csv, thousands=',')
		#create empty dataframe for stock name, volatility, and average returns(%)
		graph_df = pd.DataFrame(columns=['Name','Returns', 'Volatility'])

		#create loop to run risk return function for all stock symbols
		print("Calculating risk return for all stocks")
		for column in df.columns[1:]:           #start index from 1 because 0 is date column
				stock1,average_returns1,volatility1 = self.riskreturn(column)
				new_row = {'Name':stock1,'Returns':average_returns1,'Volatility':volatility1}
				graph_df = graph_df.append(new_row,ignore_index = True)

		#creating matplotlib graphs
		print("Plotting points")
		fig, ax = plt.subplots()
		ax.grid(True, alpha=0.3)

		ax.set_xlabel('Risk')
		ax.set_ylabel('Returns')

		#give stock name when hovering above it
		# Define some CSS to control our custom labels
		css = """
		table
		{
			border-collapse: collapse;
		}
		th
		{
			color: #ffffff;
			background-color: #000000;
		}
		td
		{
			background-color: #cccccc;
		}
		table, th, td
		{
			font-family:Arial, Helvetica, sans-serif;
			border: 1px solid black;
			text-align: right;
		}
		"""
		labels = []
		for i in range(len(graph_df['Name'])):
				label = graph_df.iloc[[i], :].T
				label.columns = ['Row {0}'.format(i)]
				# .to_html() is unicode; so make leading 'u' go away with str()
				labels.append(str(label.to_html()))

		points = ax.plot(graph_df.Volatility,graph_df.Returns, 'o', color='b', mec='k', ms=1, mew=1, alpha=.6)

		tooltip = plugins.PointHTMLTooltip(points[0], labels,voffset=10, hoffset=10, css=css)
		plugins.connect(fig, tooltip)

		#save file as html to be able to interact with it in the future
		html_str = mpld3.fig_to_html(fig)
		Html_file = open("%s.html"%(filename),"w")
		Html_file.write(html_str)
		Html_file.close()

	#calculate company default spread
	def CDS(self, cap, stock_ICR):
		LargeCapCDS_df = pd.read_csv('Datasets/LargeCapCDS.csv')
		SmallCapCDS_df = pd.read_csv('Datasets/SmallCapCDS.csv')

		if cap <= 5*(10**9):	# if market cap is below 5 billion stock is considered small cap
			ICR_list = list(SmallCapCDS_df[">"])
			ICR_list.append(stock_ICR)
			ICR_list.sort(reverse=True)		#add stock's ICR to list and sort it to get it's index
			spread_idx = ICR_list.index(stock_ICR)
			CDS = float(SmallCapCDS_df['Spread is'][spread_idx].replace("%",""))/100
		else:
			ICR_list = list(LargeCapCDS_df[">"])
			ICR_list.append(stock_ICR)
			ICR_list.sort(reverse=True)
			spread_idx = ICR_list.index(stock_ICR)
			CDS = float(LargeCapCDS_df['Spread is'][spread_idx].replace("%",""))/100
		return CDS

	#calculate levelled beta
	def BL(self, beta, total_debt, total_equity, marginal_tax_rate=0.17):
		BL = beta*(1+(1-marginal_tax_rate)*(total_debt/total_equity))
		return BL


	#calculate cost of equity
	def cost_of_equity(self, BL, Rf=0.01559, country_risk_premium_of_equity=0.0472, mature_mkt_prem=0.0456):
		cost_of_equity = Rf + BL*(mature_mkt_prem) + country_risk_premium_of_equity
		return cost_of_equity

	#calculate cost of debt
	def cost_of_debt(self, CDS, Rf=0.01559):
		cost_of_equity = Rf + CDS
		return cost_of_equity

	#calculate wacc
	def wacc(self, cost_of_equity, cost_of_debt, market_value_of_equity, market_value_of_debt, Tc ):
		wacc = ((market_value_of_equity/(market_value_of_equity + market_value_of_debt))*cost_of_equity) + ((market_value_of_debt/(market_value_of_equity + market_value_of_debt))*cost_of_debt*(1-Tc))
		return wacc

	#calculate fcff
	def fcff(self, EBIT, Tc, CapEx, Depreciation, non_cashItems, workingCapital):
		fcff = EBIT*(1-Tc) + CapEx + Depreciation + non_cashItems + workingCapital
		return fcff

if __name__ == "__main__":
		#function to get a csv with the price history of a list of stocks
		stocks_list = ["^STI","TS0U.SI", "A17U.SI", "BN2.SI"]  
		tickers_to_csv(stocks_list, "test")

		#set up stonks class
		csv = "test.csv"
		a = Stonks(csv, timeframe=100)
		stock = "A17U.SI"

		#demonstration of price history function
		print("####################")
		print(a.pricehistory(stock))
		print("########## Above is the price history of {stock} ##########\n")

		#demonstration of year end price function
		year = "2017"
		year_end_price = a.year_end_price(stock, year)
		print(f"Year end price of {stock} for the year {year} is {year_end_price}\n")

		#demonstration of correlation function
		stock2 = "TS0U.SI"
		correlation = a.correlation(stock, stock2)
		print(f"Correlation between {stock} and {stock2} is {correlation}\n")

		#demonstration of beta function
		beta = a.Beta(stock, index="^STI")
		print(f"Beta of {stock} is {beta}\n")

		#demonstration of expected returns function
		Er = a.expected_returns(stock, beta_index="^STI")
		print(f"Expected returns of {stock} is {Er}\n")

		#demonstration of risk return function
		stock, returns, risk = a.riskreturn(stock)
		print(f"Risk of {stock} is {risk}")
		print(f"Return of {stock} is {returns}\n")

		#demonstration of risk return graph function (output is stored as a chrome file)
		print(f"Creating risk return graph for {csv}")
		a.riskreturn_graph("test")

		#demonstration of company default spread function
		CDS = a.CDS(6000000000,8.4)
		print(f"\nCompany default spread in large cap scenario is {CDS}")

		CDS = a.CDS(4000000000,10)
		print(f"Company default spread in small cap scenario is {CDS}\n")

		#demonstration of levelled beta
		BL = a.BL(beta, 5291.92, 9190.55)
		print(f"Leveled beta in this scenario is {BL}\n")

		#demonstration of cost of equity function
		cost_of_equity = a.cost_of_equity(BL)
		print(f"Cost of equity in this scenario is {cost_of_equity}")

		#demonstration of cost of debt function
		cost_of_debt = a.cost_of_debt(CDS)
		print(f"Cost of debt in this scenario is {cost_of_debt}\n")

		#demonstration of wacc function
		wacc = a.wacc(cost_of_equity, cost_of_debt, 4000, 6000, 0.08)
		print(f"WACC in this scenario is {wacc}")