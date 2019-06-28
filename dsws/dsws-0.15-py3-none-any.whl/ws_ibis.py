"""
Workspace connection for Ibis

It contains a single class, Ibis.
It can be used for any of the following: Impala, SQLite, 
 PostgreSQL, Clickhouse, BigQuery, Pandas, MapD, MySQL
"""

import ibis
import pandas          as pd
from dsws.util     import pretty
from dsws.util     import sp
from dsws.util     import standard_conn_qry
from dsws.util     import no_return
from os import environ as env
from ast           import literal_eval

class Impyla:

    def __init__(self,kwargs,command=None):
        """
        Workspace class from the ibis library

        As convntion for DSWS, the following class methods are
        provided:
         - conn: returns a connection class that depends on 
         - qry: precesses a query, return type is dependent upon r_type requested:
            - df/raw: pandas dataframe
            - disp: pretty html form of pandas dataframe
            - msg: experimental - retuens query profile if using impala
            - cmd: standard query form to be processed. Helpful for debugging and logging
        
        Configuring an ibis class is typically done through dsws.duct, but can also be
        evaluated as:
        ```python
        from dsws.ws_ibis import Ibis

        kwargs = {'host':'node1.ratiocinate.com',
                  'port':21050,
                  'database':'default',
                  'auth_mechanism':'GSSAPI',
                  'hdfs_client':
                   {'host':'node1.ratiocinate.com',
                    'port':50070,
                    'auth_mechanism':'GSSAPI',
                    'use_https':False}}}}
        ib = Ibis(kwargs)
        ```
        Contrary to other common connections, ibis requires both an hdfs and impala 
        configurations for full functionality. HDFS client configs are passed as a dict
        value for the `hdfs_client` key. 
        """
        self.qryconf={k:v for k,v in kwargs.items() if k.isupper()}
        self.conf={a:kwargs[a] for a in connect.__code__.co_varnames if a in kwargs.keys()}
        if command is not None:
            self.command=command
    
    def conn(self):
        conf = self.conf.copy()
        if 'hdfs_client' in conf.keys():
            conf['hdfs_client']=self.hdfs_connect() 
        return(getattr(self._ibis,self._module).connect(**conf))    

    def qry(self,qry,r_type="df",limit=30):
        r_type = 'df' if r_type=='raw' else r_type
        qry=standard_conn_qry(qry)
        if r_type=="cmd":
            return(qry)
        conn   = self.conn()
        for k in self.qryconf:
          conn.raw_sql("SET %s=%s" % (k,self.qryconf[k]),False)
        for q in qry[:-1]:
          conn.raw_sql(q,False)
        if r_type=="disp" and "LIMIT" not in qry[-1].split()[-2].upper() and "SELECT" in qry[-1].split()[1].upper():
            qry[-1] = qry[-1] + " LIMIT " + str(limit)
        #cur = conn.raw_sql(qry[-1])
        if no_return(qry[-1]):
            return(None)
        if r_type in ("df","disp"):
            rslt = conn.execute(conn.sql(qry[-1]))
            if r_type=="disp":
                pretty(rslt,col="#E07862")
                rslt=None
        elif r_type=="msg":
            #TODO: Add messaging capability
            rslt=None
        else:
            rslt=None
        conn.close()
        return(rslt)
