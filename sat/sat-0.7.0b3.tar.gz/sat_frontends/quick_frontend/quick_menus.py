#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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

try:
    # FIXME: to be removed when an acceptable solution is here
    unicode("")  # XXX: unicode doesn't exist in pyjamas
except (
    TypeError,
    AttributeError,
):  # Error raised is not the same depending on pyjsbuild options
    unicode = str

from sat.core.log import getLogger
from sat.core.i18n import _, languageSwitch

log = getLogger(__name__)
from sat_frontends.quick_frontend.constants import Const as C
from collections import OrderedDict


## items ##


class MenuBase(object):
    ACTIVE = True

    def __init__(self, name, extra=None):
        """
        @param name(unicode): canonical name of the item
        @param extra(dict[unicode, unicode], None): same as in [addMenus]
        """
        self._name = name
        self.setExtra(extra)

    @property
    def canonical(self):
        """Return the canonical name of the container, used to identify it"""
        return self._name

    @property
    def name(self):
        """Return the name of the container, can be translated"""
        return self._name

    def setExtra(self, extra):
        if extra is None:
            extra = {}
        self.icon = extra.get("icon")


class MenuItem(MenuBase):
    """A callable item in the menu"""

    CALLABLE = False

    def __init__(self, name, name_i18n, extra=None, type_=None):
        """
        @param name(unicode): canonical name of the item
        @param name_i18n(unicode): translated name of the item
        @param extra(dict[unicode, unicode], None): same as in [addMenus]
        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        """
        MenuBase.__init__(self, name, extra)
        self._name_i18n = name_i18n if name_i18n else name
        self.type = type_

    @property
    def name(self):
        return self._name_i18n

    def collectData(self, caller):
        """Get data according to data_collector

        @param caller: Menu caller
        """
        assert self.type is not None  # if data collector are used, type must be set
        data_collector = QuickMenusManager.getDataCollector(self.type)

        if data_collector is None:
            return {}

        elif callable(data_collector):
            return data_collector(caller, self.name)

        else:
            if caller is None:
                log.error(u"Caller can't be None with a dictionary as data_collector")
                return {}
            data = {}
            for data_key, caller_attr in data_collector.iteritems():
                data[data_key] = unicode(getattr(caller, caller_attr))
            return data

    def call(self, caller, profile=C.PROF_KEY_NONE):
        """Execute the menu item

        @param caller: instance linked to the menu
        @param profile: %(doc_profile)s
        """
        raise NotImplementedError


class MenuItemDistant(MenuItem):
    """A MenuItem with a distant callback"""

    CALLABLE = True

    def __init__(self, host, type_, name, name_i18n, id_, extra=None):
        """
        @param host: %(doc_host)s
        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param name(unicode): canonical name of the item
        @param name_i18n(unicode): translated name of the item
        @param id_(unicode): id of the distant callback
        @param extra(dict[unicode, unicode], None): same as in [addMenus]
        """
        MenuItem.__init__(self, name, name_i18n, extra, type_)
        self.host = host
        self.id = id_

    def call(self, caller, profile=C.PROF_KEY_NONE):
        data = self.collectData(caller)
        log.debug("data collected: %s" % data)
        self.host.launchAction(self.id, data, profile=profile)


class MenuItemLocal(MenuItem):
    """A MenuItem with a local callback"""

    CALLABLE = True

    def __init__(self, type_, name, name_i18n, callback, extra=None):
        """
        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param name(unicode): canonical name of the item
        @param name_i18n(unicode): translated name of the item
        @param callback(callable): local callback.
            Will be called with no argument if data_collector is None
            and with caller, profile, and requested data otherwise
        @param extra(dict[unicode, unicode], None): same as in [addMenus]
        """
        MenuItem.__init__(self, name, name_i18n, extra, type_)
        self.callback = callback

    def call(self, caller, profile=C.PROF_KEY_NONE):
        data_collector = QuickMenusManager.getDataCollector(self.type)
        if data_collector is None:
            # FIXME: would not it be better if caller and profile where used as arguments?
            self.callback()
        else:
            self.callback(caller, self.collectData(caller), profile)


class MenuHook(MenuItemLocal):
    """A MenuItem which replace an expected item from backend"""

    pass


class MenuPlaceHolder(MenuItem):
    """A non existant menu which is used to keep a position"""

    ACTIVE = False

    def __init__(self, name):
        MenuItem.__init__(self, name, name)


class MenuSeparator(MenuItem):
    """A separation between items/categories"""

    SEP_IDX = 0

    def __init__(self):
        MenuSeparator.SEP_IDX += 1
        name = u"___separator_{}".format(MenuSeparator.SEP_IDX)
        MenuItem.__init__(self, name, name)


## containers ##


