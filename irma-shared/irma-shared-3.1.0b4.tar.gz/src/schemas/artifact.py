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

from marshmallow import fields, Schema, post_load
from ..csts import ArtifactType


class ArtifactSchema(Schema):
    id = fields.UUID(attribute='external_id')
    sha256 = fields.String()
    type = fields.Integer()
    name = fields.String()
    mimetype = fields.String()
    size = fields.Integer()
    # TODO: maybe add a Nested('ProbeResultSchema') when ProbeResult is
    # refactored

    @post_load
    def make_object(self, data):
        return Artifact(**data)


class Artifact:

    def __init__(
            self, external_id, *, sha256, type, name=None, mimetype=None,
            size=0):
        self.external_id = str(external_id)
        self.sha256 = sha256
        self.type = ArtifactType(type)
        self.name = name
        self.mimetype = mimetype
        self.size = size

    @property
    def id(self):
        return self.external_id

    def __repr__(self):
        return 'Artifact.' + self.id

    def __str__(self):
        ret = "Artifact{"
        ret += "id: {}; ".format(self.id)
        ret += "sha256: {}; ".format(self.sha256)
        ret += "type: {}; ".format(self.type.name)
        if self.name:
            ret += "name: {}; ".format(self.name)
        ret += "size: {}; ".format(self.size)
        ret += "}"
        return ret

    def __eq__(self, other):
        return isinstance(other, Artifact) and self.id == other.id

    def __ne__(self, other):
        return not (self == other)
