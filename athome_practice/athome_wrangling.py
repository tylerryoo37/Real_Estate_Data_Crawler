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

# Read links and locations csv files
# links = pd.read_csv("test_athome_links_progress_final.csv").links.to_list()
# locations = pd.read_csv("test_athome_links_progress_final.csv").locations.to_list()
#
# s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
# driver = webdriver.Chrome(service=s)
#
# driver.get(links[0])
# driver.close
# s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
# driver = webdriver.Chrome(service=s)
# driver.get(links[0])

# already_collected = pd.read_csv('aggregated_athome_data_csv.csv').link.to_list())

df = pd.read_csv('test_athome_links_week_update_progress.csv')

print(df[df['links']!='already_collected'].iloc[19])