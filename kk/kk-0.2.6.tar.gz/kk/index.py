#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import copy
import datetime
import json
import logging
import math
import os
import re
import shutil
import signal
import tempfile
import threading
import time
import urllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib import parse

import bson
import markdown
import pymongo
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import yaml
from tornado.concurrent import run_on_executor
from tornado.options import define
from tornado.options import options

from .utils import connect
from .utils import Dict
from .utils import get_ip
from .utils import JSONEncoder

define("port", default=None, help="run on the given port", type=int)
define("path", default=".", help="upload server path", type=str)
define("debug", default=True, help="debug mode", type=bool)
define("all", default=False, help="show all files", type=bool)
define('uri', default=None, help='mongodb uri', type=str)
define("db", default='upload', help="databse name", type=str)


class PageModule(tornado.web.UIModule):

    def render(self, page):
        ret = parse.urlparse(self.handler.request.uri)
        query = parse.parse_qs(ret.query)
        query.update({'page': page})
        url = parse.urlunparse((ret.scheme, ret.netloc, ret.path, ret.params, parse.urlencode(query, doseq=True), ret.fragment))
        return url


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request)
        self.get_args()

    def write(self, chunk):
        if isinstance(chunk, (dict, list)):
            chunk = json.dumps(chunk, cls=JSONEncoder)
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
        return super().write(chunk)

    def render(self, template, **kwargs):
        if self.args.f == 'json':
            self.finish(kwargs)
        else:
            super().render(template, **kwargs)

    def get_args(self, **kwargs):
        if self.application.db:
            cursor = self.application.db.tables.find({}, {'name': 1})
            self.tables = [c['name'] for c in cursor]
            cursor = self.application.db.charts.find({}, {'name': 1})
            self.charts = [c['name'] for c in cursor]
        else:
            self.tables = []
            self.charts = []

        args = {
            'page': 1,
            'count': 20,
            'sort': '_id',
            'order': 1
        }
        args.update(kwargs)

        for key, value in self.request.arguments.items():
            if len(value) >= 2:
                args[key] = list(map(lambda x: x.decode(), value))
            elif len(value) == 1 and value[0].strip():
                args[key] = value[0].strip().decode()

        for key in ['page', 'count', 'order']:
            if args.get(key) is not None:
                args[key] = int(args[key])

        self.args = Dict(args)

    def clean(self, doc, *args):
        exclude = list(set(args) | set(['page', 'count', 'sort', 'order', 'f']))
        for key in exclude:
            if key in doc:
                del doc[key]
        return doc

    def fields(self, doc, *args):
        if args:
            keys = set(doc.keys()) - set(args)
            for key in keys:
                if key in doc:
                    del doc[key]
        return doc

    def schema(self, doc, **schema):
        regex = doc.pop('_regex', False)
        for k, t in schema.items():
            if doc.get(k):
                if t not in ['int', 'float', 'datetime']:
                    if regex:
                        doc[k] = {'$regex': re.compile(doc[k])}
                    continue
                if t == 'int':
                    values = list(map(lambda item: int(item.strip()) if item.strip() else None, doc[k].strip().split('~')))
                elif t == 'float':
                    values = list(map(lambda item: float(item.strip()) if item.strip() else None, doc[k].strip().split('~')))
                elif t == 'datetime':
                    values = list(map(lambda item: item.strip(), doc[k].strip().split('~')))
                    for i, value in enumerate(values):
                        if value:
                            value = re.sub(r'[^\d]', '', value)
                            value += (14 - len(value)) * '0'
                            values[i] = datetime.datetime.strptime(value, '%Y%m%d%H%M%S')
                        else:
                            values[i] = None

                if len(values) == 1:
                    doc[k] = values[0]
                else:
                    if values[0] is not None and values[-1] is not None:
                        doc[k] = {'$gte': values[0], '$lte': values[-1]}
                    elif values[0] is not None:
                        doc[k] = {'$gte': values[0]}
                    elif values[-1] is not None:
                        doc[k] = {'$lte': values[-1]}
        return doc

    def query(self, collection, doc=None, clean=[], fields=[], schema={}):
        doc = copy.copy(doc or self.args)
        self.clean(doc, *clean)
        self.fields(doc, *fields)
        self.schema(doc, **schema)
        page, count, sort, order = self.args.page, self.args.count, self.args.sort, self.args.order
        cursor = self.application.db[collection].find(doc).skip((page - 1) * count).limit(count).sort(sort, order)
        self.args.total = cursor.count()
        self.args.pages = int(math.ceil(self.args.total / float(count)))
        return [Dict(c) for c in cursor]


