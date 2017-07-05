# coding:utf-8
import pymysql
import re
from openpyxl import Workbook


def conn_mdb():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='mdianping', charset='utf8')
    cur = conn.cursor()
    return conn, cur


def conn_db():
    conn = pymysql.connect(host='localhost', user='root', passwd='067116', db='dianping', charset='utf8')
    cur = conn.cursor()
    return conn, cur


def deal_url():
    conn, cur = conn_db()
    sql = 'select id, url from shenzhen'
    cur.execute(sql)
    data = cur.fetchall()
    for each in data:
        uid = re.search("(\d+)", each[1]).group(1)
        sql = "update shenzhen set uid = %s where id = %s"
        cur.execute(sql, (uid, each[0]))
    conn.commit()
    cur.close()
    conn.close()


def combine_data():
    conn1, cur1 = conn_db()
    conn2, cur2 = conn_mdb()
    wbk = Workbook()
    sheet = wbk.create_sheet("combine_data", 0)
    sql = "select uid, name, address, category_name, price, stars, comments from shenzhen"
    cur1.execute(sql)
    data1 = cur1.fetchall()
    cur2.execute(sql)
    data2 = cur2.fetchall()
    sql2 = "insert into shenzhen_comdata(uid, name, address, category_name, price, stars, comments, in_mobile) " \
           "values(%s, %s, %s, %s, %s, %s , %s, %s)"
    sql1 = "insert into shenzhen_comdata(uid, name, address, category_name, price, stars, comments, in_mobile, in_pc) " \
           "values(%s, %s, %s, %s, %s, %s , %s, %s, %s)"
    i = 0
    j = 0
    for each in data2:
        print("i: %s" % i)
        i += 1
        cur2.execute(sql2, (each[0], each[1], each[2], each[3], each[4], each[5], each[6], "Y"))

    for each in data1:
        print("j: %s" % j)
        j += 1

        try:
            cur2.execute(sql1, (each[0], each[1], each[2], each[3], each[4], each[5], each[6], "N", "Y"))
        except:
            sql4 = "update shenzhen_comdata set in_pc = %s where uid = %s"
            cur2.execute(sql4, ("Y", each[0]))

        # sql3 = 'select count(*) from shenzhen_comdata where uid = %s'
        # cur2.execute(sql3 % each[0])
        # is_exists = cur2.fetchone()
        # print("exists: %s" % is_exists[0])
        #
        # if is_exists[0] > 0:
        #
        # else:
        #     cur2.execute(sql1, (each[0], each[1], each[2], each[3], each[4], each[5], each[6], "N", "Y"))

    conn2.commit()
    conn1.commit()
    cur2.close()
    cur1.close()
    conn1.close()
    conn2.close()

if __name__ == '__main__':
    combine_data()
