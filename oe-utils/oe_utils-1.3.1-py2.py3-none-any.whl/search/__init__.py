# -*- coding: utf-8 -*-
from math import ceil

from pyramid.httpexceptions import HTTPBadRequest
from webob.multidict import MultiDict


def validate_params(params, valid_keys, fail_on_invalid_key=True):
    p = MultiDict()
    for k, v in params.items():
        if k in valid_keys:
            p.add(k, v)
        elif fail_on_invalid_key:
            raise HTTPBadRequest('invalid search parameter')
    return p


def get_valid_params(params, valid_keys):
    return validate_params(params, valid_keys, fail_on_invalid_key=False)


def parse_sort_string(sort):
    """
    Parse a sort string for use with elasticsearch

    :param: sort: the sort string
    """
    if sort is None:
        return ['_score']
    l = sort.rsplit(',')
    sortlist = []
    for se in l:
        se = se.strip()
        order = 'desc' if se[0:1] == '-' else 'asc'
        field = se[1:] if se[0:1] in ['-', '+'] else se
        field = field.strip()
        sortlist.append({field: {"order": order, "unmapped_type": "string", "missing": "_last"}})
    sortlist.append('_score')
    return sortlist


def parse_filter_params(query_params, filterable):
    """
    Parse query_params to a filter params dict. Merge multiple values for one key to a list.
    Filter out keys that aren't filterable.

    :param query_params: query params
    :param filterable: list of filterable keys
    :return: dict of filter values
    """
    if query_params is not None:
        filter_params = {}
        for fq in query_params.mixed():
            if fq in filterable:
                filter_params[fq] = query_params.mixed().get(fq)
        return filter_params
    else:
        return {}


class SearchResultPager(object):
    """based on http://atlas-core.readthedocs.org/en/latest/_modules/flask_sqlalchemy.html Pagination"""

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev(self):
        return self.page - 1 if self.has_prev else None

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next(self):
        return self.page + 1 if self.has_next else None

    def iter_pages(
            self, left_edge=2, left_current=2,
            right_current=5, right_edge=2
    ):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        """
        last = 0
        try:
            xrange
        except NameError:
            xrange = range
        for num in xrange(1, self.pages + 1):
            if (
                                num <= left_edge or
                            (self.page - left_current - 1 < num < self.page + right_current)
                    or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num
