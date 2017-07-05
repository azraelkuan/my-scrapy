# -*- coding: utf-8 -*-

import pymysql


def getconn():
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'db': 'shop',
        'user': 'root',
        'passwd': '067116',
        'charset': 'utf8',
        }
    conn = pymysql.connect(**config)
    return conn


class TMallPipeline(object):
    def process_item(self, item, spider):
        if self.__class__.__name__ in spider.pipelines:
            conn = getconn()
            cur = conn.cursor()
            sql = "insert tmall(uid,name,price,total_sum,month_sum,rate,rate_total,photo1,photo2,photo3,photo4,photo5) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            data = (item['uid'], item['name'], item['price'], item['total_sum'], item['month_sum'], item['rate'], item['rate_total'],
                    item['photo1'], item['photo2'], item['photo3'], item['photo4'], item['photo5'])
            cur.execute(sql, data)
            conn.commit()
            cur.close()
            conn.close()

