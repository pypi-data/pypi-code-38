"""
Workspace connection for Hive Beeline

KISS: Keep It Small & Simple
"""

import pandas                          as _pd
from dsws.util import pretty           as _pretty
from dsws.util import sp               as _sp
from dsws.util import standard_cli_qry as _standard_cli_qry
from os import environ                 as _env
import re                              as _re
from ast import literal_eval           as _literal_eval


class Hbl:

    def __init__(self):
        conf=_literal_eval(_env[self.__module__.split(".")[-1].upper()])
        self.command=conf['command']
        
    def qry(self,qry,r_type="df",limit=20,engine="mr"):
        qry=_standard_cli_qry(qry)
        cmd=self.command.split()
        cmd+=["--hiveconf",{"mr":"hive.execution.engine=mr",
                            "spark":"hive.execution.engine=spark",
                            "tez":"hive.execution.engine=tez"}[engine]]
        qry=["-e" if q=="-q" else q for q in qry]
        qry=cmd + qry
        if r_type=="cmd":
            return(str(cmd))
        rslt = _sp(qry)
        if r_type in ("df","disp"):
            dat=rslt[0].decode().split('\n')
            cols = [c.strip() for c in rslt[0].decode().split('\n')[1].split('|')[1:-1]]
            col_count = len(cols)
            rows = [tuple(c.strip() for c in r.split('|')[1:-1]) for r in rslt[0].decode().split('\n')[3:-2]]
            rows = [r for r in rows if len(r)==col_count]
            rslt = _pd.DataFrame(rows,columns=cols)           
            if r_type=="disp":
                _pretty(rslt,col={"mr":"#FCEC23",
                                  "spark":"#F9CF3B",
                                  "tez":"#3CFF33"}[engine])
                rslt=None
        elif r_type=="msg":
            rslt=rslt[1].decode().split('\n')[-4]
        else:
            rslt=None
        return(rslt)
