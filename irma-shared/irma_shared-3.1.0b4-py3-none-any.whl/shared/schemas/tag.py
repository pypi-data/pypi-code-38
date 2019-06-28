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

from marshmallow import fields, Schema, post_load


class TagSchema(Schema):
    id = fields.Integer()
    text = fields.String()

    @post_load
    def make_object(self, data):
        return Tag(**data)


class Tag:

    def __init__(self, id, text):
        self.id = id
        self.text = text

    def __repr__(self):
        return "Tag." + str(self.id)

    def __str__(self):
        return "Tag{" + "id: {}; text: {}; ".format(self.id, self.text) + "}"

    def __eq__(self, other):
        return (
            isinstance(other, Tag)
            and self.id == other.id
        )

    def __ne__(self, other):
        return not (self == other)
