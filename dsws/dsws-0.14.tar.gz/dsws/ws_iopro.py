"""
Workspace connection for IOPro

Notice: IOPro only has a 30 day evaluation period.

ws_iopro is a dsws conn type library that follows PEP-249.
It contains a single class, iopro.
IOPro uses a connection string to connect or it accepts kwargs to generate a conneciton string.
"""

import pandas          as pd
from impala.dbapi  import connect
from dsws.util     import pretty
from dsws.util     import sp
from dsws.util     import standard_conn_qry
from dsws.util     import no_return
from os import environ as env
from ast           import literal_eval

class Iopro:

    def __init__(self,kwargs,command=None):
        """
        Workspace class from the IOPro library

        As conviention for DSWS, the following class methods are
        provided:
         - conn: returns a connection class pyodbc.Connection
         - qry: precesses a query, return type is dependent upon r_type requested:
            - df/raw: pandas dataframe
            - disp: pretty html form of pandas dataframe
            - msg: experimental - retuens query profile if using impala
            - cmd: standard query form to be processed. Helpful for debugging and logging
        
        Configuring an iopro class is typically done through dsws.duct, but can also be
        evaluated as:
        ```python
        from dsws.ws_iopro import Iopro
        kwargs = {'DSN': 'Hiveodbc',
                  'autocommit': True}
        iop = Iopro(kwargs)
        ```
        
        Any values in kwargs that are capitalized and not connection arguments
        will be processed as query set statements.
        """
        self.qryconf={k:v for k,v in kwargs.items() if k.isupper()}
        self.conf={a:kwargs[a] for a in kwargs.items() if a not in self.qryconf}
        if command is not None:
            self.command=command
    
    def conn(self):
       return(connect(**self.conf))

    def qry(self,qry,r_type="df",limit=30):
        r_type = 'df' if r_type=='raw' else r_type
        qry=standard_conn_qry(qry)
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
        if no_return(qry[-1]):
            return(None)
        if r_type in ("df","disp"):
            rslt = pd.read_sql(sql=qry[-1],con=conn)
            if r_type=="disp":
                pretty(rslt,col="#5697cb")
                rslt=None
        elif r_type=="msg":
            cursor.execute(qry[-1])
            rslt=(cursor.get_summary(),cursor.get_profile())
        else:
            rslt=None
        conn.close()    
        return(rslt)
