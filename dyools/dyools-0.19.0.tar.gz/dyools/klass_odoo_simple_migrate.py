from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging
import os
import pprint
import tempfile

from .klass_offset_limit import OffsetLimit
from .klass_print import Print

logger = logging.getLogger(__name__)


def all_fields(fields, dest_fields, exclude_fields, include_fields, many2one_with_names):
    exclude_fields = exclude_fields or []
    include_fields = include_fields or []
    many2one_with_names = many2one_with_names or []
    ff = set(['id'])
    for f_name, f_spec in fields.items():
        if f_name in exclude_fields:
            continue
        if f_name not in dest_fields:
            continue
        if f_name in ['__last_update', 'write_date', 'write_uid', 'create_date', 'create_uid']:
            if f_name not in include_fields:
                continue
        if f_spec.get('store', True) == False:
            continue
        if f_spec.get('type') in ['many2many', 'one2many']:
            continue
        if f_spec.get('type') == 'many2one':
            if f_name not in many2one_with_names:
                f_name = '{}/id'.format(f_name)
        ff.add(f_name)
    return list(ff)


class OdooSimpleMigrate(object):

    def __init__(self, src, dest, path=None):
        self._src = src
        self._dest = dest
        self._path = path or (os.path.join(tempfile.gettempdir(), 'odoo_migrate'))

    def migrate(self,
                model=None,
                src_model=None,
                dest_model=None,
                src_context=None,
                dest_context=None,
                fields=None,
                exclude_fields=[],
                include_fields=[],
                many2one_with_names=[],
                domain=[],
                limit=0,
                offset=0,
                order=None,
                by=None,
                debug=False,
                ):
        kwargs = {}
        if offset: kwargs['offset'] = offset
        if limit: kwargs['limit'] = limit
        if order: kwargs['order'] = order
        self._kwargs = kwargs
        self._src_model = src_model or model
        self._dest_model = dest_model or model
        _src_context = self._src.env.context.copy()
        _src_context.update(src_context or {})
        self._src_context = _src_context
        _dest_context = self._dest.env.context.copy()
        _dest_context.update(dest_context or {})
        self._dest_context = _dest_context
        self._fields_specs = self._src.env[self._src_model].fields_get(fields)
        self._fields = all_fields(
            self._fields_specs,
            dest_fields=list(self._dest.env[self._dest_model].fields_get().keys()),
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            many2one_with_names=many2one_with_names,
        )
        self._domain = domain
        self._order = order
        self._count = self._src.env[self._src_model].with_context(self._src_context).search(self._domain, count=True,
                                                                                            **self._kwargs)
        self._by = by or self._count
        self._debug = debug
        self._migrate()

    def _migrate(self):
        kwargs = dict()
        if self._order:
            kwargs['order'] = self._order
        if self._debug:
            Print.debug('Header : {}'.format(pprint.pformat(self._fields)))
        for offset, limit in OffsetLimit(0, self._by, self._count):
            kwargs.update(dict(offset=offset, limit=limit))

            data = self._src.env[self._src_model].with_context(self._src_context).search(self._domain, **kwargs)
            if isinstance(data, list):
                data = self._src.env[self._src_model].with_context(self._src_context).browse(data)
            data = data.export_data(self._fields, raw_data=False)
            if self._debug:
                Print.debug('Data : {}'.format(pprint.pformat(data['datas'])))
            res = self._dest.env[self._dest_model].with_context(self._dest_context).load(self._fields, data['datas'])
            if not res.get('ids'):
                Print.error(res)
            Print.info('progression: [{}-{}]/{}'.format(offset, offset + limit, self._count))
