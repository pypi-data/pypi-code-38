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

from marshmallow import Schema, fields, post_load

from .artifact import ArtifactSchema
from .file import FileSchema
from .fileext import (
        FileCliSchemaV3 as FileCliSchema,
        FileExtSchemaV3 as FileExtSchema,
        FileKioskSchemaV3 as FileKioskSchema,
        FileProbeResultSchemaV3 as FileProbeResultSchema,
        FileSuricataSchemaV3 as FileSuricataSchema,
)
from .probe import ProbeSchema
from .scan import ScanSchemaV3 as ScanSchema
from .srcode import ScanRetrievalCodeSchemaV3 as ScanRetrievalCodeSchema
from .tag import TagSchema


__all__ = (
    'ArtifactSchema',
    'FileCliSchema',
    'FileExtSchema',
    'FileKioskSchema',
    'FileProbeResultSchema',
    'FileResultSchema',
    'FileSchema',
    'FileSuricataSchema',
    'Paginated',
    'ProbeSchema',
    'ScanRetrievalCodeSchema',
    'ScanSchema',
    'TagSchema',
)


class Paginated(type):
    def __new__(_, enclosed, **extra):
        class Page(Schema):
            offset = fields.Integer(allow_none=True)
            limit = fields.Integer(allow_none=True)
            total = fields.Integer()
            items = fields.Nested(enclosed, many=True, **extra)
            # NOTE: APIv3 no longer use the 'data' field

        Page.__name__ = "Paginated{}".format(enclosed.__name__)
        return Page


class FileResultSchema(Paginated(
        FileExtSchema,
        exclude=('probe_results', 'file'))):
    file = fields.Nested(FileSchema)

    @post_load
    def extend(self, data):
        for fe in data["items"]:
            fe.file = data["file"]
        return data
