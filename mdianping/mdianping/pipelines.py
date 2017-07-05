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
                sql = "select address from shenzhen where uid = %s" % item['uid']
                is_exist = cur.execute(sql)
                # print(is_exist)
                if is_exist > 0:
                    # print(item['uid'], item['center'])
                    sql = "update shenzhen set center='%s' where uid=%s" % (item['center'], item['uid'])
                    cur.execute(sql)
                else:
                    sql = "insert into shenzhen(uid,`name`,branch_name,stars,address,center,price,taste,service,tel,environment,category_name," \
                          "sub_category_name,region_name,comments,has_deals,bookable,has_takeaway,has_mobilepay,has_promote,open_time,dish_list," \
                          "city,pro) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    data = (item['uid'], item['name'], item['branch_name'], item['stars'], item['address'], item['center'], item['price'],
                            item['taste'], item['service'], item['tel'], item['environment'], item['category_name'], item['sub_category_name'],
                            item['region_name'], item['comments'], item['has_deals'], item['bookable'], item['has_takeaway'],
                            item['has_mobilepay'], item['has_promote'], item['open_time'], item['dish_list'], item['city'],
                            item['pro'])
                    cur.execute(sql, data)

                conn.commit()
                cur.close()
                conn.close()
            except:
                print("*********************data exists************************")
