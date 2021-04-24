from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import random, awoc, socket, time, math
from fake_useragent import UserAgent
from selenium import webdriver
from threading import Thread
import concurrent.futures
import threading, time
import multiprocessing
import urllib.request
import urllib.error
import numpy as np
import logging
import os.path

timeout = 30
good_list = []


def get_list_of_proxies_by_continent_detailed(continent = "Europe"):
    try:
        countries = awoc.AWOC().get_countries_list_of(continent)
        all_proxy_list = get_list_of_proxies()

        proxy_list = []
        for proxy in all_proxy_list:
            x = proxy.country in countries
            if x is True:
                proxy_list.append(proxy)
        return proxy_list
    except:
        print("No proxies found...")

def get_list_of_proxies_by_continent_string(continent = "Europe"):
    try:
        countries = awoc.AWOC().get_countries_list_of(continent)
        all_proxy_list = get_list_of_proxies()

        proxy_list = []
        for proxy in all_proxy_list:
            x = proxy.country in countries
            if x is True:
                proxy_list.append(proxy.ip + ":" + proxy.port)
        return proxy_list
    except:
        print("No proxies found...")

def get_list_of_proxies():
    return RequestProxy(log_level=logging.ERROR).get_proxy_list() # you may get different number of proxy when  you run this at each time

def get_random_proxy_from_proxy_list(proxy_list):
    return random.choice(proxy_list)


def is_bad_proxy(pip):  
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': pip})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req=urllib.request.Request('http://www.example.com')  # change the URL to test here
        sock=urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        #print('Error code: ', e.code)
        return e.code
    except Exception as detail:
        #print("ERROR:", detail)
        return True
    return False


def verify_list(thread_number, proxy_list):
    global good_list, timeout
    working_list = []
    for proxy in proxy_list:
        try:
            webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "httpProxy": proxy,
                "ftpProxy": proxy,
                "sslProxy": proxy,
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
            
            driver = webdriver.Chrome(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'drivers', 'chromedriver.exe')), options=options)
            driver.delete_all_cookies()
            driver.get("https://www.proshop.dk/Spillekonsol/Sony-PlayStation-5-Nordic/2831713")
            try:
                 # Wait for the driver to find body with id 'siteContainer'                
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'siteContainer')))   
                four_o_four = check_exists_by_xpath("//div[contains(@id, 'productList')]", driver)
                captcha = check_exists_by_class_name("cf-captcha-container", driver)
                if captcha is True:
                    print('[Thread:', thread_number, '] Proxy reached captcha page: ', e)
                if four_o_four is False and captcha is False:             
                    print('[Thread:', thread_number, '] Proxy works:', proxy)
                    #working_list.append(proxy)
                    add_good_proxy_to_file(proxy)
            except TimeoutException as e:
                print('[Thread:', thread_number, '] Proxy timed out: ', e)
            except Exception as ex:
                print("Unknown Error: ", ex)
        except Exception as ex:
            print("Unknown Error: ", ex)
            print('[Thread:', thread_number, '] Proxy failed', proxy)
            print('[Thread:', thread_number, '] Proxy failed', ex)
        #print('[Thread:', thread_number, '] Working Proxies:', working_list)
        finally:
            driver.quit()
    good_list += working_list


def get_test_proxy_file():
    directory = './'
    file = os.path.abspath(__file__)
    for i in sorted(range(len(file)), reverse=True):
        if '/' in file[i] or '\\' in file[i]:
            directory = file[:i+1]
            break
    file_list = os.listdir(directory)
    proxy_list = []
    for file in file_list:
        if len(file) > 12:
            if file[:8] == 'proxies_':
                    proxy_list.append(directory+file)
    return proxy_list

def get_finished_proxy_file():
    proxy_list = list()
    proxy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets', 'good_proxies_list.txt'))
    with open(proxy_file) as my_file:
        for line in my_file:
            proxy_list.append(str(line.strip("\n")))
    return proxy_list


def get_proxies_from_file(files):
    proxy_list = []
    for file in files:
        for prox in open(file, 'r+').readlines():
            proxy_list.append(prox.strip())
    return proxy_list

def proxy_health_setup(number_threads, proxy_l):
    thread_amount = float(number_threads)
    #proxy_list = get_proxies_from_file(get_test_proxy_list())
    proxy_list = proxy_l
    print(":==== [PROXY COUNT: " + str(len(proxy_list)) + "] ====:")
    amount = int(math.ceil(len(proxy_list)/thread_amount))
    proxy_lists = [proxy_list[x:x+amount] for x in range(0, len(proxy_list), amount)]
    if len(proxy_list) % thread_amount > 0.0:
        proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
    return proxy_lists

def proxy_health_start(threads = None, *proxy_list):
    if threads is None:
        threads = round(multiprocessing.cpu_count() / 2)
        print(">>>> Running with", threads, "threads" )
    else:
        print(">>>> Running with", str(threads), "threads" )
    if proxy_list is not None:
        proxy_list = get_list_of_proxies_by_continent_string("Europe")
    start_time = time.time()
    lists = proxy_health_setup(threads, proxy_list)
    thread_list = []
    count = 0
    for l in lists:
        
        time.sleep(1)
        thread_list.append(Thread(target=verify_list, args=(count, l)))
        thread_list[len(thread_list)-1].start()
        count += 1

    for x in thread_list:
        x.join()

    print('[All] Working Proxies:', good_list)

    #proxy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets', 'good_proxies_list.txt'))
    #f = open(proxy_file, 'w+')
    #to_write = ''
    #for i in good_list:
    #    to_write += i+'\n'
    #f.write(to_write)
    #f.close()
    stop_time = time.time()
    print('[{0:.2f} seconds]'.format(stop_time-start_time))
    time.sleep(1)

def add_good_proxy_to_file(proxy):
    proxy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets', 'good_proxies_list.txt'))
    with open(proxy_file, "a") as prox_file:
        prox_file.write(proxy+'\n')
        prox_file.close()


def remove_proxy_from_good_proxies_list(proxy):
    proxy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets', 'good_proxies_list.txt'))
    with open(proxy_file, "r") as f:
        lines = f.readlines()
    with open(proxy_file, "w") as f:
        for line in lines:
            if line.strip("\n") != proxy:
                f.write(line)
    print(">>>> Removed", proxy, "from", 'good_proxies_list.txt')


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