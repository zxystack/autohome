# *-* coding: utf-8 *-*
from gevent import monkey; monkey.patch_all()
import requests
from bs4 import BeautifulSoup
from lxml import etree
import uuid
import time
import threading

import gevent

from db import Cars, CarsInfo, session
from settings import headers, Dict


def get_brand():
	url = "https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0"
	prefix = "https://car.autohome.com.cn"
	response = requests.get(url, headers=headers)
	content = response.text
	html = etree.HTML(content)
	li_list = html.xpath('//li')
	for li in li_list:
		id = li.xpath('./@id')[0]
		link = li.xpath('./h3/a/@href')[0]
		brand = li.xpath('./h3/a/text()')[0]
		model = Cars(id=id, link=prefix+link, brand=brand.encode('utf-8'))
		session.add(model)
		session.commit()


def get_cars(url, brand):
	response = requests.get(url, headers=headers)
	content = response.text
	html = etree.HTML(content)
	div_list = html.xpath('//div[@id="brandtab-1"]/div[@class="list-cont"]/div[@class="list-cont-bg"]/div[@class="list-cont-main"]')
	car_info = []
	for div in div_list:
		id = str(uuid.uuid4())
		car_id = div.xpath('./div[@class="main-title"]/@id')[0]
		car_model = div.xpath('./div[@class="main-title"]/a/text()')[0]
		sub_link = div.xpath('./div[@class="main-title"]/a/@href')[0]
		info = div.xpath('./div[@class="main-lever"]/div[@class="main-lever-left"]/ul[@class="lever-ul"]/li')
		level = info[0].xpath('./span/text()')[0]
		try:
			struct = info[1].xpath('./a/text()')[0]
		except IndexError:
			struct = u"电动车"
		speed_changing_box = "|".join([box.text for box in info[3].xpath('./a')])
		engine = "|".join([box.text for box in info[2].xpath('./span/a')])
		colors = "|".join([color.xpath('./div[@class="tip"]/div[@class="tip-content"]/text()')[0] for color in info[-1].xpath("./div[@class='carcolor fn-left']/a")])
		price_grade = div.xpath('./div[@class="main-lever"]/div[@class="main-lever-right"]/div')
		price = price_grade[0].xpath('./span/span/text()')[0][:-1].split('-')
		low, high = price[0],price[1] if len(price) == 2 else price[0]
		try:
			grade = price_grade[1].xpath("./span")[1].text
		except IndexError:
			grade = None
		model = dict(id=id, car_model=car_model, sub_link=sub_link, level=level, struct=struct, speed_changing_box=speed_changing_box, engine=engine, colors=colors, low=low, high=high, grade=grade)
		car_info.append(model)
		pages = html.xpath('//div[@id="brandtab-1"]/div[@class="price-page"]/div[@class="page"]/a')
		page_list = [page.xpath('./@href')[0] for page in pages[2:-1]] if pages else []
		model = CarsInfo(id=id, car_id=car_id, brand=brand, car_model=car_model.encode('utf-8'), sub_link=sub_link, level=level.encode('utf-8'), struct=struct.encode('utf-8'), speed_changing_box=speed_changing_box.encode('utf-8'), engine=engine.encode('utf-8'), colors=colors.encode('utf-8'), low=low, high=high, grade=grade)
		session.add(model)
		session.commit()
	result = {
		"car_info": car_info,
		"page_list": page_list,
		"brand": brand
	}
	return result


def info(size=5):
	now = time.time()
	brands = session.query(Cars).all()
	now = time.time()
	threads = []
	step = len(brands)/size + 1
	for i in range(size):
		if i == size:
			brand = brands[i*step:]
		else:
			brand = brands[i*step:(i+1)*step]
		thread = threading.Thread(target=asasynchronous, args=(brand,))
		threads.append(thread)
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	print "spend time:",time.time()-now
	print "requests times:", ALL_COUNT

def asasynchronous(brands):
	jobs = [gevent.spawn(get_cars, brand.link, brand.brand) for brand in brands ]
	gevent.joinall(jobs)
	sub_jobs = []
	prefix = 'https://car.autohome.com.cn'
	for job in jobs:
		job = Dict(job.value)
		if job.page_list:
			for link in job.page_list:
				url = prefix + link
				sub_jobs.append(gevent.spawn(get_cars, url, job.brand))
	gevent.joinall(sub_jobs)
