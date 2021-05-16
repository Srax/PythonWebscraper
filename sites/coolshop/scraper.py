from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.proxy import remove_proxy_from_good_proxies_list
from progress.bar import Bar as Progress_Slider
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
import re, os, locale, random
import logging
import pandas as pd

locale.setlocale(locale.LC_NUMERIC,"nl")

timeout = 30
_PROXY = None
_PROXY_LIST = None

def start(PROXY_LIST = None):
    global _PROXY_LIST
    global _PROXY

    prod_tracker = pd.read_csv(os.path.join(os.path.dirname(__file__), 'trackers', 'TRACKER_PRODUCTS.csv'), sep=';')
    prod_tracker_URLS = prod_tracker.url
    tracker_log = pd.DataFrame()
    if PROXY_LIST is not None:
        _PROXY_LIST = PROXY_LIST
        _PROXY = random.choice(PROXY_LIST)

    with Progress_Slider('Coolshop\t\t', max=len(prod_tracker_URLS)) as slider:
        for index, url in enumerate(prod_tracker_URLS):
            try:
                driver = driver_setup(_PROXY)
                data = scrape(url, driver)
                if(data is not None):
                    data["company"] = prod_tracker.company[index]
                    data.set_index("company", inplace=True)
                    tracker_log = tracker_log.append(data)
            except Exception as ex:
                remove_proxy_from_good_proxies_list(_PROXY)
                if _PROXY_LIST is not None:
                    _PROXY = random.choice(_PROXY)
                logging.error(ex)
                return None
            finally:
                slider.next()
                driver.quit()
    return tracker_log

def scrape(url, driver):
    global _PROXY_LIST
    global _PROXY
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        loader = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, 'thing-header')))

        if loader is not None:
            try:
                title = soup.find("div", {"class": "thing-header"}).text.replace("\n", "").strip()
            except:
                title = None
            try:
                price = round(float(extract_integer_from_text(soup.find("div", {"class": "price-with-decimal-large"}).text)))
            except:
                price = 0
            try:
                stock = soup.find("div", {"class":"thing-stock-stock-status--in-stock"}).text
                stock = 1
            except:
                stock = 0

            now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')

            scraped_data = {
                'title': str(title),
                'price': int(price),
                'stock': stock,
                'date': now.replace("h", ":").replace("m", ""),
                'url': str(url)
            }
            return pd.DataFrame(data=scraped_data, index=[0])
        else:
            return None
    except Exception as ex:
        remove_proxy_from_good_proxies_list(_PROXY)
        if _PROXY_LIST is not None:
            _PROXY = random.choice(_PROXY)
        logging.error(ex)
        return None

def driver_setup(PROXY = None):
    if PROXY is not None:    
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType":"MANUAL",
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
    driver = webdriver.Chrome(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'drivers', 'chromedriver.exe')), chrome_options=options)
    driver.delete_all_cookies()
    return driver

def extract_integer_from_text(text):
    num = [float(s) for s in re.findall(r'-?\d+\.?\d*', text)] 
    return int(round(num[0]))