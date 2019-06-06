# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring
import os
import getpass
import wget
from tempfile import gettempdir
import shutil
import tarfile
import requests
import re
import urllib.parse as up
import json
import streamsx.database as db

def _add_toolkit_dependency(topo):
    # IMPORTANT: Dependency of this python wrapper to a specific toolkit version
    # This is important when toolkit is not set with streamsx.spl.toolkit.add_toolkit (selecting toolkit from remote build service)
    streamsx.spl.toolkit.add_toolkit_dependency(topo, 'com.ibm.streamsx.eventstore', '[2.0.0,3.0.0)')

def _add_store_file(topology, path):
    filename = os.path.basename(path)
    topology.add_file_dependency(path, 'opt')
    return 'opt/'+filename


def _download_tk(url, name):
    targetdir=gettempdir() + '/' + name
    tmpfile = gettempdir() + '/' + name + '.tgz'
    if os.path.isdir(targetdir):
        shutil.rmtree(targetdir)
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    wget.download(url, tmpfile)
    #print (tmpfile + ": " + str(os.stat(tmpfile)))
    tar = tarfile.open(tmpfile, "r:gz")
    tar.extractall(path=targetdir)
    tar.close()
    toolkit_path = targetdir + '/' + name
    tkfile = toolkit_path + '/toolkit.xml'
    if os.path.isfile(tkfile):
        f = open(tkfile, "r")
        for x in f:
            if 'toolkit name' in x:
                version_dump = x.replace('requiredProductVersion="4.3.0.0"', '').lstrip()
                print('\n'+version_dump)
                break
        f.close()
    return toolkit_path


def download_toolkit(url=None, name=None):
    """Downloads the latest Event Store toolkit toolkit from GitHub.

    Example for updating the Event Store toolkit with latest toolkit from GitHub::

        # download event store toolkit from GitHub
        eventstore_toolkit = es.update_toolkit()
        # add event store toolkit to topology
        streamsx.spl.toolkit.add_toolkit(topo, eventstore_toolkit)

    Args:
        url(str): Link to toolkit archive (*.tgz) to be downloaded.
        name(str): Folder name in temporary directory where to extract the toolkit.

    Returns:
        eventstore toolkit location
    """
    dirname = 'streamsx.toolkit'
    if url is None:
        # get latest toolkit
        r = requests.get('https://github.com/IBMStreams/streamsx.eventstore/releases/latest')
        r.raise_for_status()
        if r.text is not None:
            s = re.search(r'/IBMStreams/streamsx.eventstore/releases/download/.*tgz', r.text).group()
            url = 'https://github.com/' + s
            dirname = 'com.ibm.streamsx.eventstore'
    if url is not None:
        if name is not None:
            dirname = name;
        print('Download: ' + url)
        eventstore_toolkit = _download_tk(url, dirname)
    else:
        raise ValueError("Invalid URL")
    return eventstore_toolkit



def get_certificate(service_configuration, name='EventStore-1'):
    """Retrieve keystore and truststore file location for Event Store service in ICP4D.

    Example::

        from icpd_core import icpd_util
        
        eventstore_cfg=icpd_util.get_service_instance_details(name='your-eventstore-instance')
        es_truststore, es_keystore = get_certificate(eventstore_cfg, name='your-eventstore-instance')

    Args:
        service_configuration(dict): Event Store service instance details.
        name(str): Name of the Event Store instance

    Returns:
        truststore, keystore

    .. warning:: The function can be used only in IBM Cloud Pak for Data
    .. versionadded:: 2.3
    """
    
    eventstore_cfg = service_configuration 
    token = eventstore_cfg['user_token']
    jdbc_url = eventstore_cfg['connection_info']['jdbc']
    p = '(?:jdbc:db2.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
    m = re.search(p,jdbc_url)
    host = m.group('host')
    #print(host)

    details_url = up.urlunsplit(('https', host + ':31843', 'zen-data/v2/serviceInstance/details', 'displayName=' + name, None))
    r = requests.get(details_url, headers={"Authorization": "Bearer " + token}, verify=False)
    if r.status_code==200:
        sr = r.json()
        es_db=sr['requestObj']['CreateArguments']['metadata']['database-name']
        for x in sr['requestObj']['CreateArguments']['metadata']['connectivity-url']:
            if 'scala' in x['id']:
                es_connection = x['url']
                break
        instance_id=sr['requestObj']['CreateArguments']['metadata']['instance-id']
        clientkeystore = '/user-home/_global_/eventstore/'+instance_id+'/clientkeystore'
        es_truststore = clientkeystore
        es_keystore = clientkeystore

    else:
        clientkeystore=input("Event Store certificate:")
        es_keystore=clientkeystore
        es_keystore=es_truststore

    return es_truststore, es_keystore


