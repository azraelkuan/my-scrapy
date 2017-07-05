import pymysql


class Models(object):

    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.conn = pymysql.connect(host='localhost', port=3306, user=self.user, passwd=self.password, db=self.database, charset='utf8')

    def create_table(self, table_name):
        req = {'status': 0, 'msg': ""}
        cur = self.conn.cursor()
        sql = "select table_name from information_schema.tables"
        cur.execute(sql)
        table_names = cur.fetchall()
        for each in table_names:
            if table_name in each:
                req['status'] = 1
                req['msg'] = 'exists'
        if req['status'] == 0:
            sql1 = "create table %s like template" % table_name
            cur.execute(sql1)
            req['status'] = 0
            req['msg'] = "success"
            self.conn.commit()
        return req

    def close_db(self):
        self.conn.close()


class MDPModels(object):

    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.conn = pymysql.connect(host='localhost', port=3306, user=self.user, passwd=self.password, db=self.database, charset='utf8')

    def create_table(self, table_name):
        req = {'status': 0, 'msg': ""}
        cur = self.conn.cursor()
        sql = "select table_name from information_schema.tables"
        cur.execute(sql)
        table_names = cur.fetchall()
        for each in table_names:
            if table_name in each:
                req['status'] = 1
                req['msg'] = 'exists'
        if req['status'] == 0:
            sql1 = "create table %s like template" % table_name
            cur.execute(sql1)
            req['status'] = 0
            req['msg'] = "success"
            self.conn.commit()
        return req

    def close_db(self):
        self.conn.close()