import requests
import statistics as stats
import sys
import time
import traceback
from requests.exceptions import ConnectTimeout, ReadTimeout, Timeout
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from lura import logs
from lura.formats import yaml
from lura.attrs import attr, ottr
from lura.threads import pool
from lura.utils import common

log = logs.get_logger(__name__)

class Base(ottr):

  def __init__(self):
    super().__init__()

  def format(self, prefix=''):
    name = type(self).__name__.lower()
    text = yaml.dumps({name: self})
    if not prefix:
      return text
    res = os.linesep.join(
      f'{prefix}{line}' for line in text.rstrip(os.linesep).splitlines()
    )
    print(repr(res))
    return res

  def print(self, prefix='', *args, **kwargs):
    print(self.format(prefix), *args, **kwargs)

class Request(Base):

  def __init__(self, endpoint, type, headers, data):
    super().__init__()
    self.endpoint = endpoint
    self.type = type
    self.headers = headers
    self.data = data

class Response(Base):

  def __init__(self, headers, code, text, exc_info, start, end):
    super().__init__()
    self.headers = headers
    self.code = code
    self.text = text
    self.exc_info = exc_info
    if exc_info is not None:
      exc_info = ottr(
        type = '{}.{}'.format(exc_info[0].__module__, exc_info[0].__name__),
        value = repr(exc_info[1]),
        traceback = ''.join(traceback.format_exception(*exc_info)),
      )
    self.exc_info = exc_info
    self.start = start
    self.end = end

class Result(Base):

  def __init__(self, id, request, response, start, end):
    super().__init__()
    self.id = id
    self.request = request
    self.response = response
    self.start = start
    self.end = end

class ResultSet(Base):

  def __init__(self, results, start, end):
    super().__init__()
    self.results = results
    self.start = start
    self.end = end

class ConCurl:

  def __init__(
    self,
    endpoint,
    request_type,
    request_headers = None,
    data = None,
    thread_count = None,
    request_count = None,
    response_timeout = None,
    print_dots = None,
  ):
    super().__init__()
    self.endpoint = endpoint
    self.request_type = request_type
    if request_headers is not None:
      request_headers = self.parse_request_headers(request_headers)
    self.request_headers = request_headers
    self.data = data
    self.thread_count = 1 if thread_count is None else thread_count
    self.request_count = 10 if request_count is None else request_count
    self.response_timeout = 5 if response_timeout is None else response_timeout
    self.print_dots = True if print_dots is None else print_dots
    self.column = 0

  def parse_request_headers(self, request_headers):
    if isinstance(request_headers, Mapping):
      return request_headers
    elif isinstance(request_headers, Sequence):
      return dict((header.split(': ', 1) for header in request_headers))
    else:
      raise ValueError(f'Type not supported: {request_headers}')

  def build_request_endpoint(self, *args, **kwargs):
    return self.endpoint

  def build_request_type(self, *args, **kwargs):
    return self.request_type

  def build_request_headers(self, *args, **kwargs):
    return self.request_headers

  def build_request_data(self, *args, **kwargs):
    return self.data

  def build_request(self, id):
    endpoint = self.build_request_endpoint(id=id)
    type = self.build_request_type(id=id, endpoint=endpoint)
    headers = self.build_request_headers(id=id, endpoint=endpoint, type=type)
    data = self.build_request_data(
      id=id, endpoint=endpoint, type=type, headers=headers)
    return self.Request(endpoint, type, headers, data)

  def build_requests(self):
    return ((id, self.build_request(id)) for id in range(self.request_count))

  def build_request_call_args(self, request):
    args = (request.endpoint,)
    kwargs = dict(
      headers = request.headers,
      timeout = self.response_timeout,
      data = request.data
    )
    return args, kwargs

  def print_dot(self, code, exc):
    if not self.print_dots:
      return
    if code == 200 and exc is None:
      c = '.'
    elif code != 200 and exc is None:
      c = '!'
    elif isinstance(exc, ConnectTimeout):
      c = 'c'
    elif isinstance(exc, ReadTimeout):
      c = 'r'
    elif isinstance(exc, Timeout):
      c = 't'
    elif exc:
      c = 'x'
    else:
      c = '?'
    endl = ''
    self.column += 1
    if self.column == 80:
      endl = os.linesep
      self.column = 0
    print(c, end=endl, flush=True)

  def request(self, request):
    headers = code = text = exc_info = exc = None
    start = time.time()
    end = None
    try:
      action = request.type.lower()
      call = getattr(requests, action)
      args, kwargs = self.build_request_call_args(request)
      log.noise(f'request() {action}(*{args} **{kwargs})')
      response = call(*args, **kwargs)
      end = time.time()
      headers = dict(response.headers)
      code = response.status_code
      text = response.text
    except Exception as _:
      end = time.time() if end is None else end
      exc_info = sys.exc_info()
      exc = _
    self.print_dot(code, exc)
    return self.Response(headers, code, text, exc_info, start, end)

  def test(self, args):
    start = time.time()
    id, request = args
    response = self.request(request)
    return self.Result(id, request, response, start, time.time())

  def handle_results(self, results):
    start, end, results = results.start, results.end, results.results
    args = attr()
    args.start = start
    args.end = end
    args.runtime = end - start
    args.res = results
    args.res_200 = [
      res for res in results
      if res.response.code == 200 and res.response.exc_info is None
    ]
    args.res_not_200 = [
      res for res in results
      if res.response.code != 200 and res.response.exc_info is None
    ]
    args.res_timeouts = [
      res for res in results
      if res.response.exc_info is not None and
        res.response.exc_info.type.endswith('Timeout') # FIXME
    ]
    args.res_exc = [
      res for res in results
      if res.response.exc_info is not None and
        not res.response.exc_info.type.endswith('Timeout') # FIXME
    ]
    args.res_bad = args.res_not_200 + args.res_exc
    args.res_num = len(args.res)
    args.res_num_succeeded = len(args.res_200)
    args.res_num_failed = len(args.res_not_200)
    args.res_num_timeouts = len(args.res_timeouts)
    args.res_num_raised = len(args.res_exc)
    args.res_times = [
      res.response.end - res.response.start for res in args.res_200
    ]
    times = args.times = attr()
    names = ('mean', 'harmonic_mean', 'median')
    if args.res_times:
      times.mean = stats.mean(args.res_times)
      times.median = stats.median(args.res_times)
      times.frequency = common([int(_) for _ in args.res_times])
      times.common = times.frequency[:min(len(times.frequency), 6)]
      times.uncommon = times.frequency[-min(len(times.frequency), 6):]
    else:
      times.mean = 0.0
      times.median = 0.0
      times.frequency = [(0, 0)]
      times.common = [(0, 0)]
      times.uncommon = [(0, 0)]
    return args

  def run(self):
    start = time.time()
    if self.print_dots:
      self.column = 0
      print(
        '.=200 !=Not 200 c/r/t=Connect/Read/Other timeout x=Exception ' + \
        '?=Unknown error')
    thread_count = min(self.thread_count, self.request_count)
    results = pool.map(thread_count, self.test, self.build_requests())
    end = time.time()
    if self.print_dots:
      print(flush=True)
    return self.handle_results(ResultSet(results, start, end))

ConCurl.Request = Request
ConCurl.Response = Response
ConCurl.Result = Result
