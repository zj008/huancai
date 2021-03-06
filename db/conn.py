import pymysql
import configparser
import os
import logging

dir = os.getcwd()
print(dir)
cf = configparser.ConfigParser()
cf.read("conf/base_conf")

class Sql():
    def __init__(self):
        self.db = pymysql.Connect(
            host=cf.get("mysql", "host"),
            port=int(cf.get("mysql", "port")),
            user=cf.get("mysql", "user"),
            password=cf.get("mysql", "pass"),
            database=cf.get("mysql", "db")
        )
        self.cursor = self.db.cursor()

    def save(self, item):
        table = item.pop("table")
        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'insert into %s(%s) values(%s)' % (table, keys, values)
        try:
            self.cursor.execute(sql, tuple(item.values()))
            self.db.commit()
        except Exception as e:
            logging.error("save error: error info : " + e.__str__())
            self.db.rollback()
        logging.info("save success")
        return

    def save_if_not_exist(self, item, field="id"):
        table = item.pop("table")
        sql = "select %s from %s where %s = '%s'"%(field, table, field, item.get(field))
        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        if ret:
            logging.error(field + ": " + str(item.get(field)) + field + " exists in " + table)
            return 0
        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'insert into %s(%s) values(%s)' % (table, keys, values)
        self.cursor.execute(sql, tuple(item.values()))
        self.db.commit()
        logging.info("save success")
        return 1

    def reset_if_exist(self, item, field):
        table = item.pop("table")
        sql = "select %s from %s where %s = %s"%(field, table, field, item.get(field))
        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        if ret:
            try:
                self.cursor.execute("delete from %s where %s = %s"%(table, field, item.get(field)))
                self.db.commit()
            except Exception as e:
                logging.error("err : " + e.__str__() + "when delete from " + table)
        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'insert into %s(%s) values(%s)' % (table, keys, values)
        self.cursor.execute(sql, tuple(item.values()))
        self.db.commit()
        logging.info("save success")
        return

    def update(self, item, field):
        sql = "update %s set %s = %s where id = %s "%(item.get("table"), field, item.get(field), item.get("id"))
        print(sql)
        self.cursor.execute(sql)
        self.db.commit()
        print("update success")
        return

    def is_exists(self, item, field):
        table = item.get("table")
        sql = "select %s from %s where %s = '%s'" % (field, table, field, item.get(field))

        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        if ret:
            logging.error(field + ": " + str(item.get(field)) + field + " exists in " + table)
            return 1
        return 0

    def is_exists_by_tow(self, item, field, field2):
        table = item.get("table")
        sql = "select %s from %s where %s = '%s' and " \
              "%s = '%s'" % (field, table, field, item.get(field), field2, item.get(field2))

        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        if ret:
            logging.error(field + "=" + str(item.get(field)) + "  and " + field2 + "=" + str(item.get(field2)) + " exists in " + table)
            return 1
        return 0

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            ret = self.cursor.fetchall()
            return ret, 0
        except Exception as e:
            logging.error(f"error when execute sql: {sql}, error is {e.__str__()}")
            return None, e

    def update_fields(self, data):
        table = data.pop("table")
        id = data.pop("id")
        l = []
        try:
           for k, v in data.items():
               sql = "update %s set %s = '%s' where id = %s"%(table, k, v, id)
               self.cursor.execute(sql)
           self.db.commit()
        except Exception as e:
            logging.error(f"error when update {table}, error is {e.__str__()}")

    def close(self):
        self.cursor.close()
        self.db.close()