class ChartHandler(BaseHandler):

    def get(self, name):
        if not name:
            return self.render('chart.html', title='upload')

        chart = self.application.db.charts.find_one({'name': name})
        if not chart:
            return self.redirect('/chart')

        f = self.get_argument('f', None)
        if f == 'json':
            return self.finish({'containers': json.loads(chart['containers'])})
        else:
            return self.render('chart.html', title=name)

    def delete(self, name):
        self.application.db.charts.delete_one({'name': name})
        self.finish({'err': 0})

    def post(self, name):
        charts = json.loads(self.request.body)
        containers = []
        for chart in charts:
            chart = Dict(chart)
            chart.xAxis = chart.get('xAxis', [])
            data = {
                'chart': {
                    'type': chart.type,
                    'zoomType': 'x',
                },
                'credits': {
                    'enabled': False
                },
                'title': {
                    'text': chart.title,
                    'x': -20
                },
                'xAxis': {
                    'tickInterval': int(math.ceil(len(chart.xAxis) / 20.0)),
                    'labels': {
                        'rotation': 45 if len(chart.xAxis) > 20 else 0,
                        'style': {
                            'fontSize': 12,
                            'fontWeight': 'normal'
                        }
                    },
                    'categories': chart.xAxis
                },
                'yAxis': {
                    'title': {
                        'text': ''
                    },
                    'plotLines': [{
                        'value': 0,
                        'width': 1,
                        'color': '#808080'
                    }]
                },
                'tooltip': {
                    'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
                    'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y:.2f}</b></td></tr>',
                    'footerFormat': '</table>',
                    'shared': True,
                    'useHTML': True
                },
                'legend': {
                    'layout': 'horizontal',
                    'align': 'center',
                    'verticalAlign': 'bottom',
                    'borderWidth': 0,
                    'y': 0,
                    'x': 0
                },
                'plotOptions': {
                    'series': {
                        'marker': {
                            'radius': 1,
                            'symbol': 'diamond'
                        }
                    },
                    'pie': {
                        'allowPointSelect': True,
                        'cursor': 'pointer',
                        'dataLabels': {
                            'enabled': True,
                            'color': '#000000',
                            'connectorColor': '#000000',
                            'format': '<b>{point.name}</b>: {point.percentage:.3f} %'
                        }
                    }
                },
                'series': chart.series
            }
            containers.append(data)

        if containers:
            doc = {
                'name': name,
                'containers': json.dumps(containers, ensure_ascii=False),
                'charts': json.dumps(charts, ensure_ascii=False),
                'date': datetime.datetime.now().replace(microsecond=0)
            }
            self.application.db.charts.update_one({'name': name}, {'$set': doc}, upsert=True)
            self.finish({'err': 0})
        else:
            self.finish({'err': 1, 'msg': '未获取到必需参数'})


