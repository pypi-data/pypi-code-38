# -*- coding:UTF-8 -*-
r"""
author: boxueliu
version: 0.1.0
description: airflow analysis sql and create file
"""
import datetime
import linecache
import os
import psycopg2
import time

import MySQLdb
import cx_Oracle
import traceback2 as traceback


# import MySQLdb


class AirflowUtil:

    def __init__(self):
        self.flag = ''

    def flag_creat(self, **kwargs):
        try:
            file_path = kwargs['file_path']
            file_suffix = datetime.datetime.now().strftime('%Y%m%d')
            r"""
             cbb system to create success file flag
            :param file_path:
            :return:
            """
            flag_name = 'interface_' + file_suffix + '.flag'
            with open(os.path.join(file_path, flag_name), 'w') as file:
                file.write('')
        except Exception as e:
            raise Exception("文件生成异常", str(e))

    def get_cut_time(self, system_type, taskid, conn):
        r"""
        get daily cut time by taskid
        :param taskid:
        :param conn:
        :return:
        """
        try:
            if conn == '':
                return '1900-01-01 10:00:00', '2099-12-12 10:00:00'
            else:
                connnection = cx_Oracle.connect(conn)
                cursor = connnection.cursor()
                sql = "SELECT TO_CHAR(LAST_FIN_DAILY_DATE,'YYYY-MM-DD HH24:MI:SS')," \
                      "TO_CHAR(THIS_FIN_DAILY_DATE,'YYYY-MM-DD HH24:MI:SS') " \
                      "FROM K_ODS.FIN_DAILY_TABLE  " \
                      " WHERE SYSTEM_ID = '%s'  AND TASK_ID = '%s'   AND EFF_FLAG = '1'" \
                      % (str(system_type), str(taskid))
                cursor.execute(sql)
                connnection.commit()
                data = cursor.fetchall()
                return data[0][0], data[0][1]
        except Exception as e:
            print(e)

    def spool_csv(self, **kwargs):
        r"""
        to analysis sql file and create csv file to export data
        :param kwargs:
        :return: csv file
        dataype must be attentionai
        SAP,RTL,ODSB,ODSB_CBB,WHS,CFL
        """
        spool_path = kwargs['spool_path']
        data_path = kwargs['data_path']
        data_type = kwargs['data_type']
        sql_name = kwargs['sql_name']
        conn = kwargs['conn']
        daily_conn = kwargs['daily_conn']
        system_type = kwargs['system_type']
        database = kwargs['database']
        if kwargs['ods_conn']:
            ods_conn = kwargs['ods_conn']
        else:
            ods_conn = ''
        """
            get daily time
        """
        if database == 'MYSQL':
            connect = self.mysql_connect(conn)
        else:
            connect = cx_Oracle.connect(conn, encoding='gb18030')
        daily_start_time = ''
        daily_end_time = ''
        if data_type == 'ODSB_CBB':
            pass
        else:
            daily_start_time, daily_end_time = self.get_cut_time(system_type, data_type, daily_conn)

        cursor = connect.cursor()
        cursor1 = cursor
        sql_prefix = ''

        """     
            to analysis sql
        """
        for file_ in os.listdir(spool_path):
            data_from = 0
            data_to = 0
            notes_ = 0
            try:
                if file_ == sql_name:
                    sql_dic = self.sql_parse(spool_path + sql_name)
                    sql_ = sql_dic['sql']
                    file_name = sql_dic['file'].replace('\n', '')
                    table_ = sql_dic['table'].replace('\n', '')

                    if sql_.find('&2') != -1:
                        sql_ = sql_.replace('&2', daily_start_time)
                    if sql_.find('&3') != -1:
                        sql_ = sql_.replace('&3', daily_end_time)
                    sql_ = sql_.replace(';', '').replace('select', 'SELECT').replace('from', 'FROM')
                    count_sql = sql_.replace(sql_[sql_.index('SELECT') + 6:sql_.index('FROM')], '  count(1) ')

                    try:
                        cursor1.execute(count_sql)
                        notes_ = cursor1.fetchall()[0][0]
                        print("上游数据总条数为：" + str(notes_) + " 条")
                    except Exception as ee:
                        print(ee)

                    # 根据系统类型去导出文件为utf-8 或者gbk文件
                    if data_type == "ODSB_CBB":
                        f = open(os.path.join(data_path, file_name), 'w', encoding='utf8')
                    else:
                        f = open(os.path.join(data_path, file_name), 'w', encoding='gb18030')
                    while data_from < notes_:
                        # 判断数据库类型
                        if database == 'MYSQL':
                            sql_prefix = ' limit %s, 1000000 ' % str(data_from)
                        _sql = sql_ + sql_prefix
                        print(_sql)
                        cursor.execute(_sql)
                        while True:
                            data = cursor.fetchmany(1000)
                            data_from += len(data)
                            if data:
                                for x in data:
                                    f.write(x[0])
                                    f.write('\n')
                                    data_to += 1
                            else:
                                break
                    f.close()
                    cursor.close()

                    print('==========从上游抽数该表 ' + file_name[:file_name.find('.csv')] +
                          ' 获得数据为：' + str(data_from) + ' 条 ===============')
                    print('==========落成文件 ' + file_name + ' 的数据条数：' + str(data_to) + ' 条 =================')

                    # 查询ods 映射条数并进行校验是否正确
                    if not ods_conn == '':
                        self.data_analysis(table_, ods_conn, notes_)
                    else:
                        pass
            except Exception as e:
                raise Exception(str(e))

    def data_export(self, **kwargs):
        r"""
        导入数据到表中，从csv到table
        :param kwargs:
        :return:
        """
        file_path = kwargs['file_path']
        conn = kwargs['conn']
        schema = kwargs['schema']
        table_name = kwargs['table_name']
        try:
            if not os.path.exists(file_path):
                raise Exception("文件不存在")
            else:
                connect = cx_Oracle.connect(conn, encoding='gb18030')
                cursor = connect.cursor()
                with open(file_path, 'r', encoding='gb18030') as f:
                    list_ = f.readlines()
                    sql = 'INSERT ALL '
                    sql_suffix = ' SELECT 1 FROM DUAL '
                    for i in list_:
                        i = i.replace('\n', '')
                        a = i.split('<>')
                        sql1 = ' INTO '+str(schema)+'.'+str(table_name)+' VALUES ' + str(tuple(a))
                        sql += sql1
                    sql += sql_suffix
                cursor.execute(sql)
                connect.commit()
                print(sql)
        except Exception as e:
            raise Exception("导入数据出错", str(e))

    def data_analysis(self, table_name, ods_conn, up_num):
        r"""
        data anlysis
        :param schema:
        :param table_name:
        :param ods_conn:
        :return:
        """
        sql = ''
        try:
            if table_name:
                sql = "SELECT COUNT(1) FROM " + table_name
            ods_cursor = cx_Oracle.connect(ods_conn).cursor()
            ods_cursor.execute(sql)
            data_list = ods_cursor.fetchall()
            summary = 0
            if data_list:
                summary = data_list[0][0]
                if summary == up_num:
                    pass
                else:
                    raise Exception("数据条数映射不正确,上游数据为：" + str(up_num) + "条，映射表中有有："+str(summary)+"条")
            print('==============导入ods查询该表有 ' + str(summary) + ' 条====================')
        except Exception as e:
            raise e

    def mysql_connect(self, conn):
        r"""
        mysql connect
        :param conn:
        :return:
        """
        try:
            user = conn[:str(conn).find('/')]
            pwd = conn[str(conn).find('/') + 1:str(conn).find('@')]

            if conn.find(':') >= 0:
                host = conn[str(conn).find('@') + 1:str(conn).find(':')]
                port = int(conn[str(conn).find(':') + 1:str(conn).rfind('/')])
            else:
                host = conn[str(conn).find('@') + 1:str(conn).rfind('/')]
                port = 3306
            db = conn[str(conn).rfind('/') + 1:]
            conn = MySQLdb.connect(host, user, pwd, db, port, charset='utf8')
            return conn

        except Exception as e:
            raise Exception("mysql数据库连接异常", str(e))

    def postgre_connect(self, conn):
        try:
            user = conn[:str(conn).find('/')]
            pwd = conn[str(conn).find('/') + 1:str(conn).find('@')]

            if conn.find(':') >= 0:
                host = conn[str(conn).find('@') + 1:str(conn).find(':')]
                port = int(conn[str(conn).find(':') + 1:str(conn).rfind('/')])
            else:
                host = conn[str(conn).find('@') + 1:str(conn).rfind('/')]
                port = 5432
            db = conn[str(conn).rfind('/') + 1:]
            conn = psycopg2.connect(database=db,  user=user, password=pwd, host=host, port=port)
            return conn

        except Exception as e:
            raise Exception("mysql数据库连接异常", str(e))

    def sql_parse(self, file_name):
        r"""
        解析sql
        :param file_name:
        :return:
        """
        try:
            _file = 0
            _sql = 0
            _table = 0
            _file_str = ''
            _sql_str = ''
            _table_str = ''

            with open(file_name, 'r') as fp:
                for line in fp:
                    if line.strip().find('file:') == 0:
                        _file = 1
                        _sql = 0
                        _table = 0
                    elif line.strip().find('sql:') == 0:
                        _sql = 1
                        _file = 0
                        _table = 0
                    elif line.strip().find('table:') == 0:
                        _table = 1
                        _sql = 0
                        _file = 0
                    elif _file == 1:
                        _file_str = line
                    elif _table == 1:
                        _table_str += line
                    elif _sql == 1:
                        _sql_str += line

            return {"file": _file_str, "table": _table_str, "sql": _sql_str}

        except Exception as e:
            raise Exception("文件解析异常", str(e))

    def get_email_msg(self, _type, airflow_conn, ods_conn, ods_sql, dag_id, task_id):
        r"""
        获取email 邮件的一些信息
        :param _type:
        :param airflow_conn:
        :param ods_conn:
        :param ods_sql:
        :param dag_id:
        :param task_id:
        :return:
        """
        try:
            start_date = ''
            start_task = ''
            sap_zup_data = ''
            sap_fag_data = ''

            if _type == 'mysql':
                connect = self.mysql_connect(airflow_conn)
                airflow_sql = "select date_add(start_date,INTERVAL -8 hour )  from task_instance  where dag_id = '%s' " \
                              "and task_id = '%s' and state = 'success' order by  execution_date desc limit 1" \
                              % (dag_id, task_id)
                cursor = connect.cursor()
                cursor.execute(airflow_sql)
                start_task = cursor.fetchall()
            elif _type == 'pg':
                connect = self.postgre_connect(airflow_conn)
                airflow_sql = "select start_date + INTERVAL '+8 hour'  from airflow.public.task_instance " \
                              " where dag_id = '%s' and task_id = '%s' order by  execution_date desc limit 1"\
                              % (dag_id, task_id)
                cursor = connect.cursor()
                cursor.execute(airflow_sql)
                start_task = cursor.fetchall()
            if not ods_conn == '':
                oracle_conn = cx_Oracle.connect(ods_conn)
                oracle_cursor = oracle_conn.cursor()
                sql = ods_sql
                oracle_cursor.execute(sql)
                oracle_conn.commit()
                data = oracle_cursor.fetchall()
                if len(data) > 0:
                    sap_zup_data = str(data[0][0] / 1000)
                    sap_fag_data = str(data[1][0] / 1000)
                else:
                    sap_zup_data = 0
                    sap_fag_data = 0
            if len(start_task) > 0:
                start_date = str(start_task[0][0])
            return start_date, sap_zup_data, sap_fag_data
        except Exception as e:
            raise Exception("程序处理异常", e)
