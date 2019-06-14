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

from .helpers import timestamp_to_date


class FileSchema(Schema):
    size = fields.Integer()
    # we could create our own fields for hashes
    sha256 = fields.String()
    sha1 = fields.String()
    md5 = fields.String()

    timestamp_first_scan = fields.Number()
    timestamp_last_scan = fields.Number()
    mimetype = fields.String()
    tags = fields.Nested('TagSchema', many=True)

    @post_load
    def make_object(self, data):
        return File(**data)


class File:

    def __init__(
            self, sha256, *, size=None, sha1=None, md5=None,
            timestamp_first_scan=None, timestamp_last_scan=None,
            mimetype=None, tags=None):
        self.sha256 = sha256
        self.size = size
        self.sha1 = sha1
        self.md5 = md5

        self.timestamp_first_scan = timestamp_first_scan
        self.timestamp_last_scan = timestamp_last_scan

        self.mimetype = mimetype
        self.tags = tags or []

    @property
    def id(self):
        return self.sha256

    @property
    def pdate_first_scan(self):
        try:
            return timestamp_to_date(self.timestamp_first_scan)
        except TypeError:
            return None

    @property
    def pdate_last_scan(self):
        try:
            return timestamp_to_date(self.timestamp_last_scan)
        except TypeError:
            return None

    def __repr__(self):
        return "File." + self.id

    def __str__(self):
        ret = "File{"
        ret += "sha256: {}; ".format(self.sha256)
        # Do not display sha1 and md5 that are just noise in this context
        ret += "tags: [" + " ".join(t.text for t in self.tags) + "]; "
        if self.size is not None:
            ret += "size: {}; ".format(self.size)
        if self.timestamp_first_scan:
            ret += "first scan: {}; ".format(self.pdate_first_scan)
        if self.timestamp_last_scan:
            ret += "last scan: {0}; ".format(self.pdate_last_scan)
        if self.mimetype:
            ret += "mimetype: {0}; ".format(self.mimetype)
        ret += "}"
        return ret

    def __eq__(self, other):
        return isinstance(other, File) and self.id == other.id

    def __ne__(self, other):
        return not (self == other)
