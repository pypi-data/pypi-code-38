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

import collections
import csv
import json
import math
import sys
import urllib

import grpc
import six

from . import ErrorMessages_pb2 as err_proto
from . import SchemaMessages_pb2 as sch_proto
from . import GraphTypesService_pb2 as graph_proto
from . import GraphTypesService_pb2_grpc as graph_grpc
from . import DataService_pb2 as data_proto
from . import DataService_pb2_grpc as data_grpc
from .common import (_assert_noerrors, _to_bytes, _to_str, _to_unicode,
                     _unicode_to_str, XgtNotImplemented, XgtIOError,
                     MAX_PACKET_SIZE)

class HeaderMode:
  NONE = 'none'
  IGNORE = 'ignore'
  NORMAL = 'normal'
  STRICT = 'strict'

  _all = [NONE,IGNORE,NORMAL,STRICT]

# -----------------------------------------------------------------------------

class TableFrame(object):
  """
  TableFrame object represent a table held on the xGT server; it can be
  used to retrieve information about it and should not be instantiated directly
  by the user. Methods that return this object: `Connection.get_table_frame()`,
  `Connection.get_table_frames()` and `Connection.create_table_frame()`. A table
  may also be created by a MATCH query and may contain query results.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
  name : str
    Name of table.
  schema : list of pairs
    List of pairs associating property names with xGT data types.
  error_frame_name : str
    Name of the frame created to store errors encountered while loading data.
    (internal)

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> ... run query and store results in table01
  >>> t = conn.get_table_frame('table01')
  >>> print(t.name)

  """
  def __init__(self, conn, name, schema, error_frame_name):
    self._conn = conn
    self._name = name
    self._schema = [[c[0], c[1]] for c in schema]
    self._error_frame_name = error_frame_name

  @property
  def name(self):
    """str: Name of the table."""
    return self._name

  def error_frame_name(self):
    """str: Name of the error table this frame will produce on errors."""
    return self._error_frame_name

  @property
  def schema(self):
    """list of lists: Gets the property names and types of the table."""
    return self._schema

  def load(self, paths, headerMode=HeaderMode.NONE):
    """
    Loads data from one or more CSV files specified in the list of paths.
    Each path may have its own protocol as described below.

    Parameters
    ----------
    paths : list
      Paths to the CSV files.

      ==================== =====================================
                      Syntax for one CSV file path
      ----------------------------------------------------------
          Resource type                 Path syntax
      ==================== =====================================
          local to python: '<path to csv file>'
                           'xgt://<path to csv file>'
          xgtd computer:   'xgtd://<path to csv file>'
          AWS s3:          's3://<path to csv file>'
          https site:      'https://<path to csv file>'
          http site:       'http://<path to csv file>'
          ftps server:     'ftps://<path to csv file>'
          ftp server:      'ftp://<path to csv file>'
      ==================== =====================================

    headerMode : str
      Indicates if the files contain headers:
        - HeaderMode.NONE
        - HeaderMode.IGNORE
        - HeaderMode.NORMAL
        - HeaderMode.STRICT

      Optional. Default=HeaderMode.NONE.

    """
    if paths is None:
      raise TypeError('the "paths" parameter is None')
    if headerMode is None:
      raise TypeError('the "headerMode" parameter is None')
    if headerMode not in HeaderMode._all:
      raise TypeError('Invalid header mode: "{0}"'.format(_to_str(headerMode)))
    if not isinstance(paths, (list, tuple, six.string_types)):
      raise TypeError('one or more file paths are expected; the data type of the "paths" parameter is "{0}"'.format(type(paths)))
    client_paths, server_paths, url_paths = _group_paths(paths, True)
    if len(client_paths) == 0 and len(server_paths) == 0 and len(url_paths) == 0:
      raise XgtIOError('no valid paths found: ' + _to_unicode(paths))
    if len(client_paths) > 0:
      self._insert_from_csv(client_paths, headerMode)
    if len(server_paths) > 0:
      self._ingest(server_paths, headerMode)
    if len(url_paths) > 0:
      self._ingest(url_paths, headerMode)

  def save(self, path, offset=0, length=None, headers=False):
    """
    Writes the rows from the frame to a CSV file in the path and the
    computer indicated by the path.

    Parameters
    ----------
    path : str
      Path to the CSV file.

      ==================== =====================================
                      Syntax for one CSV file path
      ----------------------------------------------------------
          Resource type                 Path syntax
      ==================== =====================================
          local to python: '<path to csv file>'
                           'xgt://<path to csv file>'
          xgtd computer:   'xgtd://<path to csv file>'
      ==================== =====================================

    offset : int
      Position (index) of the first row to be retrieved.
      Optional. Default=0.
    length : int
      Maximum number of rows to be retrieved.
      Optional. Default=None.
    headers : boolean
      Indicates if headers should be added.
      Optional. Default=False.

    """
    if path is None:
      raise TypeError('the "paths" parameter is None')
    if not isinstance(path, six.string_types):
      msg = 'a file path is expected; the data type of the "path" ' \
            'parameter is "{0}"'.format(type(path))
      raise TypeError(msg)

    client_paths, server_paths, url_paths = _group_paths(path, False)
    if (len(client_paths) == 0 and len(server_paths) == 0 and
        len(url_paths) == 0):
      raise XgtIOError('no valid paths found: ' + _to_unicode(path))
    if len(client_paths) > 0:
      self._save_to_csv(client_paths[0], offset, length, headers)
    if len(server_paths) > 0:
      self._egest(server_paths[0], headers)

  def _insert_packet_generator(self, data, is_pandas):
    columns = []
    column_types = {}
    for item in self.schema:
      columns.append(item[0])
      column_types[item[0]] = item[1]
    schemasize = len(columns)
    nrow = len(data)
    col_names = '"' + ('","'.join(columns)) + '"'

    tbl = ''
    for i in range(nrow):
      row = ''
      data_row = ''
      if is_pandas:
        length = len(data.columns)
      else:
        length = len(data[i])
      for j in range(length):
        if is_pandas:
          col = data[columns[j]][i]
        else:
          col = data[i][j]
        if j < schemasize:
          col_type = column_types[columns[j]]
          if col is None:
            strcol = ''
          elif isinstance(col, float) and math.isnan(col):
            strcol = ''
          else:
            strcol = _to_unicode(col)
            if isinstance(col, bool):
                strcol = strcol.lower()
            if isinstance(col, six.string_types):
                strcol = '"' + strcol + '"'
          row = row + strcol + ','
        else:
          row = row + _to_unicode(col) + ','
      tbl = tbl + row[:-1] + '\n'
      if len(tbl) >= MAX_PACKET_SIZE:
        request = data_proto.UploadDataRequest()
        request.repository_name = self._name
        request.content_type = data_proto.CSV
        request.header_mode = data_proto.NONE
        request.content = tbl.encode('utf-8')
        request.expected_server_id = self._conn._server_unique_identifier
        yield request
        tbl = ''
    if len(tbl) > 0:
      request = data_proto.UploadDataRequest()
      request.repository_name = self._name
      request.content_type = data_proto.CSV
      request.header_mode = data_proto.NONE
      request.content = tbl.encode('utf-8')
      request.expected_server_id = self._conn._server_unique_identifier
      yield request
      tbl = ''

  def insert(self, data):
    """
    Inserts data rows. The properties of the new data must match the schema
    in both order and type.

    Parameters
    ----------
    data : list or Pandas dataframe
      Data represented by a list of lists of data items or by a
      Pandas Dataframe.

    """
    if data is None:
      return
    if len(data) == 0:
      return

    #---- if user passed in a pandas frame
    is_pandas = False
    try:
      import pandas
      if isinstance(data, pandas.DataFrame):
        is_pandas = True
    except:
      pass

    # Exceptions for iterators get eaten by grpc so we check outside
    # the generator function:
    if not is_pandas:
      if (isinstance(data, six.text_type) or
          not isinstance(data, collections.Iterable)):
        raise TypeError('a list of lists or a Pandas DataFrame is expected')
      for i in range(len(data)):
          if not isinstance(data[i], collections.Iterable):
              msg = 'Row #{0} is not a list. A list of lists ' \
                    'or a Pandas DataFrame is expected'.format(i)
              raise TypeError(msg)

    data_iter = self._insert_packet_generator(data, is_pandas)

    self._conn.call(data_iter, self._conn._data_svc.UploadData)

  def get_data(self, offset=0, length=None):
    """
    Returns frame data starting at a given offset and spanning a given
    length.

    Parameters
    ----------
    offset : int
      Position (index) of the first row to be retrieved.
      Optional. Default=0.
    length : int
      Maximum number of rows to be retrieved starting from the row
      indicated by offset. A value of 'None' means 'all rows' on and
      after the offset.
      Optional. Default=None.

    Returns
    -------
    list of lists

    """
    # Uses json conversion which is slow, res can get huge
    # if the frame data is huge.
    responses = self._get_data(offset=offset, length=length)
    res = ''
    for response in responses:
        _assert_noerrors(response)
        res += response.content.decode('utf-8')
    jsn = self._conn._convert_to_json('[' + res + ']')
    return jsn[1:]

  def get_data_pandas(self, offset=0, length=None):
    """
    Returns a Pandas DataFrame containing frame data starting at a given
    offset and spanning a given length.

    Parameters
    ----------
    offset : int
      Position (index) of the first row to be retrieved.
      Optional. Default=0.
    length : int
      Maximum number of rows to be retrieved starting from the row
      indicated by offset. A value of 'None' means 'all rows' on and
      after the offset.
      Optional. Default=None.

    Returns
    -------
    Pandas DataFrame

    """
    import pandas
    # Uses json conversion which is slow, res can get huge
    # if the frame data is huge.
    responses = self._get_data(offset=offset, length=length)
    res = ''
    for response in responses:
        _assert_noerrors(response)
        res += response.content.decode('utf-8')
    jsn = self._conn._convert_to_json('[' + res + ']')
    return pandas.DataFrame(columns=jsn[0:1][0], data=jsn[1:])

  @property
  def num_rows(self):
    """int: Gets the number of rows of the table."""
    request = graph_proto.GetTableFramesRequest()
    request.name.extend([self._name])
    response = self._conn.call(request, self._conn._graph_svc.GetTableFrames)
    data = response.table_type[0]
    return data.nrows

  def _get_data(self, offset=0, length=None, headers=True,
                content_type=data_proto.JSON):
    if isinstance(offset, six.string_types):
      offset = int(offset)
    if isinstance(length, six.string_types):
      length = int(length)
    if isinstance(offset, int):
      if offset < 0:
        raise ValueError('offset is negative')
    if isinstance(length, int):
      if length < 0:
        raise ValueError('length is negative')

    request = data_proto.DownloadDataRequest()
    request.repository_name = self._name
    if offset is not None:
      request.offset.value = offset
    if length is not None:
      request.length.value = length
    request.with_headers = headers
    request.content_type = content_type
    responses = self._conn.call(request, self._conn._data_svc.DownloadData)
    return responses

  def _create_csv_packet (self, repository_name, data,
                          headerMode=HeaderMode.NONE):
    request = data_proto.UploadDataRequest()
    request.repository_name = repository_name.encode('utf-8')
    request.content = _to_bytes(data)
    request.content_type = data_proto.CSV

    if headerMode == HeaderMode.IGNORE:
      request.header_mode = data_proto.IGNORE_HEADERS
    elif headerMode == HeaderMode.NORMAL:
      request.header_mode = data_proto.NORMAL
    elif headerMode == HeaderMode.STRICT:
      request.header_mode = data_proto.STRICT
    else:
      request.header_mode = data_proto.NONE

    request.expected_server_id = self._conn._server_unique_identifier

    return request

  def _insert_csv_packet_generator(self, paths, headerMode):
    for fpath in paths:
        header = ''
        data = ''
        dsize = 0
        with open(fpath, 'rb') as f:
          line = f.readline()
          while line:
            line = _to_unicode(line)
            lsize = len(line)
            if (dsize + lsize) < MAX_PACKET_SIZE:
              data += line
              dsize += lsize
            else:
              yield self._create_csv_packet(self._name, data, headerMode)
              data = line
              dsize = len(data)
            line = f.readline()
          if data:
            yield self._create_csv_packet(self._name, data, headerMode)

  def _insert_from_csv(self, paths, headerMode=HeaderMode.NONE):
    data_iter = self._insert_csv_packet_generator(paths, headerMode)
    response = self._conn.call(data_iter, self._conn._data_svc.UploadData)

  def _ingest(self, paths, headerMode=HeaderMode.NONE):
    request = data_proto.IngestUriRequest()
    request.repository_name = self._name

    if isinstance(paths, (list, tuple)):
      request.content_uri.extend(paths)
    else:
      request.content_uri.extend([paths])

    if headerMode == HeaderMode.IGNORE:
      request.header_mode = data_proto.IGNORE_HEADERS
    elif headerMode == HeaderMode.NORMAL:
      request.header_mode = data_proto.NORMAL
    elif headerMode == HeaderMode.STRICT:
      request.header_mode = data_proto.STRICT
    else:
      request.header_mode = data_proto.NONE

    if (len(self._conn.aws_access_key_id) > 0 and \
        len(self._conn.aws_secret_access_key) > 0):
      request.authorization = self._conn.aws_access_key_id + ':' + \
                              self._conn.aws_secret_access_key

    response = self._conn.call(request, self._conn._data_svc.IngestUri)

  def _save_to_csv(self, path, offset=0, length=None, headers=False):
    # This will stream the bytes directly which is > 10X faster than using json.
    responses = self._get_data(offset=offset, length=length, headers=headers,
                               content_type=data_proto.CSV)
    with open(path, 'wb') as fobject:
      if headers:
        columns = [i[0] for i in self.schema]
        cnt = 0
        for col in columns:
          if cnt > 0:
            fobject.write(_to_bytes(','))
          cnt += 1
          fobject.write(_to_bytes(col))
        fobject.write('\n')
      # Each packet can be directly written to the file since we have the
      # raw data. This avoids extra conversion issues and extra memory from
      # json.
      for response in responses:
          _assert_noerrors(response)
          fobject.write(response.content)
    fobject.close()

  def _egest(self, path, headers=False):
    request = data_proto.EgestUriRequest()
    request.repository_name = self._name
    request.content_uri = path
    request.with_headers = headers
    response = self._conn.call(request, self._conn._data_svc.EgestUri)

  def __str__(self):
    print_frame = "{'name': '" + self.name + "'" + \
                  ", 'schema': " + _to_unicode(self.schema) + "}"
    return _unicode_to_str(print_frame)

