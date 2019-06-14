import requests
import sys
import time
import traceback
from requests.exceptions import ConnectTimeout, ReadTimeout, Timeout
from collections.abc import Mapping, Sequence
from lura import fmt
from lura.attrs import attr
from lura.io import slurp
from lura.threads import pool
from statistics import mean

def Request(endpoint, type, headers, data):
  return attr(
    endpoint=endpoint, type=type, headers=headers, data=data)

def Response(headers, code, text, exc_info, start, end):
  return attr(
    headers=headers, code=code, text=text, exc_info=exc_info, start=start,
    end=end)

def Result(id, request, response, start, end):
  return attr(id=id, request=request, response=response, start=start, end=end)

class MultiCurl:

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
    type = self.build_request_type(id=id, endpoint=self.endpoint)
    headers = self.build_request_headers(id=id, endpoint=endpoint, type=type)
    data = self.build_request_data(
      id=id, endpoint=endpoint, type=type, headers=headers)
    return Request(endpoint, type, headers, data)

  def build_requests(self):
    return ((id, self.build_request(id)) for id in range(self.request_count))

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
    if self.print_dots:
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
      print(c, end='', flush=True)
    return Response(headers, code, text, exc_info, start, end)

  def test(self, args):
    start = time.time()
    id, request = args
    response = self.request(request)
    return Result(id, request, response, start, time.time())

  def run(self):
    start = time.time()
    if self.print_dots:
      print(
        '.=200 !=Not 200 c/r/t=Connect/Read/Other timeout x=Exception ' + \
        '?=Unknown error')
    results = pool.map(self.thread_count, self.test, self.build_requests())
    end = time.time()
    if self.print_dots:
      print()
    return start, time.time(), results

def multicurl(*args, **kwargs):
  return ConCurl(*args, **kwargs).run()
