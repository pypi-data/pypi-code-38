#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT standard user interface for managing contacts
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
from sat.tools import xml_tools
from twisted.words.protocols.jabber import jid
from xml.dom.minidom import Element


class ContactList(object):
    """Add, update and remove contacts."""

    def __init__(self, host):
        self.host = host
        self.__add_id = host.registerCallback(self._addContact, with_data=True)
        self.__update_id = host.registerCallback(self._updateContact, with_data=True)
        self.__confirm_delete_id = host.registerCallback(
            self._getConfirmRemoveXMLUI, with_data=True
        )

        host.importMenu(
            (D_("Contacts"), D_("Add contact")),
            self._getAddDialogXMLUI,
            security_limit=2,
            help_string=D_("Add contact"),
        )
        host.importMenu(
            (D_("Contacts"), D_("Update contact")),
            self._getUpdateDialogXMLUI,
            security_limit=2,
            help_string=D_("Update contact"),
        )
        host.importMenu(
            (D_("Contacts"), D_("Remove contact")),
            self._getRemoveDialogXMLUI,
            security_limit=2,
            help_string=D_("Remove contact"),
        )

        # FIXME: a plugin should not be used here, and current profile's jid host would be better than installation wise host
        if "MISC-ACCOUNT" in self.host.plugins:
            self.default_host = self.host.plugins["MISC-ACCOUNT"].getNewAccountDomain()
        else:
            self.default_host = "example.net"

    def getContacts(self, profile):
        """Return a sorted list of the contacts for that profile

        @param profile: %(doc_profile)s
        @return: list[string]
        """
        client = self.host.getClient(profile)
        ret = [contact.full() for contact in client.roster.getJids()]
        ret.sort()
        return ret

    def getGroups(self, new_groups=None, profile=C.PROF_KEY_NONE):
        """Return a sorted list of the groups for that profile

        @param new_group (list): add these groups to the existing ones
        @param profile: %(doc_profile)s
        @return: list[string]
        """
        client = self.host.getClient(profile)
        ret = client.roster.getGroups()
        ret.sort()
        ret.extend([group for group in new_groups if group not in ret])
        return ret

    def getGroupsOfContact(self, user_jid_s, profile):
        """Return all the groups of the given contact

        @param user_jid_s (string)
        @param profile: %(doc_profile)s
        @return: list[string]
        """
        client = self.host.getClient(profile)
        return client.roster.getItem(jid.JID(user_jid_s)).groups

    def getGroupsOfAllContacts(self, profile):
        """Return a mapping between the contacts and their groups

        @param profile: %(doc_profile)s
        @return: dict (key: string, value: list[string]):
            - key: the JID userhost
            - value: list of groups
        """
        client = self.host.getClient(profile)
        return {item.jid.userhost(): item.groups for item in client.roster.getItems()}

    def _data2elts(self, data):
        """Convert a contacts data dict to minidom Elements

        @param data (dict)
        @return list[Element]
        """
        elts = []
        for key in data:
            key_elt = Element("jid")
            key_elt.setAttribute("name", key)
            for value in data[key]:
                value_elt = Element("group")
                value_elt.setAttribute("name", value)
                key_elt.childNodes.append(value_elt)
            elts.append(key_elt)
        return elts

    def getDialogXMLUI(self, options, data, profile):
        """Generic method to return the XMLUI dialog for adding or updating a contact

        @param options (dict): parameters for the dialog, with the keys:
                               - 'id': the menu callback id
                               - 'title': deferred localized string
                               - 'contact_text': deferred localized string
        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        form_ui = xml_tools.XMLUI("form", title=options["title"], submit_id=options["id"])
        if "message" in data:
            form_ui.addText(data["message"])
            form_ui.addDivider("dash")

        form_ui.addText(options["contact_text"])
        if options["id"] == self.__add_id:
            contact = data.get(
                xml_tools.formEscape("contact_jid"), "@%s" % self.default_host
            )
            form_ui.addString("contact_jid", value=contact)
        elif options["id"] == self.__update_id:
            contacts = self.getContacts(profile)
            list_ = form_ui.addList("contact_jid", options=contacts, selected=contacts[0])
            elts = self._data2elts(self.getGroupsOfAllContacts(profile))
            list_.setInternalCallback(
                "groups_of_contact", fields=["contact_jid", "groups_list"], data_elts=elts
            )

        form_ui.addDivider("blank")

        form_ui.addText(_("Select in which groups your contact is:"))
        selected_groups = []
        if "selected_groups" in data:
            selected_groups = data["selected_groups"]
        elif options["id"] == self.__update_id:
            try:
                selected_groups = self.getGroupsOfContact(contacts[0], profile)
            except IndexError:
                pass
        groups = self.getGroups(selected_groups, profile)
        form_ui.addList(
            "groups_list", options=groups, selected=selected_groups, styles=["multi"]
        )

        adv_list = form_ui.changeContainer("advanced_list", columns=3, selectable="no")
        form_ui.addLabel(D_("Add group"))
        form_ui.addString("add_group")
        button = form_ui.addButton("", value=D_("Add"))
        button.setInternalCallback("move", fields=["add_group", "groups_list"])
        adv_list.end()

        form_ui.addDivider("blank")
        return {"xmlui": form_ui.toXml()}

    def _getAddDialogXMLUI(self, data, profile):
        """Get the dialog for adding contact

        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        options = {
            "id": self.__add_id,
            "title": D_("Add contact"),
            "contact_text": D_("New contact identifier (JID):"),
        }
        return self.getDialogXMLUI(options, {}, profile)

    def _getUpdateDialogXMLUI(self, data, profile):
        """Get the dialog for updating contact

        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        if not self.getContacts(profile):
            _dialog = xml_tools.XMLUI("popup", title=D_("Nothing to update"))
            _dialog.addText(_("Your contact list is empty."))
            return {"xmlui": _dialog.toXml()}

        options = {
            "id": self.__update_id,
            "title": D_("Update contact"),
            "contact_text": D_("Which contact do you want to update?"),
        }
        return self.getDialogXMLUI(options, {}, profile)

    def _getRemoveDialogXMLUI(self, data, profile):
        """Get the dialog for removing contact

        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        if not self.getContacts(profile):
            _dialog = xml_tools.XMLUI("popup", title=D_("Nothing to delete"))
            _dialog.addText(_("Your contact list is empty."))
            return {"xmlui": _dialog.toXml()}

        form_ui = xml_tools.XMLUI(
            "form",
            title=D_("Who do you want to remove from your contacts?"),
            submit_id=self.__confirm_delete_id,
        )
        form_ui.addList("contact_jid", options=self.getContacts(profile))
        return {"xmlui": form_ui.toXml()}

    def _getConfirmRemoveXMLUI(self, data, profile):
        """Get the confirmation dialog for removing contact

        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        if C.bool(data.get("cancelled", "false")):
            return {}
        contact = data[xml_tools.formEscape("contact_jid")]

        def delete_cb(data, profile):
            if not C.bool(data.get("cancelled", "false")):
                self._deleteContact(jid.JID(contact), profile)
            return {}

        delete_id = self.host.registerCallback(delete_cb, with_data=True, one_shot=True)
        form_ui = xml_tools.XMLUI("form", title=D_("Delete contact"), submit_id=delete_id)
        form_ui.addText(
            D_("Are you sure you want to remove %s from your contact list?") % contact
        )
        return {"xmlui": form_ui.toXml()}

    def _addContact(self, data, profile):
        """Add the selected contact

        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        if C.bool(data.get("cancelled", "false")):
            return {}
        contact_jid_s = data[xml_tools.formEscape("contact_jid")]
        try:
            contact_jid = jid.JID(contact_jid_s)
        except (RuntimeError, jid.InvalidFormat, AttributeError):
            # TODO: replace '\t' by a constant (see tools.xmlui.XMLUI.onFormSubmitted)
            data["selected_groups"] = data[xml_tools.formEscape("groups_list")].split(
                "\t"
            )
            options = {
                "id": self.__add_id,
                "title": D_("Add contact"),
                "contact_text": D_('Please enter a valid JID (like "contact@%s"):')
                % self.default_host,
            }
            return self.getDialogXMLUI(options, data, profile)
        self.host.addContact(contact_jid, profile_key=profile)
        return self._updateContact(data, profile)  # after adding, updating

    def _updateContact(self, data, profile):
        """Update the selected contact

        @param data (dict)
        @param profile: %(doc_profile)s
        @return dict
        """
        if C.bool(data.get("cancelled", "false")):
            return {}
        contact_jid = jid.JID(data[xml_tools.formEscape("contact_jid")])
        # TODO: replace '\t' by a constant (see tools.xmlui.XMLUI.onFormSubmitted)
        groups = data[xml_tools.formEscape("groups_list")].split("\t")
        self.host.updateContact(contact_jid, name="", groups=groups, profile_key=profile)
        return {}

    def _deleteContact(self, contact_jid, profile):
        """Delete the selected contact

        @param contact_jid (JID)
        @param profile: %(doc_profile)s
        @return dict
        """
        self.host.delContact(contact_jid, profile_key=profile)
        return {}