class MenuContainer(MenuBase):
    def __init__(self, name, extra=None):
        MenuBase.__init__(self, name, extra)
        self._items = OrderedDict()

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item.canonical in self._items

    def __iter__(self):
        return self._items.itervalues()

    def __getitem__(self, item):
        try:
            return self._items[item.canonical]
        except KeyError:
            raise KeyError(item)

    def getOrCreate(self, item):
        log.debug(
            u"MenuContainer getOrCreate: item=%s name=%s\nlist=%s"
            % (item, item.canonical, self._items.keys())
        )
        try:
            return self[item]
        except KeyError:
            self.append(item)
            return item

    def getActiveMenus(self):
        """Return an iterator on active children"""
        for child in self._items.itervalues():
            if child.ACTIVE:
                yield child

    def append(self, item):
        """add an item at the end of current ones

        @param item: instance of MenuBase (must be unique in container)
        """
        assert isinstance(item, MenuItem) or isinstance(item, MenuContainer)
        assert item.canonical not in self._items
        self._items[item.canonical] = item

    def replace(self, item):
        """add an item at the end of current ones or replace an existing one"""
        self._items[item.canonical] = item


class MenuCategory(MenuContainer):
    """A category which can hold other menus or categories"""

    def __init__(self, name, name_i18n=None, extra=None):
        """
        @param name(unicode): canonical name
        @param name_i18n(unicode, None): translated name
        @param icon(unicode, None): same as in MenuBase.__init__
        """
        log.debug("creating menuCategory %s with extra %s" % (name, extra))
        MenuContainer.__init__(self, name, extra)
        self._name_i18n = name_i18n or name

    @property
    def name(self):
        return self._name_i18n


class MenuType(MenuContainer):
    """A type which can hold other menus or categories"""

    pass


## manager ##


