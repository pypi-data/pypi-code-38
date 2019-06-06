# -*- coding: utf-8 -*-
from past.builtins import basestring

import math
import re
try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode

DEFAULT_MAX_END = "default"


class RangeParseException(Exception):
    '''
    Used for handling errors during range parsing
    '''
    pass


class Range(object):
    def __init__(self, start, end, page=1):
        self.start = start
        self.end = end
        self.page = page

    def get_page_size(self):
        '''

        :return: the size of a page
        '''
        return self.end - self.start + 1

    def content_range(self, length):
        '''

        :param length: the total number of results
        :return: range header string
        '''
        end = self.end if self.end <= length else length - 1
        return 'items %d-%d/%d' % (self.start, end, length)

    @classmethod
    def parse(cls, request, default_start=0, default_end=9, max_end=DEFAULT_MAX_END):
        '''
        Parse the range headers into a range object. When there are no range headers,
        check for a page 'pagina' parameter, otherwise use the defaults defaults

        :param request: a request object
        :param default_start: default start for  paging (optional, default is 0)
        :param default_end: default end for paging (optional, default is 9)
        :param max_end: maximum end for paging (optional, default is 50,
                        if oe.paging.max_end settings is set, this value will be used)
        :return: :class: 'oe_utils.range_parser.Range'
        '''
        settings = request.registry.settings
        page_param = settings.get('oe.paging.page.queryparam', 'pagina')
        max_end_settings = settings.get('oe.paging.max_end', None)

        # hanling overriding of max_end by coders.
        if max_end_settings and max_end == DEFAULT_MAX_END:
            max_end = int(max_end_settings)
        # if no max_end, fallback to default value
        if max_end == DEFAULT_MAX_END:
            max_end = 50
        if 'Range' in request.headers and request.headers['Range'] is not '':
            match = re.match('^items=([0-9]+)-([0-9]+)$', request.headers['Range'])

            if match:
                start = int(match.group(1))
                end = int(match.group(2))

                if end < start:
                    end = start
                if max_end and end > start + max_end:
                    end = start + max_end
                return cls(start, end)
            else:
                raise RangeParseException('range header does not match expected format')
        elif page_param in request.params:
            per_page_param = settings.get('oe.paging.per_page.queryparam',
                                          'per_pagina')
            page = int(request.params.get(page_param))
            items_per_page = int(
                request.params.get(per_page_param,
                                   default_end - default_start + 1)
            )
            # enforcing items_per_page is less than the settings limit.
            if max_end is not None and items_per_page > max_end:
                items_per_page = max_end
            start = default_start + items_per_page * (page - 1)
            end = start + items_per_page - 1
            return cls(start, end, page)
        else:
            return cls(default_start, default_end)

    def set_response_headers(self, request, total_count):
        '''
        Set the correct range headers on the response

        :param request: a request object
        :param total_count: the total number of results
        '''
        response = request.response
        response.headerlist.append(('Access-Control-Expose-Headers', 'Content-Range, X-Content-Range'))
        response.accept_ranges = 'items'
        if total_count is None:
            raise RangeParseException('Provided length value is null')
        if total_count > 0:
            response.content_range = self.content_range(total_count)

        self.set_link_headers(request, total_count)

    def set_link_headers(self, request, total_count):
        """
        Sets Link headers on the response.

        When the Range header is present in the request no Link headers will
        be added.
        4 links will be added: first, prev, next, last.
        If the current page is already the first page, the prev link will
        not be present.
        If the current page is already  the last page, the next link will
        not be present.

        :param request: A request object
        :param total_count: The total amount of items available before paging
        """
        response = request.response
        if request.headers.get('Range'):
            # Don't set the Link headers when custom ranges were used.
            return

        settings = request.registry.settings
        page_param = settings.get('oe.paging.page.queryparam', 'pagina')
        per_page_param = settings.get('oe.paging.per_page.queryparam',
                                      'per_pagina')
        url = request.path_url
        try:
            queryparams = request.params.mixed()
        except AttributeError:
            queryparams = request.params
        page_size = self.get_page_size()
        current_page = self.start // page_size + 1
        queryparams[per_page_param] = page_size
        links = {
            'first': 1,
            'last': int(math.ceil(float(total_count) / page_size))
        }
        if current_page != links['first']:
            links['prev'] = current_page - 1
        if current_page != links['last']:
            links['next'] = current_page + 1

        response.headers['Link'] = self._make_link_headers(links, page_param,
                                                           queryparams, url)

    def _make_link_headers(self, links, page_param, queryparams, url):
        link_headers = []
        queryparams = {
            key: val.encode('utf8') if isinstance(val, basestring) else val
            for key, val in queryparams.items()
        }
        for name, page in links.items():
            queryparams[page_param] = page
            link_headers.append('<{url}?{queryparams}>; rel="{name}"'
                                .format(url=url,
                                        queryparams=urlencode(queryparams),
                                        name=name))
        return ', '.join(link_headers)
