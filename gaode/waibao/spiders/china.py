# -*- coding: utf-8 -*-
import scrapy
import sys
import io
import re
from ..items import ChinaItem


# 网页默认编码是utf-8但是命令行是gbk，所以cmd输出是会转换编码 而gbk只支持部分
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors='replace', line_buffering=True) #改变标准输出的默认编码


class ChinaSpider(scrapy.Spider):
    name = "china"
    pipelines = ['ChinaPipeline']
    allowed_domains = ["www.citypopulation.de"]
    start_urls = ['https://www.citypopulation.de/China-Townships.html']

    def parse(self, response):
        node_path = response.xpath("//h1")
        for each in node_path[1:]:
            pro_name = each.xpath("./text()").extract()[0]
            response.meta['pro_name'] = pro_name
            city_nodes = each.xpath("./following-sibling::div[@class='mcol'][1]/div[@class='col']//a")
            for city in city_nodes:
                url = "https://www.citypopulation.de/" + city.xpath("./@href").extract()[0]
                city_name = city.xpath("./text()").extract()[0]
                response.meta['city_name'] = city_name
                # print(url, city_name)
                yield scrapy.Request(url=url, callback=self.parse_city, meta=response.meta)

    def parse_city(self, response):
        item = ChinaItem()
        item['pro_name'] = response.meta['pro_name']

        district_areas = response.xpath("//section[@id='adminareas']/table[@id='tl']")
        try:
            item['city_name'] = district_areas.xpath("./tfoot/tr/td[@class='rname']/span/a/text()").extract()[0]
        except:
            item['city_name'] = ''

        if item['city_name'] != "":
            item['city_native'] = district_areas.xpath("./tfoot/tr/td[@class='rnative']/span/text()").extract()[0]
            item['city_status'] = district_areas.xpath("./tfoot/tr/td[@class='rstatus']/text()").extract()[0]
            item['city_population'] = re.sub(',', '', district_areas.xpath("./tfoot/tr/td[@class='rpop prio1']/text()").extract()[0])

            district_list = []

            district_nodes = district_areas.xpath("./tbody/tr")
            for each in district_nodes:
                district_dict = {
                    'name': each.xpath("./td[@class='rname']/span//text()").extract()[0],
                    'native': each.xpath("./td[@class='rnative']/span/text()").extract()[0],
                    'status': each.xpath("./td[@class='rstatus']/text()").extract()[0],
                    'population': re.sub(",", '', each.xpath("./td[@class='rpop prio1']/text()").extract()[0])
                }
                district_list.append(district_dict)

            township_areas = response.xpath("//section[@id='citysection']/table[@id='ts']")

            township_nodes = township_areas.xpath("./tbody/tr")
            for each in township_nodes:
                name = each.xpath("./td[@class='rname']/span//text()").extract()[0]
                native = each.xpath("./td[@class='rnative']/span/text()").extract()[0]
                tmp_status = each.xpath("./td[@class='rstatus']/text()").extract()
                status = tmp_status[0] if len(tmp_status) else ""
                population = re.sub(",", '', each.xpath("./td[@class='rpop prio1']/text()").extract()[0])
                district_name = each.xpath("./td[@class='radm']/text()").extract()[0]

                is_find = 0
                for district in district_list:
                    if district_name == district['name']:
                        item['district_name'] = district_name
                        item['district_native'] = district['native']
                        item['district_status'] = district['status']
                        item['district_population'] = district['population']
                        is_find = 1
                if is_find == 0:
                    item['district_name'] = district_name
                    item['district_native'] = ''
                    item['district_status'] = ''
                    item['district_population'] = ''

                item['township_name'] = name
                item['township_native'] = native
                item['township_status'] = status
                item['township_population'] = population

                yield item
        else:
            item['city_native'] = ''
            item['city_status'] = ''
            item['city_population'] = ''
            item['district_name'] = ''
            item['district_native'] = ''
            item['district_status'] = ''
            item['district_population'] = ''
            item['township_name'] = ''
            item['township_native'] = ''
            item['township_status'] = ''
            item['township_population'] = ''
            item['city_name'] = response.meta['city_name']
            yield item
