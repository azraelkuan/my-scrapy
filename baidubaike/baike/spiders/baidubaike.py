# -*- coding: utf-8 -*-
import scrapy
import re
import json
import logging
from baike.items import BaiduBaikeItem, ErrorItem
from scrapy.selector import Selector



class BaidubaikeSpider(scrapy.Spider):
    name = "baidubaike"
    allowed_domains = ["baike.baidu.com"]
    start_urls = ['https://baike.baidu.com/']
    sub_num = 0
    error_num = 0
    right_num = 0
    # rules = (
    #     Rule(LinkExtractor(allow='http://baike.baidu.com/view/\d+.htm?force=\d+', unique=True), follow=True),
    #     Rule(LinkExtractor(allow='http://baike.baidu.com/fenlei/.*', unique=True), follow=True),
    #     Rule(LinkExtractor(allow='http://baike.baidu.com/item/.*', unique=True), callback='parse_item', follow=True),
    #     Rule(LinkExtractor(allow='http://baike.baidu.com/view/\d+.htm', unique=True), callback='parse_item', follow=True),
    #     Rule(LinkExtractor(allow='http://baike.baidu.com/subview/\d+/\d+.htm.*', unique=True), callback='parse_item', follow=True),
    #     Rule(LinkExtractor(allow='http://baike.baidu.com/item/.*/\d+.*', unique=True), callback='parse_item', follow=True),
    # )

    def start_requests(self):
        base_url = "http://baike.baidu.com/view/%s.htm"
        for i in range(1, 10000000):
            yield scrapy.Request(url=base_url % str(i), callback=self.parse_item, meta={'i': i})

    def parse_item(self, response):
        # 错误页面直接不要
        if "error.html" in response.url:
            self.error_num += 1
            error_item = ErrorItem()
            error_item['url'] = response.url
            yield error_item

        item = BaiduBaikeItem()
        # 热度和时间
        try:
            item['last_update_time'] = response.xpath(".//span[@class='j-modified-time']//text()").extract()[0]
            item['item_id'] = re.search("newLemmaIdEnc:\"(.*)\"", response.body.decode('utf-8')).group(1)
            self.right_num += 1
        except:
            item['item_id'] = 0
            url_list = response.xpath("//ul[contains(@class, 'para-list')]//a[@data-lemmaid]/@href").extract()
            for sub_url in url_list:
                full_url = "http://baike.baidu.com" + sub_url
                self.sub_num += 1
                BaidubaikeSpider.log(self, "need to get sub baidu item, url is %s" % full_url,
                                     level=logging.WARNING)
                yield scrapy.Request(url=full_url, callback=self.parse_item, meta={'i': response.meta['i']})
        # 初始设置pv为0
        item['pv'] = 0

        if item['item_id'] != 0:
            # 链接
            item['url'] = response.url
            # 标题
            item['title'] = self.deal_key(response.xpath(".//dd[contains(@class, 'lemmaTitle-title')]/h1/text()").extract()[0])
            # 介绍
            item['summary'] = self.deal_str("".join(response.xpath("//div[@class='lemma-summary']//div[@class='para']//text()").extract()))
            # 基本信息
            try:
                basic_info_node = response.xpath(".//dl[contains(@class, 'basicInfo-block')]/*")
                item['basic_info'] = {}
                i = 0
                while i < len(basic_info_node):
                    name = self.deal_key(self.deal_str("".join(basic_info_node[i].xpath(".//text()").extract())))
                    value = self.deal_str("".join(basic_info_node[i + 1].xpath(".//text()").extract()))
                    item['basic_info'][name] = value
                    i += 2
            except:
                BaidubaikeSpider.log(self, "basic info error, url is %s" % response.url, level=logging.WARNING)
                item['basic_info'] = {}
            # 所有信息
            try:
                all_para_node = response.xpath("//div[@class='para-title level-2']")
                level2 = {}
                if len(all_para_node) != 0:
                    for j in range(len(all_para_node)-1):
                        # 找到两个一级标题之间的所有节点
                        following_nodes = all_para_node[j].xpath("./following-sibling::*").extract()
                        level2_title = self.deal_key(all_para_node[j].xpath("./h2/text()").extract()[0])
                        preceding_nodes = all_para_node[j+1].xpath("./preceding-sibling::*").extract()
                        inter_str = [var for var in following_nodes if var in preceding_nodes]
                        # 寻找二级标题
                        level2 = self.find_level3(inter_str, level2, level2_title)

                    # 最后一个二级标题
                    last_node = all_para_node[-1]
                    following_nodes = last_node.xpath("./following-sibling::*").extract()
                    level2_title = self.deal_key(last_node.xpath("./h2/text()").extract()[0])
                    inter_str = following_nodes
                    level2 = self.find_level3(inter_str, level2, level2_title)

                    item['level2'] = level2
                else:
                    para_str = response.xpath("//div[@class='lemma-summary']/following-sibling::div[@label-module='para']//text()").extract()
                    level2[item['title']] = self.deal_str(" ".join(para_str))
                    item['level2'] = level2
            except:
                BaidubaikeSpider.log(self, "all info error, url is %s" % response.url, level=logging.WARNING)
                item['level2'] = {}

            yield item

            if self.right_num % 1000 == 0:
                print(response.meta['i'], self.right_num, self.sub_num, self.error_num)

        # 热度单独爬取
        # url = "http://baike.baidu.com/api/lemmapv?id=" + item['item_id']
        # response.meta['item'] = item
        # yield scrapy.Request(url, callback=self.parse_pv, meta=response.meta)

    def parse_pv(self, response):
        data = json.loads(response.body.decode('utf-8'))
        item = response.meta['item']
        item['pv'] = data['pv']
        yield item

    # 处理字符
    def deal_str(self, string):
        string = string.replace('\xa0', '')
        string = string.replace('\n', '')
        string = string.replace('\r', '')
        string = re.sub("\[.*\]", '', string)
        string = string.strip()
        return string

    def deal_key(self, string):
        string = string.replace(".", "")
        return string

    # 判断是否有二级并添加信息
    def find_level3(self, inter_str, level2, level2_title):
        # 找到一级标题之间的二级目录节点
        para_level3_index = []
        for var in inter_str:
            if "para-title level-3" in var:
                para_level3_index.append(inter_str.index(var))
        # 如果存在二级目录节点
        level3 = {}
        if len(para_level3_index) != 0:
            # 每两个二级标题之间取信息
            for k in range(len(para_level3_index) - 1):
                first_level3_node = Selector(text=inter_str[para_level3_index[k]])
                level3_title = self.deal_key(first_level3_node.xpath("//h3/text()").extract()[0])
                level3[level3_title] = ""
                for para_index in range(para_level3_index[k] + 1, para_level3_index[k + 1]):
                    para_str = inter_str[para_index]
                    if "label-module=\"para" in para_str:
                        para_node = Selector(text=para_str)
                        para_str = self.deal_str("".join(para_node.xpath("//text()").extract()))
                        level3[level3_title] += para_str
            # 最后一个二级标题
            last_level3_node = Selector(text=inter_str[para_level3_index[-1]])
            level3_title = self.deal_key(last_level3_node.xpath("//h3/text()").extract()[0])
            level3[level3_title] = ""
            for para_index in range(para_level3_index[-1] + 1, len(inter_str)):
                para_str = inter_str[para_index]
                if "label-module=\"para" in para_str:
                    para_node = Selector(text=para_str)
                    para_str = self.deal_str("".join(para_node.xpath("//text()").extract()))
                    level3[level3_title] += para_str
            level2[level2_title] = level3
        # 如果一级标题之间没有二级标题
        else:
            level2[level2_title] = ""
            for var in inter_str:
                if "label-module=\"para" in var:
                    para_node = Selector(text=var)
                    para_str = self.deal_str("".join(para_node.xpath("//text()").extract()))
                    level2[level2_title] += para_str
        return level2
