#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Pubsub Schemas
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

from collections import Iterable
import copy
import itertools
from zope.interface import implements
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.internet import defer
from wokkel import disco, iwokkel
from wokkel import data_form
from wokkel import generic
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.tools import xml_tools
from sat.tools import utils
from sat.tools.common import date_utils
from sat.tools.common import data_format
from sat.core.log import getLogger

log = getLogger(__name__)

NS_SCHEMA = u"https://salut-a-toi/protocol/schema:0"

PLUGIN_INFO = {
    C.PI_NAME: u"PubSub Schema",
    C.PI_IMPORT_NAME: u"PUBSUB_SCHEMA",
    C.PI_TYPE: u"EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [u"XEP-0060", u"IDENTITY"],
    C.PI_MAIN: u"PubsubSchema",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: _(u"""Handle Pubsub data schemas"""),
}


class PubsubSchema(object):
    def __init__(self, host):
        log.info(_(u"PubSub Schema initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        self._i = self.host.plugins["IDENTITY"]
        host.bridge.addMethod(
            "psSchemaGet",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=self._getSchema,
            async=True,
        )
        host.bridge.addMethod(
            "psSchemaSet",
            ".plugin",
            in_sign="ssss",
            out_sign="",
            method=self._setSchema,
            async=True,
        )
        host.bridge.addMethod(
            "psSchemaUIGet",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=utils.partial(self._getUISchema, default_node=None),
            async=True,
        )
        host.bridge.addMethod(
            "psItemsFormGet",
            ".plugin",
            in_sign="ssssiassa{ss}s",
            out_sign="(asa{ss})",
            method=self._getDataFormItems,
            async=True,
        )
        host.bridge.addMethod(
            "psItemFormSend",
            ".plugin",
            in_sign="ssa{sas}ssa{ss}s",
            out_sign="s",
            method=self._sendDataFormItem,
            async=True,
        )

    def getHandler(self, client):
        return SchemaHandler()

    def _getSchemaBridgeCb(self, schema_elt):
        if schema_elt is None:
            return u""
        return schema_elt.toXml()

    def _getSchema(self, service, nodeIdentifier, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        d = self.getSchema(client, service, nodeIdentifier)
        d.addCallback(self._getSchemaBridgeCb)
        return d

    def _getSchemaCb(self, iq_elt):
        try:
            schema_elt = next(iq_elt.elements(NS_SCHEMA, "schema"))
        except StopIteration:
            raise exceptions.DataError("missing <schema> element")
        try:
            x_elt = next(schema_elt.elements((data_form.NS_X_DATA, "x")))
        except StopIteration:
            # there is not schema on this node
            return None
        return x_elt

    def getSchema(self, client, service, nodeIdentifier):
        """retrieve PubSub node schema

        @param service(jid.JID, None): jid of PubSub service
            None to use our PEP
        @param nodeIdentifier(unicode): node to get schema from
        @return (domish.Element, None): schema (<x> element)
            None if not schema has been set on this node
        """
        iq_elt = client.IQ(u"get")
        if service is not None:
            iq_elt["to"] = service.full()
        pubsub_elt = iq_elt.addElement((NS_SCHEMA, "pubsub"))
        schema_elt = pubsub_elt.addElement((NS_SCHEMA, "schema"))
        schema_elt["node"] = nodeIdentifier
        d = iq_elt.send()
        d.addCallback(self._getSchemaCb)
        return d

    @defer.inlineCallbacks
    def getSchemaForm(self, client, service, nodeIdentifier, schema=None,
                      form_type="form", copy_form=True):
        """get data form from node's schema

        @param service(None, jid.JID): PubSub service
        @param nodeIdentifier(unicode): node
        @param schema(domish.Element, data_form.Form, None): node schema
            if domish.Element, will be converted to data form
            if data_form.Form it will be returned without modification
            if None, it will be retrieved from node (imply one additional XMPP request)
        @param form_type(unicode): type of the form
        @param copy_form(bool): if True and if schema is already a data_form.Form, will deep copy it before returning
            needed when the form is reused and it will be modified (e.g. in sendDataFormItem)
        @return(data_form.Form): data form
            the form should not be modified if copy_form is not set
        """
        if schema is None:
            log.debug(_(u"unspecified schema, we need to request it"))
            schema = yield self.getSchema(client, service, nodeIdentifier)
            if schema is None:
                raise exceptions.DataError(
                    _(
                        u"no schema specified, and this node has no schema either, we can't construct the data form"
                    )
                )
        elif isinstance(schema, data_form.Form):
            if copy_form:
                schema = copy.deepcopy(schema)
            defer.returnValue(schema)

        try:
            form = data_form.Form.fromElement(schema)
        except data_form.Error as e:
            raise exceptions.DataError(_(u"Invalid Schema: {msg}").format(msg=e))
        form.formType = form_type
        defer.returnValue(form)

    def schema2XMLUI(self, schema_elt):
        form = data_form.Form.fromElement(schema_elt)
        xmlui = xml_tools.dataForm2XMLUI(form, "")
        return xmlui

    def _getUISchema(self, service, nodeIdentifier, default_node=None,
                     profile_key=C.PROF_KEY_NONE):
        if not nodeIdentifier:
            if not default_node:
                raise ValueError(_(u"nodeIndentifier needs to be set"))
            nodeIdentifier = default_node
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        d = self.getUISchema(client, service, nodeIdentifier)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def getUISchema(self, client, service, nodeIdentifier):
        d = self.getSchema(client, service, nodeIdentifier)
        d.addCallback(self.schema2XMLUI)
        return d

    def _setSchema(self, service, nodeIdentifier, schema, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        schema = generic.parseXml(schema.encode("utf-8"))
        return self.setSchema(client, service, nodeIdentifier, schema)

    def setSchema(self, client, service, nodeIdentifier, schema):
        """set or replace PubSub node schema

        @param schema(domish.Element, None): schema to set
            None if schema need to be removed
        """
        iq_elt = client.IQ()
        if service is not None:
            iq_elt["to"] = service.full()
        pubsub_elt = iq_elt.addElement((NS_SCHEMA, "pubsub"))
        schema_elt = pubsub_elt.addElement((NS_SCHEMA, "schema"))
        schema_elt["node"] = nodeIdentifier
        if schema is not None:
            schema_elt.addChild(schema)
        return iq_elt.send()

    def _getDataFormItems(self, form_ns="", service="", node="", schema="", max_items=10,
                          item_ids=None, sub_id=None, extra_dict=None,
                          profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = jid.JID(service) if service else None
        if not node:
            raise exceptions.DataError(_(u"empty node is not allowed"))
        if schema:
            schema = generic.parseXml(schema.encode("utf-8"))
        else:
            schema = None
        max_items = None if max_items == C.NO_LIMIT else max_items
        extra = self._p.parseExtra(extra_dict)
        d = self.getDataFormItems(
            client,
            service,
            node,
            schema,
            max_items or None,
            item_ids,
            sub_id or None,
            extra.rsm_request,
            extra.extra,
            form_ns=form_ns or None,
        )
        d.addCallback(self._p.transItemsData)
        return d

    @defer.inlineCallbacks
    def getDataFormItems(self, client, service, nodeIdentifier, schema=None,
                         max_items=None, item_ids=None, sub_id=None, rsm_request=None,
                         extra=None, default_node=None, form_ns=None, filters=None):
        """Get items known as being data forms, and convert them to XMLUI

        @param schema(domish.Element, data_form.Form, None): schema of the node if known
            if None, it will be retrieved from node
        @param default_node(unicode): node to use if nodeIdentifier is None or empty
        @param form_ns (unicode, None): namespace of the form
            None to accept everything, even if form has no namespace
        @param filters(dict, None): same as for xml_tools.dataFormResult2XMLUI
        other parameters as the same as for [getItems]
        @return (list[unicode]): XMLUI of the forms
            if an item is invalid (not corresponding to form_ns or not a data_form)
            it will be skipped
        @raise ValueError: one argument is invalid
        """
        if not nodeIdentifier:
            if not default_node:
                raise ValueError(
                    _(u"default_node must be set if nodeIdentifier is not set")
                )
            nodeIdentifier = default_node
        # we need the initial form to get options of fields when suitable
        schema_form = yield self.getSchemaForm(
            client, service, nodeIdentifier, schema, form_type="result", copy_form=False
        )
        items_data = yield self._p.getItems(
            client,
            service,
            nodeIdentifier,
            max_items,
            item_ids,
            sub_id,
            rsm_request,
            extra,
        )
        items, metadata = items_data
        items_xmlui = []
        for item_elt in items:
            for x_elt in item_elt.elements((data_form.NS_X_DATA, u"x")):
                form = data_form.Form.fromElement(x_elt)
                if form_ns and form.formNamespace != form_ns:
                    continue
                xmlui = xml_tools.dataFormResult2XMLUI(
                    form,
                    schema_form,
                    # FIXME: conflicts with schema (i.e. if "id" or "publisher" already exists)
                    #        are not checked
                    prepend=(
                        ("label", "id"),
                        ("text", item_elt["id"], u"id"),
                        ("label", "publisher"),
                        ("text", item_elt.getAttribute("publisher", ""), u"publisher"),
                    ),
                    filters=filters,
                    read_only=False,
                )
                items_xmlui.append(xmlui)
                break
        defer.returnValue((items_xmlui, metadata))

    def _sendDataFormItem(self, service, nodeIdentifier, values, schema=None,
                          item_id=None, extra=None, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        if schema:
            schema = generic.parseXml(schema.encode("utf-8"))
        else:
            schema = None
        d = self.sendDataFormItem(
            client,
            service,
            nodeIdentifier,
            values,
            schema,
            item_id or None,
            extra,
            deserialise=True,
        )
        d.addCallback(lambda ret: ret or u"")
        return d

    @defer.inlineCallbacks
    def sendDataFormItem(self, client, service, nodeIdentifier, values, schema=None,
                         item_id=None, extra=None, deserialise=False):
        """Publish an item as a dataform when we know that there is a schema

        @param values(dict[key(unicode), [iterable[object], object]]): values set for the
            form. If not iterable, will be put in a list.
        @param schema(domish.Element, data_form.Form, None): data schema
            None to retrieve data schema from node (need to do a additional XMPP call)
            Schema is needed to construct data form to publish
        @param deserialise(bool): if True, data are list of unicode and must be
            deserialized according to expected type.
            This is done in this method and not directly in _sendDataFormItem because we
            need to know the data type which is in the form, not availablable in
            _sendDataFormItem
        other parameters as the same as for [self._p.sendItem]
        @return (unicode): id of the created item
        """
        form = yield self.getSchemaForm(
            client, service, nodeIdentifier, schema, form_type="submit"
        )

        for name, values_list in values.iteritems():
            try:
                field = form.fields[name]
            except KeyError:
                log.warning(
                    _(u"field {name} doesn't exist, ignoring it").format(name=name)
                )
                continue
            if isinstance(values_list, basestring) or not isinstance(
                values_list, Iterable
            ):
                values_list = [values_list]
            if deserialise:
                if field.fieldType == u"boolean":
                    values_list = [C.bool(v) for v in values_list]
                elif field.fieldType == u"text-multi":
                    # for text-multi, lines must be put on separate values
                    values_list = list(
                        itertools.chain(*[v.splitlines() for v in values_list])
                    )
                elif xml_tools.isXHTMLField(field):
                   values_list = [generic.parseXml(v.encode("utf-8"))
                                  for v in values_list]
                elif u"jid" in (field.fieldType or u""):
                    values_list = [jid.JID(v) for v in values_list]
            if u"list" in (field.fieldType or u""):
                # for lists, we check that given values are allowed in form
                allowed_values = [o.value for o in field.options]
                values_list = [v for v in values_list if v in allowed_values]
                if not values_list:
                    # if values don't map to allowed values, we use default ones
                    values_list = field.values
            field.values = values_list

        yield self._p.sendItem(
            client, service, nodeIdentifier, form.toElement(), item_id, extra
        )

    ## filters ##
    # filters useful for data form to XMLUI conversion #

    def valueOrPublisherFilter(self, form_xmlui, widget_type, args, kwargs):
        """Replace missing value by publisher's user part"""
        if not args[0]:
            # value is not filled: we use user part of publisher (if we have it)
            try:
                publisher = jid.JID(form_xmlui.named_widgets["publisher"].value)
            except (KeyError, RuntimeError):
                pass
            else:
                args[0] = publisher.user.capitalize()
        return widget_type, args, kwargs

    def textbox2ListFilter(self, form_xmlui, widget_type, args, kwargs):
        """Split lines of a textbox in a list

        main use case is using a textbox for labels
        """
        if widget_type != u"textbox":
            return widget_type, args, kwargs
        widget_type = u"list"
        options = [o for o in args.pop(0).split(u"\n") if o]
        kwargs = {
            "options": options,
            "name": kwargs.get("name"),
            "styles": (u"noselect", u"extensible", u"reducible"),
        }
        return widget_type, args, kwargs

    def dateFilter(self, form_xmlui, widget_type, args, kwargs):
        """Convert a string with a date to a unix timestamp"""
        if widget_type != u"string" or not args[0]:
            return widget_type, args, kwargs
        # we convert XMPP date to timestamp
        try:
            args[0] = unicode(date_utils.date_parse(args[0]))
        except Exception as e:
            log.warning(_(u"Can't parse date field: {msg}").format(msg=e))
        return widget_type, args, kwargs

    ## Helper methods ##

    def prepareBridgeGet(self, service, node, max_items, sub_id, extra_dict, profile_key):
        """Parse arguments received from bridge *Get methods and return higher level data

        @return (tuple): (client, service, node, max_items, extra, sub_id) usable for
            internal methods
        """
        client = self.host.getClient(profile_key)
        service = jid.JID(service) if service else None
        if not node:
            node = None
        max_items = None if max_items == C.NO_LIMIT else max_items
        if not sub_id:
            sub_id = None
        extra = self._p.parseExtra(extra_dict)

        return client, service, node, max_items, extra, sub_id

    def _get(self, service="", node="", max_items=10, item_ids=None, sub_id=None,
             extra=None, default_node=None, form_ns=None, filters=None,
             profile_key=C.PROF_KEY_NONE):
        """Bridge method to retrieve data from node with schema

        this method is a helper so dependant plugins can use it directly
        when adding *Get methods
        extra can have the key "labels_as_list" which is a hack to convert
            labels from textbox to list in XMLUI, which usually render better
            in final UI.
        """
        if filters is None:
            filters = {}
        if extra is None:
            extra = {}
        # XXX: Q&D way to get list for labels when displaying them, but text when we
        #      have to modify them
        if C.bool(extra.get("labels_as_list", C.BOOL_FALSE)):
            filters = filters.copy()
            filters[u"labels"] = self.textbox2ListFilter
        client, service, node, max_items, extra, sub_id = self.prepareBridgeGet(
            service, node, max_items, sub_id, extra, profile_key
        )
        d = self.getDataFormItems(
            client,
            service,
            node or None,
            max_items=max_items,
            item_ids=item_ids,
            sub_id=sub_id,
            rsm_request=extra.rsm_request,
            extra=extra.extra,
            default_node=default_node,
            form_ns=form_ns,
            filters=filters,
        )
        d.addCallback(self._p.transItemsData)
        return d

    def prepareBridgeSet(self, service, node, schema, item_id, extra, profile_key):
        """Parse arguments received from bridge *Set methods and return higher level data

        @return (tuple): (client, service, node, schema, item_id, extra) usable for
            internal methods
        """
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        if schema:
            schema = generic.parseXml(schema.encode("utf-8"))
        else:
            schema = None
        extra = data_format.deserialise(extra)
        return client, service, node or None, schema, item_id or None, extra

    @defer.inlineCallbacks
    def copyMissingValues(self, client, service, node, item_id, form_ns, values):
        """Retrieve values existing in original item and missing in update

        Existing item will be retrieve, and values not already specified in values will
        be filled
        @param service: same as for [XEP_0060.getItems]
        @param node: same as for [XEP_0060.getItems]
        @param item_id(unicode): id of the item to retrieve
        @param form_ns (unicode, None): namespace of the form
        @param values(dict): values to fill
            This dict will be modified *in place* to fill value present in existing
            item and missing in the dict.
        """
        try:
            # we get previous item
            items_data = yield self._p.getItems(
                client, service, node, item_ids=[item_id]
            )
            item_elt = items_data[0][0]
        except Exception as e:
            log.warning(
                _(u"Can't get previous item, update ignored: {reason}").format(
                    reason=e
                )
            )
        else:
            # and parse it
            form = data_form.findForm(item_elt, form_ns)
            if form is None:
                log.warning(
                    _(
                        u"Can't parse previous item, update ignored: data form not found"
                    ).format(reason=e)
                )
            else:
                for name, field in form.fields.iteritems():
                    if name not in values:
                        values[name] = u"\n".join(unicode(v) for v in field.values)

    def _set(self, service, node, values, schema=None, item_id=None, extra=None,
             default_node=None, form_ns=None, fill_author=True,
             profile_key=C.PROF_KEY_NONE):
        """Bridge method to set item in node with schema

        this method is a helper so dependant plugins can use it directly
        when adding *Set methods
        """
        client, service, node, schema, item_id, extra = self.prepareBridgeSet(
            service, node, schema, item_id, extra
        )
        d = self.set(
            client,
            service,
            node,
            values,
            schema,
            item_id,
            extra,
            deserialise=True,
            form_ns=form_ns,
            default_node=default_node,
            fill_author=fill_author,
        )
        d.addCallback(lambda ret: ret or u"")
        return d

    @defer.inlineCallbacks
    def set(self, client, service, node, values, schema, item_id, extra, deserialise,
            form_ns, default_node=None, fill_author=True):
        """Set an item in a node with a schema

        This method can be used directly by *Set methods added by dependant plugin
        @param values(dict[key(unicode), [iterable[object]|object]]): values of the items
            if value is not iterable, it will be put in a list
            'created' and 'updated' will be forced to current time:
                - 'created' is set if item_id is None, i.e. if it's a new ticket
                - 'updated' is set everytime
        @param extra(dict, None): same as for [XEP-0060.sendItem] with additional keys:
            - update(bool): if True, get previous item data to merge with current one
                if True, item_id must be None
        @param form_ns (unicode, None): namespace of the form
            needed when an update is done
        @param default_node(unicode, None): value to use if node is not set
        other arguments are same as for [self._s.sendDataFormItem]
        @return (unicode): id of the created item
        """
        if extra is None:
            extra = {}
        if not node:
            if default_node is None:
                raise ValueError(_(u"default_node must be set if node is not set"))
            node = default_node
        now = utils.xmpp_date()
        if not item_id:
            values["created"] = now
        elif extra.get(u"update", False):
            if item_id is None:
                raise exceptions.DataError(
                    _(u'if extra["update"] is set, item_id must be set too')
                )
            yield self.copyMissingValues(client, service, node, item_id, form_ns, values)

        values["updated"] = now
        if fill_author:
            if not values.get("author"):
                identity = yield self._i.getIdentity(client, client.jid)
                values["author"] = identity["nick"]
            if not values.get("author_jid"):
                values["author_jid"] = client.jid.full()
        item_id = yield self.sendDataFormItem(
            client, service, node, values, schema, item_id, extra, deserialise
        )
        defer.returnValue(item_id)


class SchemaHandler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, service, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_SCHEMA)]

    def getDiscoItems(self, requestor, service, nodeIdentifier=""):
        return []
