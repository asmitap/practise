import time
import pandas as pd
# from pandas.tseries.offsets import *
import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# price information of all the data
def price_information(driver):
    number_of_record_xpath = '//*[@id="commodityPriceParticular_info"]'
    number_of_record = driver.find_element(By.XPATH, number_of_record_xpath).text
    #print(number_of_record)
    record_numbers = number_of_record.split()  # Split the text into a list of words
    record_number = int(record_numbers[-2])
    datas = []
    for record in range(1, record_number+1):
        #print(record)
        price_information_xpath = '//*[@id="commodityPriceParticular"]/tbody/tr[' + str(record) + ']'
        price_informations = driver.find_element(By.XPATH, price_information_xpath).text
        #print(type(price_informations))
        datas.append(price_informations)
    return datas


def made_dataframe(driver):
    product_information = price_information(driver)
    #print(product_information)
    data_new = [row.split('Rs') for row in product_information]
    #print(data_new)
    daily_df = pd.DataFrame(data_new, columns=['commodity_name', 'minimum_price', 'maximum_price', 'average_price'])
    # Remove whitespace from the columns
    daily_df.columns = daily_df.columns.str.strip()
    # Remove whitespace from the product names
    daily_df['commodity_name'] = daily_df['commodity_name'].str.strip()
    # Convert prices to numeric values
    daily_df['minimum_price'] = pd.to_numeric(daily_df['minimum_price'].str.strip())
    daily_df['maximum_price'] = pd.to_numeric(daily_df['maximum_price'].str.strip())
    daily_df['average_price'] = pd.to_numeric(daily_df['average_price'].str.strip())
    return daily_df


#to calculate the date range
def daterange(initial_date, end_date):
    dates = []
    while initial_date <= end_date:
        dates.append(pd.Timestamp(initial_date))
        initial_date += pd.DateOffset(days=1)
    return dates

def selectdate(date_range, driver):
    final_df = pd.DataFrame()
    for date_input in date_range:
        date_id = 'datePricing'
        date_to_find = driver.find_element(By.ID, date_id)
        submit_button_xpath = '//*[@id="queryFormDues"]/div/div[2]/button'
        submit_button = driver.find_element(By.XPATH, submit_button_xpath)
        date_formatted = date_input.strftime('%m/%d/%Y') # convert into string
        date_to_find.send_keys(date_formatted)
        time.sleep(15)
        submit_button.click()
        daily_dataframe = made_dataframe(driver)
        daily_dataframe['date'] = date_input
        final_df = pd.concat([final_df, daily_dataframe], axis=0)
    return final_df
    

def scrapdata(initial_date,end_date):
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    driver.get('https://kalimatimarket.gov.np/price')
    driver.implicitly_wait(5)
    # select english language
    language_xpath = '/html/body/header/div[3]/div/div/nav/ul/li[7]/a'
    language_select = driver.find_element(By.XPATH, language_xpath)
    language_select.click()
    time.sleep(2)
    country_xpath = '/html/body/header/div[3]/div/div/nav/ul/li[7]/ul'
    country_select = driver.find_element(By.XPATH, country_xpath)
    time.sleep(2)
    country_select.click()
    time.sleep(2)
    date_range = daterange(initial_date, end_date)
    final_price_info = selectdate(date_range, driver)
    return(final_price_info)
    # final_price_info.to_csv('tarkari20231.csv')
    driver.close()



