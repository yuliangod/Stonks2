from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from datetime import date

#set up selenium
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
#options.add_argument('--headless')
driver = webdriver.Chrome(executable_path="chromedriver", options=options)

driver.get('https://secure.fundsupermart.com/fsm/funds/fund-selector')

#Create empty dataset to concat all the values together
df2 = pd.DataFrame()

# Click on generate funds table button
try:
    generate_funds_table = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Generate Funds Table"))
    )
except:
    print("Generate funds table button has been changed")
    driver.quit()
generate_funds_table.click()

#close annoying popup that inteferes with next page button
try:
    pop_up = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, "//i[@class = 'fa fa-times']"))
    )
except:
    print("Popup button has been changed")
    driver.quit()
pop_up.click()

#create loop to search through all pages in table
try:        #search for next page button first to ensure that window is loaded
    next_page = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.LINK_TEXT, "2"))
    )
except:
    print("Next page button has been changed")
    driver.quit()

#calculate number of pages to search through
try:
    entries = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//label[@class='ng-binding']"))
    )
except:
    print("Number of funds per page stat have been changed")
    driver.quit()
entries = entries.text
total_num_entries = re.compile(r' (\d(\d)+) entries')
mo4 = total_num_entries.search(entries)
entries = mo4.group(1)
pages = int(entries)//25 + 1        #find number of pages to search through

for b in range(pages):      #for b in range(pages):
    #find number of funds on current page
    try:
        idx = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='ng-binding ng-scope']"))
        )
    except:
        print("Number of funds per page stat have been changed")
        driver.quit()
    idx = idx.text
    num = re.compile(r'(.*) to (.*)')
    mo3 = num.search(idx)
    num1 = mo3.group(1)
    num2 = mo3.group(2)
    num = int(num2) - int(num1) + 1

    #Create loop to loop through all the funds in the table
    for a in range(num):    #    for a in range(num):
        #create empty dataframe to store values
        df = pd.DataFrame(columns=['Date'])
        a = a+1
        xpath = '//tbody/tr[%s]/td[2]/a'%a
        print(xpath)
        #Click on fund names to open up its individual website
        try:
            first_fund_name = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except:
            print("Fund name buttons have been changed")
            driver.quit()
        first_fund_name.click()
        first_fund_name = first_fund_name.text  #store fund name to slot into dataframe     later on
        driver.switch_to.window(driver.window_handles[1])

        #Click on price history button
        try:
            price_history = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Price History"))
            )
        except:
            print("Price history button has been changed")
            driver.quit()
        try:
            price_history.click()       #sometimes price history button gets blocked by other html tags so wait 2 seconds to solve error
        except:
            time.sleep(2)
            price_history.click()

        #Click show all button to get past 3 months of price history
        try:
            show_all = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Show All"))
            )
        except:
            print("Show all button has been changed")
            driver.quit()
        show_all.click()

        #extract data to beautiful soup
        page_source = driver.page_source
        soup = bs(page_source, 'lxml')
        data = soup.find_all('div', attrs={'class':'table-row ng-scope'})

        #create loop to extract data from all rows of the table
        for i in range(len(data)):
            message = data[i].get_text()

            # use regex to extract date and nav price
            NAV_price = re.compile(r'(\d,)?\d(\d)*.(\d\d\d\d)')
            Date = re.compile(r'(\d\d) (\w\w\w) (\d\d\d\d)')
            mo = NAV_price.search(message)
            mo2 = Date.search(message)
            NAV_price = mo.group()
            Date = mo2.group()

            # add data to dataframe
            new_row = {'Date':Date,first_fund_name:NAV_price}
            df = df.append(new_row,ignore_index = True)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df2 = pd.concat([df2, df], axis=1)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    driver.switch_to.window(driver.window_handles[0])
    b = str(int(b) + 2)      #get next page
    print(b)
    if b == str(pages + 1):
        break
    try:
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, b))
        )
    except:
        print("Either the script couldn't find the next page or the script successfully completed" )
    next_page.click()
    
df2.to_csv('FSM/PriceHistory/fsm-pricehistory-%s.csv'%(date.today()))
