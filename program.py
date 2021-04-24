from sites.proshop import scraper as proshop
from sites.elgiganten import scraper as elgiganten
from sites.bilka import scraper as bilka
from sites.fonix import scraper as fonix
from sites.foetex import scraper as foetex
from scripts import dbclient, smtp, proxy
import threading, sys, os, random, time
import concurrent.futures
import pandas as pd
import numpy as np

#proxy.get_random_proxy_from_proxy_list
def scrape_all_shops(proxy_list):
    proshop_scraped = proshop.search_product_list(proxy_list)
    #foetex_scraped = foetex.search_product_list(1,1)
    #elgiganten_scraped = elgiganten.search_product_list(1,1)
    #bilka_scraped = bilka.search_product_list(1,1)
    #fonix_scraped = fonix.search_product_list(1,1)
    #return pd.concat([proshop_scraped, elgiganten_scraped, fonix_scraped, foetex_scraped])
    return proshop_scraped

def get_items_in_stock(df):
    if 'stock' in df:
        df_instock = df[df["stock"] > 0]
        if (df_instock["stock"].any()):
            return df_instock
    return None

def compare_dataframes_colums(df1, df2, column_name = ''):
    return df1[column_name].equals(df2[column_name])

def run_repeatedly():
    print(">>>> Running")
    proxy_list = list(proxy.get_finished_proxy_file())
    df_scraped_old = pd.DataFrame() # Empty for initiation
    while True:
        sleep_time = random.randrange(150, 300)
        df_scraped = scrape_all_shops(proxy_list)
        df_instock = get_items_in_stock(df_scraped)
        if(df_instock is not None):
            if(compare_dataframes_colums(df_scraped, df_scraped_old, 'stock') is False):
                smtp.send_mail_to_all_on_mailing_list("Playstation 5 stock update!", df_instock)
        df_scraped_old = df_scraped.copy()
        print(df_scraped)
        countdown("> Repeating in: ", sleep_time)

def countdown(msg, t):    
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(msg + str(timer), end="\r")
        time.sleep(1)
        t -= 1

def start():
    run_repeatedly()

proxy.proxy_health_start(6)
start() ## Lets start

