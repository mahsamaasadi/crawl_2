import pandas as pd
import requests
from bs4 import BeautifulSoup
import threading
import re

def farsi_to_english(farsi_num):
    farsi_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(farsi_digits, english_digits)
    return farsi_num.translate(translation_table)

def new_price(price_str):
    cleaned_price = re.sub(r'[^\d]', '', price_str)
    return cleaned_price

def crawl_technolife():
    url = "https://www.technolife.ir/product/list/164_163_130/%D8%AA%D9%85%D8%A7%D9%85%DB%8C-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1%D9%87%D8%A7-%D9%88-%D9%84%D9%BE-%D8%AA%D8%A7%D9%BE-%D9%87%D8%A7?only_available=true&manufacturer_id=19&pto=20000000&pfrom=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    sections = soup.find_all("section",
                             class_="relative w-full rounded-[10px] bg-white pt-[52px] xl:max-w-[32%] 2xl:w-[24%] 3xl:w-[19.2%] border shadow-[0px_1px_4px_rgba(0,0,0,0.08)]")

    names = []
    prices = []
    for section in sections:
        name = section.find("h2",
                            class_="yekanbakh-en line-clamp-3 h-[75px] overflow-hidden text-sm font-medium leading-6.5 -tracking-0.5 text-gray-800")
        price = section.find("p", class_="text-[22px] font-semiBold leading-5 text-gray-800")

        names.append(name.text.strip())
        try:
            price_text = price.text.strip().replace(',', '').replace('تومان', '').strip()
            cleaned_price = new_price(farsi_to_english(price_text))
            prices.append(cleaned_price)
        except:
            price_text = section.find("p", class_="text-[22px] font-semiBold leading-5 text-red-600").text.strip().replace(',', '').replace('تومان', '').strip()
            cleaned_price = new_price(farsi_to_english(price_text))
            prices.append(cleaned_price)

    data = {"name": names, "price": prices}
    technolife_df = pd.DataFrame(data)
    technolife_df['price'] = technolife_df['price'].astype(int)

    print('Technolife data crawled')

    return technolife_df

def crawl_torob():
    url = "https://torob.com/browse/99/%D9%84%D9%BE-%D8%AA%D8%A7%D9%BE-%D9%88-%D9%86%D9%88%D8%AA-%D8%A8%D9%88%DA%A9-laptop/b/29/asus-%D8%A7%DB%8C%D8%B3%D9%88%D8%B3/?price__gt=10000000&price__lt=20000000&stock_status=new&available=true"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    names_html = soup.find_all("h2", class_="jsx-9e6201846c11ef54 product-name")
    prices_html = soup.find_all("div", class_="jsx-9e6201846c11ef54 product-price-text")

    names = []
    for name in names_html:
        names.append(name.text.strip())

    prices = []
    for price in prices_html:
        price_text = price.text.strip().replace(',', '').replace('تومان', '').strip()
        cleaned_price = new_price(farsi_to_english(price_text))
        prices.append(cleaned_price)

    data = {"name": names, "price": prices}
    torob_df = pd.DataFrame(data)
    torob_df['price'] = torob_df['price'].astype(int)

    print('Torob data crawled')

    return torob_df

def main():
    technolife_thread = threading.Thread(target=crawl_technolife, name='technolife_thread')
    torob_thread = threading.Thread(target=crawl_torob, name='torob_thread')

    technolife_thread.start()
    torob_thread.start()

    technolife_thread.join()
    torob_thread.join()

    technolife_df = crawl_technolife()
    torob_df = crawl_torob()

    technolife_df.to_csv('technolife_data.csv', index=False, encoding='utf-8')
    torob_df.to_csv('torob_data.csv', index=False, encoding='utf-8')

    print('DataFrames saved')

if __name__ == '__main__':
    main()
