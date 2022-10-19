import requests
import json
import re
from scrapy.selector import Selector

def latlon(urll: str):
    coordinates = re.compile(r'\!2d([^!]+)\!3d([^!]+)')
    return list(map(float, coordinates.search(urll).group(1, 2)))

def time_func(span_list):
    morning_list = span_list[0].replace('.', ':').split(' ')
    evening_list = span_list[1].replace('.', ':').split(' ')
    mon_thu_time = 'mon-thu ' + morning_list[2] + '-' + morning_list[4] + ' ' \
        + evening_list[2] + '-' + evening_list[4]
    fri_time = 'fri ' + morning_list[2] + '-' + morning_list[4] + ' ' \
        + evening_list[2] + '-' + evening_list[-3]
    return [mon_thu_time, fri_time]

request = requests.get('https://oriencoop.cl/sucursales.htm')
datas_list = []

pages = [st.split('/')[-1] for st in Selector(
    text=request.text).xpath("//ul[@class='sub-menu']/li/a/@href").extract()]

for page in pages:
    response = requests.get('https://oriencoop.cl/sucursales/' + page)
    print(page)
    div = Selector(text=response.text).xpath(
        "//div[@class='s-dato']/p").extract()
    mapa_url = Selector(text=response.text).xpath(
        "//div[@class='s-mapa']/iframe/@src").get()

    datas = dict()

    time_span_list = Selector(text=div[3]).xpath("//span/text()").extract()
    datas['address'] = Selector(text=div[0]).xpath("//span/text()").get()
    datas['latlon'] = latlon(mapa_url)
    datas['name'] = Selector(text=response.text).xpath(
        '//div[@class="s-dato"]/h3/text()').get()
    datas['phones'] = [
        Selector(text=div[1]).xpath("//span/text()").get(),
        *Selector(text=response.text).xpath("//li[@class='call']/a/text()").extract()
    ]
    datas['working_hours'] = time_func(time_span_list)
    datas_list.append(datas)

print(json.dumps(datas_list, indent=4, ensure_ascii=False))