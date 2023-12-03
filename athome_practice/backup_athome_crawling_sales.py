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
links = pd.read_csv("test_athome_links_progress_final.csv").links.to_list()
locations = pd.read_csv("test_athome_links_progress_final.csv").locations.to_list()

link_index = 3653
links = links[link_index:]
locations = locations[link_index:]

# Locate the chrome driver
s = Service('/Users/tylerryoo/PycharmProjects/luxembourg_crawling_hass/chromedriver')
driver = webdriver.Chrome(service=s)

result = []
not_extracted_properly = []
page_not_found = []
first = True
# Iterate through the links
for link, location in zip(links, locations):
    print("Link Index: ", link_index, "|" , link)
    link_index += 1
    try:
        driver.get(link)
        time.sleep(2)

    except TimeoutException:
        print("TimeoutException!")
        time.sleep(10)
        driver.refresh()
        driver.get(link)

    # If it's the first link --> handle accept cookies button
    if first:
        # Accept Cookies
        # driver.refresh()
        # time.sleep(10)
        driver.find_element(By.XPATH, "//button[@id = 'onetrust-accept-btn-handler']").click()
        first = False
    try:
        # print('try extracting')
        name = driver.find_element(By.XPATH, "//h1[@class = 'KeyInfoBlockStyle__PdpTitle-sc-1o1h56e-2 ilPGib']").text #sometimes this xpath changes
        price = driver.find_element(By.XPATH, "//div[@class = 'KeyInfoBlockStyle__Price-sc-1o1h56e-5 fpNLMn']").text #sometimes this xpath changes
        agency = driver.find_element(By.XPATH, "//div[@class = 'agency-details__name agency-details__name--centered']").text

        # print('try extracting')
        # find all the units that fall under property project
        unit = driver.find_elements(By.XPATH, "//div[@class = 'residence-type select']/a")
        unit_links = [u.get_attribute('href') for u in unit]
        # print('try extracting')

    except NoSuchElementException:
        print(link_index - 1, "PAGE NOT FOUND")
        page_not_found.append(link_index)
        continue


    if len(unit_links) == 0:
        print(link)
        print(name)
        print(price)
        print(agency)
        print(location)

        status = True
        while status:
            try:
                # expand all
                wait = WebDriverWait(driver, 10)
                try:
                    see_all = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[text() = 'See all']")))
                    for see in see_all:
                        driver.execute_script("arguments[0].click();", see)
                except TimeoutException:
                    print("No See all")
                    pass

                        char_name = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-name']")
                        label = [ch_name.text for ch_name in char_name]
                        print(label)
                        # print([ch_name.text for ch_name in char_name])
                        char_val = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-response']")
                        value = [ch_val.text for ch_val in char_val]
                        # print([ch_val.text for ch_val in char_val])

                        if ('' not in label) and ('' not in value) and len(see_all):
                            break
                        time.sleep(3)

                        if ('' in label) and ('' in value):
                            detail = {label[i]: value[i] for i in range(len(label))}
                            not_extracted_properly.append([link, detail])
                            print()
                            print("WARNING: DATA NOT EXTRACTED PROPERLY")
                            print()

                # char_name = driver.find_elements(By.XPATH,"//div[@class = 'feature-bloc-content-specification-content-name']")
                # label = [ch_name.text for ch_name in char_name]
                print(label)
                # print([ch_name.text for ch_name in char_name])
                # char_val = driver.find_elements(By.XPATH,"//div[@class = 'feature-bloc-content-specification-content-response']")
                # value = [ch_val.text for ch_val in char_val]
                print(value)
                # print([ch_val.text for ch_val in char_val])
                detail = {label[i]: value[i] for i in range(len(label))}

                result.append([name, price, location, link, agency, detail])
                result_df = pd.DataFrame(columns=['property', 'price', 'location', 'link', 'agency', 'detail'], data= result)
                result_df.to_csv("test_athome_data_progress.csv", encoding='utf-8-sig')
                not_extracted_properly_df = pd.DataFrame(not_extracted_properly)
                not_extracted_properly_df.to_csv("test_athome_not_extracted_properly.csv", encoding = 'utf-8-sig')
                page_not_found_df = pd.DataFrame(page_not_found)
                page_not_found_df.to_csv("page_not_found_list.csv")

                status = False

            except NoSuchElementException:
                pass
            except ElementClickInterceptedException:
                pass



    else:
        print(unit_links)
        print(len(unit_links))

        # iterate through all the units
        unit_link_index = 0
        for u_link in unit_links:
            driver.get(u_link)
            time.sleep(2)

            status = True
            while status:
                try:
                    # expand all
                    see_all = driver.find_elements(By.XPATH, "//div[text() = 'See all']")
                    for see in see_all:
                        driver.execute_script("arguments[0].click();", see)
                        char_name = driver.find_elements(By.XPATH,"//div[@class = 'feature-bloc-content-specification-content-name']")
                        label = [ch_name.text for ch_name in char_name]
                        # print([ch_name.text for ch_name in char_name])
                        char_val = driver.find_elements(By.XPATH,"//div[@class = 'feature-bloc-content-specification-content-response']")
                        value = [ch_val.text for ch_val in char_val]
                        # print([ch_val.text for ch_val in char_val])
                        if ('' not in label) and ('' not in value):
                            break
                        time.sleep(3)

                        # except ElementNotInteractableException:
                        #     driver.execute_script("arguments[0].click();", see)
                        #     time.sleep(3)
                        #     break

                    if ('' in label) and ('' in value):
                        detail = {label[i]: value[i] for i in range(len(label))}
                        not_extracted_properly.append([link, detail])
                        print()
                        print("WARNING: DATA NOT EXTRACTED PROPERLY")
                        print()

                    time.sleep(3)
                    print("Link Index: ", link_index-1, "| Unit Link Index: ", unit_link_index, " / ", len(unit_links))
                    unit_link_index += 1
                    print(u_link)
                    name = driver.find_element(By.XPATH,"//h1[@class = 'KeyInfoBlockStyle__PdpTitle-sc-1o1h56e-2 hWEtva']").text
                    print(name)
                    price = driver.find_element(By.XPATH,"//div[@class = 'KeyInfoBlockStyle__Price-sc-1o1h56e-5 eWOlhG']").text
                    print(price)
                    agency = driver.find_element(By.XPATH,"//div[@class = 'agency-details__name agency-details__name--centered']").text
                    print(agency)
                    print(location)
                    print(label)
                    print(value)
                    # char_name = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-name']")
                    # print([ch_name.text for ch_name in char_name])
                    # label = [ch_name.text for ch_name in char_name]
                    # char_val = driver.find_elements(By.XPATH, "//div[@class = 'feature-bloc-content-specification-content-response']")
                    # value = [ch_val.text for ch_val in char_val]
                    # print([ch_val.text for ch_val in char_val])
                    detail = {label[i]: value[i] for i in range(len(label))}

                    result.append([name, price, location, u_link, agency, detail])
                    result_df = pd.DataFrame(columns = ['property', 'price', 'location', 'link', 'agency', 'detail'], data = result)
                    result_df.to_csv("test_athome_data_progress.csv", encoding='utf-8-sig')
                    not_extracted_properly_df = pd.DataFrame(not_extracted_properly)
                    not_extracted_properly_df.to_csv("test_athome_not_extracted_properly.csv", encoding = 'utf-8-sig')
                    page_not_found_df = pd.DataFrame(page_not_found)
                    page_not_found_df.to_csv("page_not_found_list.csv")

                    status = False

                except NoSuchElementException:
                    pass
                except ElementClickInterceptedException:
                    pass

result_df = pd.DataFrame(columns=['property', 'price', 'location', 'link', 'agency', 'characteristics'], data=result)
result_df.to_csv("test_athome_data_progress_final.csv", encoding='utf-8-sig')

driver.close()




# driver.execute_script("window.scrollTo(0,  3000)")
# document.body.scrollHeight

#     curr_height = driver.execute_script("return document.documentElement.scrollHeight")
#     if curr_height == prev_height:
#         break
#     prev_height = curr_height