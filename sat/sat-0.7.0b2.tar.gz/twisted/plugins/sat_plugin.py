#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)

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

from twisted.internet import defer
if defer.Deferred.debug:
    # if we are in debug mode, we want to use ipdb instead of pdb
    try:
        import ipdb
        import pdb
        pdb.set_trace = ipdb.set_trace
        pdb.post_mortem = ipdb.post_mortem
    except ImportError:
        pass

from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

# XXX: We need to configure logs before any log method is used, so here is the best place.
from sat.core.constants import Const as C
from sat.core.i18n import _


def initialise(options):
    """Method to initialise global modules"""
    # XXX: We need to configure logs before any log method is used, so here is the best place.
    from sat.core import log_config
    log_config.satConfigure(C.LOG_BACKEND_TWISTED, C, backend_data=options)


class Options(usage.Options):
    optParameters = []


class SatMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = C.APP_NAME_FILE
    description = _(u"%s XMPP client backend") % C.APP_NAME_FULL
    options = Options

    def makeService(self, options):
        from twisted.internet import gireactor
        gireactor.install()
        # XXX: SAT must be imported after log configuration, because it write stuff to logs
        initialise(options.parent)
        from sat.core.sat_main import SAT
        return SAT()


serviceMaker = SatMaker()
