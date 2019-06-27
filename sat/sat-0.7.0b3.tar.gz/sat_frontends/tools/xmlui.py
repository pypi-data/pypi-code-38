#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT frontend tools
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
from sat.core.log import getLogger

log = getLogger(__name__)
from sat_frontends.quick_frontend.constants import Const as C
from sat.core import exceptions


_class_map = {}
CLASS_PANEL = "panel"
CLASS_DIALOG = "dialog"
CURRENT_LABEL = "current_label"
HIDDEN = "hidden"


class InvalidXMLUI(Exception):
    pass


class ClassNotRegistedError(Exception):
    pass


# FIXME: this method is duplicated in frontends.tools.xmlui.getText
def getText(node):
    """Get child text nodes
    @param node: dom Node
    @return: joined unicode text of all nodes

    """
    data = []
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            data.append(child.wholeText)
    return u"".join(data)


class Widget(object):
    """base Widget"""

    pass


class EmptyWidget(Widget):
    """Just a placeholder widget"""

    pass


class TextWidget(Widget):
    """Non interactive text"""

    pass


class LabelWidget(Widget):
    """Non interactive text"""

    pass


class JidWidget(Widget):
    """Jabber ID"""

    pass


class DividerWidget(Widget):
    """Separator"""

    pass


class StringWidget(Widget):
    """Input widget wich require a string

    often called Edit in toolkits
    """

    pass


class JidInputWidget(Widget):
    """Input widget wich require a string

    often called Edit in toolkits
    """

    pass


class PasswordWidget(Widget):
    """Input widget with require a masked string"""

    pass


class TextBoxWidget(Widget):
    """Input widget with require a long, possibly multilines string

    often called TextArea in toolkits
    """

    pass


class XHTMLBoxWidget(Widget):
    """Input widget specialised in XHTML editing,

    a WYSIWYG or specialised editor is expected
    """

    pass


class BoolWidget(Widget):
    """Input widget with require a boolean value
    often called CheckBox in toolkits
    """

    pass


class IntWidget(Widget):
    """Input widget with require an integer"""

    pass


class ButtonWidget(Widget):
    """A clickable widget"""

    pass


class ListWidget(Widget):
    """A widget able to show/choose one or several strings in a list"""

    pass


class JidsListWidget(Widget):
    """A widget able to show/choose one or several strings in a list"""

    pass


class Container(Widget):
    """Widget which can contain other ones with a specific layout"""

    @classmethod
    def _xmluiAdapt(cls, instance):
        """Make cls as instance.__class__

        cls must inherit from original instance class
        Usefull when you get a class from UI toolkit
        """
        assert instance.__class__ in cls.__bases__
        instance.__class__ = type(cls.__name__, cls.__bases__, dict(cls.__dict__))


class PairsContainer(Container):
    """Widgets are disposed in rows of two (usually label/input)"""

    pass


class LabelContainer(Container):
    """Widgets are associated with label or empty widget"""

    pass


class TabsContainer(Container):
    """A container which several other containers in tabs

    Often called Notebook in toolkits
    """

    pass


class VerticalContainer(Container):
    """Widgets are disposed vertically"""

    pass


class AdvancedListContainer(Container):
    """Widgets are disposed in rows with advaned features"""

    pass


class Dialog(object):
    """base dialog"""

    def __init__(self, _xmlui_parent):
        self._xmlui_parent = _xmlui_parent

    def _xmluiValidated(self, data=None):
        if data is None:
            data = {}
        self._xmluiSetData(C.XMLUI_STATUS_VALIDATED, data)
        self._xmluiSubmit(data)

    def _xmluiCancelled(self):
        data = {C.XMLUI_DATA_CANCELLED: C.BOOL_TRUE}
        self._xmluiSetData(C.XMLUI_STATUS_CANCELLED, data)
        self._xmluiSubmit(data)

    def _xmluiSubmit(self, data):
        if self._xmlui_parent.submit_id is None:
            log.debug(_("Nothing to submit"))
        else:
            self._xmlui_parent.submit(data)

    def _xmluiSetData(self, status, data):
        pass


