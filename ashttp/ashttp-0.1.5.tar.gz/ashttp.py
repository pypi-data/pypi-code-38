import asyncio
import json
import ssl

import cchardet as chardet
import httptools
from pyquery import PyQuery as pq

try:
    import ujson as json
except:
    pass

__all__ = ("Response", "request", 'get', 'put', 'patch', 'post', 'delete', 'head', 'options', 'json')
__version__ = '0.1.5'


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


class HTML:
    def __init__(self, url: str, html: str):
        self.html = html
        self.url = url
        self.d = pq(self.html, parser="html")
        self.d.make_links_absolute(self.url)

    @property
    def links(self):
        return [pq(i).attr("href") for i in self.d("a") if "javascript" not in i]

    @property
    def text(self):
        return self.d.text()

    @property
    def href(self):
        return self.attrs.get("href")

    @property
    def tag(self):
        return self.d[0].tag

    @property
    def attrs(self):
        return {k: v for k, v in self.d[0].items()}

    def find(self, selector: str):
        return [HTML(self.url, pq(i).outer_html()) for i in self.d(selector)]

    def find_one(self, selector: str):
        l = self.find(selector)
        if not l:
            return None
        return l[0]

    def __repr__(self):
        attr_str = " ".join([f'{k}="{v}"' for k, v in self.attrs.items()])
        return f"<HTML [{self.tag} {attr_str}]>"


class Response:
    def __init__(self, url):
        self.url = url
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

    async def html(self):
        return HTML(self.url, self.text)

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
        "Host": ip,
        "Referer": url,
    })
    if headers:
        h.update(headers)
    if data:
        h["Content-Length"] = len(data)

    header_raw = "".join([f"{k}: {v}\r\n" for k, v in h.items()])
    http_raw = f"{method} {path} HTTP/1.1\r\n{header_raw}\r\n{data}".encode()
    writer.write(http_raw)

    response = Response(url)
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
