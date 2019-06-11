# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

"""
Overview
++++++++

Provides functions to store tuple data as JSON documents in Elasticsearch indices.

This package exposes the `com.ibm.streamsx.elasticsearch <https://ibmstreams.github.io/streamsx.elasticsearch/>`_ toolkit as Python methods for use with Streaming Analytics service on
IBM Cloud and IBM Streams including IBM Cloud Pak for Data.

 * `Streaming Analytics service <https://console.ng.bluemix.net/catalog/services/streaming-analytics>`_
 * `IBM Streams developer community <https://developer.ibm.com/streamsdev/>`_
 * `Compose for Elasticsearch <https://www.ibm.com/cloud/compose/elasticsearch>`_


Credentials
+++++++++++

Elasticsearch credentials are defined using a Streams **application configuration** or the `Compose for Elasticsearch` **connection string**.

Setup connection string
=======================

You can connect to your *Elasticsearch cloud service* with the connection strings that is provided in the Overview tab of your service dashboard.

The connection string for the *Elasticsearch cloud service* can be applied with the ``credentials`` parameter to :py:func:`bulk_insert` or :py:func:`bulk_insert_dynamic`::

    connection = 'https://<USER>:<PASSWORD>@<HOST>:<PORT>/'
    es.bulk_insert(s, 'test-index-cloud', credentials=connection)


Setup application configuration
===============================

By default an application configuration named `es` is used for the ``credentials`` parameter.
A different configuration name can be specified using the ``credentials``
parameter to :py:func:`bulk_insert` or :py:func:`bulk_insert_dynamic`.

The default configuration is "es", this can be set:

* Using the "Application Configuration" tab of the "Streams Console"
* Using page selected by the sub tab "Application Configuration"
* Create a "New application configuration..." using the "Name" "es", no description is necessary
* Set the following properties for your Elasticsearch database connection: "nodeList" (value <HOST>:<PORT>), "userName", "password", "sslEnabled" (value true|false), "sslTrustAllCertificates" (value true|false)


Sample
++++++

A simple hello world example of a Streams application writing string messages to
an index::

    from streamsx.topology.topology import *
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    import streamsx.elasticsearch as es

    topo = Topology('ElasticsearchHelloWorld')

    s = topo.source(['Hello', 'World!']).as_string()
    es.bulk_insert(s, 'test-index-cloud')

    submit('STREAMING_ANALYTICS_SERVICE', topo)


A simple example of a Streams application writing JSON messages to an index, with dynamic index name (part of the stream)::

    from streamsx.topology.topology import *
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    import streamsx.elasticsearch as es

    schema = StreamSchema('tuple<rstring indexName, rstring document>')
    topo = Topology()
    s = topo.source([('idx1','{"msg":"This is message number 1"}'), ('idx2','{"msg":"This is message number 2"}')])
    s = s.map(lambda x : x, schema=schema)
    es.bulk_insert_dynamic(s, index_name_attribute='indexName', message_attribute='document')

    submit('STREAMING_ANALYTICS_SERVICE', topo)

"""

__version__='1.1.2'

__all__ = ['bulk_insert', 'bulk_insert_dynamic']
from streamsx.elasticsearch._elasticsearch import bulk_insert, bulk_insert_dynamic
