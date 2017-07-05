# -*- coding: utf-8 -*-
import scrapy
import re
import logging
from mdianping.pipelines import connDB


class GeocodeSpider(scrapy.Spider):
    name = "geocode"
    allowed_domains = ["m.dianping.com"]
    database = "shenzhen"
    i = 0

    def start_requests(self):

        conn, cur = connDB()
        sql = "select uid from %s where center=''" % self.database
        cur.execute(sql)
        data = cur.fetchall()
        # print(len(data))
        for each in data:
            uid = each[0]
            url = "https://m.dianping.com/shop/%s/map" % uid
            yield self.make_requests_from_url(url)

    def parse(self, response):
        uid = re.search("(\d+)", response.url).group(1)
        try:
            lat = re.search("lat:([\d\.]+)", response.body.decode('utf-8')).group(1)
            lng = re.search("lng:([\d\.]+)", response.body.decode('utf-8')).group(1)
            center = lng + "," + lat
        except:
            center = ""
            self.i += 1
            print(self.i)
            GeocodeSpider.log(self, "center is error, url is %s" % response.url, level=logging.WARNING)

        conn, cur = connDB()
        sql = "update %s set center = '%s' where uid = %s" % (self.database, center, uid)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