# -----------------------------------------------------------------------------

class VertexFrame(TableFrame):
  """
  VertexFrame object represents a collection of vertices held on the xGT
  server; it can be used to retrieve information about them and should not be
  instantiated directly by the user. Methods that return this object:
  `Connection.get_vertex_frame()`, `Connection.get_vertex_frames()` and
  `Connection.create_vertex_frame()`.

  Each vertex in a VertexFrame shares the same properties,
  described in `VertexFrame.schema`. Each vertex in a VertexFrame
  is uniquely identified by the property listed in `VertexFrame.key`.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
  name : str
    Name of vertex frame.
  schema : list of pairs
    List of pairs associating property names with xGT data types.
    Each vertex in the VertexFrame will have these properties.
  key : str
    The property name used to uniquely identify vertices in the graph.
    This is the name of one of the properties from the schema and
    must be unique for each vertex in the frame.
  error_frame_name : str
    Name of the frame created to store errors encountered while loading data.
    (internal)

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> v1 = conn.create_vertex_frame(
  ...        name = 'Person',
  ...        schema = [['id', xgt.INT],
  ...                  ['name', xgt.TEXT]],
  ...        key = 'id')
  >>> v2 = conn.get_vertex_frame('Company') #Company is an existing vertex frame
  >>> print(v1.name)

  """
  def __init__(self, conn, name, schema, key, error_frame_name):
    super(VertexFrame, self).__init__(conn, name, schema, error_frame_name)
    self._key = key

  @property
  def key(self):
    """str: Gets the property name that uniquely identifies vertices of this type."""
    return self._key

  @property
  def num_vertices(self):
    """int: Gets the number of vertices in the VertexFrame."""
    request = graph_proto.GetVertexFramesRequest()
    request.name.extend([self._name])
    response = self._conn.call(request, self._conn._graph_svc.GetVertexFrames)
    data = response.vertex_type[0]
    return data.nvertices

  # Override num_rows
  num_rows = num_vertices

  def __str__(self):
    print_frame = ("{'name': '" + self.name + "'" +
                   ", 'schema': " + _to_unicode(self.schema) +
                   ", 'key': '" + self.key + "'}")
    return _unicode_to_str(print_frame)

