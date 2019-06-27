#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin to detect language (experimental)
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions

try:
    from langid.langid import LanguageIdentifier, model
except ImportError:
    raise exceptions.MissingModule(
        u'Missing module langid, please download/install it with "pip install langid")'
    )

identifier = LanguageIdentifier.from_modelstring(model, norm_probs=False)


PLUGIN_INFO = {
    C.PI_NAME: "Language detection plugin",
    C.PI_IMPORT_NAME: "EXP-LANG-DETECT",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "LangDetect",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Detect and set message language when unknown"""),
}

CATEGORY = D_(u"Misc")
NAME = u"lang_detect"
LABEL = D_(u"language detection")
PARAMS = """
    <params>
    <individual>
    <category name="{category_name}">
        <param name="{name}" label="{label}" type="bool" value="true" />
    </category>
    </individual>
    </params>
    """.format(
    category_name=CATEGORY, name=NAME, label=_(LABEL)
)


class LangDetect(object):
    def __init__(self, host):
        log.info(_(u"Language detection plugin initialization"))
        self.host = host
        host.memory.updateParams(PARAMS)
        host.trigger.add("MessageReceived", self.MessageReceivedTrigger)
        host.trigger.add("sendMessage", self.MessageSendTrigger)

    def addLanguage(self, mess_data):
        message = mess_data["message"]
        if len(message) == 1 and message.keys()[0] == "":
            msg = message.values()[0]
            lang = identifier.classify(msg)[0]
            mess_data["message"] = {lang: msg}
        return mess_data

    def MessageReceivedTrigger(self, client, message_elt, post_treat):
        """ Check if source is linked and repeat message, else do nothing  """

        lang_detect = self.host.memory.getParamA(
            NAME, CATEGORY, profile_key=client.profile
        )
        if lang_detect:
            post_treat.addCallback(self.addLanguage)
        return True

    def MessageSendTrigger(self, client, data, pre_xml_treatments, post_xml_treatments):
        lang_detect = self.host.memory.getParamA(
            NAME, CATEGORY, profile_key=client.profile
        )
        if lang_detect:
            self.addLanguage(data)
        return True
