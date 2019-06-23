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


# hack to use this module with pyjamas
try:
    unicode("")  # XXX: unicode doesn't exist in pyjamas

    # normal version
    class BaseJID(unicode):
        def __new__(cls, jid_str):
            self = unicode.__new__(cls, cls._normalize(jid_str))
            return self

        def __init__(self, jid_str):
            pass

        def _parse(self):
            """Find node domain and resource"""
            node_end = self.find("@")
            if node_end < 0:
                node_end = 0
            domain_end = self.find("/")
            if domain_end == 0:
                raise ValueError("a jid can't start with '/'")
            if domain_end == -1:
                domain_end = len(self)
            self.node = self[:node_end] or None
            self.domain = self[(node_end + 1) if node_end else 0 : domain_end]
            self.resource = self[domain_end + 1 :] or None


except (
    TypeError,
    AttributeError,
):  # Error raised is not the same depending on pyjsbuild options

    # pyjamas version
    class BaseJID(object):
        def __init__(self, jid_str):
            self.__internal_str = JID._normalize(jid_str)

        def __str__(self):
            return self.__internal_str

        def __getattr__(self, name):
            return getattr(self.__internal_str, name)

        def __eq__(self, other):
            if not isinstance(other, JID):
                return False
            return (
                self.node == other.node
                and self.domain == other.domain
                and self.resource == other.resource
            )

        def __hash__(self):
            return hash("JID<{}>".format(self.__internal_str))

        def find(self, *args):
            return self.__internal_str.find(*args)

        def _parse(self):
            """Find node domain and resource"""
            node_end = self.__internal_str.find("@")
            if node_end < 0:
                node_end = 0
            domain_end = self.__internal_str.find("/")
            if domain_end == 0:
                raise ValueError("a jid can't start with '/'")
            if domain_end == -1:
                domain_end = len(self.__internal_str)
            self.node = self.__internal_str[:node_end] or None
            self.domain = self.__internal_str[
                (node_end + 1) if node_end else 0 : domain_end
            ]
            self.resource = self.__internal_str[domain_end + 1 :] or None


class JID(BaseJID):
    """This class help manage JID (Node@Domaine/Resource)"""

    def __init__(self, jid_str):
        super(JID, self).__init__(jid_str)
        self._parse()

    @staticmethod
    def _normalize(jid_str):
        """Naive normalization before instantiating and parsing the JID"""
        if not jid_str:
            return jid_str
        tokens = jid_str.split("/")
        tokens[0] = tokens[0].lower()  # force node and domain to lower-case
        return "/".join(tokens)

    @property
    def bare(self):
        if not self.node:
            return JID(self.domain)
        return JID(u"{}@{}".format(self.node, self.domain))

    def is_valid(self):
        """
        @return: True if the JID is XMPP compliant
        """
        # TODO: implement real check, according to the RFC http://tools.ietf.org/html/rfc6122
        return self.domain != ""


def newResource(entity, resource):
    """Build a new JID from the given entity and resource.

    @param entity (JID): original JID
    @param resource (unicode): new resource
    @return: a new JID instance
    """
    return JID(u"%s/%s" % (entity.bare, resource))
