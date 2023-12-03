import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from datetime import date

from bs4 import BeautifulSoup as BS
import requests

start = time.time()

"""
Revise file_name before running!
"""

file_name = "rentals_10_25_2022.csv"
property_links = pd.read_csv(file_name).links.to_list()

s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
driver = webdriver.Chrome(service=s)

# Open up each property and extract information
name = []
price = []
result = []

for prop in property_links:
    unit_links = []
    driver.get(prop)
    if prop == property_links[0]:
        # Accept Cookies
        driver.find_element(by=By.XPATH, value="//button[@class = 'nd-button nd-button--outlineLight nd-button--compact nd-cookieBar__button']").click()
    print(prop)
    name = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-titleBlock__title']")[0].text
    price_string = driver.find_elements(by=By.XPATH, value="//div[@class = 'im-mainFeatures__title']")[0].text
    price = price_string.replace("\u202f", ",")
    location = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-location']")[0].text
    agency = driver.find_elements(by=By.XPATH, value="//div[@class = 'im-lead__reference']/a/p")
    if len(agency) >= 1:
        agency = driver.find_elements(by=By.XPATH, value="//div[@class = 'im-lead__reference']/a/p")[0].text
    else:
        agency = " "

    unit = driver.find_elements(by=By.XPATH, value="//a[@class = 'im-properties__summary']")
    unit_links = [u.get_attribute('href') for u in unit]

    # If the property has only one listing
    if len(unit_links) == 0:
        unit_title = name
        unit_price = price
        unit_type = driver.find_elements(by=By.XPATH, value="//dd[@class = 'im-features__value']")[2].text
        unit_label = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-mainFeatures__label']")
        unit_info = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-mainFeatures__value']")
        unit_label = [u.text for u in unit_label]
        unit_info = [u.text for u in unit_info]
        unit_info_label = {unit_label[i]: unit_info[i] for i in range(len(unit_label))}
        result.append([name, price, location, prop, agency, unit_title, unit_price.replace("\u202f", ","), unit_type, unit_info_label])
    else:
        # If the property has more than one listing
        for unit in unit_links:
            driver.get(unit)
            unit_title = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-titleBlock__title']")[0].text
            unit_price = driver.find_elements(by=By.XPATH, value="//div[@class = 'im-mainFeatures__title']")[0].text
            unit_type = driver.find_elements(by=By.XPATH, value="//dd[@class = 'im-features__value']")[1].text
            unit_label = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-mainFeatures__label']")
            unit_info = driver.find_elements(by=By.XPATH, value="//span[@class = 'im-mainFeatures__value']")
            unit_label = [u.text for u in unit_label]
            unit_info = [u.text for u in unit_info]
            unit_info_label = {unit_label[i]: unit_info[i] for i in range(len(unit_label))}
            result.append([name, price, location, unit, agency, unit_title, unit_price.replace("\u202f", ","), unit_type, unit_info_label])

    # if prop == property_links[4]:
    #     break

rentals_unit = pd.DataFrame(columns = ['property', 'price_range', 'location', 'property_link', 'agency', 'unit', 'unit_price', 'unit_type', 'unit_info'], data = result)
# df.to_csv('test.csv', encoding = 'utf-8-sig')
# df.to_csv('result.csv', encoding = 'utf-8-sig')

today = date.today()
d1 = str(today.strftime("%m/%d/%Y"))
d1 = d1.replace("/", "_")
file_name = "rentals_unit_" + str(d1) + ".csv"

rentals_unit.to_csv(file_name, encoding = 'utf-8-sig')

end = time.time()

print(round(((end-start) / 60 / 60),1), "hours")

driver.close()