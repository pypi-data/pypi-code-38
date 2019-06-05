# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

import datetime
import requests
import os
from tempfile import gettempdir
import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring


def _add_driver_file_from_url(topology, url, filename):
    r = requests.get(url)
    tmpdirname = gettempdir()
    tmpfile = tmpdirname + '/' + filename
    with open(tmpfile, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    topology.add_file_dependency(tmpfile, 'opt')
    return 'opt/'+filename

def _add_driver_file(topology, path):
    filename = os.path.basename(path)
    topology.add_file_dependency(path, 'opt')
    return 'opt/'+filename

def _read_db2_credentials(credentials):
    jdbcurl = ""
    username = ""
    password = ""
    if isinstance(credentials, dict):
        username = credentials.get('username')
        password = credentials.get('password')
        jdbcurl = credentials.get('jdbcurl')
    else:
        raise TypeError(credentials)
    return jdbcurl, username, password

def configure_connection (instance, name = 'database', credentials = None):
    """Configures IBM Streams for a certain connection.


    Creates or updates an application configuration object containing the required properties with connection information.


    Example for creating a configuration for a Streams instance with connection details::


        streamsx.rest import Instance
        import streamsx.topology.context
        from icpd_core import icpd_util
        
        cfg = icpd_util.get_service_instance_details (name='your-streams-instance')
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False
        instance = Instance.of_service (cfg)
        app_cfg = configure_connection (instance, credentials = 'my_credentials_json')


    Args:
        instance(streamsx.rest_primitives.Instance): IBM Streams instance object.
        name(str): Name of the application configuration, default name is 'database'.
        credentials(str|dict): The service credentials, for example Db2 Warehouse service credentials.
    Returns:
        Name of the application configuration.
    """

    description = 'Database credentials'
    properties = {}
    if credentials is None:
        raise TypeError (credentials)
    
    if isinstance (credentials, dict):
        properties ['credentials'] = json.dumps (credentials)
    else:
        properties ['credentials'] = credentials
    
    # check if application configuration exists
    app_config = instance.get_application_configurations (name = name)
    if app_config:
        print ('update application configuration: ' + name)
        app_config[0].update (properties)
    else:
        print ('create application configuration: ' + name)
        instance.create_application_configuration (name, properties, description)
    return name


def run_statement(stream, credentials, schema=None, sql=None, sql_attribute=None, sql_params=None, transaction_size=1, jdbc_driver_class='com.ibm.db2.jcc.DB2Driver', jdbc_driver_lib=None, ssl_connection=None, truststore=None, truststore_password=None, keystore=None, keystore_password=None, keystore_type=None, truststore_type=None, plugin_name=None, security_mechanism=None, vm_arg=None, name=None):
    """Runs a SQL statement using DB2 client driver and JDBC database interface.

    The statement is called once for each input tuple received. Result sets that are produced by the statement are emitted as output stream tuples.
    
    This function includes the JDBC driver for DB2 database ('com.ibm.db2.jcc.DB2Driver') in the application bundle per default.

    Different drivers, e.g. for other databases than DB2, can be applied and the parameters ``jdbc_driver_class`` and ``jdbc_driver_lib`` must be specified.
    
    Supports two ways to specify the statement:

    * Statement is part of the input stream. You can specify which input stream attribute contains the statement with the ``sql_attribute`` argument. If input stream is of type ``CommonSchema.String``, then you don't need to specify the ``sql_attribute`` argument.
    * Statement is given with the ``sql`` argument. The statement can contain parameter markers that are set with input stream attributes specified by ``sql_params`` argument.

    Example with "insert" statement and values passed with input stream, where the input stream "sample_stream" is of type "sample_schema"::

        import streamsx.database as db
        
        sample_schema = StreamSchema('tuple<rstring A, rstring B>')
        ...
        sql_insert = 'INSERT INTO RUN_SAMPLE (A, B) VALUES (?, ?)'
        inserts = db.run_statement(create_table, credentials=credentials, schema=sample_schema, sql=sql_insert, sql_params="A, B")

    Example with "select count" statement and defined output schema with attribute ``TOTAL`` having the result of the query::

        sample_schema = StreamSchema('tuple<int32 TOTAL, rstring string>')
        sql_query = 'SELECT COUNT(*) AS TOTAL FROM SAMPLE.TAB1'
        query = topo.source([sql_query]).as_string()
        res = db.run_statement(query, credentials=credentials, schema=sample_schema)
    

    Args:
        stream(Stream): Stream of tuples containing the SQL statements or SQL statement parameter values. Supports ``streamsx.topology.schema.StreamSchema`` (schema for a structured stream) or ``CommonSchema.String``  as input.
        credentials(dict|str): The credentials of the IBM cloud DB2 warehouse service in JSON or the name of the application configuration.
        schema(StreamSchema): Schema for returned stream. Defaults to input stream schema if not set.             
        sql(str): String containing the SQL statement. Use this as alternative option to ``sql_attribute`` parameter.
        sql_attribute(str): Name of the input stream attribute containing the SQL statement. Use this as alternative option to ``sql`` parameter.
        sql_params(str): The values of SQL statement parameters. These values and SQL statement parameter markers are associated in lexicographic order. For example, the first parameter marker in the SQL statement is associated with the first sql_params value.
        transaction_size(int): The number of tuples to commit per transaction. The default value is 1.
        jdbc_driver_class(str): The default driver is for DB2 database 'com.ibm.db2.jcc.DB2Driver'.
        jdbc_driver_lib(str): Path to the JDBC driver library file. Specify the jar filename with absolute path, containing the class given with ``jdbc_driver_class`` parameter. Per default the 'db2jcc4.jar' is added to the 'opt' directory in the application bundle.
        ssl_connection(bool): Set to ``True`` to enable SSL connection.
        truststore(str): Path to the trust store file for the SSL connection.
        truststore_password(str): Password for the trust store file given by the truststore parameter.
        keystore(str): Path to the key store file for the SSL connection.
        keystore_password(str): Password for the key store file given by the keystore parameter.
        keystore_type(str): Type of the key store file (JKS, PKCS12).
        truststore_type(str): Type of the key store file (JKS, PKCS12).
        plugin_name(str): Name of the security plugin.
        security_mechanism(int): Value of the security mechanism.
        vm_arg(str): Arbitrary JVM arguments can be passed to the Streams operator.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        Output Stream.
    """

    if sql_attribute is None and sql is None:
        if stream.oport.schema == CommonSchema.String:
            sql_attribute = 'string'
        else:
            raise ValueError("Either sql_attribute or sql parameter must be set.")

    if jdbc_driver_lib is None and jdbc_driver_class != 'com.ibm.db2.jcc.DB2Driver':
        raise ValueError("Parameter jdbc_driver_lib must be specified containing the class from jdbc_driver_class parameter.")

    if schema is None:
        schema = stream.oport.schema

    if isinstance(credentials, dict):
        jdbcurl, username, password = _read_db2_credentials(credentials)
        app_config_name = None
    else:
        jdbcurl=None
        username=None
        password=None
        app_config_name = credentials

    _op = _JDBCRun(stream, schema, appConfigName=app_config_name, jdbcUrl=jdbcurl, jdbcUser=username, jdbcPassword=password, transactionSize=transaction_size, vmArg=vm_arg, name=name)
    if sql_attribute is not None:
        _op.params['statementAttr'] = _op.attribute(stream, sql_attribute)
    else:
        _op.params['statement'] = sql
    if sql_params is not None:
        _op.params['statementParamAttrs'] = sql_params
   
    _op.params['jdbcClassName'] = jdbc_driver_class
    if jdbc_driver_lib is None:
        _op.params['jdbcDriverLib'] = _add_driver_file_from_url(stream.topology, 'https://github.com/IBMStreams/streamsx.jdbc/raw/master/samples/JDBCSample/opt/db2jcc4.jar', 'db2jcc4.jar')
    else:
        _op.params['jdbcDriverLib'] = _add_driver_file(stream.topology, jdbc_driver_lib)

    if ssl_connection is not None:
        if ssl_connection is True:
            _op.params['sslConnection'] = _op.expression('true')
    if keystore is not None:
        _op.params['keyStore'] = _add_driver_file(stream.topology, keystore)
        if keystore_type is not None:
            _op.params['keyStoreType'] = keystore_type
    if keystore_password is not None:
        _op.params['keyStorePassword'] = keystore_password
    if truststore is not None:
        _op.params['trustStore'] = _add_driver_file(stream.topology, truststore)
        if truststore_type is not None:
            _op.params['trustStoreType'] = truststore_type
    if truststore_password is not None:
        _op.params['trustStorePassword'] = truststore_password
    if security_mechanism is not None:
        _op.params['securityMechanism'] = _op.expression(security_mechanism)
    if plugin_name is not None:
        _op.params['pluginName'] = plugin_name

    return _op.outputs[0]


class _JDBCRun(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema=None, appConfigName=None, jdbcClassName=None, jdbcDriverLib=None, jdbcUrl=None, batchSize=None, checkConnection=None, commitInterval=None, commitPolicy=None, hasResultSetAttr=None, isolationLevel=None, jdbcPassword=None, jdbcProperties=None, jdbcUser=None, keyStore=None, keyStorePassword=None, keyStoreType=None, trustStoreType=None, securityMechanism=None, pluginName=None, reconnectionBound=None, reconnectionInterval=None, reconnectionPolicy=None, sqlFailureAction=None, sqlStatusAttr=None, sslConnection=None, statement=None, statementAttr=None, statementParamAttrs=None, transactionSize=None, trustStore=None, trustStorePassword=None, vmArg=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.jdbc::JDBCRun"
        inputs=stream
        schemas=schema
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if jdbcClassName is not None:
            params['jdbcClassName'] = jdbcClassName
        if jdbcDriverLib is not None:
            params['jdbcDriverLib'] = jdbcDriverLib
        if jdbcUrl is not None:
            params['jdbcUrl'] = jdbcUrl
        if batchSize is not None:
            params['batchSize'] = batchSize
        if checkConnection is not None:
            params['checkConnection'] = checkConnection
        if commitInterval is not None:
            params['commitInterval'] = commitInterval
        if commitPolicy is not None:
            params['commitPolicy'] = commitPolicy
        if hasResultSetAttr is not None:
            params['hasResultSetAttr'] = hasResultSetAttr
        if isolationLevel is not None:
            params['isolationLevel'] = isolationLevel
        if jdbcPassword is not None:
            params['jdbcPassword'] = jdbcPassword
        if jdbcProperties is not None:
            params['jdbcProperties'] = jdbcProperties
        if jdbcUser is not None:
            params['jdbcUser'] = jdbcUser
        if keyStore is not None:
            params['keyStore'] = keyStore
        if keyStorePassword is not None:
            params['keyStorePassword'] = keyStorePassword
        if keyStoreType is not None:
            params['keyStoreType'] = keyStoreType
        if reconnectionBound is not None:
            params['reconnectionBound'] = reconnectionBound
        if reconnectionInterval is not None:
            params['reconnectionInterval'] = reconnectionInterval
        if reconnectionPolicy is not None:
            params['reconnectionPolicy'] = reconnectionPolicy
        if sqlFailureAction is not None:
            params['sqlFailureAction'] = sqlFailureAction
        if sqlStatusAttr is not None:
            params['sqlStatusAttr'] = sqlStatusAttr
        if sslConnection is not None:
            params['sslConnection'] = sslConnection
        if statement is not None:
            params['statement'] = statement
        if statementAttr is not None:
            params['statementAttr'] = statementAttr
        if statementParamAttrs is not None:
            params['statementParamAttrs'] = statementParamAttrs
        if transactionSize is not None:
            params['transactionSize'] = transactionSize
        if trustStore is not None:
            params['trustStore'] = trustStore
        if trustStorePassword is not None:
            params['trustStorePassword'] = trustStorePassword
        if trustStoreType is not None:
            params['trustStoreType'] = trustStoreType
        if securityMechanism is not None:
            params['securityMechanism'] = securityMechanism
        if pluginName is not None:
            params['pluginName'] = pluginName


        super(_JDBCRun, self).__init__(topology,kind,inputs,schema,params,name)



