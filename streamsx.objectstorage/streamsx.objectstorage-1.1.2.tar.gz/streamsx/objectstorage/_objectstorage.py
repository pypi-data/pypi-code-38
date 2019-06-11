# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

import datetime

import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring
import json

def configure_connection(instance, name='cos', credentials=None):
    """Configures IBM Streams for a certain connection.


    Creates an application configuration object containing the required properties with connection information.


    Example for creating a configuration for a Streams instance with connection details::


        streamsx.rest import Instance
        import streamsx.topology.context
        from icpd_core import icpd_util
        import streamsx.objectstorage as cos

        cfg = icpd_util.get_service_instance_details(name='your-streams-instance')
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False
        instance = Instance.of_service(cfg)
        app_cfg = cos.configure_connection(instance, credentials='my_credentials_json')


    Args:
        instance(streamsx.rest_primitives.Instance): IBM Streams instance object.
        name(str): Name of the application configuration, default name is 'cos'.
        credentials(str|dict): The service credentials for IBM Cloud Object Storage.
    Returns:
        Name of the application configuration.

    .. warning:: The function can be used only in IBM Cloud Pak for Data
    .. versionadded:: 1.1
    """

    description = 'COS credentials'
    properties = {}
    if credentials is None:
        raise TypeError(credentials)

    if isinstance(credentials, dict):
        properties['cos.creds'] = json.dumps(credentials)
    else:
        properties['cos.creds'] = credentials

    # check if application configuration exists
    app_config = instance.get_application_configurations(name=name)
    if app_config:
        print('update application configuration: ' + name)
        app_config[0].update(properties)
    else:
        print('create application configuration: ' + name)
        instance.create_application_configuration(name, properties, description)
    return name


def scan(topology, bucket, endpoint, pattern='.*', directory='/', credentials=None, vm_arg=None, name=None):
    """Scan a directory in a bucket for object names.

    Scans an object storage directory and emits the names of new or modified objects that are found in the directory.

    Example scanning a directory ``/sample`` for objects matching the pattern::

        import streamsx.objectstorage as cos

        scans = cos.scan(topo, bucket='your-bucket-name', directory='/sample', pattern='SAMPLE_[0-9]*\\.ascii\\.text$')

    Args:
        topology(Topology): Topology to contain the returned stream.
        bucket(str): Bucket name. Bucket must have been created in your Cloud Object Storage service before using this function.
        endpoint(str): Endpoint for Cloud Object Storage. Select the endpoint for your bucket location and resiliency: `IBM® Cloud Object Storage Endpoints <https://console.bluemix.net/docs/services/cloud-object-storage/basics/endpoints.html>`_. Use a private enpoint when running in IBM cloud Streaming Analytics service.
        pattern(str): Limits the object names that are listed to the names that match the specified regular expression.
        directory(str): Specifies the name of the directory to be scanned. Any subdirectories are not scanned.
        credentials(str|dict): Credentials in JSON or name of the application configuration containing the credentials for Cloud Object Storage. When set to ``None`` the application configuration ``cos`` is used.
        vm_arg(str): Arbitrary JVM arguments can be passed. For example, increase JVM's maximum heap size ``'-Xmx 8192m'``.     
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        Stream: Object names stream with schema ``CommonSchema.String``.
    """

    appConfigName=credentials
    # check if it's the credentials for the service
    if isinstance(credentials, dict):
         appConfigName = None

    _op = _ObjectStorageScan(topology, CommonSchema.String, pattern=pattern, directory=directory, endpoint=endpoint, appConfigName=appConfigName, vmArg=vm_arg, name=name)
    _op.params['objectStorageURI'] = 's3a://'+bucket
    if isinstance(credentials, dict):
        iam_api_key, service_instance_id = _read_iam_credentials(credentials)
        _op.params['IAMApiKey'] = iam_api_key
        _op.params['IAMServiceInstanceId'] = service_instance_id

    return _op.outputs[0]