def get_service_details(service_configuration, name='EventStore-1'):
    """Retrieve connection information for Event Store service in ICP4D.

    Example for retrieving Event Store service details::

        from icpd_core import icpd_util
        
        eventstore_cfg=icpd_util.get_service_instance_details(name='your-eventstore-instance')
        es_db, es_connection, es_user, es_password, es_truststore, es_truststore_password, es_keystore, es_keystore_password = get_service_details(eventstore_cfg, name='your-eventstore-instance')

    Args:
        service_configuration(dict): Event Store service instance details.
        name(str): Name of the Event Store instance

    Returns:
        database_name, connection, user, password, truststore, truststore_password, keystore, keystore_password

    .. warning:: The function can be used only in IBM Cloud Pak for Data
    .. versionadded:: 2.1
    """
    
    eventstore_cfg = service_configuration 
    token = eventstore_cfg['user_token']
    jdbc_url = eventstore_cfg['connection_info']['jdbc']
    p = '(?:jdbc:db2.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
    m = re.search(p,jdbc_url)
    host = m.group('host')
    port = m.group('port')
    #print(host)
    jdbc_conn=host+':'+port

    details_url = up.urlunsplit(('https', host + ':31843', 'zen-data/v2/serviceInstance/details', 'displayName=' + name, None))
    r = requests.get(details_url, headers={"Authorization": "Bearer " + token}, verify=False)
    if r.status_code==200:
        sr = r.json()
        es_db=sr['requestObj']['CreateArguments']['metadata']['database-name']
        for x in sr['requestObj']['CreateArguments']['metadata']['connectivity-url']:
            if 'scala' in x['id']:
                es_connection = x['url']
                break

        if ';' not in es_connection:
            es_connection = jdbc_conn + ';' + es_connection

        instance_id=sr['requestObj']['CreateArguments']['metadata']['instance-id']
        es_user=sr['requestObj']['CreateArguments']['metadata']['credentials']['user']
        password=sr['requestObj']['CreateArguments']['metadata']['credentials']['password']
        es_password=getpass.getpass('Event Store password:')

        clientkeystore = '/user-home/_global_/eventstore/'+instance_id+'/clientkeystore'
        es_truststore = clientkeystore
        es_keystore = clientkeystore

        session=requests.session()
        requests.packages.urllib3.disable_warnings()
        rest_url = 'https://' + host + ':31843/icp4data-databases/'+instance_id+'/zen/com/ibm/event/api/v1/oltp/certificate_password'
        response = session.get(rest_url, headers={"Authorization": "Bearer " + token}, verify=False)
        if response.status_code==200:
            es_truststore_password=response.text
            es_keystore_password=es_truststore_password
        else:
            es_truststore_password=getpass.getpass("Event Store truststore password:")
            es_keystore_password=es_truststore_password
    else:
        es_db=input("Event Store database name (for example EVENTDB):")
        es_connection=input("Event Store connection (for example '<HOST1>:<JDBC_PORT>;<HOST1>:1101,<HOST2>:1101,<HOST3>:1101':")
        es_user=input("Event Store user:")
        es_password=getpass.getpass('Event Store password:')
        es_truststore_password=getpass.getpass("Event Store truststore password:")
        es_keystore_password=es_truststore_password
        clientkeystore=input("Event Store certificate:")
        es_truststore = clientkeystore
        es_keystore = clientkeystore

    return es_db, es_connection, es_user, es_password, es_truststore, es_truststore_password, es_keystore, es_keystore_password


