from sites.proshop import scraper as proshop
from sites.elgiganten import scraper as elgiganten
from sites.bilka import scraper as bilka
from sites.fonix import scraper as fonix
import pandas as pd



bilka_scraped = bilka.search_product_list(1,1)
proshop_scraped = proshop.search_product_list(1,1)
elgiganten_scraped = elgiganten.search_product_list(1,1)
fonix_scraped = fonix.search_product_list(1,1)
df_final = pd.concat([proshop_scraped, elgiganten_scraped, bilka_scraped, fonix_scraped])
df1 = df_final[df_final["stock"] > 0]
print(df_final)