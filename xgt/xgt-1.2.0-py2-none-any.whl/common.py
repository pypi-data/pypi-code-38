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

import datetime as dt
import json
import logging
import math
import re
import sys

import grpc
import six

from . import ErrorMessages_pb2 as err_proto
from . import SchemaMessages_pb2 as sch_proto
from . import AdminService_pb2 as admin_proto
from . import AdminService_pb2_grpc as admin_grpc
from . import JobService_pb2 as job_proto
from . import JobService_pb2_grpc as job_grpc
from . import GraphTypesService_pb2 as graptype_proto
from . import GraphTypesService_pb2_grpc as graptype_grpc

log = logging.getLogger(__name__)

BOOLEAN = 'boolean'
INT = 'int'
FLOAT = 'float'
DATE = 'date'
TIME = 'time'
DATETIME = 'datetime'
IPADDRESS = 'ipaddress'
TEXT = 'text'

DEFAULT_OPT_LEVEL = 2
# Send in 2MB chunks (grpc recommends 16-64 KB, but this got the best perf locally)
# FYI: by default grpc only supports up to 4MB.
MAX_PACKET_SIZE = 2097152

class XgtError(Exception):
  """
  Base exception class from which all other xgt exceptions inherit. It is
  raised in error cases that don't have a specific xgt exception type.
  """
  def __init__(self, msg, trace=''):
    if six.PY2:
      if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
      if isinstance(trace, unicode):
        trace = trace.encode('utf-8')
    self.msg = msg
    self.trace = trace

    if log.getEffectiveLevel() >= logging.DEBUG:
      if self.trace != '':
        log.debug(self.trace)
      else:
        log.debug(self.msg)
    Exception.__init__(self, self.msg)

class XgtNotImplemented(XgtError):
  """Raised for functionality with pending implementation."""
class XgtInternalError(XgtError):
  """
  Intended for internal server purposes only. This exception should not become
  visible to the user.
  """
class XgtIOError(XgtError):
  """An I/O problem occured either on the client or server side."""
class XgtServerMemoryError(XgtError):
  """
  The server memory usage is close to or at capacity and work could be lost.
  """
class XgtConnectionError(XgtError):
  """
  The client cannot properly connect to the server. This can include a failure
  to connect due to an xgt module version error.
  """
class XgtSyntaxError(XgtError):
  """A query was provided with incorrect syntax."""
class XgtTypeError(XgtError):
  """
  An unexpected type was supplied.

  For queries, an invalid data type was used either as an entity or as a
  property. For frames, either an edge, vertex or table frames was expected
  but the wrong frame type or some other data type was provided. For
  properties, the property declaration establishes the expected data type. A
  type error is raise if the data type used is not appropriate.
  """
class XgtValueError(XgtError):
  """An invalid or unexpected value was provided."""
class XgtNameError(XgtError):
  """
  An unexpected name was provided. Typically can occur during object retrieval
  where the object name was not found.
  """
class XgtArithmeticError(XgtError):
  """An invalid arithmetic calculation was detected and cannot be handled."""
class XgtFrameDependencyError(XgtError):
  """
  The requested action will produce an invalid graph or break a valid graph.
  """
class XgtTransactionError(XgtError):
  """A Transaction was attempted but didn't complete."""

