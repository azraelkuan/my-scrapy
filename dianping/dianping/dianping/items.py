# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DianpingItem(scrapy.Item):
    name = scrapy.Field()
    stars = scrapy.Field()
    address = scrapy.Field()
    price = scrapy.Field()
    taste = scrapy.Field()
    service = scrapy.Field()
    tel = scrapy.Field()
    environment = scrapy.Field()
    category_name = scrapy.Field()
    category_sub_name = scrapy.Field()
    district_name = scrapy.Field()
    district_sub_name = scrapy.Field()
    comments = scrapy.Field()
    tuan = scrapy.Field()
    ding = scrapy.Field()
    wai = scrapy.Field()
    cu = scrapy.Field()
    ka = scrapy.Field()
    open_time = scrapy.Field()
    dish_list = scrapy.Field()
    tag_list = scrapy.Field()
    url = scrapy.Field()
    other_dish_list = scrapy.Field()
    city = scrapy.Field()
    pro = scrapy.Field()