def read(stream, bucket, endpoint, credentials=None, vm_arg=None, name=None):
    """Read an object in a bucket.

    Reads the object specified in the input stream and emits content of the object.

    Example of reading object with the objects names from the ``scanned`` stream::

        import streamsx.objectstorage as cos

        r = cos.read(scanned, bucket=bucket, endpoint=endpoint)

    Args:
        stream(Stream): Stream of tuples with object names to be read. Expects ``CommonSchema.String`` in the input stream.
        bucket(str): Bucket name. Bucket must have been created in your Cloud Object Storage service before using this function.
        endpoint(str): Endpoint for Cloud Object Storage. Select the endpoint for your bucket location and resiliency: `IBM® Cloud Object Storage Endpoints <https://console.bluemix.net/docs/services/cloud-object-storage/basics/endpoints.html>`_. Use a private enpoint when running in IBM cloud Streaming Analytics service.
        credentials(str|dict): Credentials in JSON or name of the application configuration containing the credentials for Cloud Object Storage. When set to ``None`` the application configuration ``cos`` is used.
        vm_arg(str): Arbitrary JVM arguments can be passed. For example, increase JVM's maximum heap size ``'-Xmx 8192m'``.        
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        Stream: Object content line by line with schema ``CommonSchema.String``.
    """

    appConfigName=credentials
    # check if it's the credentials for the service
    if isinstance(credentials, dict):
         appConfigName = None

    _op = _ObjectStorageSource(stream, CommonSchema.String, endpoint=endpoint, appConfigName=appConfigName, vmArg=vm_arg, name=name)
    _op.params['objectStorageURI'] = 's3a://'+bucket
    if isinstance(credentials, dict):
        iam_api_key, service_instance_id = _read_iam_credentials(credentials)
        _op.params['IAMApiKey'] = iam_api_key
        _op.params['IAMServiceInstanceId'] = service_instance_id
    return _op.outputs[0]

def _read_iam_credentials(credentials):
    iam_api_key = ""
    service_instance_id = ""
    api_key = credentials.get('apikey')
    resource_instance_id = credentials.get('resource_instance_id')
    # need to extract the last part of the resource_instance_id for ObjectStorage toolkit operators
    data = resource_instance_id.split(":")
    for temp in data:
        if temp != '':
            service_instance_id = temp
    return api_key, service_instance_id

def _check_time_per_object(time_per_object):
    if isinstance(time_per_object, datetime.timedelta):
        result = time_per_object.total_seconds()
    elif isinstance(time_per_object, int) or isinstance(time_per_object, float):
        result = time_per_object
    else:
        raise TypeError(time_per_object)
    if result <= 1:
        raise ValueError("Invalid time_per_object value. Value must be at least one second.")
    return result

def write(stream, bucket, endpoint, object, time_per_object=10.0, header=None, credentials=None, vm_arg=None, name=None):
    """Write strings to an object.

    Adds a COS-Writer where each tuple on `stream` is
    written into an object.

    Example of creating an object with two lines::

        import streamsx.objectstorage as cos
        to_cos = topo.source(['Hello', 'World!'])
        to_cos = to_cos.as_string()
        cos.write(to_cos, self.bucket, self.endpoint, '/sample/hw%OBJECTNUM.txt')

    Args:
        stream(Stream): Stream of tuples to be written to an object. Expects ``CommonSchema.String`` in the input stream.
        bucket(str): Bucket name. Bucket must have been created in your Cloud Object Storage service before using this function.
        endpoint(str): Endpoint for Cloud Object Storage. Select the endpoint for your bucket location and resiliency: `IBM® Cloud Object Storage Endpoints <https://console.bluemix.net/docs/services/cloud-object-storage/basics/endpoints.html>`_. Use a private enpoint when running in IBM cloud Streaming Analytics service.
        object(str): Name of the object to be created in your bucket. For example, ``SAMPLE_%OBJECTNUM.text``, %OBJECTNUM is an object number, starting at 0. When a new object is opened for writing the number is incremented.
        time_per_object(int|float|datetime.timedelta): Specifies the approximate time, in seconds, after which the current output object is closed and a new object is opened for writing.
        header(str): Specify the content of the header row. This header is added as first line in the object. Use this parameter when writing strings in CSV format and you like to query the objects with the IBM SQL Query service. By default no header row is generated.
        credentials(str|dict): Credentials in JSON or name of the application configuration containing the credentials for Cloud Object Storage. When set to ``None`` the application configuration ``cos`` is used.
        vm_arg(str): Arbitrary JVM arguments can be passed. For example, increase JVM's maximum heap size ``'-Xmx 8192m'``.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        streamsx.topology.topology.Sink: Stream termination.
    """

    appConfigName=credentials
    # check if it's the credentials for the service
    if isinstance(credentials, dict):
         appConfigName = None

    _op = _ObjectStorageSink(stream, objectName=object, endpoint=endpoint, appConfigName=appConfigName, vmArg=vm_arg, name=name)
    _op.params['storageFormat'] = 'raw'
    _op.params['objectStorageURI'] = 's3a://'+bucket
    _op.params['timePerObject'] = streamsx.spl.types.float64(_check_time_per_object(time_per_object))
    if header is not None:
        _op.params['headerRow'] = header
    if isinstance(credentials, dict):
        iam_api_key, service_instance_id = _read_iam_credentials(credentials)
        _op.params['IAMApiKey'] = iam_api_key
        _op.params['IAMServiceInstanceId'] = service_instance_id

    return streamsx.topology.topology.Sink(_op)
    
