import requests
import statistics as stats
import sys
import time
from requests.exceptions import ConnectTimeout, ReadTimeout, Timeout
from collections.abc import Mapping, Sequence
from lura import logs
from lura.attrs import attr
from lura.threads import pool
from lura.utils import common

log = logs.get_logger(__name__)

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

  def new_request(self, endpoint, type, headers, data):
    return attr(
      endpoint=endpoint, type=type, headers=headers, data=data)

  def new_response(self, headers, code, text, exc_info, start, end):
    return attr(
      headers=headers, code=code, text=text, exc_info=exc_info, start=start,
      end=end)

  def new_result(self, id, request, response, start, end):
    return attr(id=id, request=request, response=response, start=start, end=end)

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
    return self.new_request(endpoint, type, headers, data)

  def build_requests(self):
    return ((id, self.build_request(id)) for id in range(self.request_count))

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
      endl = '\n'
      self.column = 0
    print(c, end=endl, flush=True)

  def request(self, request):
    headers = code = text = exc_info = exc = None
    start = time.time()
    end = None
    try:
      call = getattr(requests, request.type.lower())
      response = call(
        request.endpoint, headers=request.headers, json=request.data,
        timeout=self.response_timeout)
      end = time.time()
      headers = response.headers
      code = response.status_code
      text = response.text
    except Exception as _:
      end = time.time() if end is None else end
      exc_info = sys.exc_info()
      exc = _
    self.print_dot(code, exc)
    return self.new_response(headers, code, text, exc_info, start, end)

  def test(self, args):
    start = time.time()
    id, request = args
    response = self.request(request)
    return self.new_result(id, request, response, start, time.time())

  def handle_results(self, start, end, results):
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
        isinstance(res.response.exc_info[1], Timeout)
    ]
    args.res_exc = [
      res for res in results
      if res.response.exc_info is not None and
        not isinstance(res.response.exc_info[1], Timeout)
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
    return self.handle_results(start, end, results)