def configure_connection(instance, name='eventstore', database=None, connection=None, user=None, password=None, keystore_password=None, truststore_password=None, plugin_name=None, plugin_flag=None, ssl_connection=None):
    """Configures IBM Streams for a connection to IBM Db2 Event Store database.

    Creates an application configuration object containing the required properties with connection information.

    Example for creating a configuration for a Streams instance with connection details::

        from streamsx.rest import Instance
        import streamsx.topology.context
        from icpd_core import icpd_util
        
        cfg=icpd_util.get_service_instance_details(name='your-streams-instance')
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False
        instance = Instance.of_service(cfg)
        app_cfg = configure_connection(instance, database='TESTDB', connection='HostIP:Port1;HostIP:Port2', user='db2-user', password='db2-password')


    Args:
        instance(streamsx.rest_primitives.Instance): IBM Streams instance object.
        name(str): Name of the application configuration
        database(str): The name of the database, as defined in IBM Db2 Event Store.
        connection(str): The set of IP addresses and port numbers needed to connect to IBM Db2 Event Store, format: <HostIP:Port from JDBC URL>;<SCALA connection URL>
        user(str): Name of the IBM Db2 Event Store User in order to connect.
        password(str): Password for the IBM Db2 Event Store User in order to connect.
        keystore_password(str): Password for key store file.
        truststore_password(str): Password for trust store file.
        plugin_name(str): The plug-in name for the SSL connection.
        plugin_flag(str): Set "false" to disable SSL plugin. If not specified the default is plugin is used.
        ssl_connection(str): Set "false" to disable SSL connection. If not specified the default is SSL enabled.

    Returns:
        Name of the application configuration.
    """

    # Prepare operator (toolkit) specific properties for application configuration
    description = 'Config for Db2 Event Store connection ' + name
    properties = {}
    if database is not None:
        properties['databaseName']=database
    if connection is not None:
        properties['connectionString']=connection
    if user is not None:
        properties['eventStoreUser']=user
    if password is not None:
        properties['eventStorePassword']=password
    if keystore_password is not None:
        properties['keyStorePassword']=keystore_password
    if truststore_password is not None:
        properties['trustStorePassword']=truststore_password
    if plugin_name is not None:
        properties['pluginName']=plugin_name
    if plugin_flag is not None:
        properties['pluginFlag']=plugin_flag
    if ssl_connection is not None:
        properties['sslConnection']=ssl_connection

    # prepare app config credentials for jdbc toolkit
    if database is not None and connection is not None and user is not None and password is not None:
        if ';' in connection:
            credentials = {}
            conn = connection.split(";", 1)
            credentials['username']=user
            credentials['password']=password
            jdbcurl = 'jdbc:db2://' + conn[0] + '/' + database
            credentials['jdbcurl']=jdbcurl
            # add for app config
            properties ['credentials'] = json.dumps (credentials)
    
    # check if application configuration exists
    app_config = instance.get_application_configurations(name=name)
    if app_config:
        print ('update application configuration: '+name)
        app_config[0].update(properties)
    else:
        print ('create application configuration: '+name)
        instance.create_application_configuration(name, properties, description)
    return name


