# -*- coding: utf-8 -*-
import pymysql


def connDB():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='dianping', charset='utf8')
    cur = conn.cursor()
    return conn, cur


class DianpingPipeline(object):
    def process_item(self, item, spider):
        if self.__class__.__name__ in spider.pipelines:
            try:
                conn, cursor = connDB()

                sql = "insert into shenzhen1(pro,city,category_name,category_sub_name,district_name,`name`,stars," \
                      "comments,price,taste,environment,service,address,tel,tuan,ding,wai,cu,ka,open_time,dish_list,other_dish_list,tag_list,url) " \
                      "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                data = (item['pro'], item['city'], item['category_name'], item['category_sub_name'],
                        item['district_name'], item['name'], item['stars'], item['comments'], item['price'],
                        item['taste'], item['environment'], item['service'], item['address'], item['tel'], item['tuan'],
                        item['ding'], item['wai'], item['cu'], item['ka'], item['open_time'], item['dish_list'],
                        item['other_dish_list'], item['tag_list'], item['url'])
                cursor.execute(sql, data)

                conn.commit()
                cursor.close()
                conn.close()
            except:
                print("************exists***************")

