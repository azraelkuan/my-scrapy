# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import GaoDeItem


class GeocodeSpider(scrapy.Spider):
    name = "geocode"
    pipelines = ['GeocodePipeline']
    allowed_domains = ["restapi.amap.com"]
    key = "604128e90f0f7ca695c811e7ccf5d6f0"

    # 需要跑的tag和keywords 可以单独设置
    tags = ['060100', '060101', '060102', '060103', '060200', '060201', '060202', '060400', '060401', '060402',
            '060403', '060404', '060405', '060406', '060407', '060408', '060409', '060411', '060413', '060414',
            '060415', '061400', '061401']
    keywords = ""
    radius = "15000"
    start_urls = [
        'http://restapi.amap.com/v3/config/district?key=' + key + '&keywords=&level=&subdistrict=1&extensions=base'
    ]

    def parse(self, response):

        address_list = ['成都尚成:成都崇州市金盆地大道295号', '绵阳广平:绵阳市涪城区绵吴路口东岳村一社',
                        '新都旺角:新都运力大道11号跃富物流（盛源加气站后面)', '江油云鹏:江油市河南工业园江豆商城3号仓库',
                        "四川中胜:成都市建设北中三段48号纺织站107仓库", "德阳中合:德阳市龙泉山南段二段云湖街3号"]
        location_list = ['103.683913,30.648506', '104.730205,31.448011', '104.154036,30.832696',
                         '104.756493,31.740177', '104.264430,30.740530', '104.416219,31.112427']

        url_para1 = "http://restapi.amap.com/v3/place/around?key=" + self.key
        url_para2 = "&keywords=" + self.keywords + "&location="
        url_para3 = "&types="
        url_para4 = "&offset=25&extensions=all&radius=" + self.radius + "&page="

        for tag in self.tags:
            for location in location_list:
                page_url = url_para1 + url_para2 + location + url_para3 + tag + url_para4
                url = page_url + str(1)  # 从第一页开始跑
                response.meta['page_url'] = page_url  # 记录page_url和当前的page
                response.meta['distributor'] = address_list[location_list.index(location)]
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
                        item['photo_urls'] = item['photo_urls'] + ' ' + photo['url']

                item['pro_name'] = poi['pname']
                item['pro_center'] = ""
                item['city_name'] = poi['cityname']
                item['city_center'] = ""
                item['ad_name'] = poi['adname']
                item['ad_center'] = ""
                item['distributor'] = response.meta['distributor']
                yield item

            page_url = response.meta['page_url']
            page = response.meta['page'] + 1
            url = page_url + str(page)
            response.meta['page'] = page
            yield scrapy.Request(url=url, callback=self.parse_data, meta=response.meta)
