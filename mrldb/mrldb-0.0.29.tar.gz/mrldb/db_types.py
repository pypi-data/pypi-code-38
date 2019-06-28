__doc__=f"""mrldb by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)"""
__all__=["MrlDBMsql", "MrlDBCassandra", "MrlDBSqlite"]
from .type_mysql import MrlDBMsql
from .type_cassandra import MrlDBCassandra
from .type_sqlite import MrlDBSqlite
