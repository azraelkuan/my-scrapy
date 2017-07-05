# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduBaikeItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    basic_info = scrapy.Field()
    level2 = scrapy.Field()
    pv = scrapy.Field()
    item_id = scrapy.Field()
    last_update_time = scrapy.Field()


class SWGItem(scrapy.Item):
    question = scrapy.Field()
    answer = scrapy.Field()


class ErrorItem(scrapy.Item):
    url = scrapy.Field()
