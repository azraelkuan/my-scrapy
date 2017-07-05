
# -*- coding: utf-8 -*-
import scrapy
from baike.items import SWGItem



class SwgSpider(scrapy.Spider):
    name = "swg"
    allowed_domains = ["chazidian.com"]

    def start_requests(self):
        for i in range(1, 64):
            url = "https://www.chazidian.com/kepu-1/%s/"
            url %= str(i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        info_urls = response.xpath("//ul[@class='common']//li//a/@href").extract()
        for each in info_urls:
            yield scrapy.Request(url=each, callback=self.parse_item)

    def parse_item(self, response):
        print(response.url)
        question = response.xpath("//span[@id='print_title']//text()").extract()[0]
        answer = "".join(response.xpath("//div[@id='print_content']/p/text()").extract()).strip()
        item = SWGItem()
        item['question'] = question
        item['answer'] = answer
        yield item