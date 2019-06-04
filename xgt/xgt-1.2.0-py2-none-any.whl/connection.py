# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2018-2019 Trovares Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and 
#  limitations under the License.
#
#===----------------------------------------------------------------------===#

import json
import os
import time
from datetime import timedelta, datetime
from os.path import expanduser

import grpc
import six

from . import ErrorMessages_pb2 as err_proto
from . import SchemaMessages_pb2 as sch_proto
from . import AdminService_pb2 as admin_proto
from . import AdminService_pb2_grpc as admin_grpc
from . import GraphTypesService_pb2 as graph_proto
from . import GraphTypesService_pb2_grpc as graph_grpc
from . import DataService_pb2 as data_proto
from . import DataService_pb2_grpc as data_grpc
from . import JobService_pb2 as job_proto
from . import JobService_pb2_grpc as job_grpc
from .common import (_assert_noerrors, _validated_property_name,
                     _validated_schema, _validated_frame_name,
                     _validate_opt_level, _to_unicode, Job,
                     XgtError, XgtNameError, XgtTypeError, XgtValueError,
                     XgtConnectionError, DEFAULT_OPT_LEVEL)
from .graph import TableFrame, VertexFrame, EdgeFrame
from .version import __version__

class Connection(object):
  """
  Connection to the server with functionality to create, change, and remove
  graph structures and run jobs.

  Parameters
  ----------
  host : str
    IP address of the computer where the server is running.
  port : int
    Port where the server is listening on for RPC calls.
  flags: dict
    Dictionary containing flags. Possible flags are:

    aws_access_key_id : str
      Amazon Access Key ID, used for authentication when loading data
      files from S3 buckets. The default is an empty string.
    aws_secret_access_key : str
      Amazon Access Key ID, used for authentication when loading data
      files from S3 buckets. The default is an empty string.
    ssl : boolean
      If true use ssl authentication for secure server channels.
      The default is False.
    ssl_root_dir : str
      Path to the root folder for ssl certificates and private keys.
      Defaults to the user's home directory.
    ssl_server_cn : str
      Common name on the certificate of the server to connect to.
      The default is the hostname.
  """

  def __init__(self, host='127.0.0.1', port=4367, flags=None):
    if flags is None:
      flags = {}
    self.port = port
    self.aws_access_key_id = flags.get('aws_access_key_id', '')
    self.aws_secret_access_key = flags.get('aws_secret_access_key', '')
    self.ssl = flags.get('ssl', False)
    self.ssl_root_dir = flags.get('ssl_root_dir', expanduser("~") + '/.ssl/')
    self.ssl_server_cn = flags.get('ssl_server_cn', host)
    self.host = host
    self.cwd = os.getcwd()
    self.client = six.moves.http_client
    self.current_opt_level = DEFAULT_OPT_LEVEL

    self._channel = self._create_channel()
    self._admin_svc = admin_grpc.AdminServiceStub(self._channel)
    self._graph_svc = graph_grpc.GraphTypesServiceStub(self._channel)
    self._data_svc = data_grpc.DataServiceStub(self._channel)
    self._job_svc = job_grpc.JobServiceStub(self._channel)

    self._server_unique_identifier = 0
    self._initialize_server_unique_identifier()
    self._version_check()

  def _create_channel(self):
    channel = None
    connection_string = self.host + ':' + _to_unicode(self.port)
    if (self.ssl):
      chain_cert = open(self.ssl_root_dir + '/certs/ca-chain.cert.pem', 'rb').read()
      client_key = open(self.ssl_root_dir + '/private/client.key.pem', 'rb').read()
      client_cert = open(self.ssl_root_dir + '/certs/client.cert.pem', 'rb').read()
      creds = grpc.ssl_channel_credentials(chain_cert, client_key, client_cert)
      try:
        channel = grpc.secure_channel(
            connection_string, creds,
            options=(('grpc.ssl_target_name_override', self.ssl_server_cn,),))
      except grpc.RpcError as ex:
        raise XgtConnectionError(ex.details(), '')
    else:
      try:
        channel = grpc.insecure_channel(connection_string)
      except grpc.RpcError as ex:
        raise XgtConnectionError(ex.details(), '')
    return channel

  def _initialize_server_unique_identifier(self):
    try:
      request = admin_proto.IdentifierRequest()
      response = self._run_rpc_function(request, self._admin_svc.Identifier)
      self._server_unique_identifier = response.server_unique_identifier
    except Exception:
      raise XgtConnectionError('Failure on connection initialization.')

  def call(self, request, rpc_function):
    response = self._run_rpc_function(request, rpc_function)
    try:
      _ = iter(response)
      # For response that return an iterator, it is the caller's responsibility
      # to check each packet for errors. E.g.:
      #   for result in response:
      #     _assert_noerrors(result)
      return response
    except TypeError:
      pass
    _assert_noerrors(response)
    return response

  def _run_rpc_function(self, request, rpc_function):
    try:
      _ = iter(request)
      # Iterators passed in as a request have already filled in the server id
      # per element of the iterator, so do not need to do it here.
    except TypeError:
      request.expected_server_id = self._server_unique_identifier
    try:
      response = rpc_function(request)
    except grpc.RpcError as ex:
      raise XgtConnectionError(ex.details(), '')
    return response

  def _convert_to_json(self, json_str):
    try:
      jsn = json.loads(json_str)
    except Exception as ex:
      raise XgtError("invalid json string: " + _to_unicode(ex) +
                     "\n==> " + _to_unicode(json_str[:1000]))
    if 'type' in jsn:
      if jsn['type'] == 'error' and 'data' in jsn and 'trace' in jsn and \
         'errorcode' in jsn:
        try:
          error_code_name = jsn['errorcode']
          error_class = _code_error_map[error_code_name]
          raise error_class(_to_unicode(jsn['data']),
                            _to_unicode(jsn['trace']))
        except XgtError:
          raise
        except Exception as ex:
          raise XgtError("Error detected while raising exception" +
                         _to_unicode(ex), _to_unicode(ex))
      elif jsn['type'] == 'error' and 'data' in jsn and 'trace' in jsn:
        raise XgtError(jsn['data'], jsn['trace'])
      elif jsn['type'] == 'error' and 'data' in jsn:
        raise XgtError(jsn['data'])
      elif jsn['type'] == "warning" and 'data' in jsn:
        print(jsn['data'])
    elif 'trace' in jsn:
      raise XgtError("Error: " + _to_unicode(jsn['error']),
                     _to_unicode(jsn['trace']))
    elif 'error' in jsn:
      raise XgtError("Error: " + _to_unicode(jsn['error']))
    return jsn

  def _version_check(self):
    server_version = None
    request = admin_proto.VersionRequest()
    response = self.call(request, self._admin_svc.Version)
    server_version = response.version
    if server_version != __version__:
      msg = "Version matching for xgt and " \
            "the server failed. Install the appropriate xgt " \
            "package. xGT version: " + server_version
      raise XgtError(msg)

  def _change_exit_error_count(self, action):
    action_u = action.upper()
    request = admin_proto.ChangeErrorCountRequest()
    request.action = admin_proto.ErrorCountActionEnum.Value(action_u)
    response = self.call(request, self._admin_svc.ChangeErrorCount)
    return response.error_count

  #------------------------- Housekeeping Methods
  @property
  def server_version(self):
    """
    Obtains the current product version from the server.

    Returns
    -------
    str
      Version number.

    """
    request = admin_proto.VersionRequest()
    response = self.call(request, self._admin_svc.Version)
    return response.version

  @property
  def max_user_memory_size(self):
    """
    Returns the maximum amount of memory available for user data on the xGT server.

    Returns
    -------
    int
      Maximum available user memory, in bytes.
    """
    request = admin_proto.MaxUserMemorySizeRequest()
    response = self.call(request, self._admin_svc.MaxUserMemorySize)
    return response.pool_size

  @property
  def free_user_memory_size(self):
    """
    Returns the amount of free memory available for user data on the xGT server.

    Returns
    -------
    int
      Currently available user memory, in bytes.
    """
    request = admin_proto.FreeUserMemorySizeRequest()
    response = self.call(request, self._admin_svc.FreeUserMemorySize)
    return response.free_memory_size

  def _stat_report(self):
    request = admin_proto.StatReportRequest()
    response = self.call(request, self._admin_svc.StatReport)
    return response.stat_report_json

  def _stat_reset(self):
    request = admin_proto.StatResetRequest()
    self.call(request, self._admin_svc.StatReset)

  #------------------------- Catalog Getter Methods
  def get_table_frames(self,names=None):
    """
    Get a list of TableFrame objects present in the server.

    A TableFrame object allows for interaction with a table present in the xGT server.
    For example, a table may be created by a MATCH query and may contain query results.
    It may also be explicitly created with `Connection.create_table_frame()`.

    Parameters
    ----------
    names : list of strings or None
      If a list, the list of names of tables frames to retrieve.
      If None, all table frames are returned.

    Returns
    -------
    list
      TableFrame objects representing tables present in the server.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create graph
    >>> qr1 = 'MATCH (a:Employee) RETURN a.PersonID INTO Result1'
    >>> conn.run_job(qr1)
    >>> table_frames = conn.get_table_frames()
    >>> print [f.name for f in table_frames]
    ['Employee_table', 'ReportsTo_table', 'Result1']
    >>> result1_data = table_frames[2].get_data_pandas()

    """
    if names is None:
      names = []
    elif isinstance(names, six.string_types):
      raise TypeError('Invalid argument: "names" must be a list of strings')
    else:
      names = [_validated_frame_name(n) for n in names]

    request = graph_proto.GetTableFramesRequest()
    if names is not None:
      request.name.extend(names)
    response = self.call(request, self._graph_svc.GetTableFrames)
    frames = []
    for data in response.table_type:
      schema = []
      for prop in data.schema.property:
        prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
        prop_type = _to_unicode(prop_type)
        schema.append([prop.name, prop_type])
      frames.append(TableFrame(self, data.name, schema, data.error_name))
    return frames

  def get_table_frame(self, name):
    """
    Get a TableFrame object that allows interaction with a table present in the xGT server.

    A TableFrame object allows for interaction with a table present in the xGT server.
    For example, a table may be created by a MATCH query and may contain query results.
    It may also be explicitly created with `Connection.create_table_frame()`.

    Parameters
    ----------
    name : str
      Table name.

    Returns
    -------
    TableFrame
      Frame to the table.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create graph and run queries ...
    >>> t = conn.get_table_frame('Employee_table')
    >>> print(str(t))
    {
      'name': 'Employee_table',
      'schema': [
        ['PersonID', 'int'],
        ['Name', 'text'],
        ['PostalCode', 'int']]
    }
    >>> qr1 = 'MATCH (a:Employee) RETURN a.PersonID INTO Result1'
    >>> conn.run_job(qr1)
    >>> result1_table = conn.get_table_frame('Result1')
    >>> num_results = result1_table.num_rows
    >>> result1_data = result1_table.get_data_pandas()

    """
    frames = self.get_table_frames([name])
    return frames[0]

  def get_vertex_frames(self, names = None):
    """
    Get a list of VertexFrame objects present in the xGT server.

    A VertexFrame represents a collection of vertices held on the xGT
    server and can be used to retrieve information about them.
    `VertexFrame.get_data_pandas()` and `VertexFrame.get_data()` are
    used to retrieve member vertices.
    Each vertex in a VertexFrame shares the same properties,
    described in `VertexFrame.schema`. Each vertex in a VertexFrame
    is uniquely identified by the property listed in `VertexFrame.key`.

    Parameters
    ----------
    names : list of strings or None
      If a list, the list of names of vertex frames to retrieve.
      If None, all vertex frames are returned.

    Returns
    -------
    list
      VertexFrame objects present in the server.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> print [f.name for f in conn.get_vertex_frames()]
    ['Company', 'Person']
    >>> print [f.num_vertices for f in conn.get_vertex_frames()]
    [3, 101]

    """
    if names is None:
      names = []
    elif isinstance(names, six.string_types):
      raise TypeError('Invalid argument: "names" must be a list of strings')
    else:
      names = [_validated_frame_name(n) for n in names]

    request = graph_proto.GetVertexFramesRequest()
    request.name.extend(names)
    response = self.call(request, self._graph_svc.GetVertexFrames)
    frames = []
    for data in response.vertex_type:
      schema = []
      for prop in data.schema.property:
        prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
        prop_type = _to_unicode(prop_type)
        schema.append([prop.name, prop_type])
      vertex_key_val = sch_proto.RoleEnum.Value('VERTEX_KEY')
      key = None
      for prop in data.schema.property:
        prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
        prop_type = _to_unicode(prop_type)
        if prop.role == vertex_key_val:
          key = prop.name
          break
      frames.append(VertexFrame(self, data.name, schema, key, data.error_name))
    return frames

  def get_vertex_frame(self, name):
    """
    Get a VertexFrame object that allows interaction with a collection of vertices.

    A VertexFrame represents a collection of vertices held on the xGT
    server and can be used to retrieve information about them.
    `VertexFrame.get_data_pandas()` and `VertexFrame.get_data()` are
    used to retrieve member vertices.
    Each vertex in a VertexFrame shares the same properties,
    described in `VertexFrame.schema`. Each vertex in a VertexFrame
    is uniquely identified by the property listed in `VertexFrame.key`.

    Parameters
    ----------
    name : str
      VertexFrame name.

    Returns
    -------
    VertexFrame
      Frame to the collection of vertices.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> v = conn.get_vertex_frame('Person')
    >>> print(str(v))
    {
      'name': 'Person',
      'key': 'id',
      'schema': [
        ['id', 'int'],
        ['name', 'text']],
    }
    >>> print(str(v.num_vertices))
    101
    >>> vertices = v.get_data_pandas()

    """
    frames = self.get_vertex_frames([name])
    return frames[0]

  def get_edge_frames(self, names=None, graph=None):
    """
    Get a list of EdgeFrame objects present in the xGT server.

    An EdgeFrame represents a collection of edges held on the xGT
    server and can be used to retrieve information about them.
    `EdgeFrame.get_data_pandas()` and `EdgeFrame.get_data()` are
    used to retrieve member edges.
    Edge edge in an EdgeFrame shares the same properties, described
    in `EdgeFrame.schema`.

    Parameters
    ----------
    names : list of strings or None
      If a list, the list of names of edge frames to retrieve.
      If None, all edge frames are returned.

    Returns
    -------
    list
      EdgeFrame objects present in the server.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> print [f.name for f in conn.get_edge_frames()]
    ['RelatedTo', 'WorksFor']

    """
    if names is None:
      names = []
    elif isinstance(names, six.string_types):
      raise TypeError('Invalid argument: "names" must be a list of strings')
    else:
      names = [_validated_frame_name(n) for n in names]

    request = graph_proto.GetEdgeFramesRequest()
    request.name.extend(names)
    response = self.call(request, self._graph_svc.GetEdgeFrames)
    frames = []
    for data in response.edge_type:
      schema = []
      for prop in data.schema.property:
        prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
        prop_type = _to_unicode(prop_type)
        schema.append([prop.name, prop_type])
      source_key = data.source_key
      target_key = data.target_key
      frames.append(EdgeFrame(self, data.name, schema,
                              data.source_vertex, data.target_vertex,
                              source_key, target_key, data.error_name))
    return frames

  def get_edge_frame(self, name):
    """
    Get an EdgeFrame object that allows interaction with a collection of edges.

    An EdgeFrame represents a collection of edges held on the xGT
    server and can be used to retrieve information about them.
    `EdgeFrame.get_data_pandas()` and `EdgeFrame.get_data()` are
    used to retrieve member edges.
    Edge edge in an EdgeFrame shares the same properties, described
    in `EdgeFrame.schema`.

    Parameters
    ----------
    name : str
      EdgeFrame name.

    Returns
    -------
    EdgeFrame
      Frame to the collection of edges.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create graph and run queries ...
    >>> e = conn.get_edge_frame('WorksFor')
    >>> print(str(e))
    {
      'name': 'WorksFor',
      'source': 'Person',
      'target': 'Company',
      'schema': [
        ['srcid', 'int'],
        ['trgid', 'int']],
      'source_key' : 'srcid',
      'target_key' : 'trgid'
    }
    >>> edges = e.get_data_pandas()

    """
    frames = self.get_edge_frames([name])
    return frames[0]

  #------------------------- DDL Methods
  def create_table_frame(self, name, schema):
    """
    Create a new TableFrame in the server.

    A TableFrame object represents a table held on the xGT server and can be
    used to retrieve information about it. The TableFrame schema describes
    the names and data types of table properties.

    Parameters
    ----------
    name : str
      Name of table.
    schema : list of pairs
      List of pairs associating property names with xGT data types.

    Returns
    -------
    TableFrame
      Frame to the table.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> conn.create_table_frame(
          name = 'tab1',
    ...   schema = [['id', xgt.INT],
    ...             ['name', xgt.TEXT]])

    """
    name = _validated_frame_name(name)
    schema = _validated_schema(schema)

    request = graph_proto.CreateTableFrameRequest()
    request.table_type.name = name
    for col_name,col_type in schema:
      prop = sch_proto.Property()
      prop.name = col_name
      prop.data_type = sch_proto.UvalTypeEnum.Value(col_type)
      prop.role = sch_proto.RoleEnum.Value('PROPERTY')
      request.table_type.schema.property.extend([prop])
    response = self.call(request, self._graph_svc.CreateTableFrame)
    data = response.table_type[0]
    schema = []
    for prop in data.schema.property:
      prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
      prop_type = _to_unicode(prop_type)
      schema.append([prop.name, prop_type])
    frame = TableFrame(self, data.name, schema, data.error_name)
    return frame

  def create_vertex_frame(self, name, schema, key):
    """
    Create a new VertexFrame in the server.

    A VertexFrame represents a grouping or collection of vertices
    held on the xGT server, all sharing the same property names
    and types. This function creates a new frame of vertices
    on the xGT server and returns a VertexFrame representing it.

    Parameters
    ----------
    name : str
      Name of vertex frame.
    schema : list of pairs
      List of pairs associating property names with xGT data types.
      Each vertex in the VertexFrame will have these properties.
    key : str
      The property name used to uniquely identify vertices in the graph.
      This is the name of one of the properties from the schema and
      must be unique for each vertex in the frame.

    Returns
    -------
    VertexFrame
      Frame to the collection of vertices.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> pers_vtx = conn.create_vertex_frame(
                     name = 'Person',
    ...              schema = [['id', xgt.INT],
    ...                        ['name', xgt.TEXT]],
    ...              key = 'id')

    """
    name = _validated_frame_name(name)
    schema = _validated_schema(schema)
    key = _validated_property_name(key)

    key_found = False
    if key not in [prop for prop,_ in schema]:
      msg = u'The vertex key "{0}" does not match any schema property ' \
            u'name in this frame.'
      raise XgtNameError(msg.format(key))

    request = graph_proto.CreateVertexFrameRequest()
    request.vertex_type.name = name
    for col_name,col_type in schema:
      prop = sch_proto.Property()
      prop.name = col_name
      prop.data_type = sch_proto.UvalTypeEnum.Value(col_type)
      if col_name == key:
        prop.role = sch_proto.RoleEnum.Value('VERTEX_KEY')
      else:
        prop.role = sch_proto.RoleEnum.Value('PROPERTY')
      request.vertex_type.schema.property.extend([prop])
    response = self.call(request, self._graph_svc.CreateVertexFrame)
    frame = None
    data = response.vertex_type[0]
    schema = []
    for prop in data.schema.property:
      prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
      prop_type = _to_unicode(prop_type)
      schema.append([prop.name, prop_type])
    vertex_key_val = sch_proto.RoleEnum.Value('VERTEX_KEY')
    key = None
    for prop in data.schema.property:
      prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
      prop_type = _to_unicode(prop_type)
      if prop.role == vertex_key_val:
        key = prop.name
        break
    frame = VertexFrame(self, data.name, schema, key, data.error_name)
    return frame

  def create_edge_frame(self, name, schema, source, target, source_key, target_key):
    """
    Create a new EdgeFrame in the server.

    An EdgeFrame represents a collection of edges held on the xGT server
    that share the same property names and types. The source vertex
    of each edge in an EdgeFrame must belong to the same VertexFrame.
    This source VertexFrame is identified by the source parameter of
    this function. The target vertex of each edge in an EdgeFrame must
    belong to the same VertexFrame. This target VertexFrame is identified
    by the target parameter.

    For each edge in the EdgeFrame, its source vertex is identified by
    the edge property name given in the parameter source_key, which must
    be one of the properties listed in the schema. The edge target vertex
    is identified by the property name given in the parameter target_key,
    which must be one of the properties listed in the schema.

    Parameters
    ----------
    name : str
      Name of edge frame.
    schema : list of pairs
      List of pairs associating property names with xGT data types.
      Each edge in the EdgeFrame will have these properties.
    source : str or VertexFrame
      The name of a VertexFrame or a VertexFrame object.
      The source vertex of each edge in this EdgeFrame will belong
      to this VertexFrame.
    target : str or VertexFrame
      The name of a VertexFrame or a VertexFrame object.
      The target vertex of each edge in this EdgeFrame will belong
      to this VertexFrame.
    source_key : str
      The edge property name that identifies the source vertex of an edge.
      This is one of the properties from the schema.
    target_key : str
      The edge property name that identifies the target vertex of an edge.
      This is one of the properties from the schema.

    Returns
    -------
    EdgeFrame
      Frame to the collection of edges.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> conn.create_vertex_frame(
          name = 'Person',
    ...   schema = [['id', xgt.INT],
    ...             ['name', xgt.TEXT]],
    ...   key = 'id')
    >>> conn.create_vertex_frame(
          name = 'Company',
    ...   schema = [['id', xgt.INT],
    ...             ['size', xgt.TEXT],
    ...             ['name', xgt.TEXT]],
    ...   key = 'id')
    >>> conn.create_edge_frame(
          name = 'WorksFor',
    ...   schema = [['srcid', xgt.INT],
    ...             ['role', xgt.TEXT],
    ...             ['trgid', xgt.INT]],
    ...   source = 'Person',
    ...   target = 'Company',
    ...   source_key = 'srcid',
    ...   target_key = 'trgid')

    """
    name = _validated_frame_name(name)
    schema = _validated_schema(schema)
    source_key = _validated_property_name(source_key)
    target_key = _validated_property_name(target_key)

    if source_key not in [prop for prop, _ in schema]:
      msg = u'The source key "{0}" does not match any schema property ' \
            u'name in this frame.'
      raise XgtNameError(msg.format(source_key))
    if target_key not in [prop for prop, _ in schema]:
      msg = u'The target key "{0}" does not match any schema property ' \
            u'name in this frame.'
      raise XgtNameError(msg.format(target_key))

    if isinstance(source, VertexFrame):
      source_name = source.name
    else:
      source_name = _validated_frame_name(source)
    if isinstance(target, VertexFrame):
      target_name = target.name
    else:
      target_name = _validated_frame_name(target)

    request = graph_proto.CreateEdgeFrameRequest()
    request.edge_type.name = name
    request.edge_type.source_vertex = source_name
    request.edge_type.target_vertex = target_name
    request.edge_type.source_key = source_key
    request.edge_type.target_key = target_key
    for col_name, col_type in schema:
      prop = sch_proto.Property()
      prop.name = col_name
      prop.data_type = sch_proto.UvalTypeEnum.Value(col_type)
      if col_name == source_key:
        prop.role = sch_proto.RoleEnum.Value('EDGE_SOURCE_KEY')
      elif col_name == target_key:
        prop.role = sch_proto.RoleEnum.Value('EDGE_TARGET_KEY')
      else:
        prop.role = sch_proto.RoleEnum.Value('PROPERTY')
      request.edge_type.schema.property.extend([prop])

    response = self.call(request, self._graph_svc.CreateEdgeFrame)
    data = response.edge_type[0]
    schema = []
    for prop in data.schema.property:
      prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
      prop_type = _to_unicode(prop_type)
      schema.append([prop.name, prop_type])
    frame = EdgeFrame(self, data.name, schema,
                      data.source_vertex, data.target_vertex, data.source_key,
                      data.target_key, data.error_name)
    return frame

  def drop_frame(self, frame):
    """
    Drop a VertexFrame, EdgeFrame, or TableFrame.

    Parameters
    ----------
    frame : str, VertexFrame, EdgeFrame, or TableFrame
      A frame or the name of frame to drop on the xGT server.

    Returns
    -------
    bool
      True if frame was found and dropped and False if frame was not found.

    """
    if isinstance(frame, TableFrame):
      name = frame.name
    else:
      name = _validated_frame_name(frame)
    request = graph_proto.DeleteTypeRequest()
    request.name = name
    response = self.call(request, self._graph_svc.DeleteType)
    return response.found_and_deleted

  #------------------------- Job Methods

  def set_optimization_level(self, optlevel = DEFAULT_OPT_LEVEL):
    """
    Set the optimization level for TQL queries.

    Parameters
    ----------
    optlevel : int
      The optimization level values are:
        - 0: No optimization.
        - 1: General optimization.
        - 2: WHERE-clause optimization.

      Optional. Default is 2'.
    """
    if _validate_opt_level(optlevel):
      self.current_opt_level = optlevel

  def get_jobs(self, jobids=None):
    """
    Get a list of Job objects, each representing the state of
    the job on the server at the point in time of the
    invocation of this function.

    Parameters
    ----------
    jobids : list of ints
      A list of job ids for which to return Job objects.
      By default all jobs are returned.

    Returns
    -------
    list
      A list of Job objects, each representing the state
      of a job in the server.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges and run queries ...
    >>> all_jobs = conn.get_jobs()
    >>> for j in all_jobs:
    >>> ... print j
    id:6, status:completed
    id:7, status:completed
    id:8, status:running

    """

    if jobids is None:
      request = job_proto.GetJobsRequest()
      response = self.call(request, self._job_svc.GetJobs)
      jobids = []
      for s in response.job_status:
        jobids.append(s.job_id)
    return [Job(self, i) for i in jobids]

  def cancel_job(self, job):
    """
    Cancel the execution of a job in the server.

    A job can be canceled only if it is *running* and will have a status of
    *canceled* after its cancellation. A job that already had a status of
    *completed* or *failed* before invoking this function will keep that
    status after invoking this function.

    Parameters
    ----------
    job : Job, int
      A Job object or an integer job id to cancel.

    Returns
    -------
    bool
      True if the job was cancelled. False if the job already had a
      status of completed or failed before invoking this function.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges and run queries ...
    >>> print(conn.cancel_job(18))
    id:18, status:completed
    >>> all_jobs = conn.get_jobs()
    >>> for j in all_jobs:
    >>> ... conn.cancel_job(j)

    """
    if isinstance(job, Job):
      jobid = job.id
    elif isinstance(job, six.integer_types):
      jobid = job
    else:
      raise TypeError("Job must be a Job object or an int.")

    # Get job status.
    request = job_proto.GetJobsRequest()
    request.job_id.extend([jobid])
    response = self.call(request, self._job_svc.GetJobs)
    # Cancel job if it's not in a terminal state.
    if len(response.job_status) > 0:
      job_status = response.job_status[0]
      if job_status.status in [job_proto.SCHEDULED, job_proto.RUNNING]:
        request = job_proto.CancelJobsRequest()
        request.job_id.extend([jobid])
        self.call(request, self._job_svc.CancelJobs)
        return True
      else:
        return False
    else:
      return False

  def run_job(self, query, optlevel=None, timeout=None):
    """
    Run a TQL query as a job. This function blocks
    until the job stops running.

    Parameters
    ----------
    queries : str
      One TQL query string.
    optlevel : int
      The optimization level values are:
        - 0: No optimization.
        - 1: General optimization.
        - 2: WHERE-clause optimization.

      Optional. Default=None, which implies a value of '2'.
    timeout : int
      Maximum number of seconds that the query should take before being
      automatically canceled.
      Optional. Default=None where an infinite value is assumed.

    Returns
    -------
    Job
      A Job object for the query.

    Raises
    -------
    XgtError
      If the query is not a string (str) or the query text is
      larger than 209,000 characters.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges ...
    >>> job = conn.run_job('MATCH (a:Employee) RETURN a.PersonID INTO Result1')
    >>> print(job)
    id:20, status:completed

    >>> conn.run_job('MATCH (a) RETURN a.id INTO Result1')
    ...
    xgt.common.XgtError: Failed jobs:
    id: 22
    error:
    VertexFrameManager: No object registered with this ObjectID 18446744073709551615

    """
    job = self.schedule_job(query, optlevel)
    return  self.wait_for_job(job, timeout)

  def schedule_job(self, query, optlevel=None):
    """
    Schedule a TQL query as a job. This function
    returns immediately after scheduling the job.

    Parameters
    ----------
    query : str
      One TQL query string.
    optlevel : int
      The optimization level values are:
        - 0: No optimization.
        - 1: General optimization.
        - 2: WHERE-clause optimization.


    Returns
    -------
    Job
      A Job object representing the job that has been scheduled.

    Raises
    -------
    XgtError
      If the query is not a string (str) or the query text is
      larger than 209,000 characters.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges ...
    >>> query = 'MATCH (a:Employee) RETURN a.PersonID INTO Result1'
    >>> job = conn.schedule_job(query)
    >>> print(job)
    id:25, status:scheduled

    """
    if not isinstance(query, six.string_types):
      raise TypeError(
          "Unexpected argument type '" + _to_unicode(type(query)) + "'")
    if optlevel is None:
      optlevel = self.current_opt_level
    elif _validate_opt_level(optlevel):
      pass

    request = job_proto.ScheduleJobsCypherRequest()
    request.cypher_query.extend([query])
    request.optimization_level = optlevel
    response = self.call(request, self._job_svc.ScheduleJobsCypher)
    one_job = response.job_status[0]
    return Job(self, one_job.job_id)

  def wait_for_job(self, job, timeout=None):
    """
    Wait for a job. This function blocks until the job stops running.

    Parameters
    ----------
    job : Job, int
      A Job object or an integer job id.
    timeout : int
      Number of seconds each job is allowed to execute before being
      automatically cancelled.
      Optional. Default=None (no timeout).

    Returns
    -------
    Job
      A Job object representing the state of the job on the server.

    Raises
    -------
    XgtError
      If the query is not a string (str) or the query text is
      larger than 209,000 characters.
      If one or more query jobs failed.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges ...
    >>> qr1 = 'MATCH (a:Employee) RETURN a.PersonID INTO Result1'
    >>> jb1 = conn.schedule_job(qr1)
    >>> qr2 = 'MATCH (b:Employee) RETURN b.PersonID INTO Result2'
    >>> jb2 = conn.schedule_job(qr2)
    >>> jb1 = conn.wait_for_job(jb1)
    >>> print(jb1)
    id:31, status:completed
    >>> jb2 = conn.wait_for_job(jb2)
    >>> print(jb2)
    id:32, status:completed

    """
    if isinstance(job, Job):
      jobid = job.id
    elif isinstance(job, six.integer_types):
      jobid = job
    else:
      raise TypeError("Job must be a Job object or an int.")
    begin = datetime.utcnow()
    endtime = self._calculate_endtime(begin, timeout)
    check_interval_sec = 0.1
    loop = True
    while True:
      status = ''
      request = job_proto.GetJobsRequest()
      request.job_id.extend([jobid])
      response = self.call(request, self._job_svc.GetJobs)
      job = response.job_status[0]  # Retrieve only one job from the list.
      status = job_proto.JobStatusEnum.Name(job.status).lower()
      loop = loop and (status in ['scheduled', 'started', 'running',
                                  'transactionnotstarted',
                                  'transactioncommitting'])
      if not endtime is None:
        end = datetime.utcnow()
        if end >= endtime:
          was_cancelled = self.cancel_job(jobid)
      if not loop:
        break
      time.sleep(check_interval_sec)
      if check_interval_sec < 10.0:
        check_interval_sec = check_interval_sec + 0.1
    job_obj = Job(self, jobid)
    if job_obj.status == 'failed':
      msg = (u'Failed job. id={0} msg="{1}"').format(jobid, job_obj.error)
      raise job_obj.error_type(msg, job_obj.trace)
    return job_obj

  def _calculate_endtime(self, begin, timeout):
    endtime = None
    if not timeout is None:
      try:
        endtime = begin + timedelta(seconds=timeout)
      except TypeError:
        msg = ('Expected an int value for “timeout” argument, ' +
               'not "{0}"').format(_to_unicode(timeout))
        raise TypeError(msg)
    return endtime
