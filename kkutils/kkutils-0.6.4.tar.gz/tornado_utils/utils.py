#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-07-30 21:41:46
'''
import functools
import math
import urllib.parse

import tornado.web
from tornado.template import Template


def auth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        token = self.get_argument('token', None)
        if token == 'diguadawang':
            return method(self, *args, **kwargs)
        else:
            raise tornado.web.HTTPError(403)
    return wrapper


def cache(cache_time=86400):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.app.cache_enabled and not self.settings['debug']:
                html = self.app.rd.get(self.cache_key)
                if html:
                    self.finish(html)
                else:
                    self.cache_time = cache_time
                    func(self, *args, **kwargs)
            else:
                func(self, *args, **kwargs)
        return wrapper
    return decorate


class PageModule(tornado.web.UIModule):

    def get_url(self, page):
        ret = urllib.parse.urlparse(self.handler.request.uri)
        query = urllib.parse.parse_qs(ret.query)
        query.update({'page': page})
        url = urllib.parse.urlunparse((ret.scheme, ret.netloc, ret.path, ret.params,
                                       urllib.parse.urlencode(query, doseq=True), ret.fragment))
        return url

    def render(self, total, **kwargs):
        ''' Args:
        count: how many items each page shows
        total: the total items number
        '''
        t = Template('''<nav>
<ul class="pagination">
  <li class="page-item {% if page == 1 %}active{% end %}"><a class="page-link" href="{{ get_url(1) }}">1</a></li>
    {% if page > 2 and pages > 4 %}
    <li class="page-item disabled"><span class="page-link">«</span></li>
    {% end %}
    {% for i in range(max(2,pages-2) if page >= pages-1 else max(2,page-1), min(4,page+3,pages) if page<=2 else min(pages,page+2))  %}
    <li class="page-item {% if page == i %}active{% end %}"><a class="page-link" href="{{ get_url(i) }}">{{i}}</a></li>
    {% end %}
    {% if page + 1 < pages and pages > 4 %}
    <li class="page-item disabled"><span class="page-link">»</span></li>
    {% end %}
    {% if pages > 1 %}
    <li class="page-item {% if page == pages %}active{% end %}"><a class="page-link" href="{{ get_url(pages) }}">{{pages}}</a></li>
    {% end %}
    <li class="page-item disabled"><span class="page-link">{{ total }}项</span></li>
  </ul>
</nav>''')
        kwargs.setdefault('count', int(self.handler.get_argument('count', 20)))
        kwargs.setdefault('page', int(self.handler.get_argument('page', 1)))
        pages = int(math.ceil(total / kwargs['count']))
        return t.generate(pages=pages, total=total, get_url=self.get_url, **kwargs)

    def css_files(self):
        pass
        # return '//cdn.bootcss.com/bootstrap/4.1.1/css/bootstrap.min.css'
