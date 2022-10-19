from bs4 import BeautifulSoup
import requests
import re
import json

def get_html(url: str, city_id: str = None, post=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    }
    if post:
        payload = {'CITY_ID': city_id}
        response = requests.post(url, headers=headers, data=payload)
    else:
        response = requests.get(url, headers=headers)
    return response.text

def cities_ids(soup: BeautifulSoup):
    data_block = soup.find(class_='col-xs-12 col-sm-6 citys-box')
    regions = data_block.find_all(name='div', recursive=False)[1:]
    cities = []
    for region in regions:
        cities_region = region.find(class_='cities-container').find_all(name='div')
        for city in cities_region:
            cities.append(city)
    cities_id = [city.label.get('id') for city in cities]
    return cities_id

def bs4_soup(html_text: str):
    soup = BeautifulSoup(html_text, 'lxml')
    return soup

def shops_id(soup: BeautifulSoup):
    all_cities_ids = cities_ids(soup=soup)
    shops_ids = []
    for city_id in all_cities_ids:
        city_html = get_html('https://som1.ru/shops/', city_id=city_id, post=True)
        city_soup = bs4_soup(city_html)
        shops_block = city_soup.find_all(class_='shops-col shops-button')
        for shop in shops_block:
            shops_ids.append(shop.a.get('href').split('/')[2])
    return shops_ids

def datas_parse(shop_soup: BeautifulSoup):
    shop_info = shop_soup.find(class_='shop-info-table').find_all(name='tr')
    map = shop_soup.find('script', text=re.compile('showShopsMap')).get_text().split('\'')
    address = shop_info[0].td.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()
    latlon = [float(map[3]), float(map[5])]
    name = map[9]
    phones = [shop_info[1].td.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()]
    all_phones = phones[0].split(',')
    phones = [phone.strip() for phone in all_phones]
    working_hours = [shop_info[2].td.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()]
    if ',' in working_hours[0]:
        all_working_hours = working_hours[0].split(',')
        working_hours = [hours.strip() for hours in all_working_hours]
    datas_dict = dict(address=address,
                          latlon=latlon,
                          name=name,
                          phones=phones,
                          working_hours=working_hours)
    return datas_dict

def url(city_shop_id: str):
    url1 = 'https://som1.ru/shops/'
    url2 = city_shop_id
    return f'{url1}{url2}/'

def all_datas(soup: BeautifulSoup):
    shops_ids = shops_id(soup=soup)
    all_datass = []
    for shop_id in shops_ids:
        shop_url = url(city_shop_id=shop_id)
        shop_html = get_html(shop_url)
        shop_soup = bs4_soup(shop_html)
        shop_data = datas_parse(shop_soup=shop_soup)
        all_datass.append(shop_data)
    return all_datass

def output(data: list[dict]):
    print(json.dumps(data, indent=4, ensure_ascii=False))

def main():
    url = 'https://som1.ru/shops/'
    html = get_html(url)
    soup = bs4_soup(html)
    all_datass = all_datas(soup)
    output(data=all_datass)

if __name__ == '__main__':
    main()