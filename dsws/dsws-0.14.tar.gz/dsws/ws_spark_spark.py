"""
Workspace session for spark

KISS: Keep It Small & Simple
"""

import pandas                           as _pd
from dsws.util import pretty            as _pretty
from dsws.util import sp                as _sp
from dsws.util import standard_sess_qry as _standard_sess_qry
from os import environ                  as _env
import re                               as _re
from ast import literal_eval            as _literal_eval
from pyspark.sql import SparkSession    as _SparkSession

class Spark:

    def __init__(self):
        self.conf=_literal_eval(_env[self.__module__.split(".")[-1].upper()])
    

    def init(self):
        ss=_SparkSession.builder
        for k,v in self.conf.items():
            ss=ss.config(k,v)
        return(ss.getOrCreate())

        
    def qry(self,qry,r_type="df",limit=20):
        qry=_standard_sess_qry(qry)
        spark=self.init()
        if r_type=="disp" and "LIMIT" not in qry.upper() and "SELECT" in qry.upper():
            qry = qry + " LIMIT " + str(limit)
        rslt=spark.sql(qry).toPandas()
        if r_type == "disp":
            _pretty(rslt,col="#F4A460")
            rslt=None
        return(rslt)