class Job(object):
  """
  Represents a user-scheduled Job.

  An instance of this object is created by job-scheduling functions like
  `xgt.Connection.run_job` and `xgt.Connection.schedule_job`.

  A `Job` is used as a proxy for a job in the server and allows the user
  to monitor its execution, possibly cancel it, and learn about its status
  during and after execution.

  """
  def __init__(self, conn, job_id):
    self._conn = conn
    self._id = job_id

  def _get_job_data(self):
    request = job_proto.GetJobsRequest()
    request.job_id.extend([self._id])
    response = self._conn.call(request, self._conn._job_svc.GetJobs)
    job = response.job_status[0]  # Retrieve only one job from the list.
    job_data = {
      'jobid': job.job_id,
      'status': job_proto.JobStatusEnum.Name(job.status).lower(),
      'start_time': job.start_time.ToDatetime().isoformat(),
      'end_time': job.end_time.ToDatetime().isoformat(),
      'error_type': None }
    if job.error:
      if len(job.error) > 0:
        error_code_name = err_proto.ErrorCodeEnum.Name(job.error[0].code)
        job_data['error_type'] = _code_error_map[error_code_name]
        job_data['error'] = ', '.join([e.message for e in job.error])
        job_data['trace'] = ', '.join([e.detail for e in job.error])

    if log.getEffectiveLevel() >= logging.DEBUG:
      job_id = job_data['jobid']
      job_status = job_data['status']
      if 'error' in job_data:
        error = job_data['error']
      else:
        error = ''
      if 'trace' in job_data:
        trace = job_data['trace']
      else:
        trace = ''
      msg = u'Job: {0} Status: {1}'.format(_to_unicode(job_id),
                                          job_status)
      if error != '':
        msg = msg + "\nError: \n" + error
      if trace != '':
        msg = msg + "\nTrace: \n" + trace
      log.debug(msg)

    return job_data

  @property
  def id(self):
    """
    int: Identifier of the job.

    A 64-bit integer value that uniquely identifies a job. It is
    automatically incremented for each scheduled job over the lifetime of
    the `xgtd` server process.

    """
    return self._id

  @property
  def status(self):
    """
    str: Status of the job.

        ============  ===============================================
        Job status
        -------------------------------------------------------------
           Status                       Description
        ============  ===============================================
           scheduled  The state after the job has been created, but
                      before it has started running.
             running  The job is being executed.
           completed  The job finished successfully.
            canceled  The job was canceled.
              failed  The job failed. When the job fails the `error`
                      and `trace` properties are populated.
        ============  ===============================================

    """
    data = self._get_job_data()
    if 'status' in data:
      return _to_unicode(data['status'])
    else:
      return ''

  @property
  def start_time(self):
    """
    str: Date and time when the job was scheduled.

    This is a formatted string that has a resolution of seconds.
    """
    data = self._get_job_data()
    if 'start_time' in data:
      return dt.datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M:%S')
    else:
      return ''

  @property
  def end_time(self):
    """
    str: Date and time when the job finished running.

    This is a formatted string that has a resolution of seconds.
    """
    data = self._get_job_data()
    if 'end_time' in data:
      return dt.datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M:%S')
    else:
      return ''

  @property
  def error_type(self):
    """
    object: Class that belongs to the XgtError hierarchy that corresponds to
            the original exception type thrown and caused the Job to fail.
    """
    data = self._get_job_data()
    if 'error_type' in data:
      return data['error_type']
    else:
      return XgtError

  @property
  def error(self):
    """
    str: User-friendly error message describing the reason a job failed.
    """
    data = self._get_job_data()
    if 'error' in data:
      return _to_unicode(data['error'])
    else:
      return ''

  @property
  def trace(self):
    """
    str: Very detailed error message for a failed job.

    This error message contains the friendly error message and a stack
    strace for the code that participated in the error.
    """
    data = self._get_job_data()
    if 'trace' in data:
      return _to_unicode(data['trace'])
    else:
      return ''

  def __str__(self):
    txt = (u'id:{0}, status:{1}').format(self.id, self.status)
    if len(self.error) > 0:
      txt = txt + (u', nerror:{0}').format(self.error)
    return _unicode_to_str(txt)

# Validation support functions

def _validated_schema(obj):
  '''Takes a user-supplied object and returns a valid schema.

  Users can supply a variety of objects as valid schemas. To simplify internal
  processing, we canonicalize these into a list of string-type pairs,
  performing validation along the way.
  '''
  # Validate the shape first
  try:
    if len(obj) < 1:
      raise XgtTypeError('A schema must not be empty.')
    for pairlike in obj:
      assert len(pairlike) == 2
  except:
    raise XgtTypeError('A schema must be a non-empty list of (property, type) pairs.')
  # Looks good. Return a canonical schema.
  return [(_validated_property_name(name), _validated_property_type(xgt_type))
          for name,xgt_type in obj]

def _validated_frame_name(obj):
  '''Takes a user-supplied object and returns a unicode frame name string.'''
  name = _as_unicode(obj)
  if len(name) < 1:
    raise XgtValueError('Frame names cannot be empty.')
  if u'.' in name:
    raise XgtValueError('Frame names cannot contain periods: '+name)
  return name

def _validated_property_name(obj):
  '''Takes a user-supplied object and returns a unicode proprty name string.'''
  name = _as_unicode(obj)
  return name

def _validated_property_type(obj):
  '''Takes a user-supplied object and returns an xGT schema type.'''
  prop_type = _as_unicode(obj)
  valid_prop_types = [BOOLEAN, INT, FLOAT, DATE, TIME, DATETIME, IPADDRESS, TEXT]
  if prop_type.lower() not in valid_prop_types:
    raise XgtTypeError('Invalid property type "'+prop_type+'"')
  return prop_type.upper()

def _validate_opt_level(optlevel):
  """
  Valid optimization level values are:
    - 0: No optimization.
    - 1: General optimization.
    - 2: WHERE-clause optimization.
    - 3: Degree-cycle optimization.
  """
  if isinstance(optlevel, int):
    if optlevel not in [0, 1, 2, 3]:
      raise XgtValueError("Invalid optlevel '" + str(optlevel) +"'")
  else:
    raise XgtTypeError("optlevel must be an integer")
  return True

def _assert_noerrors(response):
  if len(response.error) > 0:
    error = response.error[0]
    try:
      error_code_name = err_proto.ErrorCodeEnum.Name(error.code)
      error_class = _code_error_map[error_code_name]
      raise error_class(error.message, error.detail)
    except XgtError:
      raise
    except Exception as ex:
      raise XgtError("Error detected while raising exception" +
                     _to_unicode(ex), _to_unicode(ex))

