from pyspark.sql import SparkSession,DataFrame
from pyspark.sql.types import *
import pandas as pd
import numpy as np

import sys
sys.path.append("..")
from table import Table
from tableset import TableSet
from relationship import Relationship
from dfs import dfs

if __name__ == "__main__":
    
    spark = SparkSession \
        .builder \
        .appName("Save CSV AS Table") \
        .enableHiveSupport()\
        .getOrCreate()
    sdf=spark.sql(''' select * from fact.fact_fund_detail_10000 ''')

    ts = TableSet("ssss")

ts.table_from_dataframe(table_id="1111",dataframe=sdf,index='customer_no')

ts.table_from_dataframe(table_id="2222",dataframe=sdf,index='bank_no')

ts.table_from_dataframe(table_id="3333",dataframe=sdf,index='bank_no')

re1 = Relationship(ts["1111"]["customer_no"],ts["2222"]["customer_no"])

re2 = Relationship(ts["2222"]["bank_no"],ts["3333"]["bank_no"])

ts.add_relationships([re1,re2])

dfs(tableset = ts, target_table = '1111',max_depth=1)