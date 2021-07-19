import sys
sys.path.append('./')

from Stonks import tickers_to_csv
import pandas as pd
import numpy as np

def generate_csv(csv, name="SGX-priceHist.csv" ,minCap=0, only_dividends=False):
    sgx_df = pd.read_csv(csv)
    tickers_list = ["^STI"]
    for index, rows in sgx_df.iterrows():
        if sgx_df.loc[index, 'Mkt Cap ($M)'] > minCap:
            tickers_list.append(f"{rows['Trading Code']}.SI")
    if only_dividends==True:
        for index, rows in sgx_df.iterrows():
            if sgx_df.loc[index, 'Mkt Cap ($M)'] > minCap:
                if not np.isnan(rows["Yield (%)"]):
                    tickers_list.append(f"{rows['Trading Code']}.SI")
        
    tickers_to_csv(tickers_list, f"SGXstocks/PriceHistory/{name}")

if __name__ == "__main__":
    csv = "SGXstocks/StocksTable/myData.csv"
    sgx_df = pd.read_csv(csv)

    generate_csv(csv, name="SGX-priceHist.csv" ,minCap=0, only_dividends=False)