def write_parquet(stream, bucket, endpoint, object, time_per_object=10.0, credentials=None, vm_arg=None, name=None):
    """Create objects in parquet format.

    Adds a COS-Writer where each tuple on `stream` is
    written into an object in parquet format.

    Args:
        stream(Stream): Stream of tuples to be written to an object. Supports ``streamsx.topology.schema.StreamSchema`` (schema for a structured stream) as input. Attributes are mapped to parquet columns.
        bucket(str): Bucket name. Bucket must have been created in your Cloud Object Storage service before using this function.
        endpoint(str): Endpoint for Cloud Object Storage. Select the endpoint for your bucket location and resiliency: `IBM® Cloud Object Storage Endpoints <https://console.bluemix.net/docs/services/cloud-object-storage/basics/endpoints.html>`_. Use a private enpoint when running in IBM cloud Streaming Analytics service.
        object(str): Name of the object to be created in your bucket. For example, ``SAMPLE_%OBJECTNUM.parquet``, %OBJECTNUM is an object number, starting at 0. When a new object is opened for writing the number is incremented.
        time_per_object(int|float|datetime.timedelta): Specifies the approximate time, in seconds, after which the current output object is closed and a new object is opened for writing.
        credentials(str|dict): Credentials in JSON or name of the application configuration containing the credentials for Cloud Object Storage. When set to ``None`` the application configuration ``cos`` is used.
        vm_arg(str): Arbitrary JVM arguments can be passed. For example, increase JVM's maximum heap size ``'-Xmx 8192m'``.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        streamsx.topology.topology.Sink: Stream termination.
    """

    appConfigName=credentials
    # check if it's the credentials for the service
    if isinstance(credentials, dict):
         appConfigName = None

    _op = _ObjectStorageSink(stream, objectName=object, endpoint=endpoint, appConfigName=appConfigName, vmArg=vm_arg, name=name)
    _op.params['storageFormat'] = 'parquet'
    _op.params['parquetCompression'] = 'SNAPPY'
    _op.params['parquetEnableDict'] = True
    _op.params['objectStorageURI'] = 's3a://'+bucket
    _op.params['timePerObject'] = streamsx.spl.types.float64(_check_time_per_object(time_per_object))
    if isinstance(credentials, dict):
        iam_api_key, service_instance_id = _read_iam_credentials(credentials)
        _op.params['IAMApiKey'] = iam_api_key
        _op.params['IAMServiceInstanceId'] = service_instance_id

    return streamsx.topology.topology.Sink(_op)


