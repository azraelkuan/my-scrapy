# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MDianPingItem(scrapy.Item):
    uid = scrapy.Field()
    name = scrapy.Field()
    branch_name = scrapy.Field()
    stars = scrapy.Field()
    address = scrapy.Field()
    center = scrapy.Field()
    price = scrapy.Field()
    taste = scrapy.Field()
    service = scrapy.Field()
    tel = scrapy.Field()
    environment = scrapy.Field()
    category_name = scrapy.Field()
    sub_category_name = scrapy.Field()
    region_name = scrapy.Field()
    comments = scrapy.Field()
    has_deals = scrapy.Field()
    bookable = scrapy.Field()
    has_takeaway = scrapy.Field()
    has_mobilepay = scrapy.Field()
    has_promote = scrapy.Field()
    open_time = scrapy.Field()
    dish_list = scrapy.Field()
    city = scrapy.Field()
    pro = scrapy.Field()