def _assert_isstring(name, text):
  if not isinstance(text, six.string_types):
    msg = name + " is not a string: '" + _to_unicode(text) + "'"
    raise TypeError(msg)

def _obj_to_str(obj, level=0):
  ret = ''
  if isinstance(obj, (str, six.text_type)):
    ret = ret + six.text_type(obj)
  elif isinstance(obj, list):
    ret = ret + _list_to_str(obj, level)
  elif isinstance(obj, dict):
    ret = ret + _dict_to_str(obj, level)
  else:
    ret = ret + '\n' + json.dumps(obj, indent=4, sort_keys=True)
  return ret

def _dict_to_str(obj, level):
  ret = ''
  indent = '\n' + '    ' * level
  for k in list(obj):
    ret = ret + indent + six.text_type(k) + ': '
    ret = ret + _obj_to_str(obj[k], level+1)
  return ret

def _list_to_str(obj, level):
  ret = ''
  indent = '\n' + '    ' * level
  for i in obj:
    ret = ret + indent + _obj_to_str(i, level+1)
  return ret

# Unicode support functions.

# Why the two functions _to_* and _as_*? There are two general cases when you
# want to convert something to a certain type of string. The first case is if
# you are creating a string that will be handed to a user. Exceptions and log
# messages fall into this category. In this case, you really want a
# *constructor*, turning any object into some type of string, even if it
# doesn't natively contain character data. The second case is when you want to
# collapse unicode and byte data into one or the other. This includes most xGT
# operations, referencing frames or properties, for instance. In this case, if
# the method is passed some other type (maybe an int or class instance), you
# want an exception to be thrown.
#
# So, to summarize:
#   _to_unicode( u'xyzzy' ) => u'xyzzy'
#   _to_unicode( b'xyzzy' ) => u'xyzzy'
#   _to_unicode( 12345.67 ) => u'12345.67'
#
#   _as_unicode( u'xyzzy' ) => u'xyzzy'
#   _as_unicode( b'xyzzy' ) => u'xyzzy'
#   _as_unicode( 12345.67 ) => TypeError
#
# _to_bytes/_as_bytes and _to_str work similarly (_as_str is not provided, as
# it would effectively be the same as the str() built-in).

def _unicode_to_str(text):
  if six.PY2 and isinstance(text, unicode):
    return text.encode('utf-8')
  else:
    return text

def _to_unicode(value):
  '''Constructs a unicode string out of any object.'''
  if isinstance(value, six.text_type):
    return value
  elif isinstance(value, six.binary_type):
    return value.decode('utf-8')
  else:
    return six.text_type(value)

def _as_unicode(value):
  '''Converts unicode or binary strings to unicode. Other types raise a TypeError.'''
  if isinstance(value, six.text_type):
    return value
  elif isinstance(value, six.binary_type):
    return value.decode('utf-8')
  raise TypeError('Cannot convert '+six.text_type(type(value))+' to unicode.')

def _to_bytes(value):
  '''Constructs a human-readable byte string out of any object.'''
  if isinstance(value, six.text_type):
    return value.encode('utf-8')
  elif isinstance(value, six.binary_type):
    return value
  else:
    return six.text_type(value).encode('utf-8')

def _as_bytes(value):
  '''Converts unicode or binary strings to bytes. Other types raise a TypeError.'''
  if isinstance(value, six.text_type):
    return value.encode('utf-8')
  elif isinstance(value, six.binary_type):
    return value
  raise TypeError('Cannot convert '+six.text_type(type(value))+' to bytes.')

def _to_str(value):
  '''Constructs a str out of any object.'''
  # We can't use the str built-in as a constructor because Python 2 believes
  # that unicode characters cannot be converted to str types. We want to.
  if isinstance(value, str):
    return value
  elif six.PY2 and isinstance(value, unicode):
    return value.encode('utf-8')
  elif six.PY3 and isinstance(value, bytes):
    return value.decode('utf-8')
  else:
    return str(value)

_code_error_map = {
  'GENERIC_ERROR': XgtError,
  'NOT_IMPLEMENTED': XgtNotImplemented,
  'INTERNAL_ERROR': XgtInternalError,
  'IO_ERROR': XgtIOError,
  'SERVER_MEMORY_ERROR': XgtServerMemoryError,
  'CONNECTION_ERROR': XgtConnectionError,
  'SYNTAX_ERROR': XgtSyntaxError,
  'TYPE_ERROR': XgtTypeError,
  'VALUE_ERROR': XgtValueError,
  'NAME_ERROR': XgtNameError,
  'ARITHMETIC_ERROR': XgtArithmeticError,
  'FRAME_DEPENDENCY_ERROR': XgtFrameDependencyError,
  'TRANSACTION_ERROR': XgtTransactionError,
}
