#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Jabber Search (xep-0055)
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
from sat.core.log import getLogger

log = getLogger(__name__)

from twisted.words.protocols.jabber.xmlstream import IQ
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from wokkel import data_form
from sat.core.constants import Const as C
from sat.core.exceptions import DataError
from sat.tools import xml_tools

from wokkel import disco, iwokkel

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler
from zope.interface import implements


NS_SEARCH = "jabber:iq:search"

PLUGIN_INFO = {
    C.PI_NAME: "Jabber Search",
    C.PI_IMPORT_NAME: "XEP-0055",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0055"],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: ["XEP-0059"],
    C.PI_MAIN: "XEP_0055",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of Jabber Search"""),
}

# config file parameters
CONFIG_SECTION = "plugin search"
CONFIG_SERVICE_LIST = "service_list"

DEFAULT_SERVICE_LIST = ["salut.libervia.org"]

FIELD_SINGLE = "field_single"  # single text field for the simple search
FIELD_CURRENT_SERVICE = (
    "current_service_jid"
)  # read-only text field for the advanced search


class XEP_0055(object):
    def __init__(self, host):
        log.info(_("Jabber search plugin initialization"))
        self.host = host

        # default search services (config file + hard-coded lists)
        self.services = [
            jid.JID(entry)
            for entry in host.memory.getConfig(
                CONFIG_SECTION, CONFIG_SERVICE_LIST, DEFAULT_SERVICE_LIST
            )
        ]

        host.bridge.addMethod(
            "searchGetFieldsUI",
            ".plugin",
            in_sign="ss",
            out_sign="s",
            method=self._getFieldsUI,
            async=True,
        )
        host.bridge.addMethod(
            "searchRequest",
            ".plugin",
            in_sign="sa{ss}s",
            out_sign="s",
            method=self._searchRequest,
            async=True,
        )

        self.__search_menu_id = host.registerCallback(self._getMainUI, with_data=True)
        host.importMenu(
            (D_("Contacts"), D_("Search directory")),
            self._getMainUI,
            security_limit=1,
            help_string=D_("Search user directory"),
        )

    def _getHostServices(self, profile):
        """Return the jabber search services associated to the user host.

        @param profile (unicode): %(doc_profile)s
        @return: list[jid.JID]
        """
        client = self.host.getClient(profile)
        d = self.host.findFeaturesSet(client, [NS_SEARCH])
        return d.addCallback(lambda set_: list(set_))

    ## Main search UI (menu item callback) ##

    def _getMainUI(self, raw_data, profile):
        """Get the XMLUI for selecting a service and searching the directory.

        @param raw_data (dict): data received from the frontend
        @param profile (unicode): %(doc_profile)s
        @return: a deferred XMLUI string representation
        """
        # check if the user's server offers some search services
        d = self._getHostServices(profile)
        return d.addCallback(lambda services: self.getMainUI(services, raw_data, profile))

    def getMainUI(self, services, raw_data, profile):
        """Get the XMLUI for selecting a service and searching the directory.

        @param services (list[jid.JID]): search services offered by the user server
        @param raw_data (dict): data received from the frontend
        @param profile (unicode): %(doc_profile)s
        @return: a deferred XMLUI string representation
        """
        # extend services offered by user's server with the default services
        services.extend([service for service in self.services if service not in services])
        data = xml_tools.XMLUIResult2DataFormResult(raw_data)
        main_ui = xml_tools.XMLUI(
            C.XMLUI_WINDOW,
            container="tabs",
            title=_("Search users"),
            submit_id=self.__search_menu_id,
        )

        d = self._addSimpleSearchUI(services, main_ui, data, profile)
        d.addCallback(
            lambda __: self._addAdvancedSearchUI(services, main_ui, data, profile)
        )
        return d.addCallback(lambda __: {"xmlui": main_ui.toXml()})

    def _addSimpleSearchUI(self, services, main_ui, data, profile):
        """Add to the main UI a tab for the simple search.

        Display a single input field and search on the main service (it actually does one search per search field and then compile the results).

        @param services (list[jid.JID]): search services offered by the user server
        @param main_ui (XMLUI): the main XMLUI instance
        @param data (dict): form data without SAT_FORM_PREFIX
        @param profile (unicode): %(doc_profile)s

        @return: a __ Deferred
        """
        service_jid = services[
            0
        ]  # TODO: search on all the given services, not only the first one

        form = data_form.Form("form", formNamespace=NS_SEARCH)
        form.addField(
            data_form.Field(
                "text-single",
                FIELD_SINGLE,
                label=_("Search for"),
                value=data.get(FIELD_SINGLE, ""),
            )
        )

        sub_cont = main_ui.main_container.addTab(
            "simple_search",
            label=_("Simple search"),
            container=xml_tools.VerticalContainer,
        )
        main_ui.changeContainer(sub_cont.append(xml_tools.PairsContainer(main_ui)))
        xml_tools.dataForm2Widgets(main_ui, form)

        # FIXME: add colspan attribute to divider? (we are in a PairsContainer)
        main_ui.addDivider("blank")
        main_ui.addDivider("blank")  # here we added a blank line before the button
        main_ui.addDivider("blank")
        main_ui.addButton(self.__search_menu_id, _("Search"), (FIELD_SINGLE,))
        main_ui.addDivider("blank")
        main_ui.addDivider("blank")  # a blank line again after the button

        simple_data = {
            key: value for key, value in data.iteritems() if key in (FIELD_SINGLE,)
        }
        if simple_data:
            log.debug("Simple search with %s on %s" % (simple_data, service_jid))
            sub_cont.parent.setSelected(True)
            main_ui.changeContainer(sub_cont.append(xml_tools.VerticalContainer(main_ui)))
            main_ui.addDivider("dash")
            d = self.searchRequest(service_jid, simple_data, profile)
            d.addCallbacks(
                lambda elt: self._displaySearchResult(main_ui, elt),
                lambda failure: main_ui.addText(failure.getErrorMessage()),
            )
            return d

        return defer.succeed(None)

    def _addAdvancedSearchUI(self, services, main_ui, data, profile):
        """Add to the main UI a tab for the advanced search.

        Display a service selector and allow to search on all the fields that are implemented by the selected service.

        @param services (list[jid.JID]): search services offered by the user server
        @param main_ui (XMLUI): the main XMLUI instance
        @param data (dict): form data without SAT_FORM_PREFIX
        @param profile (unicode): %(doc_profile)s

        @return: a __ Deferred
        """
        sub_cont = main_ui.main_container.addTab(
            "advanced_search",
            label=_("Advanced search"),
            container=xml_tools.VerticalContainer,
        )
        service_selection_fields = ["service_jid", "service_jid_extra"]

        if "service_jid_extra" in data:
            # refresh button has been pushed, select the tab
            sub_cont.parent.setSelected(True)
            # get the selected service
            service_jid_s = data.get("service_jid_extra", "")
            if not service_jid_s:
                service_jid_s = data.get("service_jid", unicode(services[0]))
            log.debug("Refreshing search fields for %s" % service_jid_s)
        else:
            service_jid_s = data.get(FIELD_CURRENT_SERVICE, unicode(services[0]))
        services_s = [unicode(service) for service in services]
        if service_jid_s not in services_s:
            services_s.append(service_jid_s)

        main_ui.changeContainer(sub_cont.append(xml_tools.PairsContainer(main_ui)))
        main_ui.addLabel(_("Search on"))
        main_ui.addList("service_jid", options=services_s, selected=service_jid_s)
        main_ui.addLabel(_("Other service"))
        main_ui.addString(name="service_jid_extra")

        # FIXME: add colspan attribute to divider? (we are in a PairsContainer)
        main_ui.addDivider("blank")
        main_ui.addDivider("blank")  # here we added a blank line before the button
        main_ui.addDivider("blank")
        main_ui.addButton(
            self.__search_menu_id, _("Refresh fields"), service_selection_fields
        )
        main_ui.addDivider("blank")
        main_ui.addDivider("blank")  # a blank line again after the button
        main_ui.addLabel(_("Displaying the search form for"))
        main_ui.addString(name=FIELD_CURRENT_SERVICE, value=service_jid_s, read_only=True)
        main_ui.addDivider("dash")
        main_ui.addDivider("dash")

        main_ui.changeContainer(sub_cont.append(xml_tools.VerticalContainer(main_ui)))
        service_jid = jid.JID(service_jid_s)
        d = self.getFieldsUI(service_jid, profile)
        d.addCallbacks(
            self._addAdvancedForm,
            lambda failure: main_ui.addText(failure.getErrorMessage()),
            [service_jid, main_ui, sub_cont, data, profile],
        )
        return d

    def _addAdvancedForm(self, form_elt, service_jid, main_ui, sub_cont, data, profile):
        """Add the search form and the search results (if there is some to display).

        @param form_elt (domish.Element): form element listing the fields
        @param service_jid (jid.JID): current search service
        @param main_ui (XMLUI): the main XMLUI instance
        @param sub_cont (Container): the container of the current tab
        @param data (dict): form data without SAT_FORM_PREFIX
        @param profile (unicode): %(doc_profile)s

        @return: a __ Deferred
        """
        field_list = data_form.Form.fromElement(form_elt).fieldList
        adv_fields = [field.var for field in field_list if field.var]
        adv_data = {key: value for key, value in data.iteritems() if key in adv_fields}

        xml_tools.dataForm2Widgets(main_ui, data_form.Form.fromElement(form_elt))

        # refill the submitted values
        # FIXME: wokkel's data_form.Form.fromElement doesn't parse the values, so we do it directly in XMLUI for now
        for widget in main_ui.current_container.elem.childNodes:
            name = widget.getAttribute("name")
            if adv_data.get(name):
                widget.setAttribute("value", adv_data[name])

        # FIXME: add colspan attribute to divider? (we are in a PairsContainer)
        main_ui.addDivider("blank")
        main_ui.addDivider("blank")  # here we added a blank line before the button
        main_ui.addDivider("blank")
        main_ui.addButton(
            self.__search_menu_id, _("Search"), adv_fields + [FIELD_CURRENT_SERVICE]
        )
        main_ui.addDivider("blank")
        main_ui.addDivider("blank")  # a blank line again after the button

        if adv_data:  # display the search results
            log.debug("Advanced search with %s on %s" % (adv_data, service_jid))
            sub_cont.parent.setSelected(True)
            main_ui.changeContainer(sub_cont.append(xml_tools.VerticalContainer(main_ui)))
            main_ui.addDivider("dash")
            d = self.searchRequest(service_jid, adv_data, profile)
            d.addCallbacks(
                lambda elt: self._displaySearchResult(main_ui, elt),
                lambda failure: main_ui.addText(failure.getErrorMessage()),
            )
            return d

        return defer.succeed(None)

    def _displaySearchResult(self, main_ui, elt):
        """Display the search results.

        @param main_ui (XMLUI): the main XMLUI instance
        @param elt (domish.Element):  form result element
        """
        if [child for child in elt.children if child.name == "item"]:
            headers, xmlui_data = xml_tools.dataFormEltResult2XMLUIData(elt)
            if "jid" in headers:  # use XMLUI JidsListWidget to display the results
                values = {}
                for i in range(len(xmlui_data)):
                    header = headers.keys()[i % len(headers)]
                    widget_type, widget_args, widget_kwargs = xmlui_data[i]
                    value = widget_args[0]
                    values.setdefault(header, []).append(
                        jid.JID(value) if header == "jid" else value
                    )
                main_ui.addJidsList(jids=values["jid"], name=D_(u"Search results"))
                # TODO: also display the values other than JID
            else:
                xml_tools.XMLUIData2AdvancedList(main_ui, headers, xmlui_data)
        else:
            main_ui.addText(D_("The search gave no result"))

    ## Retrieve the  search fields ##

    def _getFieldsUI(self, to_jid_s, profile_key):
        """Ask a service to send us the list of the form fields it manages.

        @param to_jid_s (unicode): XEP-0055 compliant search entity
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a deferred XMLUI instance
        """
        d = self.getFieldsUI(jid.JID(to_jid_s), profile_key)
        d.addCallback(lambda form: xml_tools.dataFormEltResult2XMLUI(form).toXml())
        return d

    def getFieldsUI(self, to_jid, profile_key):
        """Ask a service to send us the list of the form fields it manages.

        @param to_jid (jid.JID): XEP-0055 compliant search entity
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a deferred domish.Element
        """
        client = self.host.getClient(profile_key)
        fields_request = IQ(client.xmlstream, "get")
        fields_request["from"] = client.jid.full()
        fields_request["to"] = to_jid.full()
        fields_request.addElement("query", NS_SEARCH)
        d = fields_request.send(to_jid.full())
        d.addCallbacks(self._getFieldsUICb, self._getFieldsUIEb)
        return d

    def _getFieldsUICb(self, answer):
        """Callback for self.getFieldsUI.

        @param answer (domish.Element): search query element
        @return: domish.Element
        """
        try:
            query_elts = answer.elements("jabber:iq:search", "query").next()
        except StopIteration:
            log.info(_("No query element found"))
            raise DataError  # FIXME: StanzaError is probably more appropriate, check the RFC
        try:
            form_elt = query_elts.elements(data_form.NS_X_DATA, "x").next()
        except StopIteration:
            log.info(_("No data form found"))
            raise NotImplementedError(
                "Only search through data form is implemented so far"
            )
        return form_elt

    def _getFieldsUIEb(self, failure):
        """Errback to self.getFieldsUI.

        @param failure (defer.failure.Failure): twisted failure
        @raise: the unchanged defer.failure.Failure
        """
        log.info(_("Fields request failure: %s") % unicode(failure.getErrorMessage()))
        raise failure

    ## Do the search ##

    def _searchRequest(self, to_jid_s, search_data, profile_key):
        """Actually do a search, according to filled data.

        @param to_jid_s (unicode): XEP-0055 compliant search entity
        @param search_data (dict): filled data, corresponding to the form obtained in getFieldsUI
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a deferred XMLUI string representation
        """
        d = self.searchRequest(jid.JID(to_jid_s), search_data, profile_key)
        d.addCallback(lambda form: xml_tools.dataFormEltResult2XMLUI(form).toXml())
        return d

    def searchRequest(self, to_jid, search_data, profile_key):
        """Actually do a search, according to filled data.

        @param to_jid (jid.JID): XEP-0055 compliant search entity
        @param search_data (dict): filled data, corresponding to the form obtained in getFieldsUI
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a deferred domish.Element
        """
        if FIELD_SINGLE in search_data:
            value = search_data[FIELD_SINGLE]
            d = self.getFieldsUI(to_jid, profile_key)
            d.addCallback(
                lambda elt: self.searchRequestMulti(to_jid, value, elt, profile_key)
            )
            return d

        client = self.host.getClient(profile_key)
        search_request = IQ(client.xmlstream, "set")
        search_request["from"] = client.jid.full()
        search_request["to"] = to_jid.full()
        query_elt = search_request.addElement("query", NS_SEARCH)
        x_form = data_form.Form("submit", formNamespace=NS_SEARCH)
        x_form.makeFields(search_data)
        query_elt.addChild(x_form.toElement())
        # TODO: XEP-0059 could be used here (with the needed new method attributes)
        d = search_request.send(to_jid.full())
        d.addCallbacks(self._searchOk, self._searchErr)
        return d

    def searchRequestMulti(self, to_jid, value, form_elt, profile_key):
        """Search for a value simultaneously in all fields, returns the results compilation.

        @param to_jid (jid.JID): XEP-0055 compliant search entity
        @param value (unicode): value to search
        @param form_elt (domish.Element): form element listing the fields
        @param profile_key (unicode): %(doc_profile_key)s
        @return: a deferred domish.Element
        """
        form = data_form.Form.fromElement(form_elt)
        d_list = []

        for field in [field.var for field in form.fieldList if field.var]:
            d_list.append(self.searchRequest(to_jid, {field: value}, profile_key))

        def cb(result):  # return the results compiled in one domish element
            result_elt = None
            for success, form_elt in result:
                if not success:
                    continue
                if (
                    result_elt is None
                ):  # the result element is built over the first answer
                    result_elt = form_elt
                    continue
                for item_elt in form_elt.elements("jabber:x:data", "item"):
                    result_elt.addChild(item_elt)
            if result_elt is None:
                raise defer.failure.Failure(
                    DataError(_("The search could not be performed"))
                )
            return result_elt

        return defer.DeferredList(d_list).addCallback(cb)

    def _searchOk(self, answer):
        """Callback for self.searchRequest.

        @param answer (domish.Element): search query element
        @return: domish.Element
        """
        try:
            query_elts = answer.elements("jabber:iq:search", "query").next()
        except StopIteration:
            log.info(_("No query element found"))
            raise DataError  # FIXME: StanzaError is probably more appropriate, check the RFC
        try:
            form_elt = query_elts.elements(data_form.NS_X_DATA, "x").next()
        except StopIteration:
            log.info(_("No data form found"))
            raise NotImplementedError(
                "Only search through data form is implemented so far"
            )
        return form_elt

    def _searchErr(self, failure):
        """Errback to self.searchRequest.

        @param failure (defer.failure.Failure): twisted failure
        @raise: the unchanged defer.failure.Failure
        """
        log.info(_("Search request failure: %s") % unicode(failure.getErrorMessage()))
        raise failure


class XEP_0055_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_SEARCH)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