# -----------------------------------------------------------------------------

class EdgeFrame(TableFrame):
  """
  EdgeFrame object represents a collection of edges held on the xGT server;
  it can be used to retrieve information about them and should not be
  instantiated directly by the user. Methods that return this object:
  `Connection.get_edge_frame()`, `Connection.get_edge_frames()` and
  `Connection.create_edge_frame()`. Each edge in an EdgeFrame shares the same
  properties, described in `EdgeFrame.schema`.

  The source vertex of each edge in an EdgeFrame must belong to the same
  VertexFrame. This name of this VertexFrame is given by `EdgeFrame.source_name`.
  The targe vertex of each edge in an EdgeFrame must belong to the same
  VertexFrame. This name of this VertexFrame is given by `EdgeFrame.target_name`.

  For each edge in the EdgeFrame, its source vertex is identified by
  the edge property name given by `EdgeFrame.source_key`, which is
  be one of the properties listed in the schema. The edge target vertex
  is identified by the property name given by `EdgeFrame.target_key`.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
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
  error_frame_name : str
    Name of the frame created to store errors encountered while loading data.
    (internal)

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> e1 = conn.create_edge_frame(
  ...        name = 'WorksFor',
  ...        schema = [['srcid', xgt.INT],
  ...                  ['role', xgt.TEXT],
  ...                  ['trgid', xgt.INT]],
  ...        source = 'Person',
  ...        target = 'Company',
  ...        source_key = 'srcid',
  ...        target_key = 'trgid')
  >>> e2 = conn.get_edge_frame('RelatedTo') #RelatedTo is an existing edge frame
  >>> print(e1.name)

  """
  def __init__(self, conn, name, schema, source, target, source_key, target_key, error_frame_name):
    super(EdgeFrame, self).__init__(conn, name, schema, error_frame_name)
    self._source_name = source
    self._target_name = target
    self._source_key = source_key
    self._target_key = target_key

  @property
  def source_name(self):
    """str: Gets the name of the source vertex frame."""
    return self._source_name

  @property
  def target_name(self):
    """str: Gets the name of the target vertex frame."""
    return self._target_name

  @property
  def source_key(self):
    """str: The edge property name that identifies the source vertex of an edge."""
    return self._source_key

  @property
  def target_key(self):
    """str: The edge property name that identifies the target vertex of an edge."""
    return self._target_key

  @property
  def num_edges(self):
    """int: Gets the number of edges of the edge frame."""
    request = graph_proto.GetEdgeFramesRequest()
    request.name.extend([self._name])
    response = self._conn.call(request, self._conn._graph_svc.GetEdgeFrames)
    data = response.edge_type[0]
    return data.nedges

  # Override num_rows
  num_rows = num_edges

  def __str__(self):
    print_frame = ("{'name': '" + self.name + "'" +
                   ", 'source': '" + self.source_name + "'" +
                   ", 'target': '" + self.target_name + "'" +
                   ", 'schema': " + _to_unicode(self.schema) +
                   ", 'source_key': '" + self.source_key + "'" +
                   ", 'target_key': '" + self.target_key + "'}")
    return _unicode_to_str(print_frame)

