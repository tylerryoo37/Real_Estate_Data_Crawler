import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import requests

today = date.today()
d1 = str(today.strftime("%m/%d/%Y"))
d1 = d1.replace("/", "_")
print(d1)


# s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
# driver = webdriver.Chrome(service=s)

df = pd.read_csv("original_data/athome_not_extracted_properly.csv")

for i in df['0']:
    print(i)
    webpage = requests.get(i)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    dom = etree.HTML(str(soup))
    feature_name = dom.xpath("//div[@class = 'feature-bloc-content-specification-content-name']")
    print([i.text for i in feature_name])
    break

# def collect_info():
#     char_name = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-name']")
#     label = [ch_name.text for ch_name in char_name]
#     char_val = driver.find_elements(By.XPATH,
#                                     "//div[@class = 'feature-bloc-content-specification-content-response']")
#     value = [ch_val.text for ch_val in char_val]
#     return label, value

# for i in df['0']:
#     print(i)
#     webpage = requests.get(i)
#     soup = BeautifulSoup(webpage.content, 'html.parser')
#     print(soup)
#     dom = etree.HTML(str(soup))
    # print(dom.xpath("//div[@class = 'feature-bloc-content-specification-content-name']")[0].text)

    # driver.get(i)
    # wait = WebDriverWait(driver, 10)
    # see_all = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[text() = 'See all']")))
    # for see in see_all:
    #     driver.execute_script("arguments[0].click();", see)
    #     time.sleep(3)
    #     prop_label, prop_value = collect_info()
    #     print(prop_label, prop_value)







