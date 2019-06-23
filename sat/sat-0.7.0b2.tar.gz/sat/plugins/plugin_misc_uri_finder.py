#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin to find URIs
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.internet import defer
import textwrap
log = getLogger(__name__)
import json
import os.path
import os
import re

PLUGIN_INFO = {
    C.PI_NAME: _("URI finder"),
    C.PI_IMPORT_NAME: "uri_finder",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "URIFinder",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: textwrap.dedent(_(u"""\
    Plugin to find URIs in well know location.
    This allows to retrieve settings to work with a project (e.g. pubsub node used for merge-requests).
    """))
}


SEARCH_FILES = ('readme', 'contributing')


class URIFinder(object):

    def __init__(self, host):
        log.info(_(u"URI finder plugin initialization"))
        self.host = host
        host.bridge.addMethod("URIFind", ".plugin",
                              in_sign='sas', out_sign='a{sa{ss}}',
                              method=self.find,
                              async=True)

    def find(self, path, keys):
        """Look for URI in well known locations

        @param path(unicode): path to start with
        @param keys(list[unicode]): keys lookeds after
            e.g.: "tickets", "merge-requests"
        @return (dict[unicode, unicode]): map from key to found uri
        """
        keys_re = u'|'.join(keys)
        label_re = r'"(?P<label>[^"]+)"'
        uri_re = re.compile(ur'(?P<key>{keys_re})[ :]? +(?P<uri>xmpp:\S+)(?:.*use {label_re} label)?'.format(
            keys_re=keys_re, label_re = label_re))
        path = os.path.normpath(path)
        if not os.path.isdir(path) or not os.path.isabs(path):
            raise ValueError(u'path must be an absolute path to a directory')

        found_uris = {}
        while path != u'/':
            for filename in os.listdir(path):
                name, __ = os.path.splitext(filename)
                if name.lower() in SEARCH_FILES:
                    file_path = os.path.join(path, filename)
                    with open(file_path) as f:
                        for m in uri_re.finditer(f.read()):
                            key = m.group(u'key')
                            uri = m.group(u'uri')
                            label = m.group(u'label')
                            if key in found_uris:
                                log.warning(_(u"Ignoring already found uri for key \"{key}\"").format(key=key))
                            else:
                                uri_data = found_uris[key] = {u'uri': uri}
                                if label is not None:
                                    uri_data[u'labels'] = json.dumps([label])
            if found_uris:
                break
            path = os.path.dirname(path)

        return defer.succeed(found_uris)
