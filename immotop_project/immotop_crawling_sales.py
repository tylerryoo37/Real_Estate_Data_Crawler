import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from datetime import date

start = time.time()
# Set up the path
# print(os.getcwd())
s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
driver = webdriver.Chrome(service=s)

# Homepage of the website
driver.get('https://www.immotop.lu/vente-maisons-appartements/luxembourg-pays/?criterio=rilevanza') # sales
time.sleep(1)

# Accept Cookies
driver.find_element(by=By.XPATH, value = "//button[@class = 'nd-button nd-button--compact nd-cookieBar__button']").click()

# Extract all the property links
# Getting the first page
property_links = []
properties = driver.find_elements(by=By.XPATH, value="//a[@class = 'in-card__title']")
for p in properties:
    property_links.append(p.get_attribute('href'))

# Click Next
click_next = driver.find_elements(By.XPATH, '//a[@class = "in-pagination__item"]')[0]
click_next.click()
time.sleep(3)

# From page 2 until the last page
status = False
while not status:
    try:
        properties = driver.find_elements(by = By.XPATH, value = "//a[@class = 'in-card__title']")
        for p in properties:
            property_links.append(p.get_attribute('href'))
        click_next = driver.find_elements(By.XPATH, '//a[@class = "in-pagination__item"]')
        if len(click_next) > 1:
            click_next[1].click()
        else:
            status = True
        time.sleep(3)
    except TimeoutException:
        status = True

driver.close()

property_df = pd.DataFrame(columns = ['links'], data = property_links)

today = date.today()
d1 = str(today.strftime("%m/%d/%Y"))
d1 = d1.replace("/", "_")
file_name = "sales_" + str(d1) + ".csv"

property_df.to_csv(file_name)

end = time.time()

print(round(((end - start) / 60),1))