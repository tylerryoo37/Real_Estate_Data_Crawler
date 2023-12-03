import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from selenium.webdriver.common.action_chains import ActionChains

start = time.time()

# Set up the path
# print(os.getcwd())

s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
driver = webdriver.Chrome(service=s)

# Homepage of the website
driver.get('https://www.athome.lu/srp/?q=faee1a4a') # sales

# From specific page
# driver.get('https://www.athome.lu/en/srp/?tr=buy&q=faee1a4a&loc=L2-luxembourg&ptypes=house,flat,new-property,build,ground&page=409')

# Accept Cookies
driver.find_element(By.XPATH, "//button[@id = 'onetrust-accept-btn-handler']").click()

# Translate to English
button = driver.find_element(By.CLASS_NAME, "icon-chevron-down")
button.click()
driver.find_element(By.XPATH, "//*[@id='app']/div/div/header/div[1]/div[3]/div[2]/ul/li[2]/button").click()
time.sleep(3)

# Search Luxembourg properties
luxembourg = driver.find_element(By.XPATH, "//input[@type = 'text']")
luxembourg.send_keys("Luxembourg")
time.sleep(3)
luxembourg.send_keys(Keys.RETURN)
time.sleep(3)

# Click on 5 property types to search for
property_setting = driver.find_elements(By.CLASS_NAME, 'handle')[1]
property_setting.click()

house = driver.find_element(By.XPATH, "//a[@title = 'House']")
house.click()

apartment = driver.find_element(By.XPATH, "//a[@title = 'Apartment']")
apartment.click()

new_prop = driver.find_element(By.XPATH, "//a[@title = 'New property']")
new_prop.click()

new_house = driver.find_element(By.XPATH, "//a[@title = 'New house']")
new_house.click()

land = driver.find_element(By.XPATH, "//a[@title = 'Land']")
land.click()

# Return the filtered result
search = driver.find_element(By.XPATH, "//input[@type = 'submit']")
search.click()
time.sleep(2)

# Extract all the property links and locations
property_links = []
collect_status = []
locations = []
prop_num = 1


def check_prop_link(prop_num):
    # check for all five types of properties
    if (p_link.startswith('https://www.athome.lu/en/buy/new-property/') or
        p_link.startswith('https://www.athome.lu/en/buy/apartment/') or
        p_link.startswith('https://www.athome.lu/en/buy/house/') or
        p_link.startswith('https://www.athome.lu/en/buy/new-house/') or
        p_link.startswith('https://www.athome.lu/en/buy/ground/')):
        property_links.append(p.get_attribute('href'))
        collect_status.append('newly_added')
        print(prop_num, ": newly added!")
        print("Newly Added Link:", [p.get_attribute('href')])
        print()
        prop_num += 1

    return prop_num

# Iterate through all the pages and extract property links and locations
status = True
while status:
    try:
        # Extract property links
        wait = WebDriverWait(driver, 10)
        properties = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article/div/h3/a[@href]")))
        # properties = driver.find_elements(By.XPATH,"//article/div/h3/a[@href]" )
        try:
            for p in properties:
                p_link = p.get_attribute('href')
                prop_num = check_prop_link(prop_num)
        except TimeoutException:
            driver.refresh()
            time.sleep(3)
            properties = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article/div/h3/a[@href]")))
            for p in properties:
                p_link = p.get_attribute('href')
                prop_num = check_prop_link(prop_num)
        except StaleElementReferenceException:
            driver.refresh()
            time.sleep(3)
            properties = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article/div/h3/a[@href]")))
            for p in properties:
                p_link = p.get_attribute('href')
                prop_num = check_prop_link(prop_num)

        try:
            # Extract locations
            location = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[@itemprop = 'addressLocality']")))
            for lo in location:
                locations.append(lo.text)
        except StaleElementReferenceException:
            driver.refresh()
            time.sleep(3)
            location = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[@itemprop = 'addressLocality']")))
            for lo in location:
                locations.append(lo.text)

        # Save to csv files in case code breaks
        property_df = pd.DataFrame(list(zip(property_links, locations, collect_status)), columns=['proj_link', 'location', 'collect_status'])
        property_df.to_csv("athome_links_final.csv", encoding='utf-8-sig')

        # Scroll down all the way to the bottom to go to the next page
        # driver.execute_script("window.scrollTo(0,  document.body.scrollHeight)")

        click_next = driver.find_element(By.CLASS_NAME, 'nextPage')
        # print(click_next)
        driver.execute_script("arguments[0].click();", click_next)
        # click_next.click()
        time.sleep(5)

    except TimeoutException:
        status = False
    except NoSuchElementException:
        status = False

driver.close()

property_df = pd.DataFrame(list(zip(property_links, locations, collect_status)), columns=['proj_link', 'location', 'collect_status'])
property_df.to_csv("athome_links_final.csv", encoding='utf-8-sig')

end = time.time()

print(round(((end - start) / 60 / 60), 1))