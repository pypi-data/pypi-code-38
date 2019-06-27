#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
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
import urwid
import copy
from sat.core import exceptions
from urwid_satext import sat_widgets
from urwid_satext import files_management
from sat.core.log import getLogger

log = getLogger(__name__)
from sat_frontends.primitivus.constants import Const as C
from sat_frontends.primitivus.widget import PrimitivusWidget
from sat_frontends.tools import xmlui


class PrimitivusEvents(object):
    """ Used to manage change event of Primitivus widgets """

    def _event_callback(self, ctrl, *args, **kwargs):
        """" Call xmlui callback and ignore any extra argument """
        args[-1](ctrl)

    def _xmluiOnChange(self, callback):
        """ Call callback with widget as only argument """
        urwid.connect_signal(self, "change", self._event_callback, callback)


class PrimitivusEmptyWidget(xmlui.EmptyWidget, urwid.Text):
    def __init__(self, _xmlui_parent):
        urwid.Text.__init__(self, "")


class PrimitivusTextWidget(xmlui.TextWidget, urwid.Text):
    def __init__(self, _xmlui_parent, value, read_only=False):
        urwid.Text.__init__(self, value)


class PrimitivusLabelWidget(xmlui.LabelWidget, PrimitivusTextWidget):
    def __init__(self, _xmlui_parent, value):
        super(PrimitivusLabelWidget, self).__init__(_xmlui_parent, value + ": ")


class PrimitivusJidWidget(xmlui.JidWidget, PrimitivusTextWidget):
    pass


class PrimitivusDividerWidget(xmlui.DividerWidget, urwid.Divider):
    def __init__(self, _xmlui_parent, style="line"):
        if style == "line":
            div_char = u"─"
        elif style == "dot":
            div_char = u"·"
        elif style == "dash":
            div_char = u"-"
        elif style == "plain":
            div_char = u"█"
        elif style == "blank":
            div_char = " "
        else:
            log.warning(_("Unknown div_char"))
            div_char = u"─"

        urwid.Divider.__init__(self, div_char)


class PrimitivusStringWidget(
    xmlui.StringWidget, sat_widgets.AdvancedEdit, PrimitivusEvents
):
    def __init__(self, _xmlui_parent, value, read_only=False):
        sat_widgets.AdvancedEdit.__init__(self, edit_text=value)
        self.read_only = read_only

    def selectable(self):
        if self.read_only:
            return False
        return super(PrimitivusStringWidget, self).selectable()

    def _xmluiSetValue(self, value):
        self.set_edit_text(value)

    def _xmluiGetValue(self):
        return self.get_edit_text()


class PrimitivusJidInputWidget(xmlui.JidInputWidget, PrimitivusStringWidget):
    pass


class PrimitivusPasswordWidget(
    xmlui.PasswordWidget, sat_widgets.Password, PrimitivusEvents
):
    def __init__(self, _xmlui_parent, value, read_only=False):
        sat_widgets.Password.__init__(self, edit_text=value)
        self.read_only = read_only

    def selectable(self):
        if self.read_only:
            return False
        return super(PrimitivusPasswordWidget, self).selectable()

    def _xmluiSetValue(self, value):
        self.set_edit_text(value)

    def _xmluiGetValue(self):
        return self.get_edit_text()


class PrimitivusTextBoxWidget(
    xmlui.TextBoxWidget, sat_widgets.AdvancedEdit, PrimitivusEvents
):
    def __init__(self, _xmlui_parent, value, read_only=False):
        sat_widgets.AdvancedEdit.__init__(self, edit_text=value, multiline=True)
        self.read_only = read_only

    def selectable(self):
        if self.read_only:
            return False
        return super(PrimitivusTextBoxWidget, self).selectable()

    def _xmluiSetValue(self, value):
        self.set_edit_text(value)

    def _xmluiGetValue(self):
        return self.get_edit_text()


class PrimitivusBoolWidget(xmlui.BoolWidget, urwid.CheckBox, PrimitivusEvents):
    def __init__(self, _xmlui_parent, state, read_only=False):
        urwid.CheckBox.__init__(self, "", state=state)
        self.read_only = read_only

    def selectable(self):
        if self.read_only:
            return False
        return super(PrimitivusBoolWidget, self).selectable()

    def _xmluiSetValue(self, value):
        self.set_state(value == "true")

    def _xmluiGetValue(self):
        return C.BOOL_TRUE if self.get_state() else C.BOOL_FALSE


