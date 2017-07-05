# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import re, logging
from shop.items import TMallItem


class TmallSpider(scrapy.Spider):
    name = "tmall"
    pipelines = ['TMallPipeline']
    allowed_domains = ["tmall.com", "mdskip.taobao.com"]
    start_urls = []

    def start_requests(self):
        home_url = "https://chaoshi.tmall.com/"
        session = requests.session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        login_req = session.get(home_url, headers=headers)
        cookies = session.cookies.get_dict()
        target_url = "https://list.tmall.com/search_product.htm?spm=a3204.7084713.1996500281.70.hHKbTj&user_id=725677994&cat=51456014&active=1&acm=lb-zebra-26901-329683.1003.4.468295&style=g&search_condition=23&scm=1003.4.lb-zebra-26901-329683.OTHER_2_468295"
        yield scrapy.Request(url=target_url, callback=self.parse, cookies=cookies, meta={'cookies': cookies})

    def parse(self, response):
        cookies = response.meta['cookies']
        item_nodes = response.xpath("//div[@class='mainItemsList']//li[@data-itemid]")
        for each in item_nodes:
            url = "https:" + each.xpath(".//h3/a/@href").extract()[0]
            item_id = re.search("id=(\d+)", url).group(1)
            item_name = each.xpath(".//h3/a/text()").extract()[0].strip()

            try:
                item_sum = each.xpath(".//div[@class='item-sum']/strong/text()").extract()[0]
            except:
                item_sum = 0
                TmallSpider.log(self, "total sum is error, url is %s" % response.url, level=logging.INFO)

            item_price = each.xpath(".//span[@class='ui-price']/strong/text()").extract()[0]
            yield scrapy.Request(url, callback=self.parse_item, cookies=cookies, meta={
                'cookies': cookies,
                'item_id': item_id,
                'item_name': item_name,
                'item_sum': item_sum,
                'item_price': item_price
            })
        page_next_node =response.xpath("//a[@class='page-next']/@href").extract()
        if len(page_next_node):
            page_next_url = "https://list.tmall.com/search_product.htm" + page_next_node[0]
            yield scrapy.Request(url=page_next_url, callback=self.parse, cookies=cookies, meta={'cookies': cookies})

    def parse_item(self, response):
        item = TMallItem()
        item['uid'] = response.meta['item_id']
        item['name'] = response.meta['item_name']
        item['total_sum'] = response.meta['item_sum']
        item['price'] = response.meta['item_price']
        tmp_photos = response.xpath("//ul[@id='J_UlThumb']/li/a/img/@src").extract()
        item['photo1'] = ""
        item['photo2'] = ""
        item['photo3'] = ""
        item['photo4'] = ""
        item['photo5'] = ""
        photo_index = 1
        for each in tmp_photos:
            each = "https:" + each
            each = each.replace("60x60", "430x430")
            item['photo'+str(photo_index)] = each
            photo_index += 1
        cookies = response.meta['cookies']
        url = "https:" + re.search("\"initApi\":\"(.*?)\",\"initC", response.body.decode('gbk', 'ignore')).group(1)
        yield scrapy.Request(url, callback=self.parse_info, cookies=cookies, meta={'item': item, 'cookies':cookies})

    def parse_info(self, response):
        data = json.loads(response.body.decode('gbk', 'ignore'))
        item = response.meta['item']
        item['month_sum'] = data['defaultModel']['sellCountDO']['sellCount']
        url = "https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=%s&callback=jsonp319" % item['uid']
        yield scrapy.Request(url, callback=self.parse_info1, cookies=response.meta['cookies'], meta={'item': item})

    def parse_info1(self, response):
        jsonp_data = response.body.decode('gbk', 'ignore')
        data = re.search("jsonp319\((.*)\)", jsonp_data).group(1)
        data = json.loads(data)
        item = response.meta['item']
        item['rate'] = data['dsr']['gradeAvg']
        item['rate_total'] = data['dsr']['rateTotal']
        yield item