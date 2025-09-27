import requests
from bs4 import BeautifulSoup, NavigableString
from typing import Iterator
from itertools import islice

shop_url = "https://www.lcddisplej.cz/kategorie/displeje-dle-velikosti-notebooku/"
max_product_count = 150

def get_soup(url: str) -> BeautifulSoup:
    res = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(res.content, 'html.parser')

def get_size_category_urls(categories_soup: BeautifulSoup) -> Iterator[str]:
    for li in categories_soup.find_all('li', class_="sub1"):
        for a in li.find_all('a'):
            url = a.get('href')
            if url is not None:
                yield url
    
def get_product_urls(products_url: str) -> Iterator[str]:
    products_soup = get_soup(products_url)
    next_page = None

    pagination = products_soup.find('div', class_="strankovani")
    if pagination is not None and not isinstance(pagination, NavigableString):
        page_buttons = pagination.find_all(recursive=False)
        if page_buttons:
            next_button = page_buttons[-1]
            next_page = next_button.get('href', None)

    for div in products_soup.find_all('div', class_="polozka_odkaz"):
        for a in div.find_all('a'):
            url = a.get('href')
            if url is not None:
                yield url
    
    if next_page is not None:
        yield from get_product_urls(next_page)

def main():
    page_with_size_categories = get_soup(shop_url)
    product_urls = islice(
        (
            product_url
            for category_url in get_size_category_urls(page_with_size_categories)
            for product_url in get_product_urls(category_url)
        ),
        max_product_count
    )

    for url in product_urls:
        print(url)
