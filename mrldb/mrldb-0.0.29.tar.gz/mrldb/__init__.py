__all__=["MrlDBMsql", "MrlDBCassandra", "MrlDBSqlite", "MrlDBCluster", "mdbcl", "mdbstr"]
from .db_types import *
from .mrl_cluster import *
from .dbutils import dbutils as mdbstr
##version#start##
__version__='0.0.29'
##version#end##
__doc__=f"""mrldb v{__version__} by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)
"""
