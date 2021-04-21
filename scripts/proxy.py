from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
import logging
import random
import awoc
import urllib.request
import socket
import urllib.error
import concurrent.futures
import time
import threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_list_of_proxies_by_continent(continent = "Europe"):
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

def get_list_of_proxies_by_continent_new(continent = "Europe"):
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