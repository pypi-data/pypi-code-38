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


class ProbeSchema(Schema):
    name = fields.String()
    display_name = fields.String()
    category = fields.String()

    @post_load
    def make_object(self, data):
        return Probe(**data)


class Probe:

    def __init__(self, *, name, display_name, category):
        self.name = name
        self.display_name = display_name
        self.category = category

    @property
    def id(self):
        # TODO: edit when real probe objects are implemented
        raise NotImplementedError("Not a real Probe object")

    def __repr__(self):
        # TODO: edit when real probe objects are implemented
        return self.__class__.__name__ + "." + self.name

    def __str__(self):
        # TODO: edit when real probe objects are implemented
        ret = "Probe{"
        ret += "name: {}; ".format(self.name)
        ret += "display_name: {}; ".format(self.display_name)
        ret += "category: {}; ".format(self.category)
        ret += "}"
        return ret

    def __eq__(self, other):
        # TODO: edit when real probe objects are implemented
        return isinstance(other, Probe) and self.name == other.name

    def __ne__(self, other):
        return not (self == other)
