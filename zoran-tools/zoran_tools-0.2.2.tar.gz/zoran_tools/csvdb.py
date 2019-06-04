import csv
import os
import sqlite3

from zoran_tools.path_tools import create_father_dir
from zoran_tools.csv_tools import readcsv


class CSV2DB(object):
    def __init__(self, name=None, memory=':memory:'):
        if name:
            self.name = name
        self.db = sqlite3.connect(memory)
        self.table_dict = dict()

    def create_table(self, name, columns):
        """
        根据表名和字段在数据库中创建一个表
        :param name:
        :param columns:
        :return:
        """
        if name not in self.tables:
            sql = 'create table {}({});'.format(name, columns)
            self.db.execute(sql)
            return True
        else:
            return False

    def get_table(self, name=None, filename=None, content=None, fields=None, encoding='utf8'):
        """
        从文件或列表中创建一个Table对象，并在数据库中创建一个表
        """
        table = _Table(db=self, name=name, filename=filename, content=content, fields=fields, encoding=encoding)
        table.create()
        self.table_dict[table.name] = table
        return self

    def table(self, name):
        return self.table_dict[name]

    @property
    def tables(self, printit=False):
        """
        查询数据库所有的表
        """
        sql = 'SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;'
        tables = self.runsql(sql).fetchall()
        if printit:
            print(tables)
        return tables

    def runsql(self, sql):
        """
        运行SQL语句
        :param sql:
        :return:
        """
        return self.db.execute(sql)

    def sql(self, sql):
        """
        运行SQL语句，与self.runsql()一致，另建一个功能重复的函数是为了与Spark中接口命名保持统一
        """
        return self.runsql(sql)

    def run_insert(self, name, content):
        """
        进行表插入
        :param name: 表名
        :param content: 要插入的列表，列表的每一个元素是一个要插入的行
        """
        self.db.executemany(
            'INSERT INTO {} VALUES ({})'.format(name, ','.join(['?']*len(content[0]))),
            [tuple(r) for r in content]
        )
        return len(content)


class _Table(object):
    def __init__(self, db, name=None, filename=None, content=None, fields=None, encoding='utf8'):
        """
        表对象
        :param db: 表所属的数据库
        :param name: 表名
        :param filename: 表内容来自的CSV文件
        :param content: 表内容来自的列表
        :param field: 表字段
        :param encoding: 
        """
        if (not name and not filename) or (not filename and not content):
            raise ValueError
        self.db = db
        self._name = name
        self._filename = filename
        self._content = content
        self._fields = fields
        self.encoding = encoding

    @property
    def name(self):
        """
        表名
        """
        if self._name:
            return self._name
        else:
            return os.path.basename(os.path.splitext(self._filename)[0])


    @property
    def fields(self):
        """
        字段
        """
        if self._fields:
            return self._fields
        else:
            pat = '_{} varchar(600)'  # 与Spark生成的字段名保持一致
            row_length = len(self.content[0])
            if row_length == 0:
                raise ValueError
            indexes = list(range(1, row_length + 1))
            fields = ','.join([pat.format(i) for i in indexes])
            return fields

    @property
    def content(self):
        if self._content:
            return self._content
        else:
            return readcsv(filename=self._filename, encoding=self.encoding)

    def collect(self):
        return self.content  # 重复功能是为了与Spark函数保持一致

    def _create(self):
        self.db.create_table(name=self.name, columns=self.fields)

    def _insert(self):
        self.db.run_insert(name=self.name, content=self.content)

    def create(self):
        self._create()
        self._insert()

    def select_all(self):
        sql = 'select * from {};'.format(self.name)
        return self.db.runsql(sql).fetchall()

