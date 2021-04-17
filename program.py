from sites.proshop import scraper as proshop
from sites.elgiganten import scraper as elgiganten
from sites.bilka import scraper as bilka
from sites.fonix import scraper as fonix
from scripts import dbclient, smtp
import concurrent.futures
import pandas as pd
import threading
import sys, os
import random
import time

def scrape_all_shops():
    bilka_scraped = bilka.search_product_list(1,random.randint(1, 10))
    proshop_scraped = proshop.search_product_list(1,random.randint(1, 10))
    elgiganten_scraped = elgiganten.search_product_list(1,random.randint(1, 10))
    fonix_scraped = fonix.search_product_list(1,random.randint(1, 10))
    return pd.concat([proshop_scraped, elgiganten_scraped, bilka_scraped, fonix_scraped])

def get_items_in_stock(df):
    if 'stock' in df:
        df_instock = df[df["stock"] > 0]
        if (df_instock["stock"].any()):
            return df_instock
    return None

def compare_dataframes_colums(df1, df2, column_name = ''):
    return df1[column_name].equals(df2[column_name])

def run_repeatedly():
    print("running")
    df_scraped_old = pd.DataFrame() # Empty for initiation
    while True:
        sleep_time = random.randint(10, 30)
        df_scraped = scrape_all_shops()
        df_instock = get_items_in_stock(df_scraped)
        if(df_instock is not None):
            if(compare_dataframes_colums(df_scraped, df_scraped_old, 'stock') is False):
                smtp.send_mail_to_all_on_mailing_list("Playstation 5 stock update!", df_instock)
        df_scraped_old = df_scraped.copy()
        print(df_scraped)
        print("\nRepeating in " + str(sleep_time) + " seconds...\n")
        time.sleep(sleep_time)


try:
    run_repeatedly()
except:
    print("Bruh")
finally:
    run_repeatedly()



#threads = []
#bilka_thread = threading.Thread(target=bilka.search_product_list, args=(1,1))
#proshop_thread = threading.Thread(target=proshop.search_product_list, args=(1,1))
#elgiganten_thread = threading.Thread(target=elgiganten.search_product_list, args=(1,1))
#fonix_thread = threading.Thread(target=fonix.search_product_list, args=(1,1))
#threads = [bilka_thread, proshop_thread, elgiganten_thread, fonix_thread]
# Start all threads
#for x in threads:
#    x.start()
#for x in threads:
#    x.join()