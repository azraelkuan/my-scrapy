# -*- coding: utf-8 -*-
import scrapy
import re
from baike.items import SWGItem


class A10whySpider(scrapy.Spider):
    name = "10why"
    allowed_domains = ["10why.net"]
    start_urls = ['http://www.10why.net/archives']

    def parse(self, response):
        urls = response.xpath("//a[re:match(@class, 'post-\d+')]/@href").extract()
        for each in urls:
            if "post" in each:
                yield scrapy.Request(url=each, callback=self.parse_item)

    def parse_item(self, response):
        print(response.url)
        item = SWGItem()
        item['question'] = response.xpath("//h1[@class='entry-title']/text()").extract()[0]
        item['answer'] = "".join(response.xpath("//div[@class='entry-content']/p/text()").extract()).strip()
        yield item
