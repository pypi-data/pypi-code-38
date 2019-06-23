#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

""" XMPP uri parsing tools """

import urlparse
import urllib

# FIXME: basic implementation, need to follow RFC 5122


def parseXMPPUri(uri):
    """Parse an XMPP uri and return a dict with various information

    @param uri(unicode): uri to parse
    @return dict(unicode, unicode): data depending of the URI where key can be:
        type: one of ("pubsub", TODO)
            type is always present
        sub_type: can be:
            - microblog
            only used for pubsub for now
        path: XMPP path (jid of the service or entity)
        node: node used
        id: id of the element (item for pubsub)
    @raise ValueError: the scheme is not xmpp
    """
    uri_split = urlparse.urlsplit(uri.encode("utf-8"))
    if uri_split.scheme != "xmpp":
        raise ValueError(u"this is not a XMPP URI")

    # XXX: we don't use jid.JID for path as it can be used both in backend and frontend
    # which may use different JID classes
    data = {u"path": urllib.unquote(uri_split.path).decode("utf-8")}

    query_end = uri_split.query.find(";")
    query_type = uri_split.query[:query_end]
    if query_end == -1 or "=" in query_type:
        raise ValueError("no query type, invalid XMPP URI")

    pairs = urlparse.parse_qs(uri_split.geturl())
    for k, v in pairs.items():
        if len(v) != 1:
            raise NotImplementedError(u"multiple values not managed")
        if k in ("path", "type", "sub_type"):
            raise NotImplementedError(u"reserved key used in URI, this is not supported")
        data[k.decode("utf-8")] = urllib.unquote(v[0]).decode("utf-8")

    if query_type:
        data[u"type"] = query_type.decode("utf-8")
    elif u"node" in data:
        data[u"type"] = u"pubsub"
    else:
        data[u"type"] = ""

    if u"node" in data:
        if data[u"node"].startswith(u"urn:xmpp:microblog:"):
            data[u"sub_type"] = "microblog"

    return data


def addPairs(uri, pairs):
    for k, v in pairs.iteritems():
        uri.append(
            u";"
            + urllib.quote_plus(k.encode("utf-8"))
            + u"="
            + urllib.quote_plus(v.encode("utf-8"))
        )


def buildXMPPUri(type_, **kwargs):
    uri = [u"xmpp:"]
    subtype = kwargs.pop("subtype", None)
    path = kwargs.pop("path")
    uri.append(urllib.quote_plus(path.encode("utf-8")).replace(u"%40", "@"))

    if type_ == u"pubsub":
        if subtype == "microblog" and not kwargs.get("node"):
            kwargs[u"node"] = "urn:xmpp:microblog:0"
        if kwargs:
            uri.append(u"?")
            addPairs(uri, kwargs)
    else:
        raise NotImplementedError(u"{type_} URI are not handled yet".format(type_=type_))

    return u"".join(uri)
