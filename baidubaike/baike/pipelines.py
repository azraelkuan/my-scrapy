# -*- coding: utf-8 -*-
import pymysql
import json


class BaikePipeline(object):

    def process_item(self, item, spider):
        conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='baike', charset='utf8')
        cur = conn.cursor()
        if len(item) > 1:
            try:
                sql = "insert into baidubaike(title,summary,basic_info,level2,pv,item_id,last_update_time,url) values(%s,%s,%s,%s,%s,%s,%s,%s)"
                data = (item['title'], item['summary'], json.dumps(item['basic_info']), json.dumps(item['level2']), item['pv'], item['item_id'], item['last_update_time'], item['url'])
                cur.execute(sql, data)
                conn.commit()
                cur.close()
                conn.close()
            except:
                print("exists,id is %s" % item['item_id'])
        else:
            try:
                sql = "insert into error(url) values('%s')"
                cur.execute(sql % item['url'])
                conn.commit()
                cur.close()
                conn.close()
            except:
                print("error page exists")



