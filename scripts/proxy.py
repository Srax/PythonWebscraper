from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
import logging
import random
import awoc

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

def get_list_of_proxies():
    return RequestProxy(log_level=logging.ERROR).get_proxy_list() # you may get different number of proxy when  you run this at each time

def get_random_proxy_from_proxy_list(proxy_list):
    return random.choice(proxy_list)