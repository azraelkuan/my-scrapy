# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import SpItem

class SpSpider(scrapy.Spider):
    name = "sp"
    pipelines = ['SpPipeline']
    allowed_domains = ["yahoo.co.jp"]
    start_urls = (
        'http://search.loco.yahoo.co.jp/search?areacd=13',
    )

    def parse(self, response):
        area_nodes = response.xpath("//li[@id='lsPanel2']/ul[@class='linkList']/li/a")
        for area_node in area_nodes:
            url = area_node.xpath("./@href").extract()[0]
            district_name = area_node.xpath("./text()").extract()[0]
            # print(url, district_name)
            response.meta['district_name'] = district_name
            yield scrapy.Request(url=url, callback=self.parse_sub, meta=response.meta)

    def parse_sub(self, response):
        sub_area_nodes = response.xpath("//li[@id='lsPanel2']/ul[@class='linkList']/li/a")
        for sub_area_node in sub_area_nodes:
            url = sub_area_node.xpath("./@href").extract()[0]
            sub_district_name = sub_area_node.xpath("./text()").extract()[0]
            # print(url, sub_district_name)
            response.meta['sub_district_name'] = sub_district_name
            yield scrapy.Request(url=url, callback=self.parse_tag, meta=response.meta)

    def parse_tag(self, response):
        parameter = '&genrecd='
        tags = {'0205001': 'コンビニ', '0205002': 'スーパー'}   # 包括超市002和便利店001
        for (key, val) in tags.items():
            url = response.url + parameter + key
            # print(url)
            response.meta['tag'] = val
            yield scrapy.Request(url=url, callback=self.parse_store, meta=response.meta)

    def parse_store(self, response):
        # 分页链接
        next_pages = response.xpath("//div[@id='Sp1']//span[@class='m']/a")
        for next_page in next_pages:
            next_page_text = "".join(next_page.xpath('.//text()').extract())
            if "次へ" in next_page_text:
                page_url = next_page.xpath("./@href").extract()[0]
                print(page_url)
                yield scrapy.Request(url=page_url, callback=self.parse_store, meta=response.meta)

        # 商店链接
        store_nodes = response.xpath("//div[@class='LSaj cf']//div[@class='rc']//h3//a")
        for store_node in store_nodes:
            store_url = store_node.xpath("./@href").extract()[0]
            yield scrapy.Request(url=store_url, callback=self.parse_data, meta=response.meta)

    def parse_data(self, response):
        url = response.url
        # 商店的唯一标识
        uid = re.search("place/(.*)/\?", url).group(1)
        # 商店名称
        name = response.xpath("//div[@class='title']//p[@itemprop='itemreviewed']/a/text()").extract()
        # 商店地址
        address = "".join(response.xpath("//div[@class='access']/p[@class='address']/text()").extract()).strip()
        # 其他信息
        info_nodes = response.xpath("//div[@id='outline']/ul[@class='detailInfo']//li")
        tel = ''
        open_time = ''
        rest_time = ''
        feature = ''
        for info_node in info_nodes:
            try:
                line_text = ''
                text_list = info_node.xpath(".//text()").extract()
                for text in text_list:
                    text = text.strip()
                    line_text += text
                line_text = re.sub("情報提供.*", "", line_text)
                line_text = re.sub("[ /]", "", line_text)
                if "電話番号" in line_text:
                    tel = re.search("電話番号([-0-9]+)", line_text).group(1)
                if "営業時間" in line_text:
                    open_time = re.search("営業時間(.*)", line_text).group(1)
                if "定休日" in line_text:
                    rest_time = re.search("定休日(.*)", line_text).group(1)
                if "特徴" in line_text:
                    feature = re.search("特徴(.*)", line_text).group(1)
            except:
                print('有信息错误，不能解码')

        item = SpItem()
        item['uid'] = uid
        item['name'] = name
        item['address'] = address
        item['tag'] = response.meta['tag']
        item['district_name'] = response.meta['district_name']
        item['sub_district_name'] = response.meta['sub_district_name']
        item['tel'] = tel
        item['open_time'] = open_time
        item['rest_time'] = rest_time
        item['feature'] = feature
        yield item




