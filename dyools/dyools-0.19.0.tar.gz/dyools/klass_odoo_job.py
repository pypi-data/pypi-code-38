from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging
import os

from .klass_is import IS
from .klass_job import JobExtractorAbstract, JobLoaderAbstract, JobTransformerAbstract, JobErrorAbstract
from .klass_random import Random
from .klass_str import Str
from .klass_yaml_config import YamlConfig

logger = logging.getLogger(__name__)


class OdooJobExtractor(JobExtractorAbstract):
    _source_name = False
    _source_fields = False

    def __init__(self, **kwargs):
        if not self._source_name:
            raise ValueError('Please define the source model, static variable: _source_name')
        if not self._source_fields:
            raise ValueError('Please define the source fields, static variable: _source_fields')
        super(OdooJobExtractor, self).__init__(**kwargs)

    def extract(self, methods, _, pool):
        odoo = self.get_source()
        ids = odoo.env[self._source_name].search(self.domain, offset=self.offset, limit=self.limit)
        data = odoo.env[self._source_name].read(ids, self._source_fields)
        pool.append((methods, data))

    def count(self):
        return self.get_source().env[self._source_name].search_count(self.domain)


class OdooJobLoader(JobLoaderAbstract):
    _destination_name = False
    _destination_fields = False

    def __init__(self, **kwargs):
        if not self._destination_name:
            raise ValueError('Please define the destination model, static variable: _destination_name')
        if not self._destination_fields:
            raise ValueError('Please define the destination fields, static variable: _destination_fields')
        super(OdooJobLoader, self).__init__(**kwargs)

    def load(self, methods, queued_data, pool):
        odoo = self.get_destination()
        if self.context.get('primary_keys'):
            logger.info('sender: odoojob use create/write based on fields = %s' % self.context['primary_keys'])
            for record in queued_data:
                domain = [(pk, '=', record[pk]) for pk in self.context['primary_keys']]
                ids = odoo.env[self._destination_name].search(domain)
                if ids:
                    try:
                        odoo.env[self._destination_name].write(ids, record)
                    except:
                        pool.append((methods, dict(method='write', model=self._destination_name, ids=ids, vals=record)))
                else:
                    try:
                        odoo.env[self._destination_name].create(record)
                    except:
                        pool.append((methods, dict(method='create', model=self._destination_name, vals=record)))
        else:
            fields, data = self._generic_transform(odoo, queued_data)
            logger.info('sender: odoojob use load model=%s fields=%s', self._destination_name, fields)
            logger.debug('sender: odoojob call load with fields=%s data=%s', fields, data)
            result = odoo.env[self._destination_name].load(fields, data)
            if not result.get('ids'):
                pool.append((methods, dict(method='load', model=self._destination_name, fields=fields, data=data)))

    def _generic_transform(self, odoo, read_data):
        ffield = odoo.env[self._destination_name].fields_get()
        load_data = []
        fields = []
        if read_data:
            fields = list(read_data[0].keys())
            fields = [x for x in fields if x in self._destination_fields]
        for record in read_data:
            line = []
            for f in fields:
                if f == 'id':
                    record[f] = Str(record[f]).to_code().lower()
                    line.append('__migration__.%s_%s' % (Str(self._destination_name).dot_to_underscore(), record[f]))
                    continue
                if IS.iterable(record[f]) and len(record[f]) == 2:
                    line.append('__migration__.%s_%s' % (Str(ffield[f]).dot_to_underscore(), record[f][0]))
                    continue
                if IS.iterable(record[f]):
                    _res = []
                    for item in record[f]:
                        _res.append('__migration__.%s_%s' % (Str(ffield[f]).dot_to_underscore(), item))
                    line.append(','.join(_res))
                    continue
                line.append(record[f])
            load_data.append(line)
        return fields, load_data


class OdooJobTransformer(JobTransformerAbstract):

    def transform(self, methods, queued_data, pool):
        return pool.append((methods, queued_data))


class OdooJobError(JobErrorAbstract):

    def error(self, methods, queued_data, pool):
        path = os.path.join(self.error_path, Str(queued_data.get('model')).dot_to_underscore(), Random.uuid() + '.yml')
        yaml = YamlConfig(path, create_if_not_exists=True)
        yaml.set_data(queued_data)
        yaml.dump()
        self.logger.error(queued_data)
