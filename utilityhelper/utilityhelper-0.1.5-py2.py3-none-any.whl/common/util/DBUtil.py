#coding:utf-8
from __future__ import (print_function, unicode_literals)
import os
import time
try:
    import MySQLdb
except:
    import pymysql
    pymysql.install_as_MySQLdb()

class Singleton(type):    
    def __init__(cls, name, bases, dict):    
        super(Singleton, cls).__init__(name, bases, dict)    
        cls._instance = None
            
    def __call__(cls, *args, **kw):    
        if cls._instance is None:    
            cls._instance = super(Singleton, cls).__call__(*args, **kw)    
        return cls._instance


class MySQLUtil(object, metaclass=Singleton):
    '''
                对MySQLdb常用函数进行封装的类
    '''    
    _instance = None #本类的实例
    _conn = None # 数据库conn
    _cur = None #游标
    error_code = '' #MySQL错误号码
       
    def __init__(self, dbconfig):
        
        '''构造器：根据数据库连接参数，创建MySQL连接'''
        try:    
#             self._timecount = 0
#             self._TIMEOUT = 10
            self._conn = MySQLdb.connect(host=dbconfig['host'],
                                           port=dbconfig['port'], 
                                           user=dbconfig['user'],
                                           passwd=dbconfig['passwd'],
                                           db=dbconfig['db'],
                                           charset=dbconfig['charset'])
            self._cur = self._conn.cursor()
            
            print("self._conn=", self._conn)
            print("self._cur=", self._cur)
            print("self._instance=", self._instance)
            
        except MySQLdb.Error as e:
            self.error_code = e.args[0]
            error_msg = str(e.args[0]) + " - "+ e.args[1]
            print("e=", e)
            print("MySQLdb.Error=",MySQLdb.Error)
            print("error_msg=", error_msg)
            raise DBUtilError(e) 
            #raise Exception(error_msg)
          
            # 如果没有超过预设超时时间，则再次尝试连接，
#             if self._timecount < self._TIMEOUT:
#                 interval = 5
#                 self._timecount += interval
#                 time.sleep(interval)
#                 return self.__init__(dbconfig)
#             else:
#                 raise Exception(error_msg)

    def query(self,sql):
        '''执行 SELECT 语句'''     
        try:
            self._cur.execute("SET NAMES utf8") 
            result = self._cur.execute(sql)
        except MySQLdb.Error as e:
            self.error_code = e.args[0]
            print("query error:",e.args[0],e.args[1])
            result = False
            raise DBUtilError(e)
        return result

    def update(self,sql):
        '''执行 UPDATE 及 DELETE 语句'''
        try:
            self._cur.execute("SET NAMES utf8") 
            result = self._cur.execute(sql)
            self._conn.commit()
        except MySQLdb.Error as e:
            self.error_code = e.args[0]
            print("数据库更新错误,错误代码:",e.args[0],e.args[1])
            result = False
            raise DBUtilError(e)
        return result
        
    def insert(self,sql):
        '执行 INSERT 语句。如主键为自增长int，则返回新生成的ID'
        try:
            self._cur.execute("SET NAMES utf8")
            self._cur.execute(sql)
            self._conn.commit()
            return self._conn.insert_id()
        except MySQLdb.Error as e:
            self.error_code = e.args[0]
            print("数据库insert错误,错误代码:",e.args[0],e.args[1])
            raise DBUtilError(e)
            #return False
    
    def insertMany(self, sql, dataTuple):
        '''                
                            执行 批量INSERT 语句。如主键为自增长int，则返回新生成的ID
        '''
        try:
            self._cur.execute("SET NAMES utf8")
            self._cur.executemany(sql, dataTuple)
            self._conn.commit()
            return self._conn.insert_id()
        except MySQLdb.Error as e:
            self.error_code = e.args[0]
            print("数据库insertMany错误,错误代码:",e.args[0],e.args[1])
            return False 

    def deleteMany(self, sql, dataTuple):
        '执行 批量INSERT 语句。如主键为自增长int，则返回新生成的ID'
        try:
            self._cur.execute("SET NAMES utf8")
            self._cur.executemany(sql, dataTuple)
            self._conn.commit()
        except MySQLdb.Error as e:
            self.error_code = e.args[0]
            print("数据库deleteMany错误,错误代码:",e.args[0],e.args[1])
            return False 
                     
    def fetchAllRows(self):
        '返回结果列表'
        return self._cur.fetchall()
    
    def fetchOneRow(self):
        '返回一行结果，然后游标指向下一行。到达最后一行以后，返回None'
        return self._cur.fetchone()
     
    def getRowCount(self):
        '获取结果行数'
        return self._cur.rowcount
    
    def getTableHead(self):
        #cursor结果集合的描述（列名字，数据类型，是否允许空，列标志）
        #type: 3(LONG), 253(VAR_STRING)，10（DATE）
        #是否允许空：0
        #列标志：20483， 4097， 4225
        head_list = []
        desc = self._cur.description
        if(desc != None):
            #推倒式列表
            head_list = [col[0] for col in desc]
        return head_list
                  
    def commit(self):
        '数据库commit操作'
        self._conn.commit()
                
    def rollback(self):
        '数据库回滚操作'
        self._conn.rollback()
           
    def __del__(self): 
        '释放资源（系统GC自动调用）'
        try:
            print("__del__ ", self)
            self._cur.close() 
            self._conn.close() 
        except:
            pass
        
    def getConnection(self):
        return self._conn
        
    def close(self):
        '关闭数据库连接'
        self.__del__()
    
    @classmethod
    def getInstance(cls):
        return cls._instance


class DBUtilError(Exception):
    def __init__(self, e):
        Exception.__init__(self)
        self.errID = e.args[0]
        self.errMsg = e.args[1]
        self.errInfo = str(self.errID) + " - " + self.errMsg
    
    def __str__(self, *args, **kwargs):
        return self.errInfo
