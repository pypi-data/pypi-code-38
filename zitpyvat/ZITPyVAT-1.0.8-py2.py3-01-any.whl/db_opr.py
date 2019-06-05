# -*- coding: utf-8 -*-
# @CreateTime : 2018/11/9 14:43
# @Author     : Liu Gang
# @File       : db_opr.py
# @Software   : PyCharm

"""
1.00.01 add ts_result table create
        190605 liugang
"""

import sqlite3
import time

DB_OPR_VER = "V1.00.01"


def gettime(time_format=0):
    """
    get system current time
    :param time_format: the format for return value
    :return:
    """
    if time_format == 0:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    elif time_format == 1:
        return time.strftime("%Y%m%d", time.localtime(time.time()))
    elif time_format == 2:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


class VatData:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.course = self.conn.cursor()

    def __del__(self):
        pass

    def check_table_exist(self, tb_name):
        sql = 'SELECT count(*) FROM sqlite_master WHERE type="table" AND name = "{0}"'.format(tb_name)
        # print sql
        ret = self.course.execute(sql)
        fet = ret.fetchone()
        if fet is not None:
            return fet[0]
        else:
            return -1

    def create_table(self, tb_name):
        # sql = str()
        if tb_name.count("Param") != 0:
            sql = "CREATE TABLE {0} (" \
                  "resultId INT," \
                  "partCode VARCHAR (12)," \
                  "testequipid VARCHAR (50)," \
                  "testName VARCHAR (50)," \
                  "itemName VARCHAR (50)," \
                  "testTime DATETIME," \
                  "resValue VARCHAR (50)," \
                  "lowValue VARCHAR (50)," \
                  "highValue VARCHAR (50)," \
                  "resDesc VARCHAR (50));".format(tb_name)
            print(sql)
        # add ts_result table create  190605 liugang
        elif tb_name.count("result") != 0:
            sql = "CREATE TABLE ts_result (" \
                  "resultid INT PRIMARY KEY, " \
                  "testequipid VARCHAR (50), " \
                  "testname VARCHAR (50), " \
                  "partcode VARCHAR (50), " \
                  "testtime DATETIME, " \
                  "totalresult INT)"
            print(sql)
        else:
            return False

        self.course.execute(sql)
        if self.course.rowcount != 1:
            return False
        else:
            self.conn.commit()
            return True

    def save_param(self, sheet_name, part_code, test_model, test_name, item_name, res_value, lower, upper,
                   desc):
        cur_time = gettime(2)

        ret = self.check_table_exist(sheet_name)

        if ret == -1:
            # ERROR Occur
            return False
        elif ret == 0:
            # no table, create it
            ret = self.create_table(sheet_name)
            if ret is False:
                return False

        #  本地数据暂时按此方法,远程多连接此方法会有问题  liugang  181109
        result_id = self.get_result_id() + 1

        insert_into = "INSERT INTO {0} ".format(
            sheet_name)
        values = "VALUES (%d,'%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
            result_id, part_code, test_model, test_name, item_name, cur_time, res_value, lower, upper, desc)
        sql = insert_into + values
        # print sql
        self.course.execute(sql)
        if self.course.rowcount != 1:
            return False
        else:
            self.conn.commit()
            return True

    def save_result(self, test_model, test_name, part_code, result):
        cur_time = gettime(2)
        ret = self.check_table_exist("ts_result")

        if ret == -1:
            # ERROR Occur
            return False
        elif ret == 0:
            # no table, create it
            ret = self.create_table("ts_result")
            if ret is False:
                return False
        #  本地数据暂时按此方法,远程多连接此方法会有问题  liugang  181109
        result_id = self.get_result_id() + 1

        sql = "INSERT INTO ts_result VALUES (%d,'%s','%s','%s','%s',%d);" % (
            result_id, test_model, test_name, part_code, cur_time, result)

        # print sql
        self.course.execute(sql)
        if self.course.rowcount != 1:
            return False
        else:
            self.conn.commit()
            return True

    def get_result_id(self):
        sql = "select resultid from ts_result order by resultid DESC limit 0,1;"
        ret = self.course.execute(sql)
        ret_id = 0
        fet = ret.fetchone()
        if fet is not None:
            ret_id = fet[0]

        return ret_id


if __name__ == '__main__':
    db = VatData("vatdata.db")
    # db.save_param("ts_Param_6710", "8100", "6710A3", "abc", "ort", "15", "12", "18", "PASS")
    # db.save_param("ts_Param_6710", "8100", "6710A3", "abc", "ort", "15", "12", "18", "PASS")
    # db.save_param("ts_Param_6710", "8100", "6710A3", "abc", "ort", "15", "12", "18", "PASS")
    # db.save_result("6710A3", "ort", "8100")
    # print db.get_result_id()
    # db.check_table_exist("ts_Param_6710")
    # db.create_table("ts_Param_6700")
