#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for generic data import handling
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
from twisted.internet import defer
from sat.core import exceptions
from twisted.words.protocols.jabber import jid
from functools import partial
import collections
import uuid
import json


PLUGIN_INFO = {
    C.PI_NAME: "import",
    C.PI_IMPORT_NAME: "IMPORT",
    C.PI_TYPE: C.PLUG_TYPE_IMPORT,
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "ImportPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Generic import plugin, base for specialized importers"""),
}

Importer = collections.namedtuple("Importer", ("callback", "short_desc", "long_desc"))


class ImportPlugin(object):
    def __init__(self, host):
        log.info(_("plugin Import initialization"))
        self.host = host

    def initialize(self, import_handler, name):
        """Initialize a specialized import handler

        @param import_handler(object): specialized import handler instance
            must have the following methods:
                - importItem: import a single main item (i.e. prepare data for publishing)
                - importSubitems: import sub items (i.e. items linked to main item, e.g. comments).
                    Must return a dict with kwargs for recursiveImport if items are to be imported recursively.
                    At least "items_import_data", "service" and "node" keys must be provided.
                    if None is returned, no recursion will be done to import subitems, but import can still be done directly by the method.
                - publishItem: actualy publish an item
                - itemFilters: modify item according to options
        @param name(unicode): import handler name
        """
        assert name == name.lower().strip()
        log.info(_(u"initializing {name} import handler").format(name=name))
        import_handler.name = name
        import_handler.register = partial(self.register, import_handler)
        import_handler.unregister = partial(self.unregister, import_handler)
        import_handler.importers = {}

        def _import(name, location, options, pubsub_service, pubsub_node, profile):
            return self._doImport(
                import_handler,
                name,
                location,
                options,
                pubsub_service,
                pubsub_node,
                profile,
            )

        def _importList():
            return self.listImporters(import_handler)

        def _importDesc(name):
            return self.getDescription(import_handler, name)

        self.host.bridge.addMethod(
            name + "Import",
            ".plugin",
            in_sign="ssa{ss}sss",
            out_sign="s",
            method=_import,
            async=True,
        )
        self.host.bridge.addMethod(
            name + "ImportList",
            ".plugin",
            in_sign="",
            out_sign="a(ss)",
            method=_importList,
        )
        self.host.bridge.addMethod(
            name + "ImportDesc",
            ".plugin",
            in_sign="s",
            out_sign="(ss)",
            method=_importDesc,
        )

    def getProgress(self, import_handler, progress_id, profile):
        client = self.host.getClient(profile)
        return client._import[import_handler.name][progress_id]

    def listImporters(self, import_handler):
        importers = import_handler.importers.keys()
        importers.sort()
        return [
            (name, import_handler.importers[name].short_desc)
            for name in import_handler.importers
        ]

    def getDescription(self, import_handler, name):
        """Return import short and long descriptions

        @param name(unicode): importer name
        @return (tuple[unicode,unicode]): short and long description
        """
        try:
            importer = import_handler.importers[name]
        except KeyError:
            raise exceptions.NotFound(
                u"{handler_name} importer not found [{name}]".format(
                    handler_name=import_handler.name, name=name
                )
            )
        else:
            return importer.short_desc, importer.long_desc

    def _doImport(
        self,
        import_handler,
        name,
        location,
        options,
        pubsub_service="",
        pubsub_node="",
        profile=C.PROF_KEY_NONE,
    ):
        client = self.host.getClient(profile)
        options = {key: unicode(value) for key, value in options.iteritems()}
        for option in import_handler.BOOL_OPTIONS:
            try:
                options[option] = C.bool(options[option])
            except KeyError:
                pass
        for option in import_handler.JSON_OPTIONS:
            try:
                options[option] = json.loads(options[option])
            except ValueError:
                raise exceptions.DataError(
                    _(u"invalid json option: {name}").format(name=option)
                )
        pubsub_service = jid.JID(pubsub_service) if pubsub_service else None
        return self.doImport(
            client,
            import_handler,
            unicode(name),
            unicode(location),
            options,
            pubsub_service,
            pubsub_node or None,
        )

    @defer.inlineCallbacks
    def doImport(
        self,
        client,
        import_handler,
        name,
        location,
        options=None,
        pubsub_service=None,
        pubsub_node=None,
    ):
        """Import data

        @param import_handler(object): instance of the import handler
        @param name(unicode): name of the importer
        @param location(unicode): location of the data to import
            can be an url, a file path, or anything which make sense
            check importer description for more details
        @param options(dict, None): extra options.
        @param pubsub_service(jid.JID, None): jid of the PubSub service where data must be imported
            None to use profile's server
        @param pubsub_node(unicode, None): PubSub node to use
            None to use importer's default node
        @return (unicode): progress id
        """
        if options is None:
            options = {}
        else:
            for opt_name, opt_default in import_handler.OPT_DEFAULTS.iteritems():
                # we want a filled options dict, with all empty or False values removed
                try:
                    value = options[opt_name]
                except KeyError:
                    if opt_default:
                        options[opt_name] = opt_default
                else:
                    if not value:
                        del options[opt_name]

        try:
            importer = import_handler.importers[name]
        except KeyError:
            raise exceptions.NotFound(u"Importer [{}] not found".format(name))
        items_import_data, items_count = yield importer.callback(
            client, location, options
        )
        progress_id = unicode(uuid.uuid4())
        try:
            _import = client._import
        except AttributeError:
            _import = client._import = {}
        progress_data = _import.setdefault(import_handler.name, {})
        progress_data[progress_id] = {u"position": "0"}
        if items_count is not None:
            progress_data[progress_id]["size"] = unicode(items_count)
        metadata = {
            "name": u"{}: {}".format(name, location),
            "direction": "out",
            "type": import_handler.name.upper() + "_IMPORT",
        }
        self.host.registerProgressCb(
            progress_id,
            partial(self.getProgress, import_handler),
            metadata,
            profile=client.profile,
        )
        self.host.bridge.progressStarted(progress_id, metadata, client.profile)
        session = {  #  session data, can be used by importers
            u"root_service": pubsub_service,
            u"root_node": pubsub_node,
        }
        self.recursiveImport(
            client,
            import_handler,
            items_import_data,
            progress_id,
            session,
            options,
            None,
            pubsub_service,
            pubsub_node,
        )
        defer.returnValue(progress_id)

    @defer.inlineCallbacks
    def recursiveImport(
        self,
        client,
        import_handler,
        items_import_data,
        progress_id,
        session,
        options,
        return_data=None,
        service=None,
        node=None,
        depth=0,
    ):
        """Do the import recursively

        @param import_handler(object): instance of the import handler
        @param items_import_data(iterable): iterable of data as specified in [register]
        @param progress_id(unicode): id of progression
        @param session(dict): data for this import session
            can be used by importer so store any useful data
            "root_service" and "root_node" are set to the main pubsub service and node of the import
        @param options(dict): import options
        @param return_data(dict): data to return on progressFinished
        @param service(jid.JID, None): PubSub service to use
        @param node(unicode, None): PubSub node to use
        @param depth(int): level of recursion
        """
        if return_data is None:
            return_data = {}
        for idx, item_import_data in enumerate(items_import_data):
            item_data = yield import_handler.importItem(
                client, item_import_data, session, options, return_data, service, node
            )
            yield import_handler.itemFilters(client, item_data, session, options)
            recurse_kwargs = yield import_handler.importSubItems(
                client, item_import_data, item_data, session, options
            )
            yield import_handler.publishItem(client, item_data, service, node, session)

            if recurse_kwargs is not None:
                recurse_kwargs["client"] = client
                recurse_kwargs["import_handler"] = import_handler
                recurse_kwargs["progress_id"] = progress_id
                recurse_kwargs["session"] = session
                recurse_kwargs.setdefault("options", options)
                recurse_kwargs["return_data"] = return_data
                recurse_kwargs["depth"] = depth + 1
                log.debug(_(u"uploading subitems"))
                yield self.recursiveImport(**recurse_kwargs)

            if depth == 0:
                client._import[import_handler.name][progress_id]["position"] = unicode(
                    idx + 1
                )

        if depth == 0:
            self.host.bridge.progressFinished(progress_id, return_data, client.profile)
            self.host.removeProgressCb(progress_id, client.profile)
            del client._import[import_handler.name][progress_id]

    def register(self, import_handler, name, callback, short_desc="", long_desc=""):
        """Register an Importer method

        @param name(unicode): unique importer name, should indicate the software it can import and always lowercase
        @param callback(callable): method to call:
            the signature must be (client, location, options) (cf. [doImport])
            the importer must return a tuple with (items_import_data, items_count)
            items_import_data(iterable[dict]) data specific to specialized importer
                cf. importItem docstring of specialized importer for details
            items_count (int, None) indicate the total number of items (without subitems)
                useful to display a progress indicator when the iterator is a generator
                use None if you can't guess the total number of items
        @param short_desc(unicode): one line description of the importer
        @param long_desc(unicode): long description of the importer, its options, etc.
        """
        name = name.lower()
        if name in import_handler.importers:
            raise exceptions.ConflictError(
                _(
                    u"An {handler_name} importer with the name {name} already exist"
                ).format(handler_name=import_handler.name, name=name)
            )
        import_handler.importers[name] = Importer(callback, short_desc, long_desc)

    def unregister(self, import_handler, name):
        del import_handler.importers[name]
