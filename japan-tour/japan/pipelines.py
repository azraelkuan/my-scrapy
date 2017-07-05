# -*- coding: utf-8 -*-
import pymysql

def connDB():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='japan', charset='utf8')
    cur = conn.cursor()
    return conn, cur


class SpPipeline(object):
    def process_item(self, item, spider):
        if self.__class__.__name__ in spider.pipelines:
            try:
                conn, cur = connDB()
                sql = 'insert into sp(uid, `name`, address, tag, district_name, sub_district_name, tel, open_time, rest_time, feature)' \
                      'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

                data = (item['uid'], item['name'], item['address'], item['tag'], item['district_name'], item['sub_district_name'],
                        item['tel'], item['open_time'], item['rest_time'], item['feature'])
                cur.execute(sql, data)
                conn.commit()
                cur.close()
                conn.close()
            except:
                print("*****store exist*****")


class TabeLogPipeline(object):
    def process_item(self, item, spider):
        if self.__class__.__name__ in spider.pipelines:
            try:
                table = {
                    'jp': 'tabelog_jp',
                    'en': 'tabelog_en'
                }
                table_index = item['lang']
                table_name = table[table_index]

                sql = "insert into %s (store_id, `name`, address, center, nearest_station, main_type, sub_type, sub_sub_type, tag, average_rating, dinner_rating, " \
                      "lunch_rating, rating_review_num, dinner_price, lunch_price, photo_num, tel, sub_tel, open_time, seats_num, drink, opening_day, city_name, area_name, url) " \
                      "values(%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

                data = (table_name, item['store_id'], item['name'], item['address'], item['center'], item['nearest_station'], pymysql.escape_string(item['main_type']), pymysql.escape_string(item['sub_type']),
                        item['sub_sub_type'], item['tag'], item['average_rating'], item['dinner_rating'],
                        item['lunch_rating'], item['rating_review_num'], item['dinner_price'], item['lunch_price'], item['photo_num'], item['tel'], item['sub_tel'], item['open_time'],
                        item['seats_num'], item['drink'], item['opening_day'], item['city_name'], item['area_name'], item['url'])
                conn, cur = connDB()
                cur.execute(sql % data)
                conn.commit()
                cur.close()
                conn.close()
            except:
                print("********data exists********")

