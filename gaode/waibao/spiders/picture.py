# -*- coding: utf-8 -*-
import scrapy
import re
from ..pipelines import connDB


class PictureSpider(scrapy.Spider):
    name = "picture"
    allowed_domains = ["ditu.amap.com"]
    conn, cur = connDB()
    i = 0
    database_name = "shanghai"

    def start_requests(self):

        sql = "select uid, photo_urls from `%s`" % self.database_name
        # sql = "select uid from %s where uid != ''" % self.database_name
        self.cur.execute(sql)
        data = self.cur.fetchall()

        for each in data:
            picture_str = each[1]
            picture_list = picture_str.split(' ')
            # print(len(picture_list), picture_list)

            if len(picture_list) == 4:
                uid = each[0]
                if uid:
                    url = "http://ditu.amap.com/detail/%s" % uid
                    # print(url)
                    yield self.make_requests_from_url(url)

    def parse(self, response):
        self.i += 1
        print(self.i)

        url = response.url
        uid = str(re.search("([0-9A-Z]+)", url).group(1))

        photo_urls = ''
        img_nodes = response.xpath("//div[@class='display_wrap']//li/a[@class='example-image-link']/@href")
        for img_node in img_nodes:
            img_url = img_node.extract()
            photo_urls = photo_urls + ' ' + img_url
        # print(photo_urls)
        sql = "update `%s` set photo_urls = '%s' where uid = '%s'" % (self.database_name, photo_urls, uid)
        # print(sql)
        self.cur.execute(sql)
        self.conn.commit()








