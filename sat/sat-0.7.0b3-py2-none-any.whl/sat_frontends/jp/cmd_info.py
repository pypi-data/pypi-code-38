#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
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

import base
from sat.core.i18n import _
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import date_utils
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common

__commands__ = ["Info"]


class Disco(base.CommandBase):

    def __init__(self, host):
        extra_outputs = {'default': self.default_output}
        super(Disco, self).__init__(host, 'disco', use_output='complex', extra_outputs=extra_outputs, help=_('service discovery'))
        self.need_loop=True

    def add_parser_options(self):
        self.parser.add_argument(u"jid", type=base.unicode_decoder, help=_(u"entity to discover"))
        self.parser.add_argument(u"-t", u"--type", type=str, choices=('infos', 'items', 'both'), default='both', help=_(u"type of data to discover"))
        self.parser.add_argument(u"-n", u"--node", type=base.unicode_decoder, default=u'', help=_(u"node to use"))
        self.parser.add_argument(u"-C", u"--no-cache", dest='use_cache', action="store_false", help=_(u"ignore cache"))

    def start(self):
        self.get_infos = self.args.type in ('infos', 'both')
        self.get_items = self.args.type in ('items', 'both')
        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        if not self.get_infos:
            self.gotInfos(None, jid)
        else:
            self.host.bridge.discoInfos(jid, node=self.args.node, use_cache=self.args.use_cache, profile_key=self.host.profile, callback=lambda infos: self.gotInfos(infos, jid), errback=self.error)

    def error(self, failure):
        print (_("Error while doing discovery [%s]") % failure)
        self.host.quit(1)

    def gotInfos(self, infos, jid):
        if not self.get_items:
            self.gotItems(infos, None)
        else:
            self.host.bridge.discoItems(jid, node=self.args.node, use_cache=self.args.use_cache, profile_key=self.host.profile, callback=lambda items: self.gotItems(infos, items), errback=self.error)

    def gotItems(self, infos, items):
        data = {}

        if self.get_infos:
            features, identities, extensions = infos
            features.sort()
            identities.sort(key=lambda identity: identity[2])
            data.update({
                u'features': features,
                u'identities': identities,
                u'extensions': extensions})

        if self.get_items:
            items.sort(key=lambda item: item[2])
            data[u'items'] = items

        self.output(data)
        self.host.quit()

    def default_output(self, data):
        features = data.get(u'features', [])
        identities = data.get(u'identities', [])
        extensions = data.get(u'extensions', {})
        items = data.get(u'items', [])

        identities_table = common.Table(self.host,
                                        identities,
                                        headers=(_(u'category'),
                                                 _(u'type'),
                                                 _(u'name')),
                                        use_buffer=True)

        extensions_tpl = []
        extensions_types = extensions.keys()
        extensions_types.sort()
        for type_ in extensions_types:
            fields = []
            for field in extensions[type_]:
                field_lines = []
                data, values = field
                data_keys = data.keys()
                data_keys.sort()
                for key in data_keys:
                    field_lines.append(A.color(u'\t', C.A_SUBHEADER, key, A.RESET, u': ',
                                               data[key]))
                if len(values) == 1:
                    field_lines.append(A.color(u'\t', C.A_SUBHEADER, u"value", A.RESET,
                                               u': ', values[0] or (A.BOLD + u"UNSET")))
                elif len(values) > 1:
                    field_lines.append(A.color(u'\t', C.A_SUBHEADER, u"values", A.RESET,
                                               u': '))

                    for value in values:
                        field_lines.append(A.color(u'\t  - ', A.BOLD, value))
                fields.append(u'\n'.join(field_lines))
            extensions_tpl.append(u'{type_}\n{fields}'.format(type_=type_,
                                                              fields='\n\n'.join(fields)))

        items_table = common.Table(self.host,
                                   items,
                                   headers=(_(u'entity'),
                                            _(u'node'),
                                            _(u'name')),
                                   use_buffer=True)

        template = []
        if features:
            template.append(A.color(C.A_HEADER, _(u"Features")) + u"\n\n{features}")
        if identities:
            template.append(A.color(C.A_HEADER, _(u"Identities")) + u"\n\n{identities}")
        if extensions:
            template.append(A.color(C.A_HEADER, _(u"Extensions")) + u"\n\n{extensions}")
        if items:
            template.append(A.color(C.A_HEADER, _(u"Items")) + u"\n\n{items}")

        print u"\n\n".join(template).format(features = u'\n'.join(features),
                                            identities = identities_table.display().string,
                                            extensions = u'\n'.join(extensions_tpl),
                                            items = items_table.display().string,
                                           )


class Version(base.CommandBase):

    def __init__(self, host):
        super(Version, self).__init__(host, 'version', help=_('software version'))
        self.need_loop=True

    def add_parser_options(self):
        self.parser.add_argument("jid", type=str, help=_("Entity to request"))

    def start(self):
        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        self.host.bridge.getSoftwareVersion(jid, self.host.profile, callback=self.gotVersion, errback=self.error)

    def error(self, failure):
        print (_("Error while trying to get version [%s]") % failure)
        self.host.quit(1)

    def gotVersion(self, data):
        infos = []
        name, version, os = data
        if name:
            infos.append(_("Software name: %s") %  name)
        if version:
            infos.append(_("Software version: %s") %  version)
        if os:
            infos.append(_("Operating System: %s") %  os)

        print "\n".join(infos)
        self.host.quit()


class Session(base.CommandBase):

    def __init__(self, host):
        extra_outputs = {'default': self.default_output}
        super(Session, self).__init__(host, 'session', use_output='dict', extra_outputs=extra_outputs, help=_('running session'))
        self.need_loop=True

    def default_output(self, data):
        started = data['started']
        data['started'] = u'{short} (UTC, {relative})'.format(
            short=date_utils.date_fmt(started),
            relative=date_utils.date_fmt(started, 'relative'))
        self.host.output(C.OUTPUT_DICT, 'simple', {}, data)

    def add_parser_options(self):
        pass

    def start(self):
        self.host.bridge.sessionInfosGet(self.host.profile, callback=self._sessionInfoGetCb, errback=self._sessionInfoGetEb)

    def _sessionInfoGetCb(self, data):
        self.output(data)
        self.host.quit()

    def _sessionInfoGetEb(self, error_data):
        self.disp(_(u'Error getting session infos: {}').format(error_data), error=True)
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)


class Info(base.CommandBase):
    subcommands = (Disco, Version, Session)

    def __init__(self, host):
        super(Info, self).__init__(host, 'info', use_profile=False, help=_('Get various pieces of information on entities'))