class PrimitivusIntWidget(xmlui.IntWidget, sat_widgets.AdvancedEdit, PrimitivusEvents):
    def __init__(self, _xmlui_parent, value, read_only=False):
        sat_widgets.AdvancedEdit.__init__(self, edit_text=value)
        self.read_only = read_only

    def selectable(self):
        if self.read_only:
            return False
        return super(PrimitivusIntWidget, self).selectable()

    def _xmluiSetValue(self, value):
        self.set_edit_text(value)

    def _xmluiGetValue(self):
        return self.get_edit_text()


class PrimitivusButtonWidget(
    xmlui.ButtonWidget, sat_widgets.CustomButton, PrimitivusEvents
):
    def __init__(self, _xmlui_parent, value, click_callback):
        sat_widgets.CustomButton.__init__(self, value, on_press=click_callback)

    def _xmluiOnClick(self, callback):
        urwid.connect_signal(self, "click", callback)


class PrimitivusListWidget(xmlui.ListWidget, sat_widgets.List, PrimitivusEvents):
    def __init__(self, _xmlui_parent, options, selected, flags):
        sat_widgets.List.__init__(self, options=options, style=flags)
        self._xmluiSelectValues(selected)

    def _xmluiSelectValue(self, value):
        return self.selectValue(value)

    def _xmluiSelectValues(self, values):
        return self.selectValues(values)

    def _xmluiGetSelectedValues(self):
        return [option.value for option in self.getSelectedValues()]

    def _xmluiAddValues(self, values, select=True):
        current_values = self.getAllValues()
        new_values = copy.deepcopy(current_values)
        for value in values:
            if value not in current_values:
                new_values.append(value)
        if select:
            selected = self._xmluiGetSelectedValues()
        self.changeValues(new_values)
        if select:
            for value in values:
                if value not in selected:
                    selected.append(value)
            self._xmluiSelectValues(selected)


class PrimitivusJidsListWidget(xmlui.ListWidget, sat_widgets.List, PrimitivusEvents):
    def __init__(self, _xmlui_parent, jids, styles):
        sat_widgets.List.__init__(
            self,
            options=jids + [""],  # the empty field is here to add new jids if needed
            option_type=lambda txt, align: sat_widgets.AdvancedEdit(
                edit_text=txt, align=align
            ),
            on_change=self._onChange,
        )
        self.delete = 0

    def _onChange(self, list_widget, jid_widget=None, text=None):
        if jid_widget is not None:
            if jid_widget != list_widget.contents[-1] and not text:
                # if a field is empty, we delete the line (except for the last line)
                list_widget.contents.remove(jid_widget)
            elif jid_widget == list_widget.contents[-1] and text:
                # we always want an empty field as last value to be able to add jids
                list_widget.contents.append(sat_widgets.AdvancedEdit())

    def _xmluiGetSelectedValues(self):
        # XXX: there is not selection in this list, so we return all non empty values
        return [jid_ for jid_ in self.getAllValues() if jid_]


class PrimitivusAdvancedListContainer(
    xmlui.AdvancedListContainer, sat_widgets.TableContainer, PrimitivusEvents
):
    def __init__(self, _xmlui_parent, columns, selectable="no"):
        options = {"ADAPT": ()}
        if selectable != "no":
            options["HIGHLIGHT"] = ()
        sat_widgets.TableContainer.__init__(
            self, columns=columns, options=options, row_selectable=selectable != "no"
        )

    def _xmluiAppend(self, widget):
        self.addWidget(widget)

    def _xmluiAddRow(self, idx):
        self.setRowIndex(idx)

    def _xmluiGetSelectedWidgets(self):
        return self.getSelectedWidgets()

    def _xmluiGetSelectedIndex(self):
        return self.getSelectedIndex()

    def _xmluiOnSelect(self, callback):
        """ Call callback with widget as only argument """
        urwid.connect_signal(self, "click", self._event_callback, callback)