class _ObjectStorageSink(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema=None, vmArg=None, appConfigName=None, bytesPerObject=None, closeOnPunct=None, dataAttribute=None, encoding=None, endpoint=None, headerRow=None, objectName=None, objectNameAttribute=None, objectStorageURI=None, parquetBlockSize=None, parquetCompression=None, parquetDictPageSize=None, parquetEnableDict=None, parquetEnableSchemaValidation=None, parquetPageSize=None, parquetWriterVersion=None, partitionValueAttributes=None, skipPartitionAttributes=None, storageFormat=None, timeFormat=None, timePerObject=None, tuplesPerObject=None, IAMApiKey=None, IAMServiceInstanceId=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.objectstorage::ObjectStorageSink"
        inputs=stream
        schemas=schema
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if bytesPerObject is not None:
            params['bytesPerObject'] = bytesPerObject
        if closeOnPunct is not None:
            params['closeOnPunct'] = closeOnPunct
        if dataAttribute is not None:
            params['dataAttribute'] = dataAttribute
        if encoding is not None:
            params['encoding'] = encoding
        if endpoint is not None:
            params['endpoint'] = endpoint
        if headerRow is not None:
            params['headerRow'] = headerRow
        if objectName is not None:
            params['objectName'] = objectName
        if objectNameAttribute is not None:
            params['objectNameAttribute'] = objectNameAttribute
        if objectStorageURI is not None:
            params['objectStorageURI'] = objectStorageURI
        if parquetBlockSize is not None:
            params['parquetBlockSize'] = parquetBlockSize
        if parquetCompression is not None:
            params['parquetCompression'] = parquetCompression
        if parquetDictPageSize is not None:
            params['parquetDictPageSize'] = parquetDictPageSize
        if parquetEnableDict is not None:
            params['parquetEnableDict'] = parquetEnableDict
        if parquetEnableSchemaValidation is not None:
            params['parquetEnableSchemaValidation'] = parquetEnableSchemaValidation
        if parquetPageSize is not None:
            params['parquetPageSize'] = parquetPageSize
        if parquetWriterVersion is not None:
            params['parquetWriterVersion'] = parquetWriterVersion
        if partitionValueAttributes is not None:
            params['partitionValueAttributes'] = partitionValueAttributes
        if skipPartitionAttributes is not None:
            params['skipPartitionAttributes'] = skipPartitionAttributes
        if storageFormat is not None:
            params['storageFormat'] = storageFormat
        if timeFormat is not None:
            params['timeFormat'] = timeFormat
        if timePerObject is not None:
            params['timePerObject'] = timePerObject
        if tuplesPerObject is not None:
            params['tuplesPerObject'] = tuplesPerObject
        if IAMApiKey is not None:
            params['IAMApiKey'] = IAMApiKey
        if IAMServiceInstanceId is not None:
            params['IAMServiceInstanceId'] = IAMServiceInstanceId

        super(_ObjectStorageSink, self).__init__(topology,kind,inputs,schema,params,name)


class _ObjectStorageScan(streamsx.spl.op.Source):
    def __init__(self, topology, schema, directory, pattern, vmArg=None, appConfigName=None, endpoint=None, objectStorageURI=None, initDelay=None, sleepTime=None, strictMode=None, IAMApiKey=None, IAMServiceInstanceId=None, name=None):
        kind="com.ibm.streamsx.objectstorage::ObjectStorageScan"
        inputs=None
        schemas=schema
        params = dict()
        params['directory'] = directory
        if vmArg is not None:
            params['vmArg'] = vmArg
        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if endpoint is not None:
            params['endpoint'] = endpoint
        if objectStorageURI is not None:
            params['objectStorageURI'] = objectStorageURI
        if initDelay is not None:
            params['initDelay'] = initDelay
        if sleepTime is not None:
            params['sleepTime'] = sleepTime
        if pattern is not None:
            params['pattern'] = pattern
        if strictMode is not None:
            params['strictMode'] = strictMode
        if IAMApiKey is not None:
            params['IAMApiKey'] = IAMApiKey
        if IAMServiceInstanceId is not None:
            params['IAMServiceInstanceId'] = IAMServiceInstanceId

        super(_ObjectStorageScan, self).__init__(topology,kind,schemas,params,name)


class _ObjectStorageSource(streamsx.spl.op.Invoke):
    
    def __init__(self, stream, schema, vmArg=None, appConfigName=None, endpoint=None, objectStorageURI=None, blockSize=None, encoding=None, initDelay=None, IAMApiKey=None, IAMServiceInstanceId=None, name=None):
        kind="com.ibm.streamsx.objectstorage::ObjectStorageSource"
        topology = stream.topology
        inputs=stream
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if endpoint is not None:
            params['endpoint'] = endpoint
        if objectStorageURI is not None:
            params['objectStorageURI'] = objectStorageURI
        if blockSize is not None:
            params['blockSize'] = initDelay
        if encoding is not None:
            params['encoding'] = sleepTime
        if initDelay is not None:
            params['initDelay'] = initDelay
        if IAMApiKey is not None:
            params['IAMApiKey'] = IAMApiKey
        if IAMServiceInstanceId is not None:
            params['IAMServiceInstanceId'] = IAMServiceInstanceId

        super(_ObjectStorageSource, self).__init__(topology,kind,inputs,schema,params,name)