class TableHandler(BaseHandler):

    def get(self, name):
        if not name:
            return self.render('table.html', title='upload')

        meta = self.application.db.tables.find_one({'name': name})
        if not meta:
            return self.redirect('/table')

        schema = dict(map(lambda x: x.split(':'), meta['fields']))
        entries = self.query(name, self.args, schema=schema)

        self.args.fields = list(map(lambda item: item.split(':')[0], meta['fields']))
        self.args.searchs = meta.get('search', [])
        self.args.marks = meta.get('mark', [])
        self.args.options = {
            'sort': self.args.fields,
            'order': ['1:asc', '-1:desc'],
        }
        self.render('table.html', entries=entries, title=name)

    def delete(self, name):
        if name in ['tables', 'charts']:
            return self.finish({'err': 1, 'msg': f'{name} is not allowed'})
        self.application.db[name].drop()
        self.application.db.tables.delete_one({'name': name})
        self.finish({'err': 0})

    def post(self, name):
        if name in ['tables', 'charts']:
            return self.finish({'err': 1, 'msg': f'{name} is not allowed'})
        doc = json.loads(self.request.body)
        self.application.db[name].drop()
        for key in doc.get('search', []):
            self.application.db[name].create_index(key)

        fields = dict(map(lambda x: x.split(':'), doc['fields']))
        if doc.get('docs'):
            dts = dict(filter(lambda x: x[1] == 'datetime', fields.items()))
            for k in dts:
                for item in doc['docs']:
                    item[k] = datetime.datetime.strptime(item[k], '%Y-%m-%d %H:%M:%S')
            self.application.db[name].insert_many(doc['docs'])

        meta = {'name': name}
        meta.update(dict(filter(lambda x: x[0] in ['fields', 'search', 'mark'], doc.items())))
        self.application.db.tables.update_one({'name': name}, {'$set': meta}, upsert=True)
        self.finish({'err': 0})

    def put(self, name):
        doc = json.loads(self.request.body)
        meta = self.application.db.tables.find_one({'name': name})
        type_dict = dict(map(lambda x: x.split(':'), meta['fields']))
        if type_dict[doc['key']] == 'int':
            doc['value'] = int(doc['value'])
        elif type_dict[doc['key']] == 'float':
            doc['value'] = float(doc['value'])
        elif type_dict[doc['key']] == 'datetime':
            doc['value'] = datetime.datetime.strptime(doc['value'], '%Y-%m-%d %H:%M:%S')

        if doc['action'] == 'add':
            operate = '$set' if doc.get('unique') else '$addToSet'
        else:
            operate = '$unset' if doc.get('unique') else '$pull'

        self.application.db[name].update_one({'_id': bson.ObjectId(doc['_id'])}, {operate: {doc['key']: doc['value']}})
        self.finish({'err': 0})


