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

# The xpath gets updated. Edit if code doesn't run
name_xpath = "//h1[@class = 'KeyInfoBlockStyle__PdpTitle-sc-1o1h56e-2 ilPGib']"
price_xpath = "//div[@class = 'KeyInfoBlockStyle__Price-sc-1o1h56e-5 fpNLMn']"

# Read links and locations csv files
links = pd.read_csv("athome_links_final.csv").proj_link.to_list()
locations = pd.read_csv("athome_links_final.csv").location.to_list()

# Index to specific links
link_index = 0
links = links[link_index:]
locations = locations[link_index:]

# Locate the chrome driver
s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
driver = webdriver.Chrome(service=s)

''' Three main lists that will be used to create dataframes and csv files '''
# result: used to extract all values of each property
result = []
# not_extracted_properly: used to keep track of properties not extracted properly with ''
not_extracted_properly = []
# page_not_found: used to keep track of pages that expired
page_not_found = []

def collect_info():
    char_name = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-name']")
    label = [ch_name.text for ch_name in char_name]
    char_val = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-response']")
    value = [ch_val.text for ch_val in char_val]
    return label, value

first = True # keep track of the first element and accept cookies
# Iterate through the links
for link, location in zip(links, locations):
    # locate link index
    print("Link Index: ", link_index, "|" , link)
    link_index += 1
    try:
        driver.get(link)
        time.sleep(2)

    except TimeoutException:
        print("TimeoutException! Reload the page and try again!")
        driver.close()
        # Restart the driver
        s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
        driver = webdriver.Chrome(service=s)
        driver.get(link)
        time.sleep(3)
        driver.find_element(By.XPATH, "//button[@id = 'onetrust-accept-btn-handler']").click()
        pass

    # If it's the first link --> handle accept cookies button
    if first:
        # Accept Cookies
        # driver.refresh()
        # time.sleep(10)
        driver.find_element(By.XPATH, "//button[@id = 'onetrust-accept-btn-handler']").click()
        first = False
    try:
        # extract name, price, and agency from the link
        name = driver.find_element(By.XPATH, name_xpath).text #sometimes this xpath changes
        price = driver.find_element(By.XPATH, price_xpath).text #sometimes this xpath changes
        agency = driver.find_element(By.XPATH, "//div[@class = 'agency-details__name agency-details__name--centered']").text

        # find all the units that fall under property project
        unit = driver.find_elements(By.XPATH, "//div[@class = 'residence-type select']/a")
        unit_links = [u.get_attribute('href') for u in unit]
        # print('try extracting')

    # keep track of pages that expired
    except NoSuchElementException:
        print(link_index - 1, "PAGE NOT FOUND")
        page_not_found.append([link_index - 1, link])
        continue

    # Case 1: If the link only has one property (not a house project or apartment block for example)
    if len(unit_links) == 0:
        # print the information collected from above
        print(link)
        print(name)
        print(price)
        print(agency)
        print(location)

        status = True
        while status:
            try:
                # expand all see alls
                wait = WebDriverWait(driver, 10)
                try:
                    see_all = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[text() = 'See all']")))
                    for see in see_all:
                        driver.execute_script("arguments[0].click();", see)
                        prop_label, prop_value = collect_info()

                        # if the collected_info doesn't contain '', stop expanding and break
                        if ('' not in prop_label) and ('' not in prop_value):
                            break
                        time.sleep(3)
                except TimeoutException:
                    print('TimeoutException_1')
                    driver.refresh()
                    time.sleep(3)
                    prop_label, prop_value = collect_info()

                except StaleElementReferenceException:
                    prop_label, prop_value = collect_info()

                # if there still exists '' in the collected info, the data is not extracted properly
                if ('' in prop_label) and ('' in prop_value):
                    detail = {prop_label[i]: prop_value[i] for i in range(len(prop_label))}
                    not_extracted_properly.append([link, detail])
                    print()
                    print("WARNING: DATA NOT EXTRACTED PROPERLY")
                    print()

                # print the remaining extracted information
                print(prop_label)
                print(prop_value)
                detail = {prop_label[i]: prop_value[i] for i in range(len(prop_label))}

                # save the progress of extracted information into csv files:

                # result
                result.append([name, price, location, link, agency, detail])
                result_df = pd.DataFrame(columns=['property', 'price', 'location', 'link', 'agency', 'detail'],data=result)
                result_df.to_csv("athome_data_progress.csv", encoding='utf-8-sig')

                # not_extracted_properly
                not_extracted_properly_df = pd.DataFrame(not_extracted_properly)
                not_extracted_properly_df.to_csv("athome_not_extracted_properly.csv", encoding='utf-8-sig')

                # page_not_found
                page_not_found_df = pd.DataFrame(page_not_found)
                page_not_found_df.to_csv("athome_page_not_found_list.csv")

                # change status to False to terminate the while loop
                status = False

            except NoSuchElementException:
                pass
            except ElementClickInterceptedException:
                pass

    # Case 2: If the link has more than one property (a house project or apartment block for example)
    else:
        # print unit links and the number of unit links
        print(unit_links)
        print(len(unit_links))

        # iterate through all the units
        unit_link_index = 0 # keep track of index #
        for u_link in unit_links:
            driver.get(u_link)
            time.sleep(2)

            status = True
            while status:
                try:
                    # expand all see alls
                    wait = WebDriverWait(driver, 10)
                    try:
                        see_all = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[text() = 'See all']")))
                        for see in see_all:
                            driver.execute_script("arguments[0].click();", see)
                            prop_label, prop_value = collect_info()

                            # if the collected_info doesn't contain '', stop expanding and break
                            if ('' not in prop_label) and ('' not in prop_value):
                                break
                            time.sleep(3)
                    except TimeoutException:
                        print('TimeoutException2')
                        driver.refresh()
                        time.sleep(3)
                        prop_label, prop_value = collect_info()

                    except StaleElementReferenceException:
                        prop_label, prop_value = collect_info()

                    # if there still exists '' in the collected info, the data is not extracted properly
                    if ('' in prop_label) and ('' in prop_value):
                        detail = {prop_label[i]: prop_value[i] for i in range(len(prop_label))}
                        not_extracted_properly.append([link, detail])
                        print()
                        print("WARNING: DATA NOT EXTRACTED PROPERLY")
                        print()

                    time.sleep(3)
                    print("Link Index: ", link_index-1, "| Unit Link Index: ", unit_link_index, " / ", len(unit_links))
                    unit_link_index += 1
                    name = driver.find_element(By.XPATH,name_xpath).text
                    price = driver.find_element(By.XPATH,price_xpath).text
                    agency = driver.find_element(By.XPATH,"//div[@class = 'agency-details__name agency-details__name--centered']").text

                    # print all the extracted information
                    print(u_link)
                    print(name)
                    print(price)
                    print(agency)
                    print(location)
                    print(prop_label)
                    print(prop_value)
                    detail = {prop_label[i]: prop_value[i] for i in range(len(prop_label))}

                    # save the progress of extracted information into csv files:

                    # result
                    result.append([name, price, location, u_link, agency, detail])
                    result_df = pd.DataFrame(columns = ['property', 'price', 'location', 'link', 'agency', 'detail'], data = result)
                    result_df.to_csv("athome_data_progress.csv", encoding='utf-8-sig')

                    # not_extracted_properly
                    not_extracted_properly_df = pd.DataFrame(not_extracted_properly)
                    not_extracted_properly_df.to_csv("athome_not_extracted_properly.csv", encoding = 'utf-8-sig')

                    # page_not_found
                    page_not_found_df = pd.DataFrame(page_not_found)
                    page_not_found_df.to_csv("athome_page_not_found_list.csv")

                    status = False

                except NoSuchElementException:
                    pass
                except ElementClickInterceptedException:
                    pass

result_df = pd.DataFrame(columns=['property', 'price', 'location', 'link', 'agency', 'detail'], data=result)
result_df.to_csv("athome_data_progress_final.csv", encoding='utf-8-sig')

driver.close()
