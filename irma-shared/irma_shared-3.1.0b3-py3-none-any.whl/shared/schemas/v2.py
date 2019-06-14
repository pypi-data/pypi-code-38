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

from marshmallow import Schema, fields

from .file import FileSchema
from .fileext import (
        FileCliSchemaV2 as FileCliSchema,
        FileExtSchemaV2 as FileExtSchema,
        FileKioskSchemaV2 as FileKioskSchema,
        FileProbeResultSchemaV2 as FileProbeResultSchema,
        FileSuricataSchemaV2 as FileSuricataSchema,
)
from .scan import ScanSchemaV2 as ScanSchema
from .srcode import (
        SRScanSchemaV2 as SRScanSchema,
        ScanRetrievalCodeSchemaV2 as ScanRetrievalCodeSchema,
)
from .tag import TagSchema


__all__ = (
    'FileCliSchema',
    'FileExtSchema',
    'FileKioskSchema',
    'FileProbeResultSchema',
    'FileResultSchema',
    'FileSchema',
    'FileSuricataSchema',
    'Paginated',
    'ScanRetrievalCodeSchema',
    'ScanSchema',
    'SRScanSchema',
    'TagSchema',
)


class Paginated(type):
    def __new__(_, enclosed, **extra):
        class Page(Schema):
            offset = fields.Integer()
            limit = fields.Integer()
            total = fields.Integer()
            # NOTE: IRMA API is non consistent about the field it puts its
            # results in. This behavior has been removed in v3
            data = fields.Nested(enclosed, many=True, **extra)
            items = fields.Nested(enclosed, many=True, **extra)

        Page.__name__ = "PaginatedV2{}".format(enclosed.__name__)
        return Page


class FileResultSchema(Paginated(
        FileExtSchema,
        exclude=('probe_results', 'file_infos'))):
    file_infos = fields.Nested(FileSchema)
