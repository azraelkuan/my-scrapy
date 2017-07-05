# -*- coding: utf-8 -*-
import scrapy
import json
import re
import logging
from ..items import GaoDeItem


class GaodeSpider(scrapy.Spider):
    name = "gaode"
    pipelines = ['GaoDePipeline']
    allowed_domains = ["restapi.amap.com"]
    key = "604128e90f0f7ca695c811e7ccf5d6f0"

    start_urls = [
        'http://restapi.amap.com/v3/config/district?key=' + key + '&keywords=&level=&subdistrict=1&extensions=base',
    ]

    def __init__(self, tags=None, city_list=None, keywords=None, province=None, table_name=None, *args, **kwargs):
        super(GaodeSpider, self).__init__(*args, **kwargs)
        self.tags = tags.split(";")
        self.table_name = table_name
        self.city_list = str(city_list).encode('utf-8').decode('unicode_escape').split(";")
        self.keywords = str(keywords).encode('utf-8').decode('unicode_escape')
        self.province = str(province).encode('utf-8').decode('unicode_escape')
        GaodeSpider.log(self, 'type is %s' % type(self.city_list), level=logging.INFO)
        GaodeSpider.log(self, 'city is %s' % self.city_list, level=logging.INFO)
        GaodeSpider.log(self, "tag is %s" % self.tags, level=logging.INFO)
        GaodeSpider.log(self, "kwy is %s" % self.keywords, level=logging.INFO)
        # self.city_list = kwargs.get("city_list")
        # self.keywords = kwargs.get("keywords")

    def parse(self, response):
        data = json.loads(response.body.decode("utf-8"))
        provinces = data['districts'][0]['districts']
        url_para1 = "http://restapi.amap.com/v3/config/district?key="
        url_para2 = "&keywords="
        url_para3 = "&level=district&subdistrict=3&extensions=base"
        for each in provinces:  # 所有省份
            name = each['name']
            if name == self.province:
                print(name)
                url = url_para1 + self.key + url_para2 + name + url_para3
                yield scrapy.Request(url=url, callback=self.parse_city)

    def parse_city(self, response):
        url_para1 = 'http://restapi.amap.com/v3/config/district?key='
        url_para2 = '&subdistrict=3&showbiz=false&extensions=all&keywords='

        data = json.loads(response.body.decode('utf-8'))
        cities = data['districts'][0]['districts']
        if len(self.city_list) == 0:
            for city in cities:
                print(city['name'])
                url = url_para1 + self.key + url_para2 + city['name']
                yield scrapy.Request(url=url, callback=self.parse_ad)
        else:
            for city in cities:
                for each in self.city_list:
                    if each in city['name']:
                        url = url_para1 + self.key + url_para2 + city['name']
                        yield scrapy.Request(url=url, callback=self.parse_ad)

    def parse_ad(self, response):
        url_para1 = 'http://restapi.amap.com/v3/config/district?key='
        url_para2 = '&subdistrict=3&showbiz=false&extensions=all&keywords='

        data = json.loads(response.body.decode('utf-8'))
        ads = data['districts'][0]['districts']
        if len(ads):
            for ad in ads:
                url = url_para1 + self.key + url_para2 + ad['name']
                yield scrapy.Request(url=url, callback=self.parse_points)
        else:
            url = response.url + "&test=2"
            print(url)
            yield scrapy.Request(url=url, callback=self.parse_points)

    def parse_points(self, response):
        max_point_x = max_point_y = 0
        min_point_x = min_point_y = 200

        data = json.loads(response.body.decode('utf-8'))
        polyline = data['districts'][0]['polyline']
        poly_points = re.split(';|\|', polyline)
        for poly_point in poly_points:
            point = poly_point.split(',')
            point_x = float(point[0])
            point_y = float(point[1])
            if point_x >= max_point_x:
                max_point_x = point_x
            if point_y >= max_point_y:
                max_point_y = point_y
            if point_x <= min_point_x:
                min_point_x = point_x
            if point_y <= min_point_y:
                min_point_y = point_y

        pace_step = 15.0
        if "test" in response.url:
            pace_step = 20.0

        pace_x = (max_point_x - min_point_x) / pace_step
        pace_y = (max_point_y - min_point_y) / pace_step

        points_x = []
        points_y = []
        tmp_point_x = min_point_x
        tmp_point_y = min_point_y
        while tmp_point_x <= max_point_x:
            points_x.append(tmp_point_x)
            tmp_point_x += pace_x
        while tmp_point_y <= max_point_y:
            points_y.append(tmp_point_y)
            tmp_point_y += pace_y

        url_para1 = "http://restapi.amap.com/v3/place/around?key=" + self.key
        url_para2 = "&keywords=" + self.keywords + "&location="
        url_para3 = "&types="
        url_para4 = "&offset=25&extensions=all&radius=10000&page="

        for x in points_x:
            for y in points_y:
                location = str(x) + ',' + str(y)
                if len(self.tags):
                    for tag in self.tags:
                        page_url = url_para1 + url_para2 + location + url_para3 + tag + url_para4
                        url = page_url + str(1)  # 从第一页开始跑
                        response.meta['page_url'] = page_url  # 记录page_url和当前的page
                        response.meta['page'] = 1
                        yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)
                else:
                    page_url = url_para1 + url_para2 + location + url_para3 + url_para4
                    url = page_url + str(1)  # 从第一页开始跑
                    response.meta['page_url'] = page_url  # 记录page_url和当前的page
                    response.meta['page'] = 1
                    yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)

    def parse_data(self, response):
        data = json.loads(response.body.decode('utf-8'))
        count = int(data['count'])
        if count != 0:  # count为0 表示当前页面已经没有数据
            pois = data['pois']
            for poi in pois:
                item = GaoDeItem()
                item['uid'] = poi['id']
                item['name'] = poi['name']
                item['tag'] = poi['type']

                sub_tag_list = item['tag'].split('|')
                item['sub_tag'] = ""
                for each_tag in sub_tag_list:
                    item['sub_tag'] = each_tag.split(';')[2] + " " + item['sub_tag']

                item['tel'] = poi['tel']
                if str(item['tel']) == "[]":
                    item['tel'] = ''
                item['address'] = poi['address']
                if str(item['address']) == "[]":
                    item['address'] = ''

                item['center'] = poi['location']

                item['photo_exists'] = 0
                photos = poi['photos']
                item['photo_url3'] = ""
                item['photo_url2'] = ""
                item['photo_url1'] = ""
                m = 1
                if photos:
                    item['photo_exists'] = 1
                    for photo in photos:
                        if m <= 3:
                            item['photo_url' + str(m)] = photo['url']
                            m += 1

                item['pro_name'] = poi['pname']
                item['pro_center'] = ""
                item['city_name'] = poi['cityname']
                item['city_center'] = ""
                item['ad_name'] = poi['adname']
                item['ad_center'] = ""
                item['table_name'] = self.table_name
                yield item

            page_url = response.meta['page_url']
            page = response.meta['page'] + 1
            url = page_url + str(page)
            response.meta['page'] = page
            yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)

