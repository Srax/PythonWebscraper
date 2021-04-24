from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.proxy import remove_proxy_from_good_proxies_list
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from fp.fp import FreeProxy
from time import sleep
from glob import glob
import numpy as np
import sys, re, os, locale, random
import pandas as pd

locale.setlocale(locale.LC_NUMERIC,"nl")

timeout = 30

def search_product_list(PROXY_LIST = None):
    print("\t:==== [ SCRAPING PROSHOP ] ====:")
    if PROXY_LIST is not None:
        PROXY = random.choice(PROXY_LIST)
        print("\t" + PROXY)

    """
    This function lods a csv file named TRACKER_PRODUCTS.csv, with headers: [url, code, buy_below]
    It looks for the file under in ./trackers
    
    It also requires a file called SEARCH_HISTORY.xslx under the folder ./search_history to start saving the results.
    An empty file can be used on the first time using the script.
    
    Both the old and the new results are then saved in a new file named SEARCH_HISTORY_{datetime}.xlsx
    This is the file the script will use to get the history next time it runs.

    Parameters
    ----------
    interval_count : TYPE, optional
        DESCRIPTION. The default is 1. The number of iterations you want the script to run a search on the full list.
    interval_hours : TYPE, optional
        DESCRIPTION. The default is 6.

    Returns
    -------
    New .xlsx file with previous search history and results from current search

    """
    prod_tracker = pd.read_csv(os.path.join(os.path.dirname(__file__), 'trackers', 'TRACKER_PRODUCTS.csv'), sep=';')
    prod_tracker_URLS = prod_tracker.url
    tracker_log = pd.DataFrame()
    now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')
    for x, url in enumerate(prod_tracker_URLS):
        if PROXY is not None:    
            webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "httpProxy": PROXY,
                "ftpProxy": PROXY,
                "sslProxy": PROXY,
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
        ua = UserAgent()
        user_agent = ua.chrome
        options.add_experimental_option('excludeSwitches', ['enable-logging']) # Supress Selenium "Driver listening on X" message
        options.add_argument(f'user-agent={user_agent}')
        #options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        
        driver = webdriver.Chrome(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'drivers', 'chromedriver.exe')), chrome_options=options)
        driver.delete_all_cookies()
        #Get the website
        driver.get(url)
        try:
            # Wait for the driver to find body with id 'siteContainer'                
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'siteContainer')))            
            four_o_four = check_exists_by_xpath("//div[contains(@id, 'productList')]", driver)
            captcha = check_exists_by_class_name("cf-captcha-container", driver)
            if captcha is True:
                print("\tErr: Reached Captcha Page!!")
                remove_proxy_from_good_proxies_list(PROXY)
            if four_o_four is False and captcha is False:
                try:
                    title = driver.find_element_by_xpath("//h1[@data-type='product'][@product-display-name='']").text
                except:
                    title = None
                try:    
                    price = round(float(locale.atof(driver.find_element_by_xpath("//span[@class='site-currency-wrapper']//span[@class='site-currency-attention']").text.replace("kr.", "").strip())))
                except:
                    price = 0
                
                # Check stock
                try:
                    stockList = driver.find_elements_by_xpath("//b[contains(@class, 'site-sasdsatock') and contains(@class, 'pull-right')]")
                    stockListText = []
                    for elem in stockList:
                        stockListText.append(int(elem.get_attribute('textContent').replace(".", "").replace("stk", "").replace("+", "").strip()))
                    stock = sum(stockListText)
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
                print("\t> Added", prod_tracker.company[x], ':', title)           
                sleep(1)
            else:
                print("\tErr: Reached 404 Page...")
        except TimeoutException as ex:
            print("\tErr: Site couldn't be reached...")
            remove_proxy_from_good_proxies_list(PROXY)
            PROXY = random.choice(PROXY_LIST)
        except Exception as ex:
            if "ERR_PROXY_CONNECTION_FAILED" in ex.msg:
                print("Err: Proxy Failed!")
                remove_proxy_from_good_proxies_list(PROXY)
                PROXY = random.choice(PROXY_LIST)
            else:
                print("Unknown Error: ", ex)
        finally:
            driver.quit()
    
    # after the run, checks last search history record, and appends this run results to it, saving a new file
    #last_search = glob("search_history/*.xlsx")[-1] # path to file in the folder
    #search_hist = pd.read_excel(last_search)
    
    #final_df = search_hist.append(tracker_log, sort=False)    
    #final_df.to_excel('search_history/SEARCH_HISTORY_{}.xlsx'.format(now), index=False)
    print(':==== [SCRAPE COMPLETE] ====:\n')
    return tracker_log

def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_class_name(class_name, driver):
    try:
        driver.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return False
    return True