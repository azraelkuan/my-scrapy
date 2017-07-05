# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import GaoDeItem


class GaodeSpider(scrapy.Spider):
    name = "gaode"
    pipelines = ['GaoDePipeline']
    allowed_domains = ["restapi.amap.com"]
    key = "604128e90f0f7ca695c811e7ccf5d6f0"

    # 需要跑的tag和keywords 可以单独设置
    tags = ['060200', '060201', '060202', '060400', '060401', '060402', '060403', '060404', '060405', '060406',
            '060407', '060408', '060409', '060411', '060413', '060414', '060415']
    # tags = [
    #     '050000', '050100', '050101', '050102', '050103', '050104', '050105', '050106', '050107', '050108', '050109',
    #     '050110', '050111', '050112', '050113', '050114', '050115', '050116', '050117', '050118', '050119', '050120',
    #     '050121', '050122', '050123', '050200', '050201', '050202', '050203', '050204', '050205', '050206', '050207',
    #     '050208', '050209', '050210', '050211', '050212', '050213', '050214', '050215', '050216', '050217', '050300',
    #     '050301', '050302', '050303', '050304', '050305', '050306', '050307', '050308', '050309', '050310', '050311',
    #     '050400', '050500', '050501', '050502', '050503', '050504', '050600', '050700', '050800', '050900']
    keywords = ""

    # 全国的链接
    start_urls = [
        'http://restapi.amap.com/v3/config/district?key=' + key + '&keywords=&level=&subdistrict=1&extensions=base'
    ]

    def parse(self, response):
        data = json.loads(response.body.decode("utf-8"))
        provinces = data['districts'][0]['districts']

        url_para1 = "http://restapi.amap.com/v3/config/district?key="
        url_para2 = "&keywords="
        url_para3 = "&level=district&subdistrict=3&extensions=base"

        for each in provinces:  # 所有省份
            name = each['name']
            if name == '四川省':  # 可以单独跑一个省份
                url = url_para1 + self.key + url_para2 + name + url_para3
                yield scrapy.Request(url=url, callback=self.parse_area)

    def parse_area(self, response):
        url_para1 = "http://restapi.amap.com/v3/place/around?key=" + self.key
        url_para2 = "&keywords=" + self.keywords + "&location="
        url_para3 = "&types="
        url_para4 = "&offset=25&extensions=all&radius=10000&page="

        # 初始化区域信息
        response.meta['city_name'] = ''
        response.meta['city_center'] = ''
        response.meta['ad_name'] = ''
        response.meta['ad_center'] = ''
        response.meta['street_name'] = ''
        response.meta['street_center'] = ''

        result = json.loads(response.body.decode('utf-8'))
        pros = result['districts']  # 省级
        for pro in pros:
            self.pro_center[pro['name']] = pro['center']   # 记录每一个省的中心坐标


            citys = pro['districts']  # 市级
            if citys:  # 台湾没有市，单独处理
                for city in citys:
                    self.city_center[city['name']] = city['center']  # 记录每一个市的中心坐标

                    ads = city['districts']  # 区级
                    if ads:  # 没有区单独处理
                        for ad in ads:
                            self.ad_center[ad['name']] = ad['center']  # 记录每一个区的中心坐标

                            streets = ad['districts']  # 街道
                            if streets:  # 没有街道
                                for street in streets:
                                    response.meta['street_name'] = street['name']  # 记录每一个中心店的中心坐标
                                    response.meta['street_center'] = street['center']

                                    for tag in self.tags:
                                        page_url = url_para1 + url_para2 + street[
                                            'center'] + url_para3 + tag + url_para4
                                        url = page_url + str(1)  # 从第一页开始跑
                                        response.meta['page_url'] = page_url  # 记录page_url和当前的page
                                        response.meta['page'] = 1
                                        yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)
                            else:
                                for tag in self.tags:
                                    page_url = url_para1 + url_para2 + ad['center'] + url_para3 + tag + url_para4
                                    url = page_url + str(1)  # 从第一页开始跑
                                    response.meta['page_url'] = page_url  # 记录page_url和当前的page
                                    response.meta['page'] = 1
                                    yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)

                    else:
                        for tag in self.tags:
                            page_url = url_para1 + url_para2 + city['center'] + url_para3 + tag + url_para4
                            url = page_url + str(1)  # 从第一页开始跑
                            response.meta['page_url'] = page_url  # 记录page_url和当前的page
                            response.meta['page'] = 1
                            yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)
        else:  # 台湾
            for tag in self.tags:
                page_url = url_para1 + url_para2 + pro['center'] + url_para3 + tag + url_para4
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
                item['distance'] = poi['distance']

                item['photo_urls'] = ''
                item['photo_exists'] = 0
                photos = poi['photos']
                if photos:
                    item['photo_exists'] = 1
                    for photo in photos:
                        item['photo_urls'] = item['photo_urls'] + ' ' +photo['url']

                item['pro_name'] = poi['pname']
                item['pro_center'] = self.pro_center[poi['pname']]
                item['city_name'] = poi['cityname']
                item['city_center'] = self.city_center[poi['cityname']]
                item['ad_name'] = poi['adname']
                item['ad_center'] = ""
                item['street_name'] = response.meta['street_name']
                item['street_center'] = response.meta['street_center']
                yield item

            page_url = response.meta['page_url']
            page = response.meta['page'] + 1
            url = page_url + str(page)
            response.meta['page'] = page
            yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)