class MessageDialog(Dialog):
    """Dialog with a OK/Cancel type configuration"""

    pass


class NoteDialog(Dialog):
    """Short message which doesn't need user confirmation to disappear"""

    pass


class ConfirmDialog(Dialog):
    """Dialog with a OK/Cancel type configuration"""

    def _xmluiSetData(self, status, data):
        if status == C.XMLUI_STATUS_VALIDATED:
            data[C.XMLUI_DATA_ANSWER] = C.BOOL_TRUE
        elif status == C.XMLUI_STATUS_CANCELLED:
            data[C.XMLUI_DATA_ANSWER] = C.BOOL_FALSE


class FileDialog(Dialog):
    """Dialog with a OK/Cancel type configuration"""

    pass


class XMLUIBase(object):
    """Base class to construct SàT XML User Interface

    This class must not be instancied directly
    """

    def __init__(self, host, parsed_dom, title=None, flags=None, callback=None,
                 profile=C.PROF_KEY_NONE):
        """Initialise the XMLUI instance

        @param host: %(doc_host)s
        @param parsed_dom: main parsed dom
        @param title: force the title, or use XMLUI one if None
        @param flags: list of string which can be:
            - NO_CANCEL: the UI can't be cancelled
            - FROM_BACKEND: the UI come from backend (i.e. it's not the direct result of
                            user operation)
        @param callback(callable, None): if not None, will be used with launchAction:
            - if None is used, default behaviour will be used (closing the dialog and
              calling host.actionManager)
            - if a callback is provided, it will be used instead, so you'll have to manage
                dialog closing or new xmlui to display, or other action (you can call
                host.actionManager)
                The callback will have data, callback_id and profile as arguments
        """
        self.host = host
        top = parsed_dom.documentElement
        self.session_id = top.getAttribute("session_id") or None
        self.submit_id = top.getAttribute("submit") or None
        self.xmlui_title = title or top.getAttribute("title") or u""
        self.hidden = {}
        if flags is None:
            flags = []
        self.flags = flags
        self.callback = callback or self._defaultCb
        self.profile = profile

    @property
    def user_action(self):
        return "FROM_BACKEND" not in self.flags

    def _defaultCb(self, data, cb_id, profile):
        # TODO: when XMLUI updates will be managed, the _xmluiClose
        #       must be called only if there is no update
        self._xmluiClose()
        self.host.actionManager(data, profile=profile)

    def _isAttrSet(self, name, node):
        """Return widget boolean attribute status

        @param name: name of the attribute (e.g. "read_only")
        @param node: Node instance
        @return (bool): True if widget's attribute is set (C.BOOL_TRUE)
        """
        read_only = node.getAttribute(name) or C.BOOL_FALSE
        return read_only.lower().strip() == C.BOOL_TRUE

    def _getChildNode(self, node, name):
        """Return the first child node with the given name

        @param node: Node instance
        @param name: name of the wanted node

        @return: The found element or None
        """
        for child in node.childNodes:
            if child.nodeName == name:
                return child
        return None

    def submit(self, data):
        self._xmluiClose()
        if self.submit_id is None:
            raise ValueError("Can't submit is self.submit_id is not set")
        if "session_id" in data:
            raise ValueError(
                u"session_id must no be used in data, it is automaticaly filled with "
                u"self.session_id if present"
            )
        if self.session_id is not None:
            data["session_id"] = self.session_id
        self._xmluiLaunchAction(self.submit_id, data)

    def _xmluiLaunchAction(self, action_id, data):
        self.host.launchAction(
            action_id, data, callback=self.callback, profile=self.profile
        )

    def _xmluiClose(self):
        """Close the window/popup/... where the constructor XMLUI is

        this method must be overrided
        """
        raise NotImplementedError


class ValueGetter(object):
    """dict like object which return values of widgets"""

    def __init__(self, widgets, attr="value"):
        self.attr = attr
        self.widgets = widgets

    def __getitem__(self, name):
        return getattr(self.widgets[name], self.attr)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def keys(self):
        return self.widgets.keys()