class QuickMenusManager(object):
    """Manage all the menus"""

    _data_collectors = {
        C.MENU_GLOBAL: None
    }  # No data is associated with C.MENU_GLOBAL items

    def __init__(self, host, menus=None, language=None):
        """
        @param host: %(doc_host)s
        @param menus(iterable): menus as in [addMenus]
        @param language: same as in [i18n.languageSwitch]
        """
        self.host = host
        MenuBase.host = host
        self.language = language
        self.menus = {}
        if menus is not None:
            self.addMenus(menus)

    def _getPathI18n(self, path):
        """Return translated version of path"""
        languageSwitch(self.language)
        path_i18n = [_(elt) for elt in path]
        languageSwitch()
        return path_i18n

    def _createCategories(self, type_, path, path_i18n=None, top_extra=None):
        """Create catogories of the path

        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param path(list[unicode]):  same as in [sat.core.sat_main.SAT.importMenu]
        @param path_i18n(list[unicode], None):  translated menu path (same lenght as path) or None to get deferred translation of path
        @param top_extra: extra data to use on the first element of path only. If the first element already exists and is reused, top_extra will be ignored (you'll have to manually change it if you really want to).
        @return (MenuContainer): last category created, or MenuType if path is empty
        """
        if path_i18n is None:
            path_i18n = self._getPathI18n(path)
        assert len(path) == len(path_i18n)
        menu_container = self.menus.setdefault(type_, MenuType(type_))

        for idx, category in enumerate(path):
            menu_category = MenuCategory(category, path_i18n[idx], extra=top_extra)
            menu_container = menu_container.getOrCreate(menu_category)
            top_extra = None

        return menu_container

    @staticmethod
    def addDataCollector(type_, data_collector):
        """Associate a data collector to a menu type

        A data collector is a method or a map which allow to collect context data to construct the dictionnary which will be sent to the bridge method managing the menu item.
        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param data_collector(dict[unicode,unicode], callable, None): can be:
            - a dict which map data name to local name.
                The attribute named after the dict values will be getted from caller, and put in data.
                e.g.: if data_collector={'room_jid':'target'}, then the "room_jid" data will be the value of the "target" attribute of the caller.
            - a callable which must return the data dictionnary. callable will have caller and item name as argument
            - None: an empty dict will be used
        """
        QuickMenusManager._data_collectors[type_] = data_collector

    @staticmethod
    def getDataCollector(type_):
        """Get data_collector associated to type_

        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @return (callable, dict, None): data_collector
        """
        try:
            return QuickMenusManager._data_collectors[type_]
        except KeyError:
            log.error(u"No data collector registered for {}".format(type_))
            return None

    def addMenuItem(self, type_, path, item, path_i18n=None, top_extra=None):
        """Add a MenuItemBase instance

        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param path(list[unicode]):  same as in [sat.core.sat_main.SAT.importMenu], stop at the last parent category
        @param item(MenuItem): a instancied item
        @param path_i18n(list[unicode],None):  translated menu path (same lenght as path) or  None to use deferred translation of path
        @param top_extra: same as in [_createCategories]
        """
        if path_i18n is None:
            path_i18n = self._getPathI18n(path)
        assert path and len(path) == len(path_i18n)

        menu_container = self._createCategories(type_, path, path_i18n, top_extra)

        if item in menu_container:
            if isinstance(item, MenuHook):
                menu_container.replace(item)
            else:
                container_item = menu_container[item]
                if isinstance(container_item, MenuPlaceHolder):
                    menu_container.replace(item)
                elif isinstance(container_item, MenuHook):
                    # MenuHook must not be replaced
                    log.debug(
                        u"ignoring menu at path [{}] because a hook is already in place".format(
                            path
                        )
                    )
                else:
                    log.error(u"Conflicting menus at path [{}]".format(path))
        else:
            log.debug(u"Adding menu [{type_}] {path}".format(type_=type_, path=path))
            menu_container.append(item)
            self.host.callListeners("menu", type_, path, path_i18n, item)

    def addMenu(
        self,
        type_,
        path,
        path_i18n=None,
        extra=None,
        top_extra=None,
        id_=None,
        callback=None,
    ):
        """Add a menu item

        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param path(list[unicode]):  same as in [sat.core.sat_main.SAT.importMenu]
        @param path_i18n(list[unicode], None):  translated menu path (same lenght as path), or None to get deferred translation
        @param extra(dict[unicode, unicode], None): same as in [addMenus]
        @param top_extra: same as in [_createCategories]
        @param id_(unicode): callback id (mutually exclusive with callback)
        @param callback(callable): local callback (mutually exclusive with id_)
        """
        if path_i18n is None:
            path_i18n = self._getPathI18n(path)
        assert bool(id_) ^ bool(callback)  # we must have id_ xor callback defined
        if id_:
            menu_item = MenuItemDistant(
                self.host, type_, path[-1], path_i18n[-1], id_=id_, extra=extra
            )
        else:
            menu_item = MenuItemLocal(
                type_, path[-1], path_i18n[-1], callback=callback, extra=extra
            )
        self.addMenuItem(type_, path[:-1], menu_item, path_i18n[:-1], top_extra)

    def addMenus(self, menus, top_extra=None):
        """Add several menus at once

        @param menus(iterable): iterable with:
            id_(unicode,callable): id of distant callback or local callback
            type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
            path(iterable[unicode]):  same as in [sat.core.sat_main.SAT.importMenu]
            path_i18n(iterable[unicode]):  translated menu path (same lenght as path)
            extra(dict[unicode,unicode]): dictionary of extra data (used on the leaf menu), can be:
                - "icon": icon name
        @param top_extra: same as in [_createCategories]
        """
        # TODO: manage icons
        for id_, type_, path, path_i18n, extra in menus:
            if callable(id_):
                self.addMenu(
                    type_, path, path_i18n, callback=id_, extra=extra, top_extra=top_extra
                )
            else:
                self.addMenu(
                    type_, path, path_i18n, id_=id_, extra=extra, top_extra=top_extra
                )

    def addMenuHook(
        self, type_, path, path_i18n=None, extra=None, top_extra=None, callback=None
    ):
        """Helper method to add a menu hook

        Menu hooks are local menus which override menu given by backend
        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param path(list[unicode]):  same as in [sat.core.sat_main.SAT.importMenu]
        @param path_i18n(list[unicode], None):  translated menu path (same lenght as path), or None to get deferred translation
        @param extra(dict[unicode, unicode], None): same as in [addMenus]
        @param top_extra: same as in [_createCategories]
        @param callback(callable): local callback (mutually exclusive with id_)
        """
        if path_i18n is None:
            path_i18n = self._getPathI18n(path)
        menu_item = MenuHook(
            type_, path[-1], path_i18n[-1], callback=callback, extra=extra
        )
        self.addMenuItem(type_, path[:-1], menu_item, path_i18n[:-1], top_extra)
        log.info(u"Menu hook set on {path} ({type_})".format(path=path, type_=type_))

    def addCategory(self, type_, path, path_i18n=None, extra=None, top_extra=None):
        """Create a category with all parents, and set extra on the last one

        @param type_(unicode): same as in [sat.core.sat_main.SAT.importMenu]
        @param path(list[unicode]):  same as in [sat.core.sat_main.SAT.importMenu]
        @param path_i18n(list[unicode], None):  translated menu path (same lenght as path), or None to get deferred translation of path
        @param extra(dict[unicode, unicode], None): same as in [addMenus] (added on the leaf category only)
        @param top_extra: same as in [_createCategories]
        @return (MenuCategory): last category add
        """
        if path_i18n is None:
            path_i18n = self._getPathI18n(path)
        last_container = self._createCategories(
            type_, path, path_i18n, top_extra=top_extra
        )
        last_container.setExtra(extra)
        return last_container

    def getMainContainer(self, type_):
        """Get a main MenuType container

        @param type_: a C.MENU_* constant
        @return(MenuContainer): the main container
        """
        menu_container = self.menus.setdefault(type_, MenuType(type_))
        return menu_container
