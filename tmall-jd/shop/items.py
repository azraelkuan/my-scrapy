# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TMallItem(scrapy.Item):
    uid = scrapy.Field()
    name = scrapy.Field()
    total_sum = scrapy.Field()
    price = scrapy.Field()
    month_sum = scrapy.Field()
    rate_total = scrapy.Field()
    rate = scrapy.Field()
    photo1 = scrapy.Field()
    photo2 = scrapy.Field()
    photo3 = scrapy.Field()
    photo4 = scrapy.Field()
    photo5 = scrapy.Field()
    pass