class PrimitivusPairsContainer(xmlui.PairsContainer, sat_widgets.TableContainer):
    def __init__(self, _xmlui_parent):
        options = {"ADAPT": (0,), "HIGHLIGHT": (0,)}
        if self._xmlui_main.type == "param":
            options["FOCUS_ATTR"] = "param_selected"
        sat_widgets.TableContainer.__init__(self, columns=2, options=options)

    def _xmluiAppend(self, widget):
        if isinstance(widget, PrimitivusEmptyWidget):
            # we don't want highlight on empty widgets
            widget = urwid.AttrMap(widget, "default")
        self.addWidget(widget)


class PrimitivusLabelContainer(PrimitivusPairsContainer, xmlui.LabelContainer):
    pass


class PrimitivusTabsContainer(xmlui.TabsContainer, sat_widgets.TabsContainer):
    def __init__(self, _xmlui_parent):
        sat_widgets.TabsContainer.__init__(self)

    def _xmluiAppend(self, widget):
        self.body.append(widget)

    def _xmluiAddTab(self, label, selected):
        tab = PrimitivusVerticalContainer(None)
        self.addTab(label, tab, selected)
        return tab


class PrimitivusVerticalContainer(xmlui.VerticalContainer, urwid.ListBox):
    BOX_HEIGHT = 5

    def __init__(self, _xmlui_parent):
        urwid.ListBox.__init__(self, urwid.SimpleListWalker([]))
        self._last_size = None

    def _xmluiAppend(self, widget):
        if "flow" not in widget.sizing():
            widget = urwid.BoxAdapter(widget, self.BOX_HEIGHT)
        self.body.append(widget)

    def render(self, size, focus=False):
        if size != self._last_size:
            (maxcol, maxrow) = size
            if self.body:
                widget = self.body[0]
                if isinstance(widget, urwid.BoxAdapter):
                    widget.height = maxrow
            self._last_size = size
        return super(PrimitivusVerticalContainer, self).render(size, focus)


### Dialogs ###


class PrimitivusDialog(object):
    def __init__(self, _xmlui_parent):
        self.host = _xmlui_parent.host

    def _xmluiShow(self):
        self.host.showPopUp(self)

    def _xmluiClose(self):
        self.host.removePopUp(self)


class PrimitivusMessageDialog(PrimitivusDialog, xmlui.MessageDialog, sat_widgets.Alert):
    def __init__(self, _xmlui_parent, title, message, level):
        PrimitivusDialog.__init__(self, _xmlui_parent)
        xmlui.MessageDialog.__init__(self, _xmlui_parent)
        sat_widgets.Alert.__init__(
            self, title, message, ok_cb=lambda __: self._xmluiClose()
        )


class PrimitivusNoteDialog(xmlui.NoteDialog, PrimitivusMessageDialog):
    # TODO: separate NoteDialog
    pass


class PrimitivusConfirmDialog(
    PrimitivusDialog, xmlui.ConfirmDialog, sat_widgets.ConfirmDialog
):
    def __init__(self, _xmlui_parent, title, message, level, buttons_set):
        PrimitivusDialog.__init__(self, _xmlui_parent)
        xmlui.ConfirmDialog.__init__(self, _xmlui_parent)
        sat_widgets.ConfirmDialog.__init__(
            self,
            title,
            message,
            no_cb=lambda __: self._xmluiCancelled(),
            yes_cb=lambda __: self._xmluiValidated(),
        )


class PrimitivusFileDialog(
    PrimitivusDialog, xmlui.FileDialog, files_management.FileDialog
):
    def __init__(self, _xmlui_parent, title, message, level, filetype):
        # TODO: message is not managed yet
        PrimitivusDialog.__init__(self, _xmlui_parent)
        xmlui.FileDialog.__init__(self, _xmlui_parent)
        style = []
        if filetype == C.XMLUI_DATA_FILETYPE_DIR:
            style.append("dir")
        files_management.FileDialog.__init__(
            self,
            ok_cb=lambda path: self._xmluiValidated({"path": path}),
            cancel_cb=lambda __: self._xmluiCancelled(),
            message=message,
            title=title,
            style=style,
        )


class GenericFactory(object):
    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = globals()[
                "Primitivus" + attr[6:]
            ]  # XXX: we prefix with "Primitivus" to work around an Urwid bug, WidgetMeta in Urwid don't manage multiple inheritance with same names
            return cls


