import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException
from datetime import date

# Locate the chrome driver
s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
driver = webdriver.Chrome(service=s)

driver.get('https://www.athome.lu/en/buy/apartment/oberkorn/id-7688347.html')

# Accept Cookies
driver.find_element(By.XPATH, "//button[@id = 'onetrust-accept-btn-handler']").click()

# prev_height = driver.execute_script("return document.body.scrollHeight")


status = True
while status:
    # driver.execute_script("window.scrollTo(" + str(start) + "," + str(end) + ")")
    # document.body.scrollHeight
    try:
        see_all = driver.find_elements(By.XPATH, "//div[text() = 'See all']")
        # /div[text() = 'See all']
        #//i[@class = 'icon-chevron-down']
        print(see_all)
        for see in see_all:
            see.click()
            time.sleep(3)

        char_name = driver.find_elements(By.XPATH,"//div[@class = 'feature-bloc-content-specification-content-name']")
        print([ch_name.text for ch_name in char_name])
        char_val = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-response']")
        print([ch_val.text for ch_val in char_val])

        status = False

    except NoSuchElementException:
        pass
    except ElementClickInterceptedException:
        pass

    # curr_height = driver.execute_script("return document.documentElement.scrollHeight")
    # if curr_height == prev_height:
    #     break
    # prev_height = curr_height

#
# # Iterate through the links
# for prop, lo in zip(rest_links, rest_locations):
#     driver.get(prop)
#     # If it's the first link --> handle accept cookies button
#     if prop == rest_links[0]:
#         # Accept Cookies
#         driver.find_element(By.XPATH, "//button[@id = 'onetrust-accept-btn-handler']").click()
#     print(prop)
#     name = driver.find_element(By.XPATH, "//h1[@class = 'KeyInfoBlockStyle__PdpTitle-sc-1o1h56e-2 hWEtva']").text
#     print(name)
#     price_range = driver.find_element(By.XPATH, "//div[@class = 'KeyInfoBlockStyle__Price-sc-1o1h56e-5 eWOlhG']").text
#     print(price_range)
#     agency = driver.find_element(By.XPATH, "//div[@class = 'agency-details__name agency-details__name--centered']").text
#     print(agency)
#     print(lo)
#
#     # time.sleep(1)
#     # driver.find_element(By.XPATH, "//i[@class = 'icon-chevron-up']").click()
#
#     unit = driver.find_elements(By.XPATH, "//div[@class = 'residence-type select']/a")
#     unit_links = [u.get_attribute('href') for u in unit]
#     print(unit_links)
#     print(len(unit_links))
#
#     for u_link in unit_links:
#         driver.get(u_link)
#         time.sleep(2)
#
#         prev_height = driver.execute_script("return document.body.scrollHeight")
#
#         while True:
#             # driver.execute_script("window.scrollTo(0,  3000)")
#             # document.body.scrollHeight
#             try:
#                 see_all = driver.find_elements(By.XPATH, "//i[@class = 'icon-chevron-down']/div[text() = 'See all']")
#                 for see in see_all:
#                     print(u_link)
#                     see.click()
#             except NoSuchElementException:
#                 pass
#             except ElementClickInterceptedException:
#                 pass
#
#             curr_height = driver.execute_script("return document.documentElement.scrollHeight")
#             if curr_height == prev_height:
#                 break
#             prev_height = curr_height
#
#         char_name = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-name']")
#         print([ch_name.text for ch_name in char_name])
#         char_val = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-response']")
#         print([ch_val.text for ch_val in char_val])
#
#     if u_link == unit_links[0]:
#         break
#
#     driver.close()