class XMLUIPanel(XMLUIBase):
    """XMLUI Panel

    New frontends can inherit this class to easily implement XMLUI
    @property widget_factory: factory to create frontend-specific widgets
    @property dialog_factory: factory to create frontend-specific dialogs
    """

    widget_factory = None

    def __init__(self, host, parsed_dom, title=None, flags=None, callback=None,
                 ignore=None, whitelist=None, profile=C.PROF_KEY_NONE):
        """

        @param title(unicode, None): title of the
        @property widgets(dict): widget name => widget map
        @property widget_value(ValueGetter): retrieve widget value from it's name
        """
        super(XMLUIPanel, self).__init__(
            host, parsed_dom, title=title, flags=flags, callback=callback, profile=profile
        )
        self.ctrl_list = {}  # input widget, used mainly for forms
        self.widgets = {}  #  allow to access any named widgets
        self.widget_value = ValueGetter(self.widgets)
        self._main_cont = None
        if ignore is None:
            ignore = []
        self._ignore = ignore
        if whitelist is not None:
            if ignore:
                raise exceptions.InternalError(
                    "ignore and whitelist must not be used at the same time"
                )
            self._whitelist = whitelist
        else:
            self._whitelist = None
        self.constructUI(parsed_dom)

    @staticmethod
    def escape(name):
        """Return escaped name for forms"""
        return u"%s%s" % (C.SAT_FORM_PREFIX, name)

    @property
    def main_cont(self):
        return self._main_cont

    @main_cont.setter
    def main_cont(self, value):
        if self._main_cont is not None:
            raise ValueError(_("XMLUI can have only one main container"))
        self._main_cont = value

    def _parseChilds(self, _xmlui_parent, current_node, wanted=("container",), data=None):
        """Recursively parse childNodes of an element

        @param _xmlui_parent: widget container with '_xmluiAppend' method
        @param current_node: element from which childs will be parsed
        @param wanted: list of tag names that can be present in the childs to be SàT XMLUI
                       compliant
        @param data(None, dict): additionnal data which are needed in some cases
        """
        for node in current_node.childNodes:
            if data is None:
                data = {}
            if wanted and not node.nodeName in wanted:
                raise InvalidXMLUI("Unexpected node: [%s]" % node.nodeName)

            if node.nodeName == "container":
                type_ = node.getAttribute("type")
                if _xmlui_parent is self and type_ not in ("vertical", "tabs"):
                    # main container is not a VerticalContainer and we want one,
                    # so we create one to wrap it
                    _xmlui_parent = self.widget_factory.createVerticalContainer(self)
                    self.main_cont = _xmlui_parent
                if type_ == "tabs":
                    cont = self.widget_factory.createTabsContainer(_xmlui_parent)
                    self._parseChilds(_xmlui_parent, node, ("tab",), {"tabs_cont": cont})
                elif type_ == "vertical":
                    cont = self.widget_factory.createVerticalContainer(_xmlui_parent)
                    self._parseChilds(cont, node, ("widget", "container"))
                elif type_ == "pairs":
                    cont = self.widget_factory.createPairsContainer(_xmlui_parent)
                    self._parseChilds(cont, node, ("widget", "container"))
                elif type_ == "label":
                    cont = self.widget_factory.createLabelContainer(_xmlui_parent)
                    self._parseChilds(
                        cont, node, ("widget", "container"), {CURRENT_LABEL: None}
                    )
                elif type_ == "advanced_list":
                    try:
                        columns = int(node.getAttribute("columns"))
                    except (TypeError, ValueError):
                        raise exceptions.DataError("Invalid columns")
                    selectable = node.getAttribute("selectable") or "no"
                    auto_index = node.getAttribute("auto_index") == C.BOOL_TRUE
                    data = {"index": 0} if auto_index else None
                    cont = self.widget_factory.createAdvancedListContainer(
                        _xmlui_parent, columns, selectable
                    )
                    callback_id = node.getAttribute("callback") or None
                    if callback_id is not None:
                        if selectable == "no":
                            raise ValueError(
                                "can't have selectable=='no' and callback_id at the same time"
                            )
                        cont._xmlui_callback_id = callback_id
                        cont._xmluiOnSelect(self.onAdvListSelect)

                    self._parseChilds(cont, node, ("row",), data)
                else:
                    log.warning(_("Unknown container [%s], using default one") % type_)
                    cont = self.widget_factory.createVerticalContainer(_xmlui_parent)
                    self._parseChilds(cont, node, ("widget", "container"))
                try:
                    xmluiAppend = _xmlui_parent._xmluiAppend
                except (
                    AttributeError,
                    TypeError,
                ):  # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                    if _xmlui_parent is self:
                        self.main_cont = cont
                    else:
                        raise Exception(
                            _("Internal Error, container has not _xmluiAppend method")
                        )
                else:
                    xmluiAppend(cont)

            elif node.nodeName == "tab":
                name = node.getAttribute("name")
                label = node.getAttribute("label")
                selected = C.bool(node.getAttribute("selected") or C.BOOL_FALSE)
                if not name or not "tabs_cont" in data:
                    raise InvalidXMLUI
                if self.type == "param":
                    self._current_category = (
                        name
                    )  # XXX: awful hack because params need category and we don't keep parent
                tab_cont = data["tabs_cont"]
                new_tab = tab_cont._xmluiAddTab(label or name, selected)
                self._parseChilds(new_tab, node, ("widget", "container"))

            elif node.nodeName == "row":
                try:
                    index = str(data["index"])
                except KeyError:
                    index = node.getAttribute("index") or None
                else:
                    data["index"] += 1
                _xmlui_parent._xmluiAddRow(index)
                self._parseChilds(_xmlui_parent, node, ("widget", "container"))

            elif node.nodeName == "widget":
                name = node.getAttribute("name")
                if name and (
                    name in self._ignore
                    or self._whitelist is not None
                    and name not in self._whitelist
                ):
                    # current widget is ignored, but there may be already a label
                    if CURRENT_LABEL in data:
                        # if so, we remove it from parent
                        _xmlui_parent._xmluiRemove(data.pop(CURRENT_LABEL))
                    continue
                type_ = node.getAttribute("type")
                value_elt = self._getChildNode(node, "value")
                if value_elt is not None:
                    value = getText(value_elt)
                else:
                    value = (
                        node.getAttribute("value") if node.hasAttribute("value") else u""
                    )
                if type_ == "empty":
                    ctrl = self.widget_factory.createEmptyWidget(_xmlui_parent)
                    if CURRENT_LABEL in data:
                        data[CURRENT_LABEL] = None
                elif type_ == "text":
                    ctrl = self.widget_factory.createTextWidget(_xmlui_parent, value)
                elif type_ == "label":
                    ctrl = self.widget_factory.createLabelWidget(_xmlui_parent, value)
                    data[CURRENT_LABEL] = ctrl
                elif type_ == "hidden":
                    if name in self.hidden:
                        raise exceptions.ConflictError(u"Conflict on hidden value with "
                                                       u"name {name}".format(name=name))
                    self.hidden[name] = value
                    continue
                elif type_ == "jid":
                    ctrl = self.widget_factory.createJidWidget(_xmlui_parent, value)
                elif type_ == "divider":
                    style = node.getAttribute("style") or "line"
                    ctrl = self.widget_factory.createDividerWidget(_xmlui_parent, style)
                elif type_ == "string":
                    ctrl = self.widget_factory.createStringWidget(
                        _xmlui_parent, value, self._isAttrSet("read_only", node)
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "jid_input":
                    ctrl = self.widget_factory.createJidInputWidget(
                        _xmlui_parent, value, self._isAttrSet("read_only", node)
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "password":
                    ctrl = self.widget_factory.createPasswordWidget(
                        _xmlui_parent, value, self._isAttrSet("read_only", node)
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "textbox":
                    ctrl = self.widget_factory.createTextBoxWidget(
                        _xmlui_parent, value, self._isAttrSet("read_only", node)
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "xhtmlbox":
                    ctrl = self.widget_factory.createXHTMLBoxWidget(
                        _xmlui_parent, value, self._isAttrSet("read_only", node)
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "bool":
                    ctrl = self.widget_factory.createBoolWidget(
                        _xmlui_parent,
                        value == C.BOOL_TRUE,
                        self._isAttrSet("read_only", node),
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "int":
                    ctrl = self.widget_factory.createIntWidget(
                        _xmlui_parent, value, self._isAttrSet("read_only", node)
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "list":
                    style = [] if node.getAttribute("multi") == "yes" else ["single"]
                    for attr in (u"noselect", u"extensible", u"reducible", u"inline"):
                        if node.getAttribute(attr) == "yes":
                            style.append(attr)
                    _options = [
                        (option.getAttribute("value"), option.getAttribute("label"))
                        for option in node.getElementsByTagName("option")
                    ]
                    _selected = [
                        option.getAttribute("value")
                        for option in node.getElementsByTagName("option")
                        if option.getAttribute("selected") == C.BOOL_TRUE
                    ]
                    ctrl = self.widget_factory.createListWidget(
                        _xmlui_parent, _options, _selected, style
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "jids_list":
                    style = []
                    jids = [getText(jid_) for jid_ in node.getElementsByTagName("jid")]
                    ctrl = self.widget_factory.createJidsListWidget(
                        _xmlui_parent, jids, style
                    )
                    self.ctrl_list[name] = {"type": type_, "control": ctrl}
                elif type_ == "button":
                    callback_id = node.getAttribute("callback")
                    ctrl = self.widget_factory.createButtonWidget(
                        _xmlui_parent, value, self.onButtonPress
                    )
                    ctrl._xmlui_param_id = (
                        callback_id,
                        [
                            field.getAttribute("name")
                            for field in node.getElementsByTagName("field_back")
                        ],
                    )
                else:
                    log.error(
                        _("FIXME FIXME FIXME: widget type [%s] is not implemented")
                        % type_
                    )
                    raise NotImplementedError(
                        _("FIXME FIXME FIXME: type [%s] is not implemented") % type_
                    )

                if name:
                    self.widgets[name] = ctrl

                if self.type == "param" and type_ not in ("text", "button"):
                    try:
                        ctrl._xmluiOnChange(self.onParamChange)
                        ctrl._param_category = self._current_category
                    except (
                        AttributeError,
                        TypeError,
                    ):  # XXX: TypeError is here because pyjamas raise a TypeError instead
                        #      of an AttributeError
                        if not isinstance(
                            ctrl, (EmptyWidget, TextWidget, LabelWidget, JidWidget)
                        ):
                            log.warning(_("No change listener on [%s]") % ctrl)

                elif type_ != "text":
                    callback = node.getAttribute("internal_callback") or None
                    if callback:
                        fields = [
                            field.getAttribute("name")
                            for field in node.getElementsByTagName("internal_field")
                        ]
                        cb_data = self.getInternalCallbackData(callback, node)
                        ctrl._xmlui_param_internal = (callback, fields, cb_data)
                        if type_ == "button":
                            ctrl._xmluiOnClick(self.onChangeInternal)
                        else:
                            ctrl._xmluiOnChange(self.onChangeInternal)

                ctrl._xmlui_name = name
                _xmlui_parent._xmluiAppend(ctrl)
                if CURRENT_LABEL in data and not isinstance(ctrl, LabelWidget):
                    # this key is set in LabelContainer, when present
                    # we can associate the label with the widget it is labelling
                    data.pop(CURRENT_LABEL)._xmlui_for_name = name

            else:
                raise NotImplementedError(_("Unknown tag [%s]") % node.nodeName)

    def constructUI(self, parsed_dom, post_treat=None):
        """Actually construct the UI

        @param parsed_dom: main parsed dom
        @param post_treat: frontend specific treatments to do once the UI is constructed
        @return: constructed widget
        """
        top = parsed_dom.documentElement
        self.type = top.getAttribute("type")
        if top.nodeName != "sat_xmlui" or not self.type in [
            "form",
            "param",
            "window",
            "popup",
        ]:
            raise InvalidXMLUI

        if self.type == "param":
            self.param_changed = set()

        self._parseChilds(self, parsed_dom.documentElement)

        if post_treat is not None:
            post_treat()

    def _xmluiSetParam(self, name, value, category):
        self.host.bridge.setParam(name, value, category, profile_key=self.profile)

    ##EVENTS##

    def onParamChange(self, ctrl):
        """Called when type is param and a widget to save is modified

        @param ctrl: widget modified
        """
        assert self.type == "param"
        self.param_changed.add(ctrl)

    def onAdvListSelect(self, ctrl):
        data = {}
        widgets = ctrl._xmluiGetSelectedWidgets()
        for wid in widgets:
            try:
                name = self.escape(wid._xmlui_name)
                value = wid._xmluiGetValue()
                data[name] = value
            except (
                AttributeError,
                TypeError,
            ):  # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                pass
        idx = ctrl._xmluiGetSelectedIndex()
        if idx is not None:
            data["index"] = idx
        callback_id = ctrl._xmlui_callback_id
        if callback_id is None:
            log.info(_("No callback_id found"))
            return
        self._xmluiLaunchAction(callback_id, data)

    def onButtonPress(self, button):
        """Called when an XMLUI button is clicked

        Launch the action associated to the button
        @param button: the button clicked
        """
        callback_id, fields = button._xmlui_param_id
        if not callback_id:  # the button is probably bound to an internal action
            return
        data = {}
        for field in fields:
            escaped = self.escape(field)
            ctrl = self.ctrl_list[field]
            if isinstance(ctrl["control"], ListWidget):
                data[escaped] = u"\t".join(ctrl["control"]._xmluiGetSelectedValues())
            else:
                data[escaped] = ctrl["control"]._xmluiGetValue()
        self._xmluiLaunchAction(callback_id, data)

    def onChangeInternal(self, ctrl):
        """Called when a widget that has been bound to an internal callback is changed.

        This is used to perform some UI actions without communicating with the backend.
        See sat.tools.xml_tools.Widget.setInternalCallback for more details.
        @param ctrl: widget modified
        """
        action, fields, data = ctrl._xmlui_param_internal
        if action not in ("copy", "move", "groups_of_contact"):
            raise NotImplementedError(
                _("FIXME: XMLUI internal action [%s] is not implemented") % action
            )

        def copy_move(source, target):
            """Depending of 'action' value, copy or move from source to target."""
            if isinstance(target, ListWidget):
                if isinstance(source, ListWidget):
                    values = source._xmluiGetSelectedValues()
                else:
                    values = [source._xmluiGetValue()]
                    if action == "move":
                        source._xmluiSetValue("")
                values = [value for value in values if value]
                if values:
                    target._xmluiAddValues(values, select=True)
            else:
                if isinstance(source, ListWidget):
                    value = u", ".join(source._xmluiGetSelectedValues())
                else:
                    value = source._xmluiGetValue()
                    if action == "move":
                        source._xmluiSetValue("")
                target._xmluiSetValue(value)

        def groups_of_contact(source, target):
            """Select in target the groups of the contact which is selected in source."""
            assert isinstance(source, ListWidget)
            assert isinstance(target, ListWidget)
            try:
                contact_jid_s = source._xmluiGetSelectedValues()[0]
            except IndexError:
                return
            target._xmluiSelectValues(data[contact_jid_s])
            pass

        source = None
        for field in fields:
            widget = self.ctrl_list[field]["control"]
            if not source:
                source = widget
                continue
            if action in ("copy", "move"):
                copy_move(source, widget)
            elif action == "groups_of_contact":
                groups_of_contact(source, widget)
            source = None

    def getInternalCallbackData(self, action, node):
        """Retrieve from node the data needed to perform given action.

        @param action (string): a value from the one that can be passed to the
            'callback' parameter of sat.tools.xml_tools.Widget.setInternalCallback
        @param node (DOM Element): the node of the widget that triggers the callback
        """
        # TODO: it would be better to not have a specific way to retrieve
        # data for each action, but instead to have a generic method to
        # extract any kind of data structure from the 'internal_data' element.

        try:  # data is stored in the first 'internal_data' element of the node
            data_elts = node.getElementsByTagName("internal_data")[0].childNodes
        except IndexError:
            return None
        data = {}
        if (
            action == "groups_of_contact"
        ):  # return a dict(key: string, value: list[string])
            for elt in data_elts:
                jid_s = elt.getAttribute("name")
                data[jid_s] = []
                for value_elt in elt.childNodes:
                    data[jid_s].append(value_elt.getAttribute("name"))
        return data

    def onFormSubmitted(self, ignore=None):
        """An XMLUI form has been submited

        call the submit action associated with this form
        """
        selected_values = []
        for ctrl_name in self.ctrl_list:
            escaped = self.escape(ctrl_name)
            ctrl = self.ctrl_list[ctrl_name]
            if isinstance(ctrl["control"], ListWidget):
                selected_values.append(
                    (escaped, u"\t".join(ctrl["control"]._xmluiGetSelectedValues()))
                )
            else:
                selected_values.append((escaped, ctrl["control"]._xmluiGetValue()))
        data = dict(selected_values)
        for key, value in self.hidden.iteritems():
            data[self.escape(key)] = value

        if self.submit_id is not None:
            self.submit(data)
        else:
            log.warning(
                _("The form data is not sent back, the type is not managed properly")
            )
            self._xmluiClose()

    def onFormCancelled(self, *__):
        """Called when a form is cancelled"""
        log.debug(_("Cancelling form"))
        if self.submit_id is not None:
            data = {C.XMLUI_DATA_CANCELLED: C.BOOL_TRUE}
            self.submit(data)
        else:
            log.warning(
                _("The form data is not sent back, the type is not managed properly")
            )
        self._xmluiClose()

    def onSaveParams(self, ignore=None):
        """Params are saved, we send them to backend

        self.type must be param
        """
        assert self.type == "param"
        for ctrl in self.param_changed:
            if isinstance(ctrl, ListWidget):
                value = u"\t".join(ctrl._xmluiGetSelectedValues())
            else:
                value = ctrl._xmluiGetValue()
            param_name = ctrl._xmlui_name.split(C.SAT_PARAM_SEPARATOR)[1]
            self._xmluiSetParam(param_name, value, ctrl._param_category)

        self._xmluiClose()

    def show(self, *args, **kwargs):
        pass


class XMLUIDialog(XMLUIBase):
    dialog_factory = None

    def __init__(
        self,
        host,
        parsed_dom,
        title=None,
        flags=None,
        callback=None,
        ignore=None,
        whitelist=None,
        profile=C.PROF_KEY_NONE,
    ):
        super(XMLUIDialog, self).__init__(
            host, parsed_dom, title=title, flags=flags, callback=callback, profile=profile
        )
        top = parsed_dom.documentElement
        dlg_elt = self._getChildNode(top, "dialog")
        if dlg_elt is None:
            raise ValueError("Invalid XMLUI: no Dialog element found !")
        dlg_type = dlg_elt.getAttribute("type") or C.XMLUI_DIALOG_MESSAGE
        try:
            mess_elt = self._getChildNode(dlg_elt, C.XMLUI_DATA_MESS)
            message = getText(mess_elt)
        except (
            TypeError,
            AttributeError,
        ):  # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
            message = ""
        level = dlg_elt.getAttribute(C.XMLUI_DATA_LVL) or C.XMLUI_DATA_LVL_INFO

        if dlg_type == C.XMLUI_DIALOG_MESSAGE:
            self.dlg = self.dialog_factory.createMessageDialog(
                self, self.xmlui_title, message, level
            )
        elif dlg_type == C.XMLUI_DIALOG_NOTE:
            self.dlg = self.dialog_factory.createNoteDialog(
                self, self.xmlui_title, message, level
            )
        elif dlg_type == C.XMLUI_DIALOG_CONFIRM:
            try:
                buttons_elt = self._getChildNode(dlg_elt, "buttons")
                buttons_set = (
                    buttons_elt.getAttribute("set") or C.XMLUI_DATA_BTNS_SET_DEFAULT
                )
            except (
                TypeError,
                AttributeError,
            ):  # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                buttons_set = C.XMLUI_DATA_BTNS_SET_DEFAULT
            self.dlg = self.dialog_factory.createConfirmDialog(
                self, self.xmlui_title, message, level, buttons_set
            )
        elif dlg_type == C.XMLUI_DIALOG_FILE:
            try:
                file_elt = self._getChildNode(dlg_elt, "file")
                filetype = file_elt.getAttribute("type") or C.XMLUI_DATA_FILETYPE_DEFAULT
            except (
                TypeError,
                AttributeError,
            ):  # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                filetype = C.XMLUI_DATA_FILETYPE_DEFAULT
            self.dlg = self.dialog_factory.createFileDialog(
                self, self.xmlui_title, message, level, filetype
            )
        else:
            raise ValueError("Unknown dialog type [%s]" % dlg_type)

    def show(self):
        self.dlg._xmluiShow()

    def _xmluiClose(self):
        self.dlg._xmluiClose()


def registerClass(type_, class_):
    """Register the class to use with the factory

    @param type_: one of:
        CLASS_PANEL: classical XMLUI interface
        CLASS_DIALOG: XMLUI dialog
    @param class_: the class to use to instanciate given type
    """
    # TODO: remove this method, as there are seme use cases where different XMLUI
    #       classes can be used in the same frontend, so a global value is not good
    assert type_ in (CLASS_PANEL, CLASS_DIALOG)
    log.warning(u"registerClass for XMLUI is deprecated, please use partial with "
                u"xmlui.create and class_map instead")
    if type_ in _class_map:
        log.debug(_(u"XMLUI class already registered for {type_}, ignoring").format(
            type_=type_))
        return

    _class_map[type_] = class_


def create(host, xml_data, title=None, flags=None, dom_parse=None, dom_free=None,
           callback=None, ignore=None, whitelist=None, class_map=None,
           profile=C.PROF_KEY_NONE):
    """
        @param dom_parse: methode equivalent to minidom.parseString (but which must manage unicode), or None to use default one
        @param dom_free: method used to free the parsed DOM
        @param ignore(list[unicode], None): name of widgets to ignore
            widgets with name in this list and their label will be ignored
        @param whitelist(list[unicode], None): name of widgets to keep
            when not None, only widgets in this list and their label will be kept
            mutually exclusive with ignore
    """
    if class_map is None:
        class_map = _class_map
    if dom_parse is None:
        from xml.dom import minidom

        dom_parse = lambda xml_data: minidom.parseString(xml_data.encode("utf-8"))
        dom_free = lambda parsed_dom: parsed_dom.unlink()
    else:
        dom_parse = dom_parse
        dom_free = dom_free or (lambda parsed_dom: None)
    parsed_dom = dom_parse(xml_data)
    top = parsed_dom.documentElement
    ui_type = top.getAttribute("type")
    try:
        if ui_type != C.XMLUI_DIALOG:
            cls = class_map[CLASS_PANEL]
        else:
            cls = class_map[CLASS_DIALOG]
    except KeyError:
        raise ClassNotRegistedError(
            _("You must register classes with registerClass before creating a XMLUI")
        )

    xmlui = cls(
        host,
        parsed_dom,
        title=title,
        flags=flags,
        callback=callback,
        ignore=ignore,
        whitelist=whitelist,
        profile=profile,
    )
    dom_free(parsed_dom)
    return xmlui