def _download_driver_file_from_url(url, tmpfile):
    r = requests.get(url)
    with open(tmpfile, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    return tmpfile

def _get_jdbc_driver():
    jdbc_driver_lib = '/user-home/_global_/eventstore/ibm-event_2.11-1.0.jar'
    if os.path.isfile(jdbc_driver_lib):
        return jdbc_driver_lib
    else:
        tmpfile = gettempdir() + '/ibm-event_2.11-1.0.jar'
        if os.path.isfile(tmpfile):
            return tmpfile
        else:
            _download_driver_file_from_url("https://github.com/IBMStreams/streamsx.eventstore/raw/develop/com.ibm.streamsx.eventstore/opt/ibm-event_2.11-1.0.jar", tmpfile)
            if os.path.isfile(tmpfile):
                return tmpfile
            else:
                raise ValueError("Invalid JDBC driver")


def run_statement(stream, credentials, truststore, keystore, truststore_password=None, keystore_password=None, schema=None, sql=None, sql_attribute=None, sql_params=None, transaction_size=1, jdbc_driver_class='COM.ibm.db2os390.sqlj.jdbc.DB2SQLJDriver', jdbc_driver_lib=None, ssl_connection=True, keystore_type='PKCS12', truststore_type='PKCS12', plugin_name='IBMPrivateCloudAuth', security_mechanism=15, vm_arg=None, name=None):
    """Runs a SQL statement using DB2 Event Store client driver and JDBC database interface.

    The statement is called once for each input tuple received. Result sets that are produced by the statement are emitted as output stream tuples.
    
    This function includes the JDBC driver ('ibm-event_2.11-1.0.jar') for DB2 Event Store database ('COM.ibm.db2os390.sqlj.jdbc.DB2SQLJDriver') in the application bundle per default.

    Supports two ways to specify the statement:

    * Statement is part of the input stream. You can specify which input stream attribute contains the statement with the ``sql_attribute`` argument. If input stream is of type ``CommonSchema.String``, then you don't need to specify the ``sql_attribute`` argument.
    * Statement is given with the ``sql`` argument. The statement can contain parameter markers that are set with input stream attributes specified by ``sql_params`` argument.

    Example with "select count" statement and defined output schema with attribute ``TOTAL`` having the result of the query::

        sample_schema = StreamSchema('tuple<int32 TOTAL, rstring string>')
        sql_query = 'SELECT COUNT(*) AS TOTAL FROM SAMPLE.TAB1'
        query = topo.source([sql_query]).as_string()
        res = db.run_statement(query, credentials=credentials, schema=sample_schema)
    

    Args:
        stream(Stream): Stream of tuples containing the SQL statements or SQL statement parameter values. Supports ``streamsx.topology.schema.StreamSchema`` (schema for a structured stream) or ``CommonSchema.String``  as input.
        credentials(dict|str): The credentials of the IBM cloud DB2 warehouse service in JSON or the name of the application configuration.
        truststore(str): Path to the trust store file for the SSL connection.
        keystore(str): Path to the key store file for the SSL connection.
        truststore_password(str): Password for the trust store file given by the truststore parameter.
        keystore_password(str): Password for the key store file given by the keystore parameter.
        schema(StreamSchema): Schema for returned stream. Defaults to input stream schema if not set.             
        sql(str): String containing the SQL statement. Use this as alternative option to ``sql_attribute`` parameter.
        sql_attribute(str): Name of the input stream attribute containing the SQL statement. Use this as alternative option to ``sql`` parameter.
        sql_params(str): The values of SQL statement parameters. These values and SQL statement parameter markers are associated in lexicographic order. For example, the first parameter marker in the SQL statement is associated with the first sql_params value.
        transaction_size(int): The number of tuples to commit per transaction. The default value is 1.
        jdbc_driver_class(str): The default driver is for DB2 Event Store database 'COM.ibm.db2os390.sqlj.jdbc.DB2SQLJDriver'.
        jdbc_driver_lib(str): Path to the JDBC driver library file. Specify the jar filename with absolute path, containing the class given with ``jdbc_driver_class`` parameter. Per default the 'ibm-event_2.11-1.0.jar' is added to the 'opt' directory in the application bundle.
        ssl_connection(bool): Use SSL connection, default is ``True``
        keystore_type(str): Type of the key store file, default is ``PKCS12``.
        truststore_type(str): Type of the key store file, default is ``PKCS12``.
        plugin_name(str): Name of the security plugin, default is 'IBMPrivateCloudAuth'.
        security_mechanism(int): Value of the security mechanism, default is 15 (com.ibm.db2.jcc.DB2BaseDataSource.PLUGIN_SECURITY).
        vm_arg(str): Arbitrary JVM arguments can be passed to the Streams operator.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        Output Stream.

    .. versionadded:: 2.4
    """
    
    jdbc_driver_lib = _get_jdbc_driver()  
    print ('jdbc_driver_lib: '+jdbc_driver_lib)

    return db.run_statement(stream,
                            credentials,
                            schema=schema,
                            sql=sql,
                            sql_attribute=sql_attribute,
                            sql_params=sql_params,
                            transaction_size=transaction_size,
                            jdbc_driver_class=jdbc_driver_class,
                            jdbc_driver_lib=jdbc_driver_lib,
                            ssl_connection=ssl_connection,
                            truststore=truststore,
                            truststore_password=truststore_password,
                            keystore=keystore,
                            keystore_password=keystore_password,
                            keystore_type=keystore_type,
                            truststore_type=truststore_type,
                            plugin_name=plugin_name,
                            security_mechanism=security_mechanism,
                            vm_arg=vm_arg,
                            name=name)



def insert(stream, table, schema_name=None, database=None, connection=None, user=None, password=None, config=None, batch_size=None, front_end_connection_flag=None, max_num_active_batches=None, partitioning_key=None, primary_key=None, truststore=None, truststore_password=None, keystore=None, keystore_password=None, plugin_name=None, plugin_flag=None, ssl_connection=None, schema=None, name=None):
    """Inserts tuple into a table using Db2 Event Store Scala API.

    Important: The tuple field types and positions in the IBM Streams schema must match the field names in your IBM Db2 Event Store table schema exactly.

    Creates the table if the table does not exist. Set the ``primary_key`` and ``partitioning_key`` in case the table needs to be created.

    Example of a Streams application inserting rows to a table in a Db2 Event Store database::

        # provide connection endpoint information in format <HostIP:Port from JDBC URL>;<SCALA connection URL>
        es_connection = 'HostIP:Port1;HostIP:Port2'
        # generate sample tuples with the schema of the target table
        s = topo.source([1,2,3,4,5,6,7,8,9])
        schema=StreamSchema('tuple<int32 id, rstring name>').as_tuple()
        s = s.map(lambda x : (x,'X'+str(x*2)), schema=schema)
        # insert tuple data into table as rows
        res = es.insert(s, connection=es_connection, database='TESTDB', table='SampleTable', schema_name='sample', primary_key='id', partitioning_key='id')

    Args:
        stream(Stream): Stream of tuples containing the fields to be inserted as a row. Supports ``streamsx.topology.schema.StreamSchema`` (schema for a structured stream) as input. The tuple attribute types and positions in the IBM Streams schema must match the field names in your IBM Db2 Event Store table schema exactly.
        table(str): The name of the table into which you want to insert rows.
        schema_name(str): The name of the table schema name of the table into which to insert data.
        database(str): The name of the database, as defined in IBM Db2 Event Store. Alternative this parameter can be set with function ``configure_connection()``.
        connection(str): The set of IP addresses and port numbers needed to connect to IBM Db2 Event Store. Alternative this parameter can be set with function ``configure_connection()``.
        user(str): Name of the IBM Db2 Event Store User in order to connect. Alternative this parameter can be set with function ``configure_connection()``.
        password(str): Password for the IBM Db2 Event Store User in order to connect. Alternative this parameter can be set with function ``configure_connection()``.
        config(str): The name of the application configuration. Value returned by the function ``configure_connection()``.
        batch_size(int): The number of rows that will be batched in the operator before the batch is inserted into IBM Db2 Event Store by using the batchInsertAsync method. If you do not specify this parameter, the batchSize defaults to the estimated number of rows that could fit into an 8K memory page.
        front_end_connection_flag(bool): Set to ``True`` to connect through a Secure Gateway (for Event Store Enterprise Edition version >= 1.1.2 and Developer Edition version > 1.1.4)
        max_num_active_batches(int): The number of batches that can be filled and inserted asynchronously. The default is 1.        
        partitioning_key(str): Partitioning key for the table. A string of attribute names separated by commas. The partitioning_key parameter is used only, if the table does not yet exist in the IBM Db2 Event Store database.
        primary_key(str): Primary key for the table.  A string of attribute names separated by commas. The order of the attribute names defines the order of entries in the primary key for the IBM Db2 Event Store table. The primary_key parameter is used only, if the table does not yet exist in the IBM Db2 Event Store database.
        truststore(str): Path to the trust store file for the SSL connection.
        truststore_password(str): Password for the trust store file given by the truststore parameter. Alternative this parameter can be set with function ``configure_connection()``.
        keystore(str): Path to the key store file for the SSL connection.
        keystore_password(str): Password for the key store file given by the keystore parameter. Alternative this parameter can be set with function ``configure_connection()``.
        plugin_name(str): The plug-in name for the SSL connection. The default value is IBMPrivateCloudAuth.      
        plugin_flag(str|bool): Set "false" or ``False`` to disable SSL plugin. If not specified, the default is use plugin.
        ssl_connection(str|bool): Set "false" or ``False`` to disable SSL connection. If not specified the default is SSL enabled.
        schema(StreamSchema): Schema for returned stream. Expects a Boolean attribute called "_Inserted_" in the output stream. This attribute is set to true if the data was successfully inserted and false if the insert failed. Input stream attributes are forwarded to the output stream if present in schema.            
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        streamsx.topology.topology.Sink: Stream termination
        or
        Output Stream if ``schema`` parameter is specified. This output port is intended to output the information on whether a tuple was successful or not when it was inserted into the database.
    """

    if config is None and connection is None:
         raise ValueError("Either config parameter or connection must be set.")
    if config is None and database is None:
         raise ValueError("Either config parameter or database must be set.")

    # python wrapper eventstore toolkit dependency
    _add_toolkit_dependency(stream.topology)

    _op = _EventStoreSink(stream, schema, connectionString=connection, databaseName=database, tableName=table, schemaName=schema_name, partitioningKey=partitioning_key, primaryKey=primary_key, name=name)
    if front_end_connection_flag is not None:
        if front_end_connection_flag is True:
            _op.params['frontEndConnectionFlag'] = _op.expression('true')
    if batch_size is not None:
        _op.params['batchSize'] = streamsx.spl.types.int32(batch_size)
    if max_num_active_batches is not None:
        _op.params['maxNumActiveBatches'] = streamsx.spl.types.int32(max_num_active_batches)
          
    if keystore is not None:
        _op.params['keyStore'] = _add_store_file(stream.topology, keystore)
    if keystore_password is not None:
        _op.params['keyStorePassword'] = keystore_password
    if plugin_name is not None:
        _op.params['pluginName'] = plugin_name
    if plugin_flag is not None:
        if isinstance(plugin_flag, (bool)):
            if plugin_flag:
                _op.params['pluginFlag'] = _op.expression('true')
            else:
                _op.params['pluginFlag'] = _op.expression('false')
        else:
            if 'true' in plugin_flag.lower():
                _op.params['pluginFlag'] = _op.expression('true')
            else:
                _op.params['pluginFlag'] = _op.expression('false')
    if ssl_connection is not None:
        if isinstance(ssl_connection, (bool)):
            if ssl_connection:
                _op.params['sslConnection'] = _op.expression('true')
            else:
                _op.params['sslConnection'] = _op.expression('false')
        else:
            if 'true' in ssl_connection.lower():
                _op.params['sslConnection'] = _op.expression('true')
            else:
                _op.params['sslConnection'] = _op.expression('false')
    if truststore is not None:
        _op.params['trustStore'] = _add_store_file(stream.topology, truststore)
    if truststore_password is not None:
        _op.params['trustStorePassword'] = truststore_password

    if config is not None:
        _op.params['configObject'] = config
    else:
        if user is not None:
            _op.params['eventStoreUser'] = user
        if password is not None:
            _op.params['eventStorePassword'] = password

    if schema is not None:
        return _op.outputs[0]
    else:
        return streamsx.topology.topology.Sink(_op)


class _EventStoreSink(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema, tableName, connectionString=None, databaseName=None, schemaName=None, batchSize=None, configObject=None, eventStorePassword=None, eventStoreUser=None, frontEndConnectionFlag=None, maxNumActiveBatches=None, nullMapString=None, partitioningKey=None, preserveOrder=None, primaryKey=None, keyStore=None, keyStorePassword=None, pluginFlag=None, pluginName=None, sslConnection=None, trustStore=None, trustStorePassword=None, vmArg=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.eventstore::EventStoreSink"
        inputs=stream
        schemas=schema
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if connectionString is not None:
            params['connectionString'] = connectionString
        if databaseName is not None:
            params['databaseName'] = databaseName
        if tableName is not None:
            params['tableName'] = tableName
        if schemaName is not None:
            params['schemaName'] = schemaName
        if batchSize is not None:
            params['batchSize'] = batchSize
        if configObject is not None:
            params['configObject'] = configObject
        if eventStorePassword is not None:
            params['eventStorePassword'] = eventStorePassword
        if eventStoreUser is not None:
            params['eventStoreUser'] = eventStoreUser
        if frontEndConnectionFlag is not None:
            params['frontEndConnectionFlag'] = frontEndConnectionFlag
        if maxNumActiveBatches is not None:
            params['maxNumActiveBatches'] = maxNumActiveBatches
        if nullMapString is not None:
            params['nullMapString'] = nullMapString
        if partitioningKey is not None:
            params['partitioningKey'] = partitioningKey
        if preserveOrder is not None:
            params['preserveOrder'] = preserveOrder
        if primaryKey is not None:
            params['primaryKey'] = primaryKey
        if keyStore is not None:
            params['keyStore'] = keyStore
        if keyStorePassword is not None:
            params['keyStorePassword'] = keyStorePassword
        if pluginFlag is not None:
            params['pluginFlag'] = pluginFlag
        if pluginName is not None:
            params['pluginName'] = pluginName
        if sslConnection is not None:
            params['sslConnection'] = sslConnection
        if trustStore is not None:
            params['trustStore'] = trustStore
        if trustStorePassword is not None:
            params['trustStorePassword'] = trustStorePassword

        super(_EventStoreSink, self).__init__(topology,kind,inputs,schema,params,name)



