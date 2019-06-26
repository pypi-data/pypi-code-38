from typing import TypeVar, Iterator

from tornado.httpclient import HTTPRequest as HTTPClientRequest
from tornado.httputil import HTTPServerRequest

T = TypeVar('T', int, float)
def revrange(x: T) -> Iterator[T]:
    return range(x - 1, -1, -1)

def server_request_to_client_request(request: HTTPServerRequest) -> HTTPClientRequest:
    return HTTPClientRequest(url=request.uri, method=request.method, headers=request.headers)
