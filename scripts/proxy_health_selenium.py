import math
import os
import os.path
import requests
from threading import Thread
import sys
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import sys
import numpy as np

timeout = 15
good_list = []


def verify_list(thread_number, proxy_list):
    global good_list, timeout
    working_list = []
    for proxy in proxy_list:
        try:
            webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "httpProxy":proxy,
                "ftpProxy":proxy,
                "sslProxy":proxy,
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
            options.add_experimental_option('excludeSwitches', ['enable-logging']) # Supress Selenium "Driver listening on X" message
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
            driver = webdriver.Chrome(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'drivers', 'chromedriver.exe')), options=options)
            driver.delete_all_cookies()            
            driver.set_page_load_timeout(timeout)
            try:
                driver.get("https://www.proshop.dk/Skaerm/ASUS-24-Skaerm-ROG-STRIX-XG258Q-AURA-RGB-Sort-1-ms-Adaptive-V-Sync/2617490")
                #print('[Thread:', thread_number, '] Current IP:', ip)
                #print('[Thread:', thread_number, '] match:', True if ip == prox.split(':')[0] else False)
                try:
                    title = driver.title
                except:
                    title = None
                    
                if title is not None:
                    print('[Thread:', thread_number, '] Proxy works:', proxy)
                    working_list.append(proxy)
            except TimeoutException as e:
                print('[Thread:', thread_number, '] Proxy timed out: ', e)
                driver.quit()

        except Exception as e:
            print('[Thread:', thread_number, '] Proxy failed', proxy)
            print('[Thread:', thread_number, '] Proxy failed', e)
        #print('[Thread:', thread_number, '] Working Proxies:', working_list)
    good_list += working_list


def get_proxy_list():
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


def get_proxies(files):
    proxy_list = []
    for file in files:
        for prox in open(file, 'r+').readlines():
            proxy_list.append(prox.strip())
    return proxy_list


#def setup(number_threads):
#    thread_amount = float(number_threads)
#    #proxy_list = get_proxies(get_proxy_list())
#    proxy_list = proxy.get_list_of_proxies_by_continent_new("Europe")
#    #amount = int(math.ceil(len(proxy_list)/thread_amount))
#    #proxy_lists = [proxy_list[x:x+amount] for x in range(0, len(proxy_list), amount)]
#    #if len(proxy_list) % thread_amount > 0.0:
#    #    proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
#    return proxy_list

def setup(number_threads, proxy_l):
    thread_amount = float(number_threads)
    #proxy_list = get_proxies(get_proxy_list())
    proxy_list = proxy_l
    print(":==== [PROXY COUNT: " + str(len(proxy_list)) + "] ====:")
    amount = int(math.ceil(len(proxy_list)/thread_amount))
    proxy_lists = [proxy_list[x:x+amount] for x in range(0, len(proxy_list), amount)]
    if len(proxy_list) % thread_amount > 0.0:
        proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
    return proxy_lists

def start(threads, proxy_list):
    start_time = time.time()
    lists = setup(threads, proxy_list)
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

    f = open('good_proxies_list.txt', 'w+')
    to_write = ''
    for i in good_list:
        to_write += i+'\n'
    f.write(to_write)
    f.close()
    stop_time = time.time()
    print('[{0:.2f} seconds]'.format(stop_time-start_time))
    time.sleep(1)

#if __name__ == "__main__":
#    if len(sys.argv) > 1:
#        start(sys.argv[1])
#    else:
#        start(input('How many threads you would like to test proxies with: '))