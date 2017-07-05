# coding:utf-8
from scrapy import Selector
import requests
from urllib import request


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    }


def get_xicidaili():
    url = "http://www.xicidaili.com/nn/%s"
    for i in range(1, 2):
        page_url = url % str(i)
        print(page_url)
        s = requests.session()
        req = s.get(page_url, headers=headers)
        selector = Selector(text=req.text)
        ip_nodes = selector.xpath("//table//tr")
        for each in ip_nodes[1:]:
            ip = each.xpath("./td[2]/text()").extract()[0]
            port = each.xpath("./td[3]/text()").extract()[0]
            http_type = each.xpath("./td[6]/text()").extract()[0]
            if http_type == "HTTP":
                proxies = {
                    "http": "%s://%s:%s" % ("http", ip, port),
                    "https": "%s://%s:%s" % ("http", ip, port),
                    }
                try:
                    r = requests.get('http://www.ip138.com/', proxies=proxies, timeout=5)
                    if r.status_code == 200:
                        print("%s:%s is valid" % (ip, port))
                except:
                    print("%s:%s is not valid" % (ip, port))


def get_qwdaili():
    port_dict = {
        'GEGEA': '8080',
        'HZZZC': '9999',
        'CFACE': '3128',
        'GEGE': '808',
        'DGEEDC': '45554',
        'GEA': '80',
        'HBZIE': '8998',
        'GEZEE': '8118',
        'GEGEI': '8081'
    }
    m = 0
    url = "http://www.goubanjia.com/free/gngn/index%s.shtml"
    for i in range(1, 10):
        page_url = url % str(i)
        s = requests.session()
        req = s.post(page_url, headers=headers)
        selector = Selector(text=req.text)
        ip_nodes = selector.xpath("//td[@class='ip']")
        for each in ip_nodes:
            ip_list = each.xpath("./*[name()!='p']/text()").extract()
            ip = "".join(ip_list[0:-1])
            tmp_port = each.xpath("./span[contains(@class, 'port')]/@class").extract()[0]
            port_str = tmp_port.split()[1]
            if port_str in port_dict:
                port = port_dict[port_str]
                # print(ip, port)
                proxies = {
                    "http": "%s://%s:%s" % ("http", ip, port),
                    "https": "%s://%s:%s" % ("http", ip, port),
                }
                try:
                    r = requests.get('http://www.ip138.com/', proxies=proxies, timeout=5)
                    if r.status_code == 200:
                        print("%s:%s is valid" % (ip, port))
                        m+= 1
                except:
                    print("%s:%s is not valid" % (ip, port))
            else:
                print(port_str)
    print(m)

if __name__ == '__main__':
    get_qwdaili()
