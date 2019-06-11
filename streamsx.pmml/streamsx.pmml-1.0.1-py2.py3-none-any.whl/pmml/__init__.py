# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

"""
Overview
++++++++

Provides functions to score input records using PMML models and to interact with the Watson Machine Learning (WML) repository.


Sample
++++++

A simple example of a Streams application uses the :py:func:`model_feed` and :py:func:`score` functions::

    from streamsx.topology.topology import *
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    import streamsx.pmml as pmml

    topo = Topology()
    # IBM Cloud Machine Learning service credentials
    credentials = '{"url" : "xxx", "instance_id" : "icp"}'
    models = pmml.model_feed(topo, connection_configuration=credentials, model_name="sample_pmml", polling_period=datetime.timedelta(minutes=5))
    # sample with a single model predictor field
    s = topo.source(['first tuple', 'second tuple']).as_string()
    out_schema = StreamSchema('tuple<rstring string, rstring result>')
    res = pmml.score(s, schema=out_schema, model_input_attribute_mapping='sample_predictor=string', model_stream=models, raw_result_attribute_name='result', initial_model_provisioning_timeout=datetime.timedelta(minutes=1))
    res.print()
    # Use for IBM Streams including IBM Cloud Pak for Data
    submit ('DISTRIBUTED', topo)
    # Use for IBM Streaming Analytics service in IBM Cloud
    #submit('STREAMING_ANALYTICS_SERVICE', topo)

"""


__version__='1.0.1'

__all__ = ['score', 'model_feed']
from streamsx.pmml._pmml import score, model_feed

