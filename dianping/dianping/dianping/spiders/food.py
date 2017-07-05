# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import io
from bs4 import BeautifulSoup
from ..items import DianpingItem

# 网页默认编码是utf-8但是命令行是gbk，所以cmd输出是会转换编码 而gbk只支持部分
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors='replace', line_buffering=True) #改变标准输出的默认编码


class FoodSpider(scrapy.Spider):
    name = "food"
    pipelines = ['DianpingPipeline']
    # allowed_domains = ["dianping.com"]
    start_urls = (
        'http://www.dianping.com/search/category/7/10',  # sz
    )

    # 获得所有的类别
    def parse(self, response):
        all_category = response.xpath("//div[@id='classfy']//a")
        for category in all_category:
            category_name = category.xpath(".//text()").extract()[0]
            category_link = "http://www.dianping.com" + category.xpath("./@href").extract()[0]
            city = response.xpath("//a[@class='city J-city']/text()").extract()[0]
            response.meta['city'] = city
            response.meta['pro'] = '广东'
            if category_link != response.url:
                response.meta['category_name'] = category_name
                yield scrapy.Request(url=category_link, callback=self.parse_category_sub, meta=response.meta)

    # 获得所有的子类别, 有可能没有
    def parse_category_sub(self, response):
        all_category_sub = response.xpath("//div[@id='classfy-sub']//a")
        if all_category_sub:
            for category in all_category_sub:
                category_sub_link = "http://www.dianping.com" + category.xpath("./@href").extract()[0]
                category_sub_name = category.xpath(".//text()").extract()[0]
                if category_sub_link != response.url:
                    response.meta['category_sub_name'] = category_sub_name
                    yield scrapy.Request(url=category_sub_link, callback=self.parse_district, meta=response.meta)
        else:
            response.meta['category_sub_name'] = ""
            link = response.url + "?test=1"  # 防止链接duplicate
            yield scrapy.Request(url=link, callback=self.parse_district, meta=response.meta)

    # 按区划分
    def parse_district(self, response):
        all_district = response.xpath("//div[@id='region-nav']//a")
        for district in all_district:
            district_link = "http://www.dianping.com" + district.xpath("./@href").extract()[0]
            district_name = district.xpath(".//text()").extract()[0]

            if district_link != response.url:
                response.meta['district_name'] = district_name
                yield scrapy.Request(url=district_link, callback=self.parse_sub_district, meta=response.meta)

    def parse_sub_district(self, response):
        all_sub_district = response.xpath("//div[@id='region-nav-sub']//a")
        try:
            district_tmp_num = response.xpath("//div[@class='bread J_bread']/span[@class='num']//text()").extract()[0]
            district_num = int(re.search("(\d+)", district_tmp_num).group(1))
        except:
            district_num = 0
        if district_num <= 750:
            link = response.url + "?test=2"
            yield scrapy.Request(url=link, callback=self.parse_url, meta=response.meta)
        # elif district_num <= 1500:
        #     price_high_link = response.url + 'o8'
        #     price_low_link = response.url + 'o8b1'
        #     yield scrapy.Request(url=price_high_link, callback=self.parse_url, meta=response.meta)
        #     yield scrapy.Request(url=price_low_link, callback=self.parse_url, meta=response.meta)
        else:
            if all_sub_district:
                for sub_district in all_sub_district:
                    sub_district_link = "http://www.dianping.com" + sub_district.xpath("./@href").extract()[0]

                    if sub_district_link != response.url:
                        yield scrapy.Request(url=sub_district_link, callback=self.parse_url, meta=response.meta)
                    else:
                        price_high_link = response.url + 'o8'
                        price_low_link = response.url + 'o8b1'
                        yield scrapy.Request(url=price_high_link, callback=self.parse_url, meta=response.meta)
                        yield scrapy.Request(url=price_low_link, callback=self.parse_url, meta=response.meta)

            else:
                link = response.url + "?test=2"
                yield scrapy.Request(url=link, callback=self.parse_url, meta=response.meta)

    # 获得商店的url并获得分页链接
    def parse_url(self, response):
        all_shop = response.xpath("//div[@id='shop-all-list']/ul/li")
        for shop in all_shop:
            url = shop.xpath(".//div[@class='tit']/a/@href").extract()[0]
            full_link = "http://www.dianping.com" + url
            yield scrapy.Request(url=full_link, callback=self.parse_data, meta=response.meta)

        page_links = response.xpath("//div[@class='page']/a[@class='PageLink']/@href")
        for page_link in page_links:
            link = "http://www.dianping.com" + page_link.extract()
            yield scrapy.Request(url=link, callback=self.parse_url, meta=response.meta)

    # 解析数据
    def parse_data(self, response):
        basic_info = response.xpath("//div[@id='basic-info']")
        # 名称
        try:
            name = basic_info.xpath("//h1[@class='shop-name']//text()").extract()[0].strip()
        except:
            name = "null"

        # 评分
        try:
            stars = basic_info.xpath(".//div[@class='brief-info']//span[1]/@class").extract()[0]
            stars = int(re.search("(\d+)", stars.strip()).group(1)) / 10.0
        except:
            stars = "null"

        info_data = basic_info.xpath(".//div[@class='brief-info']//span//text()").extract()
        info = ""
        for each in info_data:
            info += each
        # 评论
        try:
            comments = re.search('(\d+)条', info, re.U).group(1)
        except:
            comments = '0'
        # 价格
        try:
            price = re.search('人均：([\d\.]+)', info, re.U).group(1)
        except:
            price = '0'
        # 口味
        try:
            taste = re.search('口味：([\d\.]+)', info, re.U).group(1)
        except:
            taste = "0.0"
        # 环境
        try:
            environment = re.search('环境：([\d\.]+)', info, re.U).group(1)
        except:
            environment = "0.0"
        # 服务
        try:
            service = re.search('服务：([\d\.]+)', info, re.U).group(1)
        except:
            service = "0.0"

        # 电话
        try:
            tel = basic_info.xpath(".//span[@itemprop='tel']/text()").extract()[0]
        except:
            tel = ""

        # 地址
        try:
            address = response.xpath("//span[@itemprop='street-address']/@title").extract()[0]
        except:
            address = "null"

        # 团购
        tuan_tag = basic_info.xpath(".//a[contains(@class, 'tag-tuan-b')]")
        if tuan_tag:
            tuan = "Y"
        else:
            tuan = "N"
        # 订购
        ding_tag = basic_info.xpath(".//a[contains(@class, 'tag-ding-b')]")
        if ding_tag:
            ding = "Y"
        else:
            ding = "N"
        # 外卖
        wai_tag = basic_info.xpath(".//a[contains(@class, 'tag-wai-b')]")
        if wai_tag:
            wai = "Y"
        else:
            wai = "N"
        # 促销
        cu_tag = basic_info.xpath(".//a[contains(@class, 'tag-cu-b')]")
        if cu_tag:
            cu = "Y"
        else:
            cu = "N"
        # 会员卡
        ka_tag = basic_info.xpath(".//a[contains(@class, 'tag-ka-b')]")
        if ka_tag:
            ka = "Y"
        else:
            ka = "N"

        # 营业时间
        open_time = ""
        open_time_data = basic_info.xpath(".//p[@class='info info-indent']//span[2]//text()").extract()
        for each in open_time_data:
            if "周" or "每" in each:
                open_time = str(each).strip()

        # # 菜名
        try:
            dish_data = response.xpath("//script[@type='text/panel']//text()").extract()[0]
            soup = BeautifulSoup(dish_data, "lxml")
            dishes = soup.find("ul", class_="recommend-photo clearfix")
            dish = dishes.find_all('li')
            dish_list = ""
            for each in dish:
                dish_name = each.find('p', class_='name').string.strip()
                dish_price = each.find('span', class_='price')
                if dish_price:
                    dish_price = dish_price.string.replace('¥', '')
                    dish_list = dish_list + " " + dish_name + "(" + dish_price + ")"

                else:
                    dish_list = dish_list + " " + dish_name + "(" + "no price" + ")"
        except:
            # print("*************dish error**************")
            dish_list = ""
        try:
            other_dishes = soup.find("p", class_="recommend-name")
            other_dish = other_dishes.find_all('a', class_='item')
            other_dish_list = ''
            for each in other_dish:
                otehr_dish_name = each.contents[0].strip()
                other_dish_list = other_dish_list + " " + otehr_dish_name
        except:
            # print("*****************other dish error***************")
            other_dish_list = ''

        # 标签
        try:
            tags = response.xpath("//span[@class='good J-summary']//text()")
            tag_list = ""
            for tag in tags:
                tag = re.search("(.*)\(", tag.extract()).group(1)
                tag_list = tag + " " + tag_list
        except:
            print("*******************tag error****************")
            tag_list = ""

        item = DianpingItem()

        item['name'] = name
        item['stars'] = str(stars)
        item['comments'] = str(comments)
        item['price'] = str(price)
        item['taste'] = str(taste)
        item['service'] = str(service)
        item['environment'] = str(environment)
        item['tel'] = tel
        item['address'] = str(address).strip()
        item['tuan'] = tuan
        item['ding'] = ding
        item['wai'] = wai
        item['cu'] = cu
        item['ka'] = ka
        item['open_time'] = open_time
        item['dish_list'] = dish_list
        item['other_dish_list'] = other_dish_list
        item['tag_list'] = tag_list
        item['url'] = response.url

        item['category_name'] = response.meta['category_name']
        item['category_sub_name'] = response.meta['category_sub_name']
        item['district_name'] = response.meta['district_name']
        item['city'] = response.meta['city']
        item['pro'] = response.meta['pro']

        yield item



