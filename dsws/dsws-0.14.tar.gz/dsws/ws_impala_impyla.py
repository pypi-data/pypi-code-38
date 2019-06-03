"""
Workspace connection for Impyla

KISS: Keep It Small & Simple
"""

from impala.dbapi import connect         as _connect
import pandas                            as _pd
from dsws.util import pretty             as _pretty
from dsws.util import sp                 as _sp
from dsws.util import standard_conn_qry  as _standard_conn_qry
from dsws.util import no_return          as _no_return
from os import environ                   as _env
from ast import literal_eval             as _literal_eval

class Impyla:

    def __init__(self):
        """
        
        To simplify distinction beteween impala query configurations and
        impyla connection configurations, we'll use lower case and 
        capital letters to distinguish.
        """
        conf=_literal_eval(_env[self.__module__.split(".")[-1].upper()])
        self.qryconf=dict([(a,conf[a]) for a in conf if a.isupper()])
        self.conf=dict([(a,conf[a]) for a in _connect.__code__.co_varnames \
                            if a in conf])
    
    def conn(self):
       return(_connect(**self.conf))

    def qry(self,qry,r_type="df",limit=30):
        qry=_standard_conn_qry(qry)
        if r_type=="cmd":
            return(qry)
        conn   = self.conn()
        cursor = conn.cursor()
        for k in self.qryconf:
          cursor.execute("SET %s=%s" % (k,self.qryconf[k]))
        for q in qry[:-1]:
            cursor.execute(q)
        if r_type=="disp" and "LIMIT" not in qry[-1].split()[-2].upper() and "SELECT" in qry[-1].split()[1].upper():
            qry[-1] = qry[-1] + " LIMIT " + str(limit)
        cursor.execute(qry[-1])
        if _no_return(qry[-1]):
            return(None)
        if r_type in ("df","disp"):
            rslt = _pd.read_sql(sql=qry[-1],con=conn)
            if r_type=="disp":
                _pretty(rslt,col="#5697cb")
                rslt=None
        elif r_type=="msg":
            cursor.execute(qry[-1])
            rslt=(cursor.get_summary(),cursor.get_profile())
        else:
            rslt=None
        conn.close()    
        return(rslt)
