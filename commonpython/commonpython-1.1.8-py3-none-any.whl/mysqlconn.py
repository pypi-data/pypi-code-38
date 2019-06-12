# -*- coding: utf-8 -*-
# @Time    : 2016/11/1 9:38
# @File    : MySql.py
# @Software: PyCharm
import pymysql



'''
mysql调用规则：
    1.正常返回  200   sel 返回数据
    2.异常全部返回  None
'''
# @mysql_conn_check

mysqlInfo_interface_server={
    "host":"",
    "user":"",
    "passwd":"",
    "db":"",
    "port":"",
    "use_unicode":"",
    "charset":""
}

class MysqlConn():
    def __init__(self,mysqlInfo):
        '''
        mysql连接出错，返回500状态码    连接正常，返回连接对象
        :return:
        '''
        self.conn = pymysql.connect(host=mysqlInfo["host"], user=mysqlInfo["user"], passwd=mysqlInfo["passwd"],
                               db=mysqlInfo["db"], port=mysqlInfo["port"], charset=mysqlInfo["charset"],
                               use_unicode=mysqlInfo["use_unicode"])

        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)

    def intersetMysql(self,Sql,param=None):  # 插入数据方法
        if self.conn!=500:
            try:
                if param is None:
                    row = self.cur.execute(Sql)
                else:
                    row=self.cur.execute(Sql,param)
                # 如果不加下面这句话，并不会真实操作数据库（数据库不会发生改变）
                self.conn.commit()
                return row
            except pymysql.Error as e:
                self.conn.rollback()     #事物回滚
                return None
        else:
            return None

    def updateMysql(self,Sql,param=None):  # 修改数据方法
        if self.conn!=500:
            try:
                if param is None:
                    row=self.cur.execute(Sql)    #更新的数据条数
                else:
                    row=self.cur.execute(Sql,param)    #更新的数据条数
                # 如果不加下面这句话，并不会真实操作数据库（数据库不会发生改变）
                self.conn.commit()
                return row        #用于判断sql where条件查询不到数据
            except pymysql.Error as e:
                self.conn.rollback()
                return None
        else:
            return None


    def selectMysql(self,Sql):  # 查询数据方法
        if self.conn!=500:
            try:
                info = self.cur.fetchmany(self.cur.execute(Sql))

                # 如果不加下面这句话，并不会真实操作数据库（数据库不会发生改变）
                return info
            except Exception as e:
                return {}
        else:
            return {}



    def deleteMysql(self,Sql):  # 删除数据方法
        if self.conn!=500:
            try:
                err_now=self.cur.execute(Sql)     #删除数据条数
                # 如果不加下面这句话，并不会真实操作数据库（数据库不会发生改变）
                self.conn.commit()
                return err_now     #用于判断  where查询条件为空时删除不成功
            except pymysql.Error as e:
                self.conn.rollback()
                return None
        else:
            return None


    def close(self):
        self.cur.close()
        self.conn.close()