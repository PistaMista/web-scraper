import sys
import requests
import re
from typing import Dict, Tuple, Optional
from bs4 import BeautifulSoup, Tag, NavigableString

def get_soup(url: str) -> BeautifulSoup:
    res = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(res.content, 'html.parser')

def extract_price_number(price_str: str) -> str:
    digits = re.findall(r'\d+', price_str)
    return "".join(digits)

def extract_dimension(dimension_str: str) -> str:
    digits = re.findall(r'[\d\.]+', dimension_str)
    return "".join(digits)

def extract_resolution(resolution_str: str) -> Tuple[str, str]:
    match = re.search(r'(\d+)x(\d+)', resolution_str)
    if match:
        width, height = match.groups()
        return width, height
    return "", ""

def extract_warranty(warranty_str: str) -> str:
    digits = re.findall(r'\d+', warranty_str)
    return "".join(digits)

def get_description_dict(page: BeautifulSoup) -> Dict[str, str]:
    result: Dict[str, str] = {}
    div = page.find('div', class_="zbozi_text")
    if div is None or not isinstance(div, Tag):
        return {}

    children = div.find_all(True, recursive=False)
    desc = children[2] if len(children) >= 3 else None
    if desc is None or not isinstance(desc, Tag):
        return {}

    current_key: Optional[str] = None
    for c in desc.children:
        if isinstance(c, Tag) and c.name == "span":
            current_key = c.text.strip().rstrip(":")
        elif isinstance(c, NavigableString) and current_key is not None and c.strip():
            result[current_key] = c.strip()
        
    return result

def print_product_params(product_url: str):
    page = get_soup(product_url)
    desc_dict = get_description_dict(page)

    price = next(
        extract_price_number(price_td.string)
        for price_tr in page.find_all('tr', class_="cena_s_dph")
        if isinstance(price_tr, Tag)
        for price_td in price_tr.find_all('td', class_="right")
        if isinstance(price_td, Tag) and price_td.string is not None
    ) or ""
    dimension = extract_dimension(desc_dict["Rozměr"]) if "Rozměr" in desc_dict else ""
    res_width, res_height = extract_resolution(desc_dict["Rozlišení"]) if "Rozlišení" in desc_dict else ("", "")
    surface = desc_dict.get("Typ povrchu", "").replace(" ", "")
    backlight = desc_dict.get("Typ podsvícení", "").removesuffix(" podsvícení")
    state = desc_dict.get("Stav", "")
    warranty = extract_warranty(desc_dict["Záruka"]) if "Záruka" in desc_dict else ""

    print(f"{price}\t{dimension}\t{res_width}\t{res_height}\t{surface}\t{backlight}\t{state}\t{warranty}")

def main():
    for line in sys.stdin:
        url = line.strip()
        print_product_params(url)

