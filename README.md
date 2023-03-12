# Stonks2

### FSM folder
1) FSMscraper: webscrape through all funds listed on FundSuperMart and extract the full price history listed there, dependent on Funds.py
2) FSManalysis: analyse risk return of all funds from FSM scraper, and display the results in a html file called "riskreturn_graph"
3) FSMcreateCSV: create a CSV of funds user is interested in to be used for further analysis
4) updateCSV: further expand previously scraped price history with latest price price history scraped from updateCSV

Workflow: extract price history from 1), then filter out interesting funds on the outer perimeter of risk returns graph generated in 2). Afterwards use 3) to create a more concise CSV for further analysis. Further update price history data in the future by using 4)

### SGXstocks
1) update_database: webscrape financial statements and currency of all stock listed on SGX website
2) 01_generateCSV: filter out stocks based on market cap and whether it is dividend paying, then generate a CSV of their price history 
3) 02_FCFF_analysis: run a DCF calculation to estimate fair value of each stock
4) 03_FCFFapp: Investment analysis app to narrow down on stocks to further analyse based on plots and numbers of relevant statistics (https://github.com/yuliangod/StonksApp)
5) income_statement_calculator: quickly calculate relevant stats that can be obtained from financial statements, and generate code to display it in FCFFapp