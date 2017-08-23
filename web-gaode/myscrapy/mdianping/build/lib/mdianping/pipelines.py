# -*- coding: utf-8 -*-
import pymysql


def connDB():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='mdianping', charset='utf8')
    cur = conn.cursor()
    return conn, cur


class MdianpingPipeline(object):
    def process_item(self, item, spider):
        if self.__class__.__name__ in spider.pipelines:
            try:
                conn, cur = connDB()
                sql = "insert into %s(uid,`name`,branch_name,stars,address,center,price,taste,service,tel,environment,category_name," \
                      "sub_category_name,district,region_name,comments,has_deals,bookable,has_takeaway,has_mobilepay,has_promote,open_time,dish_list," \
                      "city,pro) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
                data = (item['table_name'], item['uid'], item['name'], item['branch_name'], item['stars'], item['address'], item['center'], item['price'],
                        item['taste'], item['service'], item['tel'], item['environment'], item['category_name'], item['sub_category_name'],
                        item['district'], item['region_name'], item['comments'], item['has_deals'], item['bookable'], item['has_takeaway'],
                        item['has_mobilepay'], item['has_promote'], item['open_time'], item['dish_list'], item['city'],
                        item['pro'])
                cur.execute(sql % data)

                conn.commit()
                cur.close()
                conn.close()
            except:
                print("*********************data exists************************")
