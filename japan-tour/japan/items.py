# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpItem(scrapy.Item):
    uid = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    tag = scrapy.Field()
    district_name = scrapy.Field()
    sub_district_name = scrapy.Field()
    tel = scrapy.Field()
    open_time = scrapy.Field()
    rest_time = scrapy.Field()
    feature = scrapy.Field()


class TabeLogItem(scrapy.Item):
    name = scrapy.Field()
    nearest_station = scrapy.Field()
    main_type = scrapy.Field()
    sub_type = scrapy.Field()
    sub_sub_type = scrapy.Field()
    average_rating = scrapy.Field()
    dinner_rating =scrapy.Field()
    lunch_rating = scrapy.Field()
    rating_review_num = scrapy.Field()
    dinner_price = scrapy.Field()
    lunch_price = scrapy.Field()
    photo_num = scrapy.Field()
    tel = scrapy.Field()
    sub_tel = scrapy.Field()
    address =scrapy.Field()
    center = scrapy.Field()
    open_time = scrapy.Field()
    seats_num = scrapy.Field()
    drink = scrapy.Field()
    opening_day = scrapy.Field()

    city_name = scrapy.Field()
    area_name = scrapy.Field()
    store_id = scrapy.Field()
    tag = scrapy.Field()
    url = scrapy.Field()

    lang = scrapy.Field()





