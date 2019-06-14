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

from marshmallow import ValidationError

from .artifact import ArtifactSchema
from .file import FileSchema
from .tag import TagSchema


__all__ = (
    'apiid',
    'ArtifactSchema',
    'FileSchema',
    'TagSchema',
    'ValidationError',
)


from .artifact import Artifact
from .fileext import FileExt
from .file import File
from .scan import Scan
from .srcode import ScanRetrievalCode
from .tag import Tag


def apiid(obj):  # pragma: no cover
    if isinstance(
            obj, (Tag, File, FileExt, Scan, ScanRetrievalCode, Artifact)):
        return obj.id
    else:
        return obj
