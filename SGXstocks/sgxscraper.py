import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


def main(stock):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path="chromedriver", options=options)

    ticker = re.compile(r'(.*)\.')
    mo = ticker.search(stock)
    ticker = mo.group(1)
    URL = 'https://www.sgx.com/securities/equities/' + ticker
    driver.get(URL)

    #accept cookies so it won't block the expand all button
    try:
        accept_cookies = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='sgx-consent-banner-wrapper container-fluid']/button"))
        )
    except:
        print("accept cookies button has been changed")
        driver.quit()
    accept_cookies.click()

    #click on expand all to get all tables with financial data to extract
    try:
        expand_all = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'sgx-accordion-expandAll-btn'))
        )
    except:
        print("Expand all button has been changed")
        driver.quit()
    expand_all.click()

    #figure out currency financials are reported in
    currency = driver.find_element_by_class_name("widget-stocks-header-currency").text
    currency_re = re.compile(r'This company reports in this currency: (\w\w\w)')
    mo = currency_re.search(currency)
    currency = mo.group(1)

    #convert tables to dataframe
    html = driver.page_source
    soup= bs(html,'html.parser')
    soup_table = soup.find_all("table")
    tables = pd.read_html(str(soup_table))
    
    IS = tables[5].set_index('Fiscal Year')
    IS = IS.replace("-", 0)

    BS = tables[6].set_index('Fiscal Year')
    BS = BS.replace("-", 0)
    
    CF = tables[7].set_index('Fiscal Year')
    CF = CF.replace("-", 0)

    #convert tables to correct currency
    #CC = CurrencyConverter()
    #conversion_rate = CC.convert(1, currency, 'SGD')

    #IS = IS.drop(["Period Ended", "Period Length", "Source"])
    #IS = IS.astype(float)
    #IS = IS * conversion_rate

    #BS = BS.drop(["Period Ended", "Source"])
    #BS = BS.astype(float)
    #BS = BS * conversion_rate

    #CF = CF.drop(["Period Ended", "Source"])
    #CF = CF.astype(float)
    #CF = CF * conversion_rate


    driver.quit()
    return IS, BS, CF, currency

def sgx_scraper(stock):
    for i in range(3):
        try:
            tables = main(stock)
            IS = tables[0]
            BS = tables[1]
            E = BS.loc['Total Equity']   #try to find total equity in balance sheet to ensure tables were scraped properly
            CF = tables[2]
            currency = tables[3]
            break
        except:
            continue
    return IS, BS, CF, currency

if __name__ == '__main__':
    stock="A17U.SI"

    IS, BS, CF, currency = sgx_scraper(stock)
    print(f"{stock} reports its financial statements in {currency}")
