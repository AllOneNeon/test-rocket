import requests
import json
import re
from scrapy.selector import Selector

request = requests.get('https://naturasiberica.ru/our-shops/')
items = Selector(text=request.text).xpath('//p[@class="card-list__description"]/text()').extract()
pages = [item.split('/')[-2] for item in Selector(text=request.text).xpath('//a[@class="card-list__link"]/@href').extract()]

head = Selector(text=request.text).xpath('//*[@id="bx_1573527503_444"]/div[2]/h2/text()').get().split(' ')
name = head[-2] + ' ' + head[-1]

adress_list = []
datas_list = []

for item in items:
    adress_list.append(item.replace('\t', '').replace('\r\n', ''))

for i, page in enumerate(pages):
    datas = dict()
    datas['address'] = adress_list[i]
    response = requests.get(f'https://www.google.com/maps/search/{adress_list[i]}')

    datas['latlon'] = [float(coord) for coord in re.split('&|=|%2C', Selector(text=response.text).xpath('//meta[@itemprop="image"]/@content').get())[1:3]]
    res = requests.get('https://naturasiberica.ru/our-shops/' + page)
    
    datas['name'] = name
    datas['phones'] = Selector(text=res.text).xpath('//*[@id="shop-phone-by-city"]/text()').extract()
    datas['working_hours'] = Selector(text=res.text).xpath('//*[@id="schedule1"]/text()').extract()
    
    print(f'Collecting data from {page}... ' + f'{i+1} of {len(pages)}')
    datas_list.append(datas)

print(json.dumps(datas_list, indent=4, ensure_ascii=False))