import pandas as pd 
from sqlalchemy import create_engine,types
from sqlalchemy.dialects.postgresql import TEXT 
import pymssql
import cx_Oracle
import psycopg2 
import MySQLdb
import datetime
import re
import sqlite3
import os 
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' 
_pool={
    'mssql':[['DmyyReader','Sjbd*0708','10.204.168.114\MSSQLSERVER2','basedb','dbo']]

    ,

    'postgresql':[['postgres','since2015','localhost','sist','sist20180204']
    ]
    ,

    'oracle':[['lmf','since2015','localhost','ORCL']]

    ,
    'mysql':[['root','since2015','localhost','test']]
}

def db_query(sql,dbtype='mssql',pool=0,conp=None):
   
    if conp is None:conp=_pool[dbtype][pool]

    if dbtype=='mssql':
        con=create_engine("mssql+pymssql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    elif dbtype=='postgresql':
        con=create_engine("postgresql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
        if len(conp)==4:conp.append('public')
        sql="set search_path to %s;"%conp[4]+sql
    elif dbtype=='oracle':
        con= create_engine('oracle://%s:%s@%s/%s'%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    elif dbtype=='sqlite':
        con=create_engine('sqlite:///%s'%conp)
       
    else:
        con= create_engine('mysql://%s:%s@%s/%s?charset=utf8'%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')

    df=pd.read_sql(sql,con)
    con.dispose()
    return df


def db_write(df,tb_name,dbtype='mssql',pool=0,conp=None,datadict=None,if_exists='replace'):
    """ conp[4] 影响表写入的schema"""
    if conp is None:conp=_pool[dbtype][pool]
    if dbtype=='mssql':
        con=create_engine("mssql+pymssql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    elif dbtype=='postgresql':
        con=create_engine("postgresql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    elif dbtype=='oracle':
        con= create_engine('oracle://%s:%s@%s/%s'%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    elif dbtype=='sqlite':
        con=create_engine('sqlite:///%s'%conp)
       
    else:
        con= create_engine('mysql://%s:%s@%s/%s?charset=utf8'%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    def sqlcol(dfparam,text=None):

        dtypedict = {}
        for i,j in zip(dfparam.columns, dfparam.dtypes):
            
            if "object" in str(j):
                if text=="postgresql-text":
                    dtypedict.update({i: TEXT()})
                else:
                    try:
                        x=int(df[i].str.len().max()/40)+1 
                    except:
                        x=50
                    dtypedict.update({i: types.VARCHAR(length=x*80)})

            if "datetime" in str(j):
                dtypedict.update({i: types.DateTime()})

            if "float" in str(j):
                dtypedict.update({i: types.Float(precision=3, asdecimal=True)})

            if "int" in str(j):
                dtypedict.update({i: types.INT()})

        return dtypedict
    if datadict is None:datadict=sqlcol(df)
    if datadict=='postgresql-text':datadict=sqlcol(df,'postgresql-text')
    if dbtype=='sqlite':
        df.to_sql(tb_name,con,if_exists=if_exists,index=False,dtype=datadict)
    else:

        df.to_sql(tb_name,con,if_exists=if_exists,index=False,schema=conp[4],dtype=datadict)
    con.dispose()



def db_command(sql,dbtype='mssql',pool=0,conp=None):

    """db_command 仅仅到数据库"""
    if conp is None:conp=_pool[dbtype][pool]
    if dbtype=='postgresql':
        con=psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432",database=conp[3])
    elif dbtype=='mssql':
        con=pymssql.connect(user=conp[0], password=conp[1], host=conp[2],database=conp[3])
    elif dbtype=='oracle':
        con = cx_Oracle.connect("%s/%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]))

    elif dbtype=='sqlite':
        con=sqlite3.connect(conp)
    else:
        con = MySQLdb.connect(user=conp[0],passwd=conp[1],host=conp[2],db=conp[3])
    cur=con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()


def db_etl(sql,datadict,dbtypes,tb_name,size='100000,10000',conp1=None,conp2=None,pool='0,1'):
    """四个关系型数据库之前互相etl"""
    pools=_get_pools(dbtypes,pool)
    if conp1 is None:conp1=pools[0]
    if conp2 is None:conp2=pools[1]
    dbtypes=list(dbtypes.split('-'))
    for i in range(len(dbtypes)):
        if dbtypes[i]=='mssql':
            dbtypes[i]='mssql+pymssql'
    print(dbtypes)
    con1=create_engine("%s://%s:%s@%s/%s"%(dbtypes[0],conp1[0],conp1[1],conp1[2],conp1[3]),encoding='utf-8')
    con2=create_engine("%s://%s:%s@%s/%s"%(dbtypes[1],conp2[0],conp2[1],conp2[2],conp2[3]),encoding='utf-8')
    size=list(map(lambda x:int(x),size.split(',')))

    begin=datetime.datetime.now()
    dfs=pd.read_sql(sql,con1,chunksize=size[1])

    count=0
    print(datadict)
    for df in dfs:
        df.rename(str.lower, axis='columns',inplace=True)
        
        
        df=df.applymap(lambda x:x.replace('\u0000', '').replace('\x00', '') if isinstance(x,str) else x)
        if count==0:
            df.to_sql(tb_name,con2,if_exists='replace',index=False,schema=conp2[4],dtype=datadict)
            
            print("开始写入-%s,%s"%(tb_name,begin))
        else:
            df.to_sql(tb_name,con2,if_exists='append',index=False,schema=conp2[4],dtype=datadict)
            print('写入第%d个df段(%s行)-%s'%(count,size[1],tb_name))
        count+=1
    end=datetime.datetime.now()
    t=(end-begin).seconds
    print("%s写入完毕,耗时 %d 秒"%(end,t))

def db_etl_byname(tb_name,dbtypes,tb_name_target=None,size='100000,10000',conp1=None,conp2=None,pool='0,1'):
    
    if tb_name_target is None:tb_name_target=tb_name
    pools=_get_pools(dbtypes,pool)
  
    if conp1 is None:conp1=pools[0]
    if conp2 is None:conp2=pools[1]

    if dbtypes=='mssql-postgresql':
        sql="select * from %s"%tb_name

        datadicts=self.get_column_types('mssql',conp1,tb_name)

        datadict=datadicts[0]
        self.db_etl(sql,datadict,'mssql-postgresql',tb_name_target,size,conp1,conp2,pool)


def _get_pools(dbtypes,pool):
    pooli=list(map(lambda x:int(x),pool.split(',')))
    dbtype_list=dbtypes.split('-')
    pools=[]
    for i,w in zip(pooli,dbtype_list):
        pools.append(_pool[w][i])
    return pools

#返回字段类型信息
def get_column_types(dbtype,conp,tb_name,columns=None):
    """返回字段的sqlalchemy types和数据库types，
        mssql必须严格conp至少要精确到库，tb_name就是na表名 没有schema前缀
    """
    if dbtype=='mssql':
        col_types=sget_column_types_mssql(conp,tb_name,columns)

    return col_types

def get_column_types_mssql(conp,tb_name,columns=None):

    """返回mssql表的columns的 sqlalchemy types和数据库types"""
    sql="""
        SELECT  CASE WHEN col.colorder = 1 THEN obj.name  
                          ELSE ''  
                     END AS 表名,  
                col.colorder AS 序号 ,  
                col.name AS 列名 ,  
                ISNULL(ep.[value], '') AS 列说明 ,  
                t.name AS 数据类型 ,  
                col.length AS 长度 ,  
                ISNULL(COLUMNPROPERTY(col.id, col.name, 'Scale'), 0) AS 小数位数 ,  
                CASE WHEN COLUMNPROPERTY(col.id, col.name, 'IsIdentity') = 1 THEN '√'  
                     ELSE ''  
                END AS 标识 ,  
                CASE WHEN EXISTS ( SELECT   1  
                                   FROM     dbo.sysindexes si  
                                            INNER JOIN dbo.sysindexkeys sik ON si.id = sik.id  
                                                                      AND si.indid = sik.indid  
                                            INNER JOIN dbo.syscolumns sc ON sc.id = sik.id  
                                                                      AND sc.colid = sik.colid  
                                            INNER JOIN dbo.sysobjects so ON so.name = si.name  
                                                                      AND so.xtype = 'PK'  
                                   WHERE    sc.id = col.id  
                                            AND sc.colid = col.colid ) THEN '√'  
                     ELSE ''  
                END AS 主键 ,  
                CASE WHEN col.isnullable = 1 THEN '√'  
                     ELSE ''  
                END AS 允许空 ,  
                ISNULL(comm.text, '') AS 默认值  
        FROM    dbo.syscolumns col  
                LEFT  JOIN dbo.systypes t ON col.xtype = t.xusertype  
                inner JOIN dbo.sysobjects obj ON col.id = obj.id  
                                                 AND obj.xtype = 'U'  
                                                 AND obj.status >= 0  
                LEFT  JOIN dbo.syscomments comm ON col.cdefault = comm.id  
                LEFT  JOIN sys.extended_properties ep ON col.id = ep.major_id  
                                                              AND col.colid = ep.minor_id  
                                                              AND ep.name = 'MS_Description'  
                LEFT  JOIN sys.extended_properties epTwo ON obj.id = epTwo.major_id  
                                                                 AND epTwo.minor_id = 0  
                                                                 AND epTwo.name = 'MS_Description'  
        WHERE   obj.name = '%s'--表名  
    """%tb_name
    con=create_engine("mssql+pymssql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')
    df=pd.read_sql(sql,con)
    
    df['列名']=df[['列名']].applymap(lambda x:x.lower())
    a={}
    b={"varchar":types.VARCHAR,
        "datetime":types.DateTime,
        "char":types.CHAR,
        "int":types.INT,
        "date":types.Date,
        "money":types.NUMERIC,
        "smallint":types.SmallInteger,
        "nvarchar":types.VARCHAR,
        "bigint":types.BIGINT,
        "decimal":types.DECIMAL,
        "numeric":types.NUMERIC,
        "smalldatetime":types.DateTime}
    c={}
    columns=self.get_column_mssql(conp,tb_name) if columns is None else columns
    #print(columns)
    for w in columns:
        t=df.loc[df['列名']==w]
       
        t=t.iloc[0,:]
        datatype,length1,pr=t['数据类型'],t['长度'],t['小数位数']
        
        c[w]=datatype
        if datatype  in b.keys():
            f=b[datatype]
        else:
            print("keyerror is %s"%datatype)
            f=types.VARCHAR
        if datatype in ['varchar','char','nvarchar']:
            a[w]=f(length1)
            
        #elif datatype in['datetime','smalldatetime','date']:
            #a[w]=f(40)
        elif datatype in['money','decimal','numeric']:
            a[w]=f(20,4)
        else:
            a[w]=f()
        
    types_sqlalchemy,types_db=a,c
    return types_sqlalchemy,types_db


def get_column_mssql(conp,tb_name):
    """获取mssql的一个表对象的字段名"""
    con1=create_engine("mssql+pymssql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8')

    sql="""
        SELECT a.name as tbname,b.name as colname FROM %s.dbo.sysobjects as a left join %s.dbo.syscolumns b 
        on a.id=b.id

        where a.name='%s'
    """%(conp[3],conp[3],tb_name)
    df=pd.read_sql(sql,con1)
    col=df['colname']
    col=col.tolist()
    col=list(map(lambda x:x.lower(),col))
    return col 








