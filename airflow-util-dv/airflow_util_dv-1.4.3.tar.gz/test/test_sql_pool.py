import time

import airflow_util_dv.sql_util as sqlutil
if __name__ == '__main__':
    # def spool_csv(self, spool_path,data_path,data_type,sql_name,conn,daily_conn,system_type,database,ods_conn):
    #
    # op_kwargs = {'spool_path':'/Users/liuboxue/Documents/workspace/DWH_AIRFLOW_ODS_SQL/RETAIL/RTL/',
    #              'data_path':  '/Users/liuboxue/Documents/workspace/DWH_AIRFLOW_ODS_SQL/RETAIL/RTL/',
    #              'system_type': 'RTL',
    #              'data_type': 'RTL1',
    #              'sql_name': 'arch_city.sql',
    #              'conn': 'DMT2_RETAIL/D77EeKsM@10.20.31.17/RTLPRDDB',
    #              'daily_conn': 'k_ods/WrnN9Szg@10.20.201.216:1521/DDMUATDB',
    #              'ods_conn': 'k_ods/WrnN9Szg@10.20.201.216:1521/DDMUATDB',
    #              'database': 'ORACLE'
    #              }

    airflow_util_dv = sqlutil.AirflowUtil()
    print(time.strftime('%Y.%m.%d %T', time.localtime(time.time())))
    airflow_util_dv.spool_csv('/u01/python/airflow/dags/DWH_AIRFLOW_ODS_SQL/CBB/sh/','/integration_ods_dev/spool_data/isit/',
                          'RTL1','AF_ARR_CASH_FLOW_D.sql','mysql/2wsx*IK<@10.20.202.184:3306/cbb',
                          'k_ods/WrnN9Szg@10.20.201.216:1521/DDMUATDB',
                          'RTL','MYSQL',''
                          )
    print(time.strftime('%Y.%m.%d %T',time.localtime(time.time())))