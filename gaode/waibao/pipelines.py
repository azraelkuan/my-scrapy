# -*- coding: utf-8 -*-
import pymysql


def connDB():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='gaode', charset='utf8')
    cur = conn.cursor()
    return conn, cur


class GaoDePipeline(object):
    def __init__(self):
        self.i = 0

    def process_item(self, item, spider):
            if self.__class__.__name__ in spider.pipelines:
                try:
                    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='gaode', charset='utf8')
                    cur = conn.cursor()
                    sql = 'insert into xishiduo(uid,`name`,address,tag,sub_tag,center,tel,pro_name,pro_center,city_name,' \
                          'city_center,ad_name,ad_center,distance,photo_urls,photo_exists) ' \
                          'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

                    data = (item['uid'], item['name'], item['address'], item['tag'], item['sub_tag'], item['center'], item['tel'],
                            item['pro_name'], item['pro_center'], item['city_name'], item['city_center'], item['ad_name'],
                            item['ad_center'], item['distance'], item['photo_urls'], item['photo_exists'])
                    cur.execute(sql, data)
                    conn.commit()
                    cur.close()
                    conn.close()
                    self.i += 1
                    print(self.i)
                except:
                    pass
            else:
                return item

class GeocodePipeline(object):
    def process_item(self, item, spider):
            if self.__class__.__name__ in spider.pipelines:
                try:
                    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='gaode', charset='utf8')
                    cur = conn.cursor()
                    sql = 'insert into test(uid,`name`,address,tag,sub_tag,center,tel,pro_name,pro_center,city_name,' \
                          'city_center,ad_name,ad_center,distance,photo_urls,photo_exists,distributor) ' \
                          'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

                    data = (item['uid'], item['name'], item['address'], item['tag'], item['sub_tag'], item['center'], item['tel'],
                            item['pro_name'], item['pro_center'], item['city_name'], item['city_center'], item['ad_name'],
                            item['ad_center'], item['distance'], item['photo_urls'], item['photo_exists'], item['distributor'])
                    cur.execute(sql, data)
                    conn.commit()
                    cur.close()
                    conn.close()
                except:
                    print("**********exists**********")
            else:
                return item


class ChinaPipeline(object):
    def process_item(self, item, spider):
            if self.__class__.__name__ in spider.pipelines:
                conn, cur = connDB()
                sql = 'insert into china(township_name, township_native, township_status, township_population, ' \
                                        'district_name, district_native, district_status, district_population, ' \
                                        'city_name, city_native, city_status, city_population, ' \
                                        'pro_name) ' \
                      'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                data = (item['township_name'], item['township_native'], item['township_status'], item['township_population'],
                        item['district_name'], item['district_native'], item['district_status'], item['district_population'],
                        item['city_name'], item['city_native'], item['city_status'], item['city_population'],
                        item['pro_name'])
                cur.execute(sql, data)
                conn.commit()
                cur.close()
                conn.close()