@tornado.web.stream_request_body
class IndexHandler(tornado.web.StaticFileHandler, BaseHandler):
    executor = ThreadPoolExecutor(5)
    default = {
        'ppt.png': ['.ppt', '.pptx'],
        'word.png': ['.doc', '.docx'],
        'excel.png': ['.xls', '.xlsx'],
        'pdf.png': ['.pdf'],
        'txt.png': ['.txt'],
        'image.png': ['.png', '.jpg', '.jpeg', '.bmp', '.gif'],
        'audio.png': ['.amr', '.ogg', '.wav', '.mp3'],
        'video.png': ['.rmvb', '.rm', '.mkv', '.mp4', '.avi', '.wmv'],
        'rar.png': ['.rar', '.tar', '.tgz', '.gz', '.bz2', '.bz', '.xz', '.zip', '.7z'],
        'c.png': ['.c', '.h'],
        'cpp.png': ['.cpp'],
        'python.png': ['.py', '.pyc'],
        'shell.png': ['.sh'],
        'go.png': ['.go'],
        'java.png': ['.java', '.javac', '.class', '.jar'],
        'javascript.png': ['.js'],
        'vue.png': ['.vue'],
        'html.png': ['.html'],
        'css.png': ['.css', '.less', '.sass', '.scss'],
        'json.png': ['.json', '.yml', '.yaml'],
        'markdown.png': ['.md'],
        'ini.png': ['.ini'],
        'db.png': ['.db', '.sql'],
    }
    icon = {}
    for key, value in default.items():
        for v in value:
            icon[v] = key

    def __init__(self, application, request, **kwargs):
        tornado.web.StaticFileHandler.__init__(self, application, request, **kwargs)
        self.f = self.get_argument('f', None)
        self.w = self.get_argument('w', None)
        self.h = self.get_argument('h', None)
        self.path = self.application.path
        self.cache = self.application.cache
        self.get_args(count=50)

    def compute_etag(self):
        if hasattr(self, 'absolute_path'):
            return super().compute_etag()

    @run_on_executor
    def search(self, q):
        entries = []
        # 防止正在扫描时cache值变化导致出错
        files = list(self.application.cache.values())
        for _, docs in files:
            for doc in docs:
                if doc[0].name.find(q) >= 0:
                    entries.append(doc)
        page, count = self.args.page, self.args.count
        self.args.total = len(entries)
        self.args.pages = int(math.ceil(len(entries) / count))
        entries = entries[(page - 1) * count:page * count]
        return entries

    @run_on_executor
    def listdir(self, root):
        entries = self.application.scan_dir(root)
        page, count = self.args.page, self.args.count
        self.args.total = len(entries)
        self.args.pages = int(math.ceil(len(entries) / count))
        entries = entries[(page - 1) * count:page * count]
        return entries

    def get_nodes(self, root):
        nodes = []
        key = self.application.path / root
        if key in self.application.cache:
            entries = self.application.cache[self.application.path / root][1]
            for doc in entries:
                if doc[3]:
                    nodes.append({'name': doc[0].name, 'spread': False, 'href': f'/{doc[0]}', 'children': self.get_nodes(doc[0])})
                else:
                    nodes.append({'name': doc[0].name, 'href': f'/{doc[0]}'})
        return nodes

    def set_headers(self):
        super().set_headers()
        self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', '0')
        if self.args.f == 'download' or re.search('wget|curl', self.request.headers.get('user-agent', ''), re.I):
            self.set_header('Content-Type', 'application/octet-stream')

    def send_html(self, html):
        self.finish(f'''<html><head>
<link href="/static/css/atom-one-dark.min.css" rel="stylesheet">
</head><body>{html}
<script src="/static/js/highlight.min.js"></script>
<script>hljs.initHighlightingOnLoad()</script>
</body></html>''')

    async def get(self, name, include_body=True):
        path = self.path / name

        if self.args.q:
            entries = await self.search(self.args.q)
            self.render('index.html', entries=entries, nodes='[]')
        elif self.args.f == 'tree':
            nodes = self.get_nodes(path)
            self.finish(nodes)
        elif self.args.f == 'download':
            self.set_header('Content-Disposition', f'attachment;filename={urllib.parse.quote(path.name)}')
            await super().get(name, include_body)
        elif path.is_file():
            if path.suffix.lower() in ['.yml', '.yaml']:
                doc = yaml.load(open(path))
                self.finish(doc)
            elif path.suffix.lower() == '.md':
                exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables', 'markdown.extensions.toc']
                html = markdown.markdown(path.read_text(), extensions=exts)
                self.send_html(html)
            elif path.suffix.lower() == '.ipynb':
                with tempfile.NamedTemporaryFile('w+', suffix=f'.html', delete=True) as fp:
                    command = f'jupyter nbconvert --to html --template full --output {fp.name} {path}'
                    logging.info(command)
                    dl = await asyncio.create_subprocess_shell(command)
                    await dl.wait()
                    self.finish(fp.read().replace('<link rel="stylesheet" href="custom.css">', ''))
            elif path.suffix.lower() in ['.py', '.sh', '.h', '.c', '.cpp', '.js', '.css', '.html', '.java', '.go', '.ini', '.vue']:
                self.send_html(f'''<pre><code>{ tornado.escape.xhtml_escape(path.read_text()) }</code></pre>''')
            else:
                await super().get(name, include_body)
        else:
            entries = await self.listdir(path)
            nodes = self.get_nodes(path) if self.get_cookie('tree') else []
            self.render('index.html', entries=entries, nodes=json.dumps(nodes))

    async def delete(self, name):
        path = self.path / name
        if path.exists():
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            self.finish(f'{name} removed')
        else:
            self.finish(f'{name} not exists')

    async def execute(self, path):
        cwd = os.getcwd()
        os.chdir(path.parent)
        if path.suffix.lower() in ['.gz', '.bz2', '.xz'] and path.name.find('.tar') >= 0 \
                or path.suffix.lower() in ['.tgz']:
            command = f'tar xf {path.name}'
        elif path.suffix.lower() in ['.gz']:
            command = f'gzip -d {path.name}'
        elif path.suffix.lower() in ['.bz2', '.bz']:
            command = f'bzip2 -d {path.name}'
        elif path.suffix.lower() in ['.zip']:
            command = f'unzip {path.name}'
        else:
            command = f'tar czf {path.name}.tar.gz {path.name}'
        logging.warning(f'execute command: {command}, path: {os.getcwd()}')
        dl = await asyncio.create_subprocess_shell(command)
        code = await dl.wait()
        os.chdir(cwd)
        return code

    async def post(self, name):
        path = self.path / name
        action = self.get_argument('action', None)
        if self.request.files:
            for items in self.request.files.values():
                for item in items:
                    filename = path / item['filename']
                    dirname = filename.parent
                    if not dirname.exists():
                        os.makedirs(dirname)
                    filename.write_bytes(item['body'])
            self.finish('upload success')
        elif action == 'execute':
            code = await self.execute(path)
            self.finish(str(code))
        else:
            self.finish('files not found')

    def prepare(self):
        path = self.path / self.request.path.lstrip('/')
        if self.request.method in ['POST', 'PUT', 'DELETE', 'HEAD']:
            if path in self.cache:
                self.cache.pop(path)
            if path.parent in self.cache:
                self.cache.pop(path.parent)

        if self.request.method == 'PUT':
            self.received = 0
            self.process = 0
            self.length = int(self.request.headers['Content-Length'])
            self.request.headers['Content-Type'] = 'application/octet-stream'
            if str(path).find('..') >= 0:
                return self.finish(f'{path} is forbidden')
            if path.is_dir():
                return self.finish(f'{path} is a directory')
            if not path.parent.exists():
                os.makedirs(path.parent)
            self.fp = open(path, 'wb')
        else:
            IndexHandler._stream_request_body = False
            super().prepare()

    def data_received(self, chunk):
        self.received += len(chunk)
        process = self.received / self.length * 100
        if int(process) > self.process + 5:
            self.process = int(process)
            self.write(f'uploading process {process:.2f}%\n')
            self.flush()
        self.fp.write(chunk)

    async def put(self, name):
        self.fp.close()
        self.finish('upload succeed')


