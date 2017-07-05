# -*- coding: utf-8 -*-

import pymysql


class GaoDePipeline(object):

    def process_item(self, item, spider):
        if self.__class__.__name__ in spider.pipelines:
            try:
                conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='gaode', charset='utf8')
                cur = conn.cursor()
                sql = "insert into %s(uid,`name`,address,tag,sub_tag,center,tel,pro_name,pro_center,city_name," \
                      "city_center,ad_name,ad_center,photo_url1,photo_url2,photo_url3,photo_exists)" \
                      "values('%s','%s','%s','%s','%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

                data = (item['table_name'], item['uid'], item['name'], item['address'], item['tag'], item['sub_tag'], item['center'], item['tel'],
                        item['pro_name'], item['pro_center'], item['city_name'], item['city_center'], item['ad_name'],
                        item['ad_center'], item['photo_url1'], item['photo_url2'], item['photo_url3'], item['photo_exists'])
                cur.execute(sql % data)
                conn.commit()
                cur.close()
                conn.close()
            except:
                pass
        else:
            return item
