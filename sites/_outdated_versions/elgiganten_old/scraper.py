from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from glob import glob
import pandas as pd
import sys, re, os, random


def search_product_list(interval_count = 1, interval_hours = 6):
    try:
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy":'23.251.138.105:8080',
            "ftpProxy":'23.251.138.105:8080',
            "sslProxy":'23.251.138.105:8080',
            "noProxy":None,
            "proxyType":"MANUAL",
            "class":"org.openqa.selenium.Proxy",
            "autodetect":False
        }

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('log-level=3')
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        driver = webdriver.Chrome(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'drivers', 'chromedriver.exe')), chrome_options=options)
        driver.delete_all_cookies()


        #print(":==== [PROXY IP: " + str(PROXY) + "] ====:")
        prod_tracker = pd.read_csv(os.path.join(os.path.dirname(__file__), 'trackers', 'TRACKER_PRODUCTS.csv'), sep=';')
        prod_tracker_URLS = prod_tracker.url
        tracker_log = pd.DataFrame()
        now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')
        interval = 0 # counter reset
        while interval < interval_count:
            for x, url in enumerate(prod_tracker_URLS):
                #Get the website
                try:
                    driver.get(url)
                    try:
                        four_o_four = check_exists_by_xpath("//*[contains(@class, 'error-page')]", driver)
                        if(four_o_four is False):
                            try:
                                title = driver.find_element_by_class_name("product-title").text
                            except:
                                title = None
                            try:    
                                price = int(driver.find_element_by_xpath("//div[@class='product-price-container']//span").get_attribute('textContent').replace("\xa0", ""))
                            except:
                                price = 0
                            
                            # Check stock
                            try:
                                stock = driver.find_element_by_xpath("//span[@class='items-in-stock align-left']//span[@class='checkout-spacing']").text
                                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', stock)]
                                stock = round(s[0])
                            except:
                                stock = 0

                            log = pd.DataFrame({
                                'date': now.replace("h", ":").replace("m", ""),
                                'company': str(prod_tracker.company[x]), # this code comes from the TRACKER_PRODUCTS file
                                'title': str(title),
                                'price': int(price),
                                'stock': int(stock),
                                'url': str(url)
                            },index=[x])

                            tracker_log = tracker_log.append(log)
                            print("\tAdded " + prod_tracker.company[x] +' > ' + title)           
                            sleep(1)
                        else:
                            print("\tProduct not found...")

                    except TimeoutException:
                        print("Err: Site couldn't be reached...")
                except:
                    print("Err: Something wen't wrong...")
            
            interval += 1# counter update
            
            sleep(interval_hours*1*1)
            print('\t> End of interval '+ str(interval))
        print(':==== [SCRAPE COMPLETE] ====:\n')
        return tracker_log
    except TimeoutException as ex:
        print(ex)
    finally:
        driver.quit()
        

def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True