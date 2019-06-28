#
# Copyright (c) 2013-2019 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from marshmallow import fields, Schema, post_load, pre_load

from .fileext import FileCliSchemaV2
from .scan import Scan, ScanSchemaV3


# {{{ V3
class ScanRetrievalCodeSchemaV3(Schema):
    id = fields.String(attribute='external_id')
    scan = fields.Nested(ScanSchemaV3, only=('id', 'date', 'status',
                                             'infected', 'probes_finished',
                                             'probes_total', 'total'))

    @post_load
    def make_object(self, data):
        return ScanRetrievalCode(**data)


class ScanRetrievalCodeSchemaV2(Schema):
    id = fields.String(attribute="external_id")

    @post_load
    def make_object(self, data):
        return ScanRetrievalCode(**data)

# }}}


# {{{ V2

class SRFileCliSchemaV2(FileCliSchemaV2):
    size = fields.Pluck('FileSchema', 'size', dump_only=True, attribute="file")

    @pre_load
    def rm_size(self, data):
        del data['size']
        return data


class SRScanSchemaV2(Schema):
    id = fields.UUID(attribute="external_id")
    date = fields.Number()
    status = fields.Integer(allow_none=True)

    probes_finished = fields.Integer()
    probes_total = fields.Integer()

    results = fields.Nested(
        SRFileCliSchemaV2,
        attribute="files_ext",
        many=True,
        only=('result_id', 'name', 'size', 'path', 'status',)
    )

    @post_load
    def make_object(self, data):
        return Scan(**data)

# }}}


# {{{ OBJECTS

class ScanRetrievalCode:

    def __init__(self, external_id, scan=None):
        self.external_id = str(external_id)
        self.scan = scan

    @property
    def id(self):
        return self.external_id

    def __eq__(self, other):
        return isinstance(other, ScanRetrievalCode) and self.id == other.id

    def __ne__(self, other):
        return not (self == other)

# }}}
