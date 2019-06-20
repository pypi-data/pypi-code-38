# -*- coding: utf-8 -*-

demo = """
#test.py
#import pandas as pd
#import numpy as np
#import esqlk as es
#import sqlite3
#
#sqlite_db_file = '.\\test.db'
#
#es.engine = sqlite3.connect(sqlite_db_file)
#
#def SQL(st=es.st_tables):
#    es.glc = globals()
#    return es.SQL(st)
#
#aa = pd.DataFrame(np.arange(12))
#
#bb = pd.DataFrame(np.arange(3))
#
#
#cc = SQL('''
#         copy ['aa'] to fixed_table
#         ''')
#
#cc = SQL('''
#         select name from fixed_table
#         ''')
#print(cc)
#
#cc = SQL('''
#         select 'aa1' as tbl,count(*) as cnt from aa
#           union all
#         select 'bb1' as tbl,count(*) as cnt from bb
#       '''
#       )
#
#print(cc)
"""


#模块自动执行，在第一次导入时
#import sys
import pandas as pd
import numpy as np
import sqlite3
 
##################################################################
#Sqlite的基本处理
#globals_from_caller 
glc = {}

engine = sqlite3.connect(':memory:')
 
st_tables = "select name from sqlite_master where type='table' order by name"
 


#解析sql 为列表
def sql_to_list(st):
#空格分列
    ll = st.split(' ')
    rr = []
 
    #剔除‘’，只保留正常字母
    for i in np.arange(len(ll)):
        tt = ll[i].strip()
        if tt != '':
            rr.append(tt)
 
    return rr
 
#获取sql的表名
def sql_get_tbl_names(st_list):
    rr = []
    for i in np.arange(len(st_list)):
        tt = st_list[i].strip()
        if tt == 'from' or tt == 'join':
            rr.append(st_list[i+1].strip())
 
    return rr
 
#处理 fixed_table
def es_copy_to(st_list):
    #判断 fixed_table 是否存在
    sql="select name from sqlite_master where type='table' and name='fixed_table'"
    tt = pd.read_sql_query(sql, engine)
 
    #如果 fixed_table 不存在，则创建之
    if tt.shape[0] == 0:
        engine.execute("create table fixed_table(name text, att text)")
        engine.execute("insert into fixed_table values ('fixed_table', 'fixed_table')")
 
    tbl_name_list = eval(st_list[1])
 
    for i in range(len(tbl_name_list)):
        tbl_name = tbl_name_list[i]
        #先删除
        engine.execute("delete from fixed_table where name ='"
                       + tbl_name + "'")
        #再增加
        engine.execute("insert into fixed_table values (?, ?)",
                       (tbl_name,tbl_name))
 
        #替换表
        pd.DataFrame(glc[tbl_name]).to_sql(tbl_name,
                    con=engine,
                    if_exists='replace',
                    index=True)
 
    return 0
 
 
#sql 执行语句
def sql_exec(st,st_list):
    #获取sql表名
    df_name_list = sql_get_tbl_names(st_list)
 
    #fixec_table列表
    ff = pd.read_sql("select name from fixed_table",con=engine)
 
    #导入表名,执行sql，输出结果
    for i in np.arange(len(df_name_list)):
        df_name = df_name_list[i]
        if df_name not in ff['name'].values:
            df = glc[df_name]
            df.to_sql(df_name, con=engine,if_exists='replace',index=True)
 
    #此处可考虑重置索引，便于统计行数，而无需再使用count(*)
    return pd.read_sql_query(st,con=engine)
 
#sql解析并执行
def es_init_check_st(st):
    #解析sql
    st_list = sql_to_list(st)
 
    #更新 fixed_table
    if st_list[0] == 'copy' and st_list[-2] == 'to':
        return es_copy_to(st_list)
 
    #执行查询语句
    return sql_exec(st,st_list)
 

#执行语句
def SQL(gg,st):
    glc = gg
    #默认查询所有表名
    if st == "select name from sqlite_master where type='table' order by name":
        return pd.read_sql_query(st, engine)
 
    st = st.strip()
    rr = es_init_check_st(st)
    return rr
