# -*- coding: utf-8 -*-

# Define here the model for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class GaoDeItem(Item):
    uid = Field()  # 高德上的id
    name = Field()
    address = Field()
    tag = Field()
    sub_tag = Field()
    center = Field()
    tel = Field()
    pro_name = Field()
    pro_center = Field()
    city_name = Field()
    city_center = Field()
    ad_name = Field()
    ad_center = Field()
    photo_url1 = Field()
    photo_url2 = Field()
    photo_url3 = Field()
    photo_exists = Field()
    table_name = Field()