# -----------------------------------------------------------------------------

def _group_paths(paths, for_ingest):
  client_prefix = 'xgt://'
  server_prefix = 'xgtd://'
  url_prefixes = ['s3://', 'https://', 'http://', 'ftps://', 'ftp://']
  client_paths = []
  server_paths = []
  url_paths = []
  if isinstance(paths, six.string_types):
    paths = [paths]
  elif not isinstance(paths, (list, tuple)):
    return client_paths, server_paths, url_paths
  for one_path in paths:
    if one_path == "":
      raise ValueError('one or more "paths" are empty')
    if one_path.startswith(client_prefix):
      _validate_client_path(one_path)
      client_paths.append(one_path[len(client_prefix):])
    elif one_path.startswith(server_prefix):
      server_paths.append(one_path[len(server_prefix):])
    elif any(map(lambda p: one_path.startswith(p), url_prefixes)):
      for url_prefix in url_prefixes:
        if for_ingest == False:
          msg = 'Url paths are invalid for data writing ' \
                '"{0}".'.format(one_path)
          raise XgtNotImplemented(msg)
        if one_path.startswith(url_prefix):
          url_paths.append(one_path)
          break
    else:
      if '://' in one_path:
        msg = 'Unsupported url protocol in path "{0}".'.format(one_path)
        raise XgtNotImplemented(msg)
      _validate_client_path(one_path)
      client_paths.append(one_path)
  return client_paths, server_paths, url_paths

def _validate_client_path(one_path):
  if one_path.endswith('.gz') or one_path.endswith('.bz2'):
    msg = 'Loading compressed files from a local filesystem is ' \
          'not supported: {0}'.format(one_path)
    raise XgtNotImplemented(msg)
