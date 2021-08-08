from sgxscraper import sgx_scraper
import pandas as pd
import os

def download_data(ticker):
    IS, BS, CF, currency = sgx_scraper(ticker)

    #create folder
    dir = os.getcwd() + "\SGXstocks\Database\\" + ticker
    if not os.path.exists(dir):
        os.mkdir(dir)

    #save financial statements
    IS.to_csv(f"SGXstocks/Database/{ticker}/IS.csv")
    BS.to_csv(f"SGXstocks/Database/{ticker}/BS.csv")
    CF.to_csv(f"SGXstocks/Database/{ticker}/CF.csv")

    #save currency in text file
    f= open(f"SGXstocks/Database/{ticker}/currency.txt","w+")
    f.write(currency)
    f.close()

def main(tickers_list, append_failed_tickers=False):
    i = 0
    num_of_tickers = len(tickers_list)
    failed_tickers = []       
    
    #downlaod financial statements to individual folders
    for ticker in tickers_list[:]:
        i += 1
    
        try:
            download_data(ticker)
            print(f"{i}/{num_of_tickers} downloaded")
    
        except:
            failed_tickers.append(ticker)
            print(f"The program could not download financial statements of these tickers: {failed_tickers}")
            print(f"{i}/{num_of_tickers} downloaded")
            continue
    
    #decide whether to append failed ticker to txt file or write new file
    if append_failed_tickers == True:
        save_type = "a"
    else:
        save_type = "w+"

    #save failed tickers to txt file
    f= open(f"SGXstocks/Database/failed_tickers.txt",save_type)
    for tickers in failed_tickers:
        f.write(tickers + "\n")
    f.close()

if __name__ == "__main__":
    #get list of all tickers
    all_tickers_df = pd.read_csv("SGXstocks/StocksTable/myData.csv")
    all_tickers_list = list(all_tickers_df["Trading Code"] + ".SI")

    #get list of failed tickers
    with open('SGXstocks/Database/failed_tickers.txt') as f:
        failed_tickers_list = [line.rstrip() for line in f]
    
    download_data("8AZ.SI")

    #main(failed_tickers_list, append_failed_tickers=False)


