import os

import cx_Oracle
import time

from airflow_util_dv.sql_util import AirflowUtil


def data_export(file_path, conn, schema, table_name):
    try:
        if not os.path.exists(file_path):
            raise Exception("文件不存在")
        else:
            connect = cx_Oracle.connect(conn, encoding='gb18030')
            cursor = connect.cursor()
            with open(file_path, 'r', encoding='gb18030') as f:
                list_ = f.readlines()
                sql = 'INSERT ALL '
                sql_retail = 'INSERT ALL '
                sql_suffix = ' SELECT 1 FROM DUAL '
                note_num = 0
                for i in list_:
                    note_num += 1
                    i = i.replace('\n', '')
                    a = i.split('<>')
                    sql1 = ' INTO ' + str(schema) + '.' + str(table_name) + ' VALUES ' + str(tuple(a))
                    sql += sql1
                    if note_num >= 1000:
                        note_num = 0
                        cursor.execute(sql+sql_suffix)
                        connect.commit()
                        sql = sql_retail
                if not note_num == 0:
                    sql += sql_suffix
                    cursor.execute(sql)
                    connect.commit()
                cursor.close()
                connect.close()
                f.close()
    except Exception as e:
        raise Exception("导入数据出错", str(e))


if __name__ == '__main__':
    # airflow_util_dv = AirflowUtil()
    daily_sql = "SELECT  count(1) FROM K_ODS.FIN_DAILY_TABLE  WHERE SYSTEM_ID = '%s' AND TASK_ID = '%s' AND EFF_FLAG = 1   " \
                "AND trunc(THIS_POST_DATE) = trunc(sysdate)"
    connect = cx_Oracle.connect('k_ods/WrnN9Szg@10.20.201.216:1521/DDMUATDB', encoding='gb18030')
    cursor = connect.cursor()
    # file_path = '/dwh_ods_uat/spool_data/RTL/ODS_LN_CS_PRT_REPYMTSKD.csv'
    # # file_path = '/Users/liuboxue/Desktop/ARCH_CITY.csv'
    # data_export(file_path, 'k_ods/WrnN9Szg@10.20.201.216:1521/DDMUATDB', 'K_ODS', 'ODS_LN_CS_PRT_REPYMTSKD_TEST')
    sql = daily_sql % ('DW', 'DW_RTL_ODS')
    print(sql)
    cursor.execute(sql)
    print(cursor.fetchall())
