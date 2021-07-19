from Funds import Funds

#set up arguments for Funds class
csv = 'FSM/PriceHistory/fsm-pricehistory-2021-06-25.csv'
dividend_csv = 'FSM/FundsTable/export(1622864030092).csv'
b = Funds(csv, dividend_csv)

b.riskreturn_graph("FSM/riskreturn_graph")     #generate risk return graph of all funds scraped from FSM website, argument is filename chart will be saved as
