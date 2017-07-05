# -*- coding: utf-8 -*-
import scrapy
import json
import re
import logging
from ..items import MDianPingItem


class FoodSpider(scrapy.Spider):
    name = "food"
    allowed_domains = ["mapi.dianping.com", "m.dianping.com"]
    pipelines = ['MdianpingPipeline']
    food_id = 10
    city_id = 7
    city = "深圳市"
    pro = "广东省"

    start_urls = ['http://mapi.dianping.com/searchshop.json?start=0&regionid=0&categoryid=0&sortid=0&cityid=%s' % city_id]

    def parse(self, response):
        data = json.loads(response.body.decode('utf-8'))
        categories = data['categoryNavs']
        for each in categories:
            if each['parentId'] == self.food_id and each['id'] != self.food_id:
                category_id = each['id']
                category_name = each['name']
                start_index = 0
                response.meta['start_index'] = start_index
                response.meta['category_id'] = category_id
                response.meta['category_name'] = category_name
                response.meta['region_id'] = '0'

                url = "http://mapi.dianping.com/searchshop.json?start=%s&regionid=0&categoryid=%s&sortid=0&cityid=%s"
                url = url % (start_index, category_id, self.city_id)
                yield scrapy.Request(url=url, callback=self.parse_region, meta=response.meta)

    def parse_region(self, response):
        data = json.loads(response.body.decode('utf-8'))
        total = int(data['recordCount'])
        if total <= 5000:
            url = response.url + "&test=2"
            yield scrapy.Request(url=url, callback=self.parse_url, meta=response.meta)
        else:
            regions = data['regionNavs']
            start_index = 0
            category_id = data['currentCategory']['id']
            for each in regions:
                if each['parentId'] == 0 and each['id'] != each['parentId'] and each['id'] != -10000:
                    region_id = each['id']
                    response.meta['region_id'] = region_id

                    url = "http://mapi.dianping.com/searchshop.json?start=%s&regionid=%s&categoryid=%s&sortid=0&cityid=%s"
                    url = url % (start_index, region_id, category_id, self.city_id)
                    yield scrapy.Request(url=url, callback=self.parse_sub_region, meta=response.meta)

    def parse_sub_region(self, response):
        data = json.loads(response.body.decode('utf-8'))
        total = int(data['recordCount'])
        if total <= 5000:
            url = response.url + "&test=3"
            yield scrapy.Request(url=url, callback=self.parse_url, meta=response.meta)
        else:
            # print(response.url)
            regions = data['regionNavs']
            start_index = 0
            category_id = data['currentCategory']['id']
            parent_region_id = data['currentRegion']['id']
            for each in regions:
                if each['parentId'] == parent_region_id and each['id'] != each['parentId']:
                    region_id = each['id']
                    response.meta['region_id'] = region_id

                    url = "http://mapi.dianping.com/searchshop.json?start=%s&regionid=%s&categoryid=%s&sortid=0&cityid=%s"
                    url = url % (start_index, region_id, category_id, self.city_id)

                    yield scrapy.Request(url=url, callback=self.parse_url, meta=response.meta)

    def parse_url(self, response):
        data = json.loads(response.body.decode('utf-8'))
        start_index = data['nextStartIndex']
        total = data['recordCount']
        region_id = response.meta['region_id']
        category_id = response.meta['category_id']
        query_id = data['queryId']

        lists = data['list']
        for each in lists:
            item = MDianPingItem()
            item['uid'] = each['id']
            item['name'] = each['name']
            item['branch_name'] = each['branchName']
            item['stars'] = int(each['shopPower']) / 10.0

            price_info = each['priceText']
            try:
                item['price'] = re.search('(\d+)', price_info).group(1)
            except:
                # print(price_info)
                FoodSpider.log(self, "price is error uid is %s" % item['uid'], level=logging.WARNING)
                item['price'] = '0'

            item['sub_category_name'] = each['categoryName']
            item['region_name'] = each['regionName']
            # print(each['hasDeals'], each['bookable'], each['hasTakeaway'], each['hasMoPay'])
            item['has_deals'] = "Y" if each['hasDeals'] is True else "N"
            item['bookable'] = "Y" if each['bookable'] is True else "N"
            item['has_takeaway'] = "Y" if each['hasTakeaway'] is True else "N"
            item['has_mobilepay'] = "Y" if each['hasMoPay'] is True else "N"
            item['has_promote'] = "Y" if each['hasPromo'] is True else "N"
            # print(item['has_deals'], item['bookable'])

            item['city'] = self.city
            item['pro'] = self.pro
            item['category_name'] = response.meta['category_name']

            response.meta['item'] = item
            url = "http://m.dianping.com/shop/%s?from=shoplist&shoplistqueryid=%s"
            url = url % (item['uid'], query_id)
            yield scrapy.Request(url=url, callback=self.parse_store, meta=response.meta)

        if start_index != total:
            url = "http://mapi.dianping.com/searchshop.json?start=%s&regionid=%s&categoryid=%s&sortid=0&cityid=%s"
            url = url % (start_index, region_id, category_id, self.city_id)
            yield scrapy.Request(url=url, callback=self.parse_url, meta=response.meta)

    def parse_store(self, response):
        item = response.meta['item']

        try:
            item['comments'] = response.xpath("//span[@class='itemNum']/span[@class='itemNum-val']/text()").extract()[0]
        except:
            FoodSpider.log(self, 'comments is error, url is %s' % response.url, level=logging.WARNING)
            item['comments'] = '0'

        try:
            taste_node_info = response.xpath("//div[@class='desc']/span[1]/text()").extract()[0]
            item['taste'] = re.search("([\d\.]+)", taste_node_info).group(1)
        except:
            FoodSpider.log(self, 'taste is error, url is %s' % response.url, level=logging.WARNING)
            item['taste'] = '0'

        try:
            environment_node_info = response.xpath("//div[@class='desc']/span[2]/text()").extract()[0]
            item['environment'] = re.search("([\d\.]+)", environment_node_info).group(1)
        except:
            FoodSpider.log(self, 'environment is error, url is %s' % response.url, level=logging.WARNING)
            item['environment'] = '0'

        try:
            service_node_info = response.xpath("//div[@class='desc']/span[3]/text()").extract()[0]
            item['service'] = re.search("([\d\.]+)", service_node_info).group(1)
        except:
            FoodSpider.log(self, 'service is error, url is %s' % response.url, level=logging.WARNING)
            item['service'] = '0'

        try:
            address_node_info = response.xpath("//div[@class='J_address']//a[@class='item']//text()").extract()
            item['address'] = ""
            for each in address_node_info:
                item['address'] += each.strip()
        except:
            FoodSpider.log(self, 'address is error, url is %s' % response.url, level=logging.WARNING)
            item['address'] = ''

        try:
            tel_node_info = response.xpath("//div[@class='J_phone']//a[contains(@class, 'item')]/@href").extract()[0]
            item['tel'] = re.search('([\d-]+)', tel_node_info).group(1)
        except:
            FoodSpider.log(self, 'tel is error, url is %s' % response.url, level=logging.WARNING)
            item['tel'] = ''

        try:
            open_time_node_info = response.xpath("//div[@class='businessTime']/text()").extract()
            item['open_time'] = ''
            for each in open_time_node_info:
                item['open_time'] += each.strip()
        except:
            FoodSpider.log(self, 'open_time is error, url is %s' % response.url, level=logging.WARNING)
            item['open_time'] = ''

        try:
            dish_list_node_info = response.xpath("//div[@class='comm-new-tag']/span[@class='item']/text()").extract()
            item['dish_list'] = ""
            for each in dish_list_node_info:
                item['dish_list'] = each.strip() + " " + item['dish_list']
        except:
            FoodSpider.log(self, 'dish_list is error, url is %s' % response.url, level=logging.WARNING)
            item['dish_list'] = ""

        # yield item
        url = re.search("(.*)\?", response.url).group(1) + "/map"
        response.meta['item'] = item
        yield scrapy.Request(url=url, callback=self.parse_map, meta=response.meta)

    def parse_map(self, response):
        item = response.meta['item']
        try:
            lat = re.search("lat:([\d\.]+)", response.body.decode('utf-8')).group(1)
            lng = re.search("lng:([\d\.]+)", response.body.decode('utf-8')).group(1)
            item['center'] = lng + "," + lat
        except:
            FoodSpider.log(self, "center is error, url is %s" % response.url, level=logging.WARNING)

        yield item








