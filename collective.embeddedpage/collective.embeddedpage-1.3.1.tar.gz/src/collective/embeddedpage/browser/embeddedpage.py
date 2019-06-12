# -*- coding: utf-8 -*-
from lxml import etree
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urlparse import urljoin
from urlparse import urlparse

import chardet
import lxml
import re
import requests


class EmbeddedPageView(BrowserView):

    template = ViewPageTemplateFile('embeddedpage.pt')

    def get_zope_request_http_headers(self):
        '''Return a dict with all x-*http headers in their original format'''
        headers = {}
        for name, value in self.request.environ.items():
            if not name.startswith('HTTP_'):
                continue
            name = name[5:].lower().replace('_', '-')
            headers[name] = '{}'.format(value)
        return self.filter_x_http_headers(headers)

    def filter_x_http_headers(self, headers):
        filtered = {}
        for name, value in headers.items():
            if name.lower().startswith('x-'):
                filtered[name] = value
        return filtered

    def __call__(self):
        resource = self.request.form.get('embeddedpage_get_resource', '')
        if resource:
            response = self.request.response
            response.setHeader('content-type', 'application/javascript')
            return response.setBody(requests.get(resource).content)
        request_type = self.request['REQUEST_METHOD']
        method = getattr(requests, request_type.lower(), requests.get)
        params = {
            'url': self.context.url,
            # Forward request x-* headers
            'headers': self.get_zope_request_http_headers(),
        }
        if request_type == 'GET':
            params['params'] = self.request.form
        else:
            params['data'] = self.request.form
        response = method(**params)

        # Forward response x-* headers
        for k, v in self.filter_x_http_headers(response.headers).items():
            self.request.response.setHeader(k, v)

        # Normalize charset to unicode
        content = response.content
        det = chardet.detect(content)
        content = content.decode(det['encoding'])
        # https://stackoverflow.com/a/28545721/2116850
        content = re.sub(r'\<\?xml.*encoding.*\?\>\ *?\n', '', content)
        el = lxml.html.fromstring(content)
        template = '{0}?embeddedpage_get_resource={1}'
        for script in el.findall('.//script'):
            src = script.attrib.get('src', '')
            if src == '':
                continue
            script.attrib['src'] = template.format(
                self.context.absolute_url(), src)
        for iframe in el.findall('.//iframe'):
            src = iframe.attrib.get('src', '')
            if urlparse(src).scheme != '':
                continue
            iframe.attrib['src'] = urljoin(self.context.url, src)
        body = el.find('body')
        if body is not None:
            for link in el.findall('.//head//link'):
                body.insert(0, link)
            el = body
        self.embeddedpage = etree.tostring(el, method='html')
        return self.template()
