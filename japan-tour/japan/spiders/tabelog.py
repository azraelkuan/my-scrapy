# -*- coding: utf-8 -*-
import scrapy
import sys
import io
import logging
from ..items import TabeLogItem
import re

# 网页默认编码是utf-8但是命令行是gbk，所以cmd输出是会转换编码 而gbk只支持部分
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors='replace', line_buffering=True) #改变标准输出的默认编码


class TabelogSpider(scrapy.Spider):
    num_jp = 0
    num_en = 0
    name = "tabelog"
    allowed_domains = ["tabelog.com"]
    start_urls = ['https://tabelog.com/tokyo/rstLst/RC/']
    pipelines = ['TabeLogPipeline']

    # 得到区域组合范围
    def parse(self, response):
        city_node = response.xpath("//a[@id='js-leftnavi-area-anchor']/span/text()")
        city_name = city_node.extract()[0].strip()
        response.meta['city_name'] = city_name

        areas_nodes = response.xpath("//div[@id='tabs-panel-balloon-pref-area']//li[@class='list-balloon__list-item']/a")
        for areas_node in areas_nodes:
            url = areas_node.xpath("./@href").extract()[0]
            yield scrapy.Request(url=url, callback=self.parse_area, meta=response.meta)

    # 获得区域
    def parse_area(self, response):
        area_nodes = response.xpath("//div[@id='tabs-panel-balloon-pref-area']//li[@class='list-balloon__list-item']/a")
        for area_node in area_nodes:
            url = area_node.xpath("./@href").extract()[0]
            area_name = area_node.xpath(".//text()").extract()[0]
            response.meta['area_name'] = area_name
            yield scrapy.Request(url=url, callback=self.parse_tag, meta=response.meta)

    # 获得类别
    def parse_tag(self, response):
        tag_nodes = response.xpath("//div[@id='js-leftnavi-genre-scroll']//li[@class='list-balloon__list-item']//a")
        for tag_node in tag_nodes:
            tag = tag_node.xpath("./text()").extract()[0]
            url = tag_node.xpath("./@href").extract()[0]
            response.meta['tag'] = tag
            yield scrapy.Request(url=url, callback=self.parse_store, meta=response.meta)

    # 获得子类别
    # def parse_sub_tag(self, response):
    #     sub_tag_nodes = response.xpath("//div[@id='js-leftnavi-genre-scroll']//li[@class='list-balloon__list-item']//a")
    #     for sub_tag_node in sub_tag_nodes:
    #         sub_tag = sub_tag_node.xpath("./text()").extract()[0]
    #         url = sub_tag_node.xpath("./@href").extract()[0]
    #         # print(sub_tag, url)
    #         response.meta['sub_tag'] = sub_tag
    #         yield scrapy.Request(url=url, callback=self.parse_store, meta=response.meta)

    def parse_store(self, response):
        store_nodes = response.xpath("//ul[@class='js-rstlist-info rstlist-info']//li[@data-rst-id]")
        for store_node in store_nodes:
            store_link = store_node.xpath("./@data-detail-url").extract()[0]
            store_id = store_node.xpath("./@data-rst-id").extract()[0]
            # print(store_link, store_id)
            response.meta['store_id'] = store_id
            yield scrapy.Request(url=store_link, callback=self.parse_jp_data, meta=response.meta)

        next_page_node = response.xpath("//div[@class='page-move']//a[@rel='next']")
        if len(next_page_node):
            next_page_url = next_page_node.xpath("./@href").extract()[0]
            # print(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse_store, meta=response.meta)

    def parse_jp_data(self, response):
        name = response.xpath("//h2[@class='display-name']//span[@property]//text()").extract()[0].strip()

        try:
            nearest_station = response.xpath("//dl[@class='rdheader-subinfo__item rdheader-subinfo__item--station']"
                                         "//a//span[@class='linktree__parent-target-text']//text()").extract()[0].strip()
        except:
            nearest_station = response.xpath("//dl[@class='rdheader-subinfo__item']/dd[@class='rdheader-subinfo__item-text']/text()").extract()[0].strip()
            TabelogSpider.log(self, "nearest_station error, url is %s" % response.url, level=logging.WARNING)

        all_type_list = response.xpath("//dl[@class='rdheader-subinfo__item']"
                                  "//a//span[@class='linktree__parent-target-text']//text()").extract()
        main_type = all_type_list[0] if len(all_type_list) > 0 else ""
        sub_type = all_type_list[1] if len(all_type_list) > 1 else ""
        sub_sub_type = all_type_list[2] if len(all_type_list) > 2 else ""

        try:
            average_rating = response.xpath("//div[@id='js-detail-score-open']//b[@rel='v:rating']/span//text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "average_rating error, url is %s" % response.url, level=logging.WARNING)
            average_rating = 0
        try:
            dinner_rating = response.xpath("//div[@class='rdheader-rating__time']/span[contains(@class, 'dinner')]/em/text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "dinner_rating error, url is %s" % response.url, level=logging.WARNING)
            dinner_rating = 0
        try:
            lunch_rating = response.xpath("//div[@class='rdheader-rating__time']/span[contains(@class, 'lunch')]/em/text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "lunch_rating error, url is %s" % response.url, level=logging.WARNING)
            lunch_rating = 0
        try:
            rating_review_num = response.xpath("//li[@class='rdheader-counts__item']//em[@class='num']/text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "rating_review_num error, url is %s" % response.url, level=logging.WARNING)
            rating_review_num = 0

        try:
            dinner_price = response.xpath("//div[@class='rdheader-budget']/p[contains(@class, 'dinner')]/span/a//text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "dinner_price error, url is %s" % response.url, level=logging.WARNING)
            dinner_price = 0
        try:
            lunch_price = response.xpath("//div[@class='rdheader-budget']/p[contains(@class, 'lunch')]/span/a//text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "lunch_price error, url is %s" % response.url, level=logging.WARNING)
            lunch_price = 0

        try:
            photo_num = response.xpath("//li[@id='rdnavi-photo']//span[@class='total-count']/strong/text()").extract()[0].strip()
        except:
            TabelogSpider.log(self, "photo_num error, url is %s" % response.url, level=logging.WARNING)
            photo_num = 0

        try:
            tel = response.xpath("//div[@id='js-rst-ppc-tel-info']/@data-rst-tel-ppc").extract()[0].strip()
        except:
            TabelogSpider.log(self, "tel error, url is %s" % response.url, level=logging.WARNING)
            tel = ""
        try:
            sub_tel = response.xpath("//p[@id='js-rst-tel-info']/@data-rst-tel").extract()[0].strip()
        except:
            TabelogSpider.log(self, "sub_tel error, url is %s" % response.url, level=logging.WARNING)
            sub_tel = ""

        try:
            address = "".join(response.xpath("//p[@rel='address']//text()").extract())
        except:
            TabelogSpider.log(self, "address error, url is %s" % response.url, level=logging.WARNING)
            address = ""

        try:
            center_node = response.xpath("//div[@class='rst-map']//img[1]/@data-original")
            center_str = "".join(center_node.extract())
            center = re.search("(\d+\.\d+,\d+\.\d+)", center_str).group(1)
        except:
            TabelogSpider.log(self, "center error, url is %s" % response.url, level=logging.WARNING)
            center = ""

        try:
            open_time_list = response.xpath("//div[@id='rstdata-wrap']//th[contains(text(), '営業時間')]/parent::tr//td//text()").extract()
            open_time = ""
            for each in open_time_list:
                open_time = open_time + " " + each.strip()
        except:
            TabelogSpider.log(self, "open_time error, url is %s" % response.url, level=logging.WARNING)
            open_time = ""

        try:
            seats_num = response.xpath("//div[@id='rstdata-wrap']//th[contains(text(), '席数')]/parent::tr//td/p/strong/text()").extract()[0]
        except:
            TabelogSpider.log(self, "seats_num error, url is %s" % response.url, level=logging.WARNING)
            seats_num = 0

        try:
            drink = response.xpath("//div[@id='rstdata-wrap']//th[contains(text(), 'ドリンク')]/parent::tr//td/p/text()").extract()[0]
        except:
            TabelogSpider.log(self, "drink error, url is %s" % response.url, level=logging.WARNING)
            drink = ""

        try:
            opening_day = response.xpath("//div[@id='rstdata-wrap']//th[contains(text(), 'オープン日')]/parent::tr//td/p/text()").extract()[0]
        except:
            TabelogSpider.log(self, "opening_day error, url is %s" % response.url, level=logging.WARNING)
            opening_day = ""

        item = TabeLogItem()
        item['name'] = name
        item['nearest_station'] = nearest_station
        item['main_type'] = main_type
        item['sub_type'] = sub_type
        item['sub_sub_type'] = sub_sub_type
        item['average_rating'] = average_rating
        item['dinner_rating'] = dinner_rating
        item['lunch_rating'] = lunch_rating
        item['rating_review_num'] = rating_review_num
        item['dinner_price'] = dinner_price
        item['lunch_price'] = lunch_price
        item['photo_num'] = photo_num
        item['tel'] = tel
        item['sub_tel'] = sub_tel
        item['address'] = address
        item['center'] = center
        item['open_time'] = open_time
        item['seats_num'] = seats_num
        item['drink'] = drink
        item['opening_day'] = opening_day

        item['city_name'] = response.meta['city_name']
        item['area_name'] = response.meta['area_name']
        item['tag'] = response.meta['tag']
        item['store_id'] = response.meta['store_id']
        item['url'] = response.url
        item['lang'] = 'jp'
        yield item

        self.num_jp += 1
        print(self.num_jp, response.url, "JP")

        # 处理英文页面
        url = re.sub("/tokyo/A", '/en/tokyo/A', response.url)
        response.meta['item'] = item
        yield scrapy.Request(url, callback=self.parse_en_data, meta=response.meta)

    def parse_en_data(self, response):
        item = response.meta['item']
        item['lang'] = 'en'

        name = response.xpath("//h2[@class='rd-header__rst-name']/a/text()").extract()[0].strip()
        try:
            nearest_station = response.xpath("//div[@class='rd-header__info-table']//span[contains(text(), 'Nearest station')]/ancestor::dl/dd/text()").extract()[0].strip()
        except:
            nearest_station = response.xpath("(//div[@class='rd-header__info-table']/dl)[1]/dd/text()").extract()[0].strip()
            TabelogSpider.log(self, "EN nearest_station error, url is %s" % response.url, level=logging.WARNING)

        all_type_list = response.xpath("//div[@class='rd-header__info-table']//span[contains(text(), 'Categories')]/ancestor::dl/dd//p//a/span/text()").extract()
        main_type = all_type_list[0] if len(all_type_list) > 0 else ""
        sub_type = all_type_list[1] if len(all_type_list) > 1 else ""
        sub_sub_type = all_type_list[2] if len(all_type_list) > 2 else ""

        try:
            address_list = response.xpath("//section[@id='anchor-rd-detail']//p[@class='rd-detail-info__rst-address']/text()").extract()
            address = ""
            for each in address_list:
                address = address + each.strip()
        except:
            TabelogSpider.log(self, "EN address error, url is %s" % response.url, level=logging.WARNING)
            address = ""

        try:
            open_time_list = response.xpath("//section[@id='anchor-rd-detail']//th[contains(text(), 'Operating Hours')]/parent::tr/td//text()").extract()
            open_time = ""
            for each in open_time_list:
                open_time = open_time + " " + each.strip()
        except:
            TabelogSpider.log(self, "EN open_time error, url is %s" % response.url, level=logging.WARNING)
            open_time = ""

        try:
            drink = response.xpath("//section[@id='anchor-rd-detail']//th[contains(text(), 'Drink')]/parent::tr/td/p/text()").extract()[0]
        except:
            TabelogSpider.log(self, "EN drink error, url is %s" % response.url, level=logging.WARNING)
            drink = ""

        item['name'] = name
        item['nearest_station'] = nearest_station
        item['main_type'] = main_type
        item['sub_type'] = sub_type
        item['sub_sub_type'] = sub_sub_type
        item['address'] = address
        item['open_time'] = open_time
        item['drink'] = drink
        item['url'] = response.url
        yield item
        self.num_en += 1
        print(self.num_en, response.url, "EN")