class Application(tornado.web.Application):

    def __init__(self):
        self.path = Path(options.path).expanduser()
        handlers = [
            (r"/chart/?(.*)", ChartHandler),
            (r"/table/?(.*)", TableHandler),
            (r"/(.*)", IndexHandler, {'path': self.path}),
        ]
        settings = dict(
            debug=options.debug,
            static_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
            template_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
            ui_modules={'Page': PageModule},
        )
        super().__init__(handlers, **settings)
        self.db = pymongo.MongoClient(options.uri)[options.db] if options.uri else None
        self.cache = {}
        tornado.ioloop.PeriodicCallback(self.scan, 3600 * 1000).start()
        self.scan()
        logging.info(f'root: {self.path.absolute()}, initialize done')

    def scan_dir(self, root):
        root = Path(root)
        if not root.exists():
            return []

        st_mtime = root.stat().st_mtime
        if root in self.cache and st_mtime == self.cache[root][0]:
            entries = self.cache[root][1]
        else:
            entries = []
            for item in root.iterdir():
                if not item.exists():
                    continue
                if not options.all and item.name.startswith('.'):
                    continue
                path = item.relative_to(self.path)
                stat = item.stat()
                filesize = stat.st_size
                if filesize / (1024 * 1024 * 1024.0) >= 1:
                    size = '%.1f GB' % (filesize / (1024 * 1024 * 1024.0))
                elif filesize / (1024 * 1024.0) >= 1:
                    size = '%.1f MB' % (filesize / (1024 * 1024.0))
                else:
                    size = '%.1f KB' % (filesize / 1024.0)
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                entries.append([path, mtime, size, item.is_dir()])
            entries.sort(key=lambda x: str(x[0]).lower())
            self.cache[root] = [st_mtime, entries]
            if len(self.cache) >= 100000:
                self.cache.popitem()
        return entries

    def scan_thread(self):
        for root, _, _ in os.walk(self.path):
            if root == '.':
                self.scan_dir(root)
            else:
                root = root.lstrip('./')
                if not options.all and any([p.startswith('.') for p in root.split('/')]):
                    continue
                self.scan_dir(root)

    def scan(self):
        t = threading.Thread(target=self.scan_thread)
        t.daemon = True
        t.start()


def get_port():
    port = 8000
    while connect('127.0.0.1', port):
        port += 1
    return port


def main():
    options.parse_command_line()
    port = options.port or get_port()
    logging.info(f'Debug: {options.debug}, Running: http://{get_ip()}:{port}')
    server = tornado.httpserver.HTTPServer(Application(), xheaders=True, max_buffer_size=1024 * 1024 * 1024 * 5)
    server.bind(port)
    server.start()

    def shutdown():
        logging.info('shutdown now')
        server.stop()
        tasks = [task for task in asyncio.Task.all_tasks() if task is not
                 asyncio.tasks.Task.current_task()]
        list(map(lambda task: task.cancel(), tasks))
        tornado.ioloop.IOLoop.current().stop()

    def sig_handler(sig, x):
        tornado.ioloop.IOLoop.current().add_callback_from_signal(shutdown)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
