import pymysql
import time
from enum import IntEnum
from .config import config

__db_clients = {}


class DBACTION(IntEnum):
    INSERT = 1,
    UPDATE = 2,
    SELECT = 3,
    FIND_BY_SQL = 4
    REPLACE = 5
    DELETE_BY_ATTR = 6
    UPDATE_BY_ATTR = 7
    BULK_INSERT = 8
    EXE_BY_SQL = 9


def get_db_factory(label=None, db_info=None):
    global __db_clients
    if not label:
        label = db_info['label']
    clients = __db_clients.get(label, None)
    if clients is None:
        if db_info:
            clients = MySQLFactory(host=db_info['host'], port=db_info['port'], db=db_info['db'],
                                   user=db_info['user'], password=db_info['pass'])
        else:
            clients = MySQLFactory(label=label)
        __db_clients[label] = clients
    return clients


class MySQLFactory:

    def __init__(self, label=None, host=None, port=None, user=None, password=None, db=None):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        if label:
            self.init_db(label)
        self.label = label
        self._conn = None
        self.cursor = None

    def init_db(self, label):
        self.host = config(label, "host")
        self.port = config(label, "port")
        self.db = config(label, "db")
        self.user = config(label, "user")
        self.password = config(label, "pass")

    def close(self):
        """关闭游标和数据库连接"""
        if self.cursor is not None:
            self.cursor.close()
        if self._conn is not None:
            self._conn.close()

    def __getCursor(self):
        """获取游标"""
        _max_retries_count = 3  # 设置最大重试次数
        _conn_retries_count = 0  # 初始重试次数
        _conn_timeout = 3  # 连接超时时间为3秒
        while _conn_retries_count <= _max_retries_count:
            try:
                self._conn = pymysql.connect(host=self.host, user=self.user,
                                             password=self.password,
                                             charset='utf8', database=self.db,
                                             port=int(self.port))
                break
            except Exception as e:
                _conn_retries_count += 1
                print(
                    'connection db error, retry {}, label: {}, db: {}, msg: {}'.format(_conn_retries_count, self.label,
                                                                                       config(self.label, "db"),
                                                                                       e.__str__()))
                time.sleep(1)  # 此为测试看效果
        # 多次连接失败 此处会自动抛出异常
        self.cursor = self._conn.cursor()
        return self.cursor

    def findBySql(self, **kwargs):
        """
        自定义sql语句查找
        limit = 是否需要返回多少行
        params = dict(field=value)
        join = 'AND | OR'
        """
        cursor = self.__getCursor()
        # sql = self.__joinWhere(kwargs["sql"], kwargs["params"], kwargs["join"])
        if kwargs.get("join", 0) == 0: kwargs["join"] = "AND"
        sql = self.__joinWhere(**kwargs)
        cursor.execute(sql, tuple(kwargs["params"].values()))
        rows = cursor.fetchmany(size=kwargs["limit"]) if kwargs["limit"] > 0 else cursor.fetchall()
        columns_names = [col[0] for col in cursor.description]
        result = [dict(zip(columns_names, row)) for row in rows] if kwargs["whole"] else dict(
            zip(columns_names, rows)) if rows else None
        self.close()
        return result

    # def countBySql(self,sql,params = {},join = 'AND'):
    def countBySql(self, **kwargs):
        """自定义sql 统计影响行数"""
        if kwargs.get("join", 0) == 0: kwargs["join"] = "AND"
        cursor = self.__getCursor()
        # sql = self.__joinWhere(kwargs["sql"], kwargs["params"], kwargs["join"])
        sql = self.__joinWhere(**kwargs)
        cursor.execute(sql, tuple(kwargs["params"].values()))
        result = cursor.fetchall()  # fetchone是一条记录， fetchall 所有记录
        self.close()
        return len(result) if result else 0

    # def insert(self,table,data):
    def insert(self, **kwargs):
        """新增一条记录
          table: 表名
          data: dict 插入的数据
        """
        fields = ','.join('`' + k + '`' for k in kwargs["data"].keys())
        values = ','.join(("%s",) * len(kwargs["data"]))
        sql = 'INSERT INTO `%s` (%s) VALUES (%s)' % (kwargs["table"], fields, values)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(kwargs["data"].values()))
        insert_id = cursor.lastrowid
        self._conn.commit()
        self.close()
        return insert_id

    def exe_by_sql(self, **kwargs):
        cursor = self.__getCursor()
        cursor.execute(kwargs['sql'])
        rows = cursor.fetchall()
        columns_names = [col[0] for col in cursor.description]
        result = [dict(zip(columns_names, row)) for row in rows]
        return result

    def bulk_insert(self, table, columns, datas):
        fields = ','.join('`' + k + '`' for k in columns)
        sql = 'INSERT INTO `%s` (%s) VALUES (%s)' % (table, fields, ('%s,' * len(columns))[:-1])
        cursor = self.__getCursor()
        cursor.executemany(sql, datas)
        self._conn.commit()
        self.close()
        return 'success'

    def replcae(self, **kwargs):
        """replace一条记录
          table: 表名
          data: dict 插入的数据
        """
        fields = ','.join('`' + k + '`' for k in kwargs["data"].keys())
        values = ','.join(("%s",) * len(kwargs["data"]))
        sql = 'REPLACE INTO `%s` (%s) VALUES (%s)' % (kwargs["table"], fields, values)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(kwargs["data"].values()))
        insert_id = cursor.lastrowid
        self._conn.commit()
        self.close()
        return insert_id

    # def updateByAttr(self,table,data,params={},join='AND'):
    def updateByAttr(self, **kwargs):
        #     """更新数据"""
        if kwargs.get("params", 0) == 0:
            kwargs["params"] = {}
        if kwargs.get("join", 0) == 0:
            kwargs["join"] = "AND"
        fields = ','.join('`' + k + '`=%s' for k in kwargs["data"].keys())
        values = list(kwargs["data"].values())
        # values.extend(list(kwargs["params"].values()))
        sql = "UPDATE `%s` SET %s " % (kwargs["table"], fields)
        kwargs["sql"] = sql
        where = []
        for _key, _value in kwargs['params'].items():
            where.append("`{}`='{}'".format(_key, _value))
        sql += 'where ' + ' and '.join(where)
        cursor = self.__getCursor()
        sql = sql % (tuple(values))
        cursor.execute(sql)
        self._conn.commit()
        self.close()
        return cursor.rowcount

    # def updateByPk(self,table,data,id,pk='id'):
    def updateByPk(self, **kwargs):
        """根据主键更新，默认是id为主键"""
        return self.updateByAttr(**kwargs)

    # def deleteByAttr(self,table,params={},join='AND'):
    def deleteByAttr(self, **kwargs):
        """删除数据"""
        if kwargs.get("params", 0) == 0:
            kwargs["params"] = {}
        if kwargs.get("join", 0) == 0:
            kwargs["join"] = "AND"
        # fields = ','.join('`'+k+'`=%s' for k in kwargs["params"].keys())
        sql = "DELETE FROM `%s` " % kwargs["table"]
        kwargs["sql"] = sql
        # sql = self.__joinWhere(sql, kwargs["params"], kwargs["join"])
        sql = self.__joinWhere(**kwargs)
        cursor = self.__getCursor()
        rowcount = cursor.rowcount
        cursor.execute(sql, tuple(kwargs["params"].values()))
        self._conn.commit()
        self.close()
        return rowcount

    # def deleteByPk(self,table,id,pk='id'):
    def deleteByPk(self, **kwargs):
        """根据主键删除，默认是id为主键"""
        return self.deleteByAttr(**kwargs)

    # def findByAttr(self,table,criteria = {}):
    def findByAttr(self, **kwargs):
        """根據條件查找一條記錄"""
        return self.__query(**kwargs)

    # def findByPk(self,table,id,pk='id'):
    def findByPk(self, **kwargs):
        return self.findByAttr(**kwargs)

    # def findAllByAttr(self,table,criteria={}, whole=true):
    def findAllByAttr(self, **kwargs):
        """根據條件查找記錄"""
        return self.__query(**kwargs)

    # def count(self,table,params={},join='AND'):
    def count(self, **kwargs):
        """根据条件统计行数"""
        if kwargs.get("join", 0) == 0: kwargs["join"] = "AND"
        sql = 'SELECT COUNT(*) FROM `%s`' % kwargs["table"]
        # sql = self.__joinWhere(sql, kwargs["params"], kwargs["join"])
        kwargs["sql"] = sql
        sql = self.__joinWhere(**kwargs)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(kwargs["params"].values()))
        result = cursor.fetchone()
        self.close()
        return result[0] if result else 0

    # def exist(self,table,params={},join='AND'):
    def exist(self, **kwargs):
        """判断是否存在"""
        return self.count(**kwargs) > 0

    # def __joinWhere(self,sql,params,join):
    def __joinWhere(self, **kwargs):
        """转换params为where连接语句"""
        if kwargs.get("params"):
            keys, _keys = self.__tParams(**kwargs)
            where = ' AND '.join(k + '=' + _k for k, _k in zip(keys, _keys)) if kwargs[
                                                                                    "join"] == 'AND' else ' OR '.join(
                k + '=' + _k for k, _k in zip(keys, _keys))
            kwargs["sql"] += ' WHERE ' + where
        return kwargs["sql"]

    # def __tParams(self,params):
    def __tParams(self, **kwargs):
        keys = ['`' + k + '`' for k in kwargs["params"].keys()]
        _keys = ['%s' for k in kwargs["params"].keys()]
        return keys, _keys

    # def __query(self,table,criteria,whole=False):
    def __query(self, **kwargs):
        if kwargs.get("whole", False) == False or kwargs["whole"] is not True:
            kwargs["whole"] = False
            kwargs["criteria"]['limit'] = 1
        # sql = self.__contact_sql(kwargs["table"], kwargs["criteria"])
        sql = self.__contact_sql(**kwargs)
        cursor = self.__getCursor()
        cursor.execute(sql)
        rows = cursor.fetchall() if kwargs["whole"] else cursor.fetchone()
        columns_names = [col[0] for col in cursor.description]
        result = [dict(zip(columns_names, row)) for row in rows] if kwargs["whole"] else dict(
            zip(columns_names, rows)) if rows else None
        return result

    # def __contact_sql(self,table,criteria):
    def __contact_sql(self, **kwargs):
        sql = 'SELECT '
        if kwargs["criteria"] and type(kwargs["criteria"]) is dict:
            #select fields
            if 'select' in kwargs["criteria"]:
                fields = kwargs["criteria"]['select'].split(',')
                select_list = []
                for field in fields:
                    if field.find('.') != -1:
                        _val = field.split('.')
                        _val[1] = '`' + _val[1] + '`'
                        _values = '{}.{}'.format(_val[0], _val[1])
                    else:
                        _values = '`'+field+'`'
                    select_list.append(_values)
                sql += ','.join(select_list)
            else:
                sql += ' * '
            # table
            sql += ' FROM `%s`' % kwargs["table"]
            # where
            if 'where' in kwargs["criteria"]:
                sql += ' WHERE ' + kwargs["criteria"]['where']
            if 'join' in kwargs['criteria']:
                join = kwargs['criteria']['join']
                on = '{}.{}={}.{}'.format(kwargs['table'], join['on']['t1'], join['table'], join['on']['t2'])
                sql += ' join {} on {}'.format(join['table'], on)
                if 'where' in join:
                    sql += ' where ' + join['where']
            # group by
            if 'group' in kwargs["criteria"]:
                sql += ' GROUP BY ' + kwargs["criteria"]['group']
            # having
            if 'having' in kwargs["criteria"]:
                sql += ' HAVING ' + kwargs["criteria"]['having']
            # order by
            if 'order' in kwargs["criteria"]:
                sql += ' ORDER BY ' + kwargs["criteria"]['order']
            # limit
            if 'limit' in kwargs["criteria"]:
                sql += ' LIMIT ' + str(kwargs["criteria"]['limit'])
            # offset
            if 'offset' in kwargs["criteria"]:
                sql += ' OFFSET ' + str(kwargs["criteria"]['offset'])
        else:
            sql += ' * FROM `%s`' % kwargs["table"]
        return sql

    def findKeySql(self, key, **kwargs):
        sqlOperate = {
            DBACTION.INSERT: lambda: self.insert(**kwargs),
            DBACTION.BULK_INSERT: lambda: self.bulk_insert(**kwargs),
            DBACTION.SELECT: lambda: self.findAllByAttr(**kwargs),
            DBACTION.FIND_BY_SQL: lambda: self.findBySql(**kwargs),
            DBACTION.REPLACE: lambda: self.replcae(**kwargs),
            DBACTION.DELETE_BY_ATTR: lambda: self.deleteByAttr(**kwargs),
            DBACTION.UPDATE_BY_ATTR: lambda: self.updateByAttr(**kwargs),
            DBACTION.EXE_BY_SQL: lambda: self.exe_by_sql(**kwargs)
        }
        code, msg = 0, ''
        try:
            results = sqlOperate[key]()
        except Exception as e:
            results = None
            msg = e.__str__()
            code = -1
        return results, code, msg


if __name__ == "__main__":
    mysqlet = MySQLFactory('mysql_stock')
    res = mysqlet.findKeySql(DBACTION.EXE_BY_SQL, sql='select * from sites')
    print(res)
    # #插入数据
    # print(mysqlet.findKeySql(Const.INSERT, table="info", data={"name":"333", "pwd": "111"}))
    # #根据字段删除,不传params参数，就是删除全部
    # criteria = {'select': 'stock_code,company_name',
    #             "where": "stock_code in {}".format(tuple(['00002', '']))}
    # c1 = mysqlet.findKeySql(ACTION.SELECT, table="stock_info", criteria=criteria, whole=True)
