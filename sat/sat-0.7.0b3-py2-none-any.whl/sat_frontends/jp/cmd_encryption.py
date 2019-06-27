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

from sat_frontends.jp import base
from sat_frontends.jp.constants import Const as C
from sat.core.i18n import _
from functools import partial
from sat.tools.common import data_format
from sat_frontends.jp import xmlui_manager

__commands__ = ["Encryption"]


class EncryptionAlgorithms(base.CommandBase):

    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        super(EncryptionAlgorithms, self).__init__(
            host, "algorithms",
            use_output=C.OUTPUT_LIST_DICT,
            extra_outputs=extra_outputs,
            use_profile=False,
            help=_("show available encryption algorithms"))
        self.need_loop = True

    def add_parser_options(self):
        pass

    def encryptionPluginsGetCb(self, plugins):
        self.output(plugins)
        self.host.quit()

    def default_output(self, plugins):
        if not plugins:
            self.disp(_(u"No encryption plugin registered!"))
            self.host.quit(C.EXIT_NOT_FOUND)
        else:
            self.disp(_(u"Following encryption algorithms are available: {algos}").format(
                algos=', '.join([p['name'] for p in plugins])))
            self.host.quit()

    def start(self):
        self.host.bridge.encryptionPluginsGet(
            callback=self.encryptionPluginsGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't retrieve plugins: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class EncryptionGet(base.CommandBase):

    def __init__(self, host):
        super(EncryptionGet, self).__init__(
            host, "get",
            use_output=C.OUTPUT_DICT,
            help=_(u"get encryption session data"))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder,
            help=_(u"jid of the entity to check")
        )

    def messageEncryptionGetCb(self, serialised):
        session_data = data_format.deserialise(serialised)
        if session_data is None:
            self.disp(
                u"No encryption session found, the messages are sent in plain text.")
            self.host.quit(C.EXIT_NOT_FOUND)
        self.output(session_data)
        self.host.quit()

    def start(self):
        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        self.host.bridge.messageEncryptionGet(
            jid, self.profile,
            callback=self.messageEncryptionGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get session: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class EncryptionStart(base.CommandBase):

    def __init__(self, host):
        super(EncryptionStart, self).__init__(
            host, "start",
            help=_(u"start encrypted session with an entity"))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "--encrypt-noreplace",
            action="store_true",
            help=_(u"don't replace encryption algorithm if an other one is already used"))
        algorithm = self.parser.add_mutually_exclusive_group()
        algorithm.add_argument(
            "-n", "--name", help=_(u"algorithm name (DEFAULT: choose automatically)"))
        algorithm.add_argument(
            "-N", "--namespace",
            help=_(u"algorithm namespace (DEFAULT: choose automatically)"))
        self.parser.add_argument(
            "jid", type=base.unicode_decoder,
            help=_(u"jid of the entity to stop encrypted session with")
        )

    def encryptionNamespaceGetCb(self, namespace):
        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        self.host.bridge.messageEncryptionStart(
            jid, namespace, not self.args.encrypt_noreplace,
            self.profile,
            callback=self.host.quit,
            errback=partial(self.errback,
                            msg=_(u"Can't start encryption session: {}"),
                            exit_code=C.EXIT_BRIDGE_ERRBACK,
                            ))

    def start(self):
        if self.args.name is not None:
            self.host.bridge.encryptionNamespaceGet(self.args.name,
                callback=self.encryptionNamespaceGetCb,
                errback=partial(self.errback,
                                msg=_(u"Can't get encryption namespace: {}"),
                                exit_code=C.EXIT_BRIDGE_ERRBACK,
                                ))
        elif self.args.namespace is not None:
            self.encryptionNamespaceGetCb(self.args.namespace)
        else:
            self.encryptionNamespaceGetCb(u"")


class EncryptionStop(base.CommandBase):

    def __init__(self, host):
        super(EncryptionStop, self).__init__(
            host, "stop",
            help=_(u"stop encrypted session with an entity"))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder,
            help=_(u"jid of the entity to stop encrypted session with")
        )

    def start(self):
        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        self.host.bridge.messageEncryptionStop(
            jid, self.profile,
            callback=self.host.quit,
            errback=partial(
                self.errback,
                msg=_(u"can't end encrypted session: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class TrustUI(base.CommandBase):

    def __init__(self, host):
        super(TrustUI, self).__init__(
            host, "ui",
            help=_(u"get UI to manage trust"))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder,
            help=_(u"jid of the entity to stop encrypted session with")
        )
        algorithm = self.parser.add_mutually_exclusive_group()
        algorithm.add_argument(
            "-n", "--name", help=_(u"algorithm name (DEFAULT: current algorithm)"))
        algorithm.add_argument(
            "-N", "--namespace",
            help=_(u"algorithm namespace (DEFAULT: current algorithm)"))

    def encryptionTrustUIGetCb(self, xmlui_raw):
        xmlui = xmlui_manager.create(self.host, xmlui_raw)
        xmlui.show()
        xmlui.submitForm()

    def encryptionNamespaceGetCb(self, namespace):
        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        self.host.bridge.encryptionTrustUIGet(
            jid, namespace, self.profile,
            callback=self.encryptionTrustUIGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't end encrypted session: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def start(self):
        if self.args.name is not None:
            self.host.bridge.encryptionNamespaceGet(self.args.name,
                callback=self.encryptionNamespaceGetCb,
                errback=partial(self.errback,
                                msg=_(u"Can't get encryption namespace: {}"),
                                exit_code=C.EXIT_BRIDGE_ERRBACK,
                                ))
        elif self.args.namespace is not None:
            self.encryptionNamespaceGetCb(self.args.namespace)
        else:
            self.encryptionNamespaceGetCb(u"")


class EncryptionTrust(base.CommandBase):
    subcommands = (TrustUI,)

    def __init__(self, host):
        super(EncryptionTrust, self).__init__(
            host, "trust", use_profile=False, help=_(u"trust manangement")
        )


class Encryption(base.CommandBase):
    subcommands = (EncryptionAlgorithms, EncryptionGet, EncryptionStart, EncryptionStop,
                   EncryptionTrust)

    def __init__(self, host):
        super(Encryption, self).__init__(
            host, "encryption", use_profile=False, help=_(u"encryption sessions handling")
        )
