import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

today = date.today()
d1 = str(today.strftime("%m/%d/%Y"))
d1 = d1.replace("/", "_")
print(d1)

filename = 'athome_links_progress_11_14_2022.csv'

start = time.time()
# Read links and locations csv files
links = pd.read_csv(filename).links.to_list()

# Index to specific links
link_index = 0
links = links[link_index:]

page_not_found = []
for link in links:
    result = requests.head(link)
    if result.status_code == 404:
        print(link_index, "PAGE NOT FOUND", result.status_code)
        page_not_found.append([link_index, link])
        print(link_index, ":", link)
        print()
    link_index += 1

page_not_found_df = pd.DataFrame(page_not_found)
file_name_page = "athome_page_not_found_" + str(d1) + ".csv"
page_not_found_df.to_csv("athome_page_not_found_list_week_x.csv")

end = time.time()

print(round(((end - start) / 60 / 60), 1))