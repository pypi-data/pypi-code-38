"""
Workspace connection for pyspark

ws_pyspark is a dsws sess type library that does not follow PEP-249.
It contains a single class, Pyspark.
It is intended to be the primary instantiation for 
insteractive spark sessions.
"""

import pandas as pd
from dsws.util import pretty
from dsws.util import sp
from dsws.util import standard_sess_qry
from os import environ as env
import re
from ast import literal_eval
from pyspark.sql import SparkSession

class Pyspark:

    def __init__(self,kwargs,command=None):
        """
        Workspace class from the pyspark library

        As convntion for DSWS, the following class methods are
        provided:
         - init: returns a session class pyspark.sql.session.SparkSession
         - qry: precesses a query, return type is dependent upon r_type requested:
            - df: pandas dataframe
            - disp: pretty html form of pandas dataframe
            - raw: not yet available, to return spark dataframe, pyspark.sql.dataframe.DataFrame
            - cmd: not yet available standard query form to be processed. Helpful for debugging and logging.
        
        Configuring a Pyspark class is typically done through dsws.duct, but can also be
        evaluated as:
        ```python
        from dsws.ws_pyspark import Pypsark
        kwargs = {'spark.yarn.executor.memoryOverhead':2048,
                  'spark.sql.shuffle.partitions':10,
                  'spark.yarn.queue':'root.default',
                  'spark.app.name':'dsws_session'}
        spark = Pyspark(kwargs)
        ```
        
        To know which values can be accepted in kwargs run, goto Apache Spark
        documentation for your respecitive version:
        https://spark.apache.org/docs/latest/configuration.html
        
        spark-sql is the most logical cli to use for the spark command. However, distributions
        may not include spark-sql and therefore will not be in bin path as expected. Simply,
        do not populate the command argument.
        https://spark.apache.org/docs/latest/sql-distributed-sql-engine.html#running-the-spark-sql-cli
        """
        self.conf=kwargs
        if command is not None:
            self.command=command

    def init(self):
        ss=SparkSession.builder
        for k,v in self.conf.items():
            ss=ss.config(k,v)
        return(ss.getOrCreate())
        
    def qry(self,qry,r_type="df",limit=20):
        qry=standard_sess_qry(qry)
        spark=self.init()
        if r_type=="disp" and "LIMIT" not in qry.upper() and "SELECT" in qry.upper():
            qry = qry + " LIMIT " + str(limit)
        rslt=spark.sql(qry).toPandas()
        if r_type == "disp":
            pretty(rslt,col="#F4A460")
            rslt=None
        return(rslt)
