# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

import psycopg2.extras


"""
psycopg2 官方文档：
  http://initd.org/psycopg/docs/index.html

PostgreSQL 中的占位符与参数
  有两种占位符：位置占位 和 名称占位

  位置占位(使用 tuple 或者 list 传递参数)：
      sql = 'INSERT INTO drug (org_id, is_local, approval, approval_number) VALUES (%s, %s, %s, %s)'
      params = (2, True, 'Z20020160', '国药准字Z20020147') 或 [2, True, 'Z20020160', '国药准字Z20020147']

  名称占位(使用 dict 传递参数)：
      sql = '''
          INSERT INTO drug (org_id, is_local, approval, approval_number)
          VALUES (%(org_id)s, %(is_local)s, %(approval)s, %(approval_number)s)
      '''
      params = {
          'org_id': 2,
          'is_local': True,
          'approval': 'Z20020171',
          'approval_number': '国药准字Z20020170'
      }
"""


class Postgres(object):

    def __init__(self, host, port, user, password, database):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursor_factory=psycopg2.extras.DictCursor
        )

    def __del__(self):
        self.conn.close()

    def fetchone(self, sql, params=None):
        """
        执行SQL，返回结果集中的第一条记录
        如果返回的结果集为空，则返回None
        :param sql: str
        :param params: 可以为array，也可以为tuple
        :return: 单条记录的list，
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        ret = cursor.fetchone()
        cursor.close()
        return ret

    def fetchall(self, sql, params=None):
        """
        执行SQL，返回结果集所有记录。如果返回的结果集为空，则返回空list(即[])
        :param sql: str
        :param params: 可以为array，也可以为tuple
        :return: 数据集
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        ret = cursor.fetchall()
        cursor.close()
        return ret

    def execute(self, sql, params=None):
        """
        执行传入的SQL语句
        如果是多句SQL，则需要用英文分号分隔
        :param sql: str
        :param params:
        :return: 返回修改的行数，或者数据集的行数
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        ret = cursor.rowcount
        cursor.close()
        return ret

    def executemany(self, sql, params_list):
        """
        用不同参数执行同一条SQL
        例如：
            sql = 'INSERT INTO drug (org_id, is_local, approval, approval_number) VALUES (%s, %s, %s, %s)'
            params_list = (
                (2, True, 'Z20020193', '国药准字Z20020147'),
                (2, True, 'Z20020194', '国药准字Z20020147')
            )
        :param sql: str
        :param params_list: tuple ot list
        :return: 返回修改的行数，或者数据集的行数
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, params_list)
        self.conn.commit()
        ret = cursor.rowcount
        cursor.close()
        return ret

    def batch_execute(self, commands):
        """
        批量执行命令
        每一个命令都是由一条SQL语句和其对应的参数构成
        命令是一个dict，结构如下例：
            {
                'sql': 'INSERT INTO sys_area (name, update_time, update_by) VALUES (%s, %s, %s)',
                'params': [‘Tom’, ‘2013-05-20 20:18:16’, ‘admin’]
            }
        :param commands: list or tuple
        :return: 返回修改的行数，或者数据集的行数
        """
        cursor = self.conn.cursor()
        ret = 0
        for cmd in commands:
            cursor.execute(cmd['sql'], cmd['params'])
            ret += cursor.rowcount
        self.conn.commit()
        cursor.close()
        return ret


if __name__ == '__main__':
    print('This is Postgres module.')
