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

"""
The Python interface to the Trovares xGT graph analytics engine.

Main Features
-------------

**Data loading**

xGT is a strongly-typed graph system. Loading data is a two-step process:

1. Describe the structure and data types of your graph.

  Define the vertex and edge frame structure with `Connection.create_vertex_frame()`
  and `Connection.create_edge_frame()`. Once the type structure is set,
  `VertexFrame` and `EdgeFrame` objects provide access to the server-side
  structures.

2. Load your edge and vertex data.
    
  The `VertexFrame` and `EdgeFrame` objcts provide high-performance,
  parallel `load()` methods to ingest data as well as a direct `insert()` method
  to add small amounts of data piecewise.

**Query processing**

Queries are expressed as strings written in `TQL <http://docs.trovares.com/learn/tql_intro/index.html>`_.

>>> query = '''
      MATCH  (emp:Employee)-[edge1:ReportsTo]->(boss:Employee)
      RETURN emp.PersonID AS EmployeeID,
             boss.PersonID AS BossID
      INTO   ResultTable
      '''

A query runs in the context of a `Job`, which can be run, scheduled and
canceled. The `run_job()` method runs the query and blocks until it finishes
successfully, terminates by an error, or it's canceled.


Example
-------
The following Python script shows some of the functions that can be used to
create a graph, load data into it, run a query and access the results, and
finally remove that graph from the system. ::

  import xgt

  #-- Connect to xgtd --
  conn = xgt.Connection()

  #-- Define and create the graph --
  emp = conn.create_vertex_frame(
          name = 'Employee',
          schema = [['PersonID', xgt.INT],
                    ['Name', xgt.TEXT],
                    ['PostalCode', xgt.INT]],
          key = 'PersonID')

  rep = conn.create_edge_frame(
          name = 'ReportsTo',
          schema = [['EmpID', xgt.INT],
                    ['BossID', xgt.INT],
                    ['StartDate', xgt.DATE],
                    ['EndDate', xgt.DATE]],
          source = 'Employee',
          target = 'Employee',
          source_key = 'EmpID',
          target_key = 'BossID')

  #-- Load data to the graph in xgtd --
  # Use the insert() method for data of a few hundred rows or less;
  # for bigger amounts of data, use the load() method with csv files.
  emp.insert(
    [[111111101, 'Manny', 98103],
     [111111102, 'Trish', 98108],
     [911111501, 'Frank', 98101],
     [911111502, 'Alice', 98102]
    ])
  rep.insert(
    [[111111101, 911111501, '2015-01-03', '2017-04-14'],
     [111111102, 911111501, '2016-04-02', '2017-04-14'],
     [911111502, 911111501, '2016-07-07', '2017-04-14'],
     [111111101, 911111502, '2017-04-15', '3000-12-31'],
     [111111102, 911111502, '2017-04-15', '3000-12-31'],
     [911111501, 911111502, '2017-04-15', '3000-12-31']
    ])

  #-- Query data --
  conn.drop_frame('Result1')
  cmd = '''
    MATCH
      (emp:Employee)-[edge1:ReportsTo]->
      (boss:Employee)-[edge2:ReportsTo]->
      (emp)
    WHERE
      edge1.EndDate <= edge2.StartDate
    RETURN
      emp.PersonID AS Employee1ID,
      boss.PersonID AS Employee2ID,
      edge1.StartDate AS FirstStart,
      edge1.EndDate AS FirstEnd,
      edge2.EndDate AS SecondEnd,
      edge2.StartDate AS SecondStart
    INTO
      Result1
    '''
  conn.run_job(cmd)

  #-- Results extraction --
  ncols = len(emp.schema)
  nrows = emp.num_vertices
  print('Employee columns: {0} rows: {1} '.format(ncols, nrows))

  ncols = len(rep.schema)
  nrows = rep.num_edges
  print('ReportsTo columns: {0} rows: {1} '.format(ncols, nrows))

  r1 = conn.get_table_frame('Result1')
  ncols = (r1.schema)
  nrows = r1.num_rows
  print('Result columns: {0} rows: {1} '.format(ncols, nrows))
  print('')

  print('--- Result1 ---')
  r1dat = r1.get_data(0, 100)
  for row in r1dat:
    print(', '.join([str(c) for c in row]))
  print('')

  #-- Drop all objects --
  conn.drop_frame('ReportsTo')
  conn.drop_frame('Employee')
  conn.drop_frame('Result1')
"""

__all__ = [
  'BOOLEAN', 'INT', 'FLOAT', 'DATE', 'TIME', 'DATETIME', 'IPADDRESS', 'TEXT',
  'DEFAULT_OPT_LEVEL',
  'XgtError', 'XgtNotImplemented', 'XgtInternalError',
  'XgtIOError', 'XgtServerMemoryError', 'XgtConnectionError',
  'XgtSyntaxError', 'XgtTypeError', 'XgtValueError', 'XgtNameError',
  'XgtArithmeticError', 'XgtFrameDependencyError', 'XgtTransactionError',
  'Job', 'Connection',
  'VertexFrame', 'EdgeFrame', 'TableFrame']

################################################################################
# GRPC PRELIMINARIES
#
# gRPC has several problems with forking. Some of these are fixed in later
# versions of the library, some are still problematic. These are workarounds.

# First, gRPC in Python 2.7.5 is known to exhibit a fork bug. This seems to
# have been fixed by 2.7.10, but the intervening versions have not been tested.
# As such, we officially support only 2.7.10+.
import sys
import warnings
version_major = sys.version_info[0]
version_minor = sys.version_info[1]
version_micro = sys.version_info[2]
if ((version_major==2 and version_minor<=6) or
    (version_major==2 and version_minor==7 and version_micro<10)):
  warnings.simplefilter('module', DeprecationWarning)
  warnings.warn('xgt uses gRPC, which is known to deadlock under old versions of Python 2.7 in the presence of multiprocessing. Please either use a newer version of Python (2.7.10+) or use Python 3.', DeprecationWarning)

# Second, the "fix" for the fork bug requires that the GRPC_ENABLE_FORK_SUPPORT
# environment variable needs to be set. The grpc version must be 1.15 or later.
# See here: https://groups.google.com/forum/#!topic/grpc-io/1ABEo5e-HsU.
import os
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "1"


from .common import (
  BOOLEAN, INT, FLOAT, DATE, TIME, DATETIME, IPADDRESS, TEXT, DEFAULT_OPT_LEVEL,
  XgtError, XgtNotImplemented, XgtInternalError,
  XgtIOError, XgtServerMemoryError, XgtConnectionError,
  XgtSyntaxError, XgtTypeError, XgtValueError, XgtNameError,
  XgtArithmeticError, XgtFrameDependencyError, XgtTransactionError,
  Job
)
from .connection import Connection
from .graph import HeaderMode, VertexFrame, EdgeFrame, TableFrame

from xgt.ErrorMessages_pb2 import (
  ErrorCodeEnum
)

from xgt.JobService_pb2 import (
  JobStatusEnum
)

from .version import __version__

import warnings
warnings.filterwarnings(action='ignore', message='numpy.dtype size changed')
warnings.filterwarnings(action='ignore', message='numpy.ufunc size changed')
