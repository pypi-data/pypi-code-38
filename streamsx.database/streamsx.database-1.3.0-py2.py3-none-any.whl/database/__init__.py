# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

"""
Overview
++++++++

Provides functions to run SQL statements to a database.


Credentials
+++++++++++

Db2 Warehouse credentials are defined using service credentials JSON.

The mandatory JSON elements are "username", "password" and "jdbcurl"::

    {
        "username": "<JDBC_USER>",
        "password": "<JDBC_PASSWORD>",
        "jdbcurl":  "<JDBC_URL>"
    }

Sample
++++++

A simple example of a Streams application that creates a table, inserts a row and deletes the table::

    from streamsx.topology.topology import *
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    import streamsx.database as db

    topo = Topology()
    sql_create = 'CREATE TABLE RUN_SAMPLE (A CHAR(10), B CHAR(10))'
    sql_insert = 'INSERT INTO RUN_SAMPLE (A, B) VALUES (\'hello\', \'world\')'
    sql_drop = 'DROP TABLE RUN_SAMPLE'
    s = topo.source([sql_create, sql_insert, sql_drop]).as_string()
    res_sql = db.run_statement(s, credentials)
    res_sql.print()
    submit('STREAMING_ANALYTICS_SERVICE', topo)
    # Use for IBM Streams including IBM Cloud Private for Data
    # submit ('DISTRIBUTED', topo, cfg)

"""

__version__='1.3.0'

__all__ = ['run_statement', 'configure_connection']
from streamsx.database._database import run_statement, configure_connection
