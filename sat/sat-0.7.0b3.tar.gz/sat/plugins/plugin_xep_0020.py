#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0020
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

log = getLogger(__name__)
from sat.core import exceptions
from twisted.words.xish import domish

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import disco, iwokkel, data_form

NS_FEATURE_NEG = "http://jabber.org/protocol/feature-neg"

PLUGIN_INFO = {
    C.PI_NAME: "XEP 0020 Plugin",
    C.PI_IMPORT_NAME: "XEP-0020",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0020"],
    C.PI_MAIN: "XEP_0020",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Feature Negotiation"""),
}


class XEP_0020(object):
    def __init__(self, host):
        log.info(_("Plugin XEP_0020 initialization"))

    def getHandler(self, client):
        return XEP_0020_handler()

    def getFeatureElt(self, elt):
        """Check element's children to find feature elements

        @param elt(domish.Element): parent element of the feature element
        @return: feature elements
        @raise exceptions.NotFound: no feature element found
        """
        try:
            feature_elt = elt.elements(NS_FEATURE_NEG, "feature").next()
        except StopIteration:
            raise exceptions.NotFound
        return feature_elt

    def _getForm(self, elt, namespace):
        """Return the first child data form

        @param elt(domish.Element): parent of the data form
        @param namespace (None, unicode): form namespace or None to ignore
        @return (None, data_form.Form): data form or None is nothing is found
        """
        if namespace is None:
            try:
                form_elt = elt.elements(data_form.NS_X_DATA).next()
            except StopIteration:
                return None
            else:
                return data_form.Form.fromElement(form_elt)
        else:
            return data_form.findForm(elt, namespace)

    def getChoosedOptions(self, feature_elt, namespace):
        """Return choosed feature for feature element

        @param feature_elt(domish.Element): feature domish element
        @param namespace (None, unicode): form namespace or None to ignore
        @return (dict): feature name as key, and choosed option as value
        @raise exceptions.NotFound: not data form is found
        """
        form = self._getForm(feature_elt, namespace)
        if form is None:
            raise exceptions.NotFound
        result = {}
        for field in form.fields:
            values = form.fields[field].values
            result[field] = values[0] if values else None
            if len(values) > 1:
                log.warning(
                    _(
                        u"More than one value choosed for {}, keeping the first one"
                    ).format(field)
                )
        return result

    def negotiate(self, feature_elt, name, negotiable_values, namespace):
        """Negotiate the feature options

        @param feature_elt(domish.Element): feature element
        @param name: the option name (i.e. field's var attribute) to negotiate
        @param negotiable_values(iterable): acceptable values for this negotiation
            first corresponding value will be returned
        @param namespace (None, unicode): form namespace or None to ignore
        @raise KeyError: name is not found in data form fields
        """
        form = self._getForm(feature_elt, namespace)
        options = [option.value for option in form.fields[name].options]
        for value in negotiable_values:
            if value in options:
                return value
        return None

    def chooseOption(self, options, namespace):
        """Build a feature element with choosed options

        @param options(dict): dict with feature as key and choosed option as value
        @param namespace (None, unicode): form namespace or None to ignore
        """
        feature_elt = domish.Element((NS_FEATURE_NEG, "feature"))
        x_form = data_form.Form("submit", formNamespace=namespace)
        x_form.makeFields(options)
        feature_elt.addChild(x_form.toElement())
        return feature_elt

    def proposeFeatures(self, options_dict, namespace):
        """Build a feature element with options to propose

        @param options_dict(dict): dict with feature as key and iterable of acceptable options as value
        @param namespace(None, unicode): feature namespace
        """
        feature_elt = domish.Element((NS_FEATURE_NEG, "feature"))
        x_form = data_form.Form("form", formNamespace=namespace)
        for field in options_dict:
            x_form.addField(
                data_form.Field(
                    "list-single",
                    field,
                    options=[data_form.Option(option) for option in options_dict[field]],
                )
            )
        feature_elt.addChild(x_form.toElement())
        return feature_elt


class XEP_0020_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_FEATURE_NEG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
