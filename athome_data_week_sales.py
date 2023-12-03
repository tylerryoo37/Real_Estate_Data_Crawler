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
from lxml import html
import requests
import random
from retry import retry

'''CHANGE FILE NAME BEFORE RUNNING:'''

filename = 'athome_links_final_01_23_2023.csv'

date_csv = filename.split("final_",1)[1]
print(date_csv)

# today = date.today()
# d1 = str(today.strftime("%m/%d/%Y"))
# d1 = d1.replace("/", "_")
# print(d1)

# Read only links and locations that were newly updated
links = pd.read_csv(filename).proj_link.to_list()
locations = pd.read_csv(filename).location.to_list()
# link_df = pd.read_csv(filename)
# links = link_df[link_df['collect_status'] != 'already_collected'].proj_link.to_list()
# locations = link_df[link_df['collect_status'] != 'already_collected'].location.to_list()

start = time.time()

# The xpath gets updated. Edit if code doesn't run
# name_xpath = "//h1[@class = 'KeyInfoBlockStyle__PdpTitle-sc-1o1h56e-2 ilPGib']"
name_xpath = "//*[@id='app']/div/div/div[1]/div/div/article/div[1]/div[1]/section[1]/h1/text()"
price_xpath = "//div[@class = 'KeyInfoBlockStyle__Price-sc-1o1h56e-5 fpNLMn']/h2"
sold_xpath = "//p[@class = 'KeyInfoBlockStyle__SubTitleSold-sc-1o1h56e-3 ipdzgi']/span"
sold_date = "//*[@id='app']/div/div/div[1]/div/div/article/div[1]/div[1]/section[1]/p/text()"

agency_xpath = "//div[@class = 'agency-details__name agency-details__name--centered']"
unit_xpath = "//div[@class = 'residence-type select']/a/@href"
char_name_xpath = "//div[@class = 'feature-bloc-content-specification-content-name']"
char_value_xpath = "//div[@class = 'feature-bloc-content-specification-content-response']/div"
char_energy_xpath = "//div[@class = 'feature-bloc-content-specification-content-response']/div/label/span"

# Index to specific links
link_index = 0
links = links[link_index:]
locations = locations[link_index:]

''' Three main lists that will be used to create dataframes and csv files '''
# result: used to extract all values of each property
result = []
# page_not_found: used to keep track of pages that expired
page_not_found = []


def collect_info():
    char_name = dom.xpath(char_name_xpath)
    label = [i.text for i in char_name]

    # all the feature values extracted except energy
    char_value = dom.xpath(char_value_xpath)
    value = [i.text for i in char_value]

    char_energy = dom.xpath(char_energy_xpath)
    energy = [j.text for j in char_energy]

    # used to replace None values with energy class
    for index, item in enumerate(value):
        if item is None:
            value[index] = energy[0]
            energy.remove(energy[0])

    if ('' in label) or ('' in value) or (None in value):
        print("VALUE NOT EXTRACTED PROPERLY: FIX ERROR")

    detail = {label[i]: value[i] for i in range(len(label))}

    return detail


window = 6.1
chrome = random.randint(0,105)
chrome_2 = random.randint(149, 5000)

