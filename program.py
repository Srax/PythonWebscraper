from sites.proshop import scraper as proshop
from sites.elgiganten import scraper as elgiganten
from sites.saling_group import scraper as saling
from sites.fonix import scraper as fonix
from sites.coolshop import scraper as coolshop
from scripts import dbclient, smtp, proxy
import random, time
import pandas as pd
import logging

logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.ERROR)

#proxy.get_random_proxy_from_proxy_list
def scrape_all_shops(proxy_list):
    proshop_scraped = proshop.start(None)
    elgiganten_scraped = elgiganten.start(None)
    saling_scraped = saling.start(None)
    fonix_scraped = fonix.start(None)
    coolshop_scraped = coolshop.start(None)
    return pd.concat([proshop_scraped, elgiganten_scraped, saling_scraped, fonix_scraped, coolshop_scraped])


def get_items_in_stock(df):
    if 'stock' in df:
        df_instock = df[df['stock'] > 0]
        if (df_instock['stock'].any()):
            return df_instock
    return None

def compare_dataframes_colums(df1, df2, column_name = ''):
    return df1[column_name].equals(df2[column_name])

def run_repeatedly():
    print(">>>> Running")
    proxy_list = list(proxy.get_finished_proxy_file())
    df_scraped_old = pd.DataFrame(data={'title': "test",'price': 0,'stock': 0,'date': "time",'url':'fake_url'}, index=[0]) # Empty for initiation'df_instock = get_items_in_stock(df_scraped)
    while True:
        sleep_time = random.randrange(5, 6)
        df_scraped = scrape_all_shops(proxy_list)
        df_instock = get_items_in_stock(df_scraped)
        if df_instock is not None:
            s = compare_dataframes_colums(df_scraped, df_scraped_old, 'stock')
            if s is False:
                smtp.send_mail_to_all_on_mailing_list("Playstation 5 stock update!", df_instock)
                print("\nITS IN STOCK HOLY SHIT!!!!\n")
        df_scraped_old = df_scraped.copy()
        print("\n", df_scraped, "\n")
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

#proxy.proxy_health_start()
start() ## Lets start