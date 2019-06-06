# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

"""
Overview
++++++++

Provides a function to insert IBM Streams tuple data into a table in `IBM Db2 Event Store <https://www.ibm.com/products/db2-event-store>`_.

IBM Db2 Event Store is an in-memory database designed to rapidly ingest and analyze streamed data in event-driven applications. It provides the fabric for fast data with its ability to process massive volume of events in real-time, coupled with optimization for streamed data performance for advanced analytics and actionable insights.

Sample
++++++

A simple example of a Streams application inserting rows to
a table in a Db2 Event Store database::

    from streamsx.topology.topology import Topology
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    from streamsx.topology.context import ContextTypes
    import streamsx.spl.toolkit
    import streamsx.eventstore as es

    topo = Topology('EventStoreSample')
   
    # provide connection endpoint information in format <HostIP:Port from JDBC URL>;<SCALA connection URL>
    es_connection = 'HostIP:Port1;HostIP:Port2'

    # generate sample tuples with the schema of the target table
    s = topo.source([1,2,3,4,5,6,7,8,9])
    schema=StreamSchema('tuple<int32 id, rstring name>').as_tuple()
    s = s.map(lambda x : (x,'X'+str(x*2)), schema=schema)

    # insert tuple data into table as rows
    res = es.insert(s, connection=es_connection, database='TESTDB', table='SampleTable', schema_name='sample', primary_key='id', partitioning_key='id')

    submit (ContextTypes.DISTRIBUTED, topo)
    # The Streams job is kept running.

"""

__version__='2.4.1'

__all__ = ['insert', 'configure_connection', 'download_toolkit', 'get_service_details', 'get_certificate', 'run_statement']
from streamsx.eventstore._eventstore import insert,configure_connection,download_toolkit,get_service_details,get_certificate,run_statement