for link, location in zip(links, locations):

    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    #            'Content-Type' : 'text/html'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT ' + str(window) + '; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' + str(chrome) + '.0.3626.' + str(chrome_2) + ' Safari/537.36',
               'Content-Type': 'text/html'}
    if link_index % 100 == 0:
        print()
        print(headers)
        print()
        window += 0.1
        window = round(window, 2)
        chrome = random.randint(0,105)
        chrome_2 = random.randint(149, 5000)

    # locate link index
    print("Link Index: ", link_index, "|", link)
    link_index += 1
    print(link)
    webpage = requests.get(link, headers = headers)
    time.sleep(0.05)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    dom = etree.HTML(str(soup))
    # dom = html.fromstring(webpage.content)

    # keep track of pages that expired
    if webpage.status_code == 404 or webpage.status_code == 410:
        print(link_index - 1, "PAGE NOT FOUND")
        page_not_found.append([link, webpage.status_code])
        name, price, location, agency, detail = '', '', '', '', ''

        result.append([name, price, location, link, link, agency, detail])
        result_df = pd.DataFrame(columns=['property', 'price', 'location', 'proj_link', 'link', 'agency', 'detail'], data=result)
        file_name = "athome_data_final_" + str(date_csv)
        result_df.to_csv(file_name, encoding='utf-8-sig')

        # page_not_found
        page_not_found_df = pd.DataFrame(columns = ['link', 'expire_status'], data = page_not_found)
        file_name = "athome_expired_final_" + str(date_csv)
        page_not_found_df.to_csv(file_name)
        continue

    # if page not expired
    else:
        print(link_index - 1, "PAGE RUN SUCCESSFULLY")

        # extract name, price, and agency from the link
        try:
            name = dom.xpath(name_xpath)[0]
        except IndexError:
            i = 0
            while i < 100:
                try:
                    print("RETRYING...")
                    i += 1
                    window = 6.1
                    chrome = random.randint(0, 105)
                    chrome_2 = random.randint(149, 5000)
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT ' + str(
                        window) + '; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' + str(
                        chrome) + '.0.3626.' + str(chrome_2) + ' Safari/537.36',
                               'Content-Type': 'text/html'}
                    webpage = requests.get(link, headers=headers, timeout=5)
                    print(link)
                    soup = BeautifulSoup(webpage.content, 'html.parser')
                    dom = etree.HTML(str(soup))
                    time.sleep(3)
                    name = dom.xpath(name_xpath)[0]
                    i = 100
                    print("if" + i + "is: 100, RETRY IS DONE!")
                except IndexError:
                    print("ERROR STILL OCCURS")
                    continue

        try:
            price = dom.xpath(price_xpath)[0].text
        except IndexError:
            try:
                date = dom.xpath(sold_date)[1]
                price = dom.xpath(sold_xpath)[0].text + " " + date
            except IndexError:
                price = dom.xpath(sold_xpath)[0].text
        # catching the case when the page is not fully loaded
        try:
            agency = dom.xpath(agency_xpath)[0].text
        except IndexError:
            continue

        # find all the units that fall under property project
        unit = dom.xpath(unit_xpath)
        unit_links = ["http://athome.lu" + i for i in unit]

    # Case 1: If the link only has one property (not a house project or apartment block for example)
    if len(unit_links) == 0:
        # print the information collected from above
        print(name)
        print(price)
        print(agency)
        print(link)
        print(location)

        # collect feature information
        detail = collect_info()
        print(detail)

        page_not_found.append([link, webpage.status_code])

        # save the progress of extracted information into csv files:

        # result
        result.append([name, price, location, link, link, agency, detail])
        result_df = pd.DataFrame(columns=['property', 'price', 'location', 'proj_link', 'link', 'agency', 'detail'], data=result)
        file_name = "athome_data_final_" + str(date_csv)
        result_df.to_csv(file_name, encoding='utf-8-sig')

        # page_not_found
        page_not_found_df = pd.DataFrame(columns = ['link', 'expire_status'], data = page_not_found)
        file_name = "athome_expired_final_" + str(date_csv)
        page_not_found_df.to_csv(file_name)

    # Case 2: If there are more than one property in each listing
    else:
        # print unit links and the number of unit links
        print("Length of Unit Links: ", len(unit_links) - 1)

        # iterate through all the units
        unit_link_index = 0  # keep track of index
        for u_link in unit_links:
            webpage = requests.get(u_link, headers=headers)
            # time.sleep(0.05)
            soup = BeautifulSoup(webpage.content, 'html.parser')
            # print(soup)
            dom = etree.HTML(str(soup))

            if webpage.status_code == 404 or webpage.status_code == 410:
                print(link_index - 1, "PAGE NOT FOUND")
                page_not_found.append([link, webpage.status_code])
                name, price, location, agency, detail = '', '', '', '', ''
                continue
            else:
                print(link_index - 1, "PAGE RUN SUCCESSFULLY")
                page_not_found.append([u_link, webpage.status_code])

                detail = collect_info()

                print("Link Index: ", link_index - 1, "| Unit Link Index: ", unit_link_index, " / ", len(unit_links) - 1)

                unit_link_index += 1
                try:
                    name = dom.xpath(name_xpath)[0]
                except IndexError:
                    webpage = requests.get(u_link, headers=headers)
                    # time.sleep(0.05)
                    soup = BeautifulSoup(webpage.content, 'html.parser')
                    dom = etree.HTML(str(soup))
                    name = dom.xpath(name_xpath)[0]

                try:
                    price = dom.xpath(price_xpath)[0].text
                except IndexError:
                    try:
                        date = dom.xpath(sold_date)[1]
                        price = dom.xpath(sold_xpath)[0].text + " " + date
                    except IndexError:
                        price = dom.xpath(sold_xpath)[0].text

                agency = dom.xpath(agency_xpath)[0].text

                # print all the extracted information
                print(name)
                print(price)
                print(location)
                print(link)
                print(unit_links)
                print(agency)
                print(detail)

            # save the progress of extracted information into csv files:

            # result
            result.append([name, price, location, link, u_link, agency, detail])
            result_df = pd.DataFrame(columns=['property', 'price', 'location', 'proj_link', 'link', 'agency', 'detail'], data=result)
            file_name = "athome_data_final_" + str(date_csv)
            result_df.to_csv(file_name, encoding='utf-8-sig')

            # page_not_found
            page_not_found_df = pd.DataFrame(columns=['link', 'expire_status'], data=page_not_found)
            file_name = "athome_expired_final_" + str(date_csv)
            page_not_found_df.to_csv(file_name)

result_df = pd.DataFrame(columns=['property', 'price', 'location', 'proj_link', 'link', 'agency', 'detail'], data=result)
file_name = "athome_data_final_" + str(date_csv)
result_df.to_csv(file_name, encoding='utf-8-sig')

end = time.time()

print(round(((end - start) / 60 / 60), 1))