class WidgetFactory(GenericFactory):
    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = GenericFactory.__getattr__(self, attr)
            cls._xmlui_main = self._xmlui_main
            return cls


class XMLUIPanel(xmlui.XMLUIPanel, PrimitivusWidget):
    widget_factory = WidgetFactory()

    def __init__(
        self,
        host,
        parsed_xml,
        title=None,
        flags=None,
        callback=None,
        ignore=None,
        whitelist=None,
        profile=C.PROF_KEY_NONE,
    ):
        self.widget_factory._xmlui_main = self
        self._dest = None
        xmlui.XMLUIPanel.__init__(
            self,
            host,
            parsed_xml,
            title=title,
            flags=flags,
            callback=callback,
            ignore=ignore,
            profile=profile,
        )
        PrimitivusWidget.__init__(self, self.main_cont, self.xmlui_title)


    def _parseChilds(self, _xmlui_parent, current_node, wanted=("container",), data=None):
        # Small hack to always have a VerticalContainer as main container in Primitivus.
        # this used to be the default behaviour for all frontends, but now
        # TabsContainer can also be the main container.
        if _xmlui_parent is self:
            node = current_node.childNodes[0]
            if node.nodeName == "container" and node.getAttribute("type") == "tabs":
                _xmlui_parent = self.widget_factory.createVerticalContainer(self)
                self.main_cont = _xmlui_parent
        return super(XMLUIPanel, self)._parseChilds(_xmlui_parent, current_node, wanted,
                                                    data)


    def constructUI(self, parsed_dom):
        def postTreat():
            assert self.main_cont.body

            if self.type in ("form", "popup"):
                buttons = []
                if self.type == "form":
                    buttons.append(urwid.Button(_("Submit"), self.onFormSubmitted))
                    if not "NO_CANCEL" in self.flags:
                        buttons.append(urwid.Button(_("Cancel"), self.onFormCancelled))
                else:
                    buttons.append(
                        urwid.Button(_("OK"), on_press=lambda __: self._xmluiClose())
                    )
                max_len = max([len(button.get_label()) for button in buttons])
                grid_wid = urwid.GridFlow(buttons, max_len + 4, 1, 0, "center")
                self.main_cont.body.append(grid_wid)
            elif self.type == "param":
                tabs_cont = self.main_cont.body[0].base_widget
                assert isinstance(tabs_cont, sat_widgets.TabsContainer)
                buttons = []
                buttons.append(sat_widgets.CustomButton(_("Save"), self.onSaveParams))
                buttons.append(
                    sat_widgets.CustomButton(
                        _("Cancel"), lambda x: self.host.removeWindow()
                    )
                )
                max_len = max([button.getSize() for button in buttons])
                grid_wid = urwid.GridFlow(buttons, max_len, 1, 0, "center")
                tabs_cont.addFooter(grid_wid)

        xmlui.XMLUIPanel.constructUI(self, parsed_dom, postTreat)
        urwid.WidgetWrap.__init__(self, self.main_cont)

    def show(self, show_type=None, valign="middle"):
        """Show the constructed UI
        @param show_type: how to show the UI:
            - None (follow XMLUI's recommendation)
            - 'popup'
            - 'window'
        @param valign: vertical alignment when show_type is 'popup'.
            Ignored when show_type is 'window'.

        """
        if show_type is None:
            if self.type in ("window", "param"):
                show_type = "window"
            elif self.type in ("popup", "form"):
                show_type = "popup"

        if show_type not in ("popup", "window"):
            raise ValueError("Invalid show_type [%s]" % show_type)

        self._dest = show_type
        if show_type == "popup":
            self.host.showPopUp(self, valign=valign)
        elif show_type == "window":
            self.host.newWidget(self)
        else:
            assert False
        self.host.redraw()

    def _xmluiClose(self):
        if self._dest == "window":
            self.host.removeWindow()
        elif self._dest == "popup":
            self.host.removePopUp(self)
        else:
            raise exceptions.InternalError(
                "self._dest unknown, are you sure you have called XMLUI.show ?"
            )


class XMLUIDialog(xmlui.XMLUIDialog):
    dialog_factory = GenericFactory()


xmlui.registerClass(xmlui.CLASS_PANEL, XMLUIPanel)
xmlui.registerClass(xmlui.CLASS_DIALOG, XMLUIDialog)
create = xmlui.create
