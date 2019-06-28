import asyncio
import json
import ssl

import cchardet as chardet
import httptools

try:
    import uvloop
    import ujson as json

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass

__all__ = ("Response", "request", 'get', 'put', 'patch', 'post', 'delete', 'head', 'options', 'json')
__version__ = '0.1.3'


class CaseInsensitiveDict(dict):
    def __init__(self, item: dict = None):
        super().__init__()
        if item:
            for k, v in item.items():
                self.__setitem__(k, v)

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __delitem__(self, key):
        return super().__delitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())


class Response:
    def __init__(self):
        self.headers: CaseInsensitiveDict = CaseInsensitiveDict()
        self.content: bytes = b""
        self.status_code: int = 0
        self.content_length: int = 0
        self.encoding: str = "utf-8"
        self.text: str = ""

    def on_header(self, name: bytes, value: bytes):
        if name.decode() == "Content-Length":
            self.content_length = int(value.decode())
        self.headers[name.decode()] = value.decode()

    def on_body(self, body: bytes):
        self.content += body

    async def done(self):
        result = chardet.detect(self.content)
        self.encoding = result['encoding'] or "utf-8"
        self.text = self.content.decode(self.encoding, "ignore")
        return self.text

    async def json(self):
        return json.loads(self.text)

    def __repr__(self):
        return f'<Response [{self.status_code}]>'


async def request(method: str, url: str, headers: dict = None, data: str = ""):
    if not url.startswith("http"):
        url = "http://" + url

    sslcontext = None
    parsed_url = httptools.parse_url(url.encode())
    ip = parsed_url.host.decode()
    port = parsed_url.port
    if port:
        port = port.decode()
    if not port:
        if parsed_url.schema == b"https":
            sslcontext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            port = 443
        else:
            port = 80
    path = parsed_url.path or b"/"
    path = path.decode()

    reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port, ssl=sslcontext), timeout=30)
    h = CaseInsensitiveDict({
        "User-Agent": "ashttp",
        "Host": ip
    })
    if headers:
        h.update(headers)
    if data:
        h["Content-Length"] = len(data)

    header_raw = "".join([f"{k}: {v}\r\n" for k, v in h.items()])
    http_raw = f"{method} {path} HTTP/1.1\r\n{header_raw}\r\n{data}".encode()
    writer.write(http_raw)

    response = Response()
    parser = httptools.HttpResponseParser(response)

    size = 0
    while True:
        chunk = await reader.read(100)
        size += len(chunk)
        parser.feed_data(chunk)
        if len(chunk) < 100 and size >= response.content_length:
            break
    response.status_code = parser.get_status_code()
    await response.done()
    writer.close()

    return response


async def get(url, headers=None) -> Response:
    return await request("GET", url, headers=headers)


async def post(url, headers=None, data=None) -> Response:
    return await request("POST", url, headers=headers, data=data)


async def put(url, headers=None, data=None) -> Response:
    return await request("PUT", url, headers=headers, data=data)


async def patch(url, headers=None, data=None) -> Response:
    return await request("PATCH", url, headers=headers, data=data)


async def delete(url, headers=None) -> Response:
    return await request("DELETE", url, headers=headers)


async def options(url, headers=None) -> Response:
    return await request("OPTIONS", url, headers=headers)


async def head(url, headers=None) -> Response:
    return await request("HEAD", url, headers=headers)
