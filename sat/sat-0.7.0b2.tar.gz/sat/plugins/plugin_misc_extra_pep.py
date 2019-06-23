#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for displaying messages from extra PEP services
# Copyright (C) 2015 Adrien Cossa (souliane@mailoo.org)

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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.memory import params
from twisted.words.protocols.jabber import jid


PLUGIN_INFO = {
    C.PI_NAME: "Extra PEP",
    C.PI_IMPORT_NAME: "EXTRA-PEP",
    C.PI_TYPE: "MISC",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "ExtraPEP",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Display messages from extra PEP services"""),
}


PARAM_KEY = u"Misc"
PARAM_NAME = u"blogs"
PARAM_LABEL = u"Blog authors following list"
PARAM_DEFAULT = (jid.JID("salut-a-toi@libervia.org"),)


class ExtraPEP(object):

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(param_name)s" label="%(param_label)s" type="jids_list" security="0">
            %(jids)s
        </param>
     </category>
    </individual>
    </params>
    """ % {
        "category_name": PARAM_KEY,
        "category_label": D_(PARAM_KEY),
        "param_name": PARAM_NAME,
        "param_label": D_(PARAM_LABEL),
        "jids": u"\n".join({elt.toXml() for elt in params.createJidElts(PARAM_DEFAULT)}),
    }

    def __init__(self, host):
        log.info(_(u"Plugin Extra PEP initialization"))
        self.host = host
        host.memory.updateParams(self.params)

    def getFollowedEntities(self, profile_key):
        return self.host.memory.getParamA(PARAM_NAME, PARAM_KEY, profile_key=profile_key)
