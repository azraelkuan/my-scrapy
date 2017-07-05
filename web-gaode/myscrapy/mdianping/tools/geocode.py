# coding:utf-8
import json
import pymysql
import re
from urllib import request, parse


def conn_mdb():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='mdianping', charset='utf8')
    cur = conn.cursor()
    return conn, cur


def geocode():
    database = "shenzhen"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
        # 'Accept-Encoding': ' gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://m.dianping.com/shop/21337516?from=shoplist&shoplistqueryid=4a9f6f39-2ddb-452d-b2c6-627d7a466dbf',
        'Host': 'm.dianping.com',
        'Cookie':'PHOENIX_ID=0a060913-15905e38e3c-ffa427; download_banner=on; chwlsource=default; _hc.v=f6aff8a8-e11c-825c-ba48-dfd15c589492.1481862514; switchcityflashtoast=1; m_flash2=1; source=m_browser_test_33; issqt=false; sqttype=0; __mta=254517175.1481862513857.1481862513857.1481862518242.2; msource=default; default_ab=shop%3AA%3A1%7Cindex%3AA%3A1%7CshopList%3AA%3A1; __mta=254517175.1481862513857.1481862518242.1481862520106.3; pvhistory="5ZWG5oi35L2N572uPjo8L3Nob3AvMjEzNDA4ODMvbWFwPjo8MTQ4MTg2Mjc2ODU5Nl1fWw=="; cityid=7',
    }

    conn, cur = conn_mdb()
    sql = "select uid from %s where center=''" % database
    cur.execute(sql)
    data = cur.fetchall()
    # print(len(data))
    for each in data:
        uid = each[0]
        url = "https://m.dianping.com/shop/%s/map" % uid
        print(url)
        req = request.Request(url=url, headers=headers)
        response = request.urlopen(req)
        print(response.read().decode('utf-8'))

        # try:
        lat = re.search(".*", response.read().decode('utf-8')).group(0)
        lng = re.search(".*", response.read().decode('utf-8')).group(0)
        center = lng + "," + lat
        # except:
        #     center = ''
        print(center)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    geocode()
