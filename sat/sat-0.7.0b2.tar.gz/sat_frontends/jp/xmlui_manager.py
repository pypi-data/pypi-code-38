#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# JP: a SàT frontend
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

from sat.core.log import getLogger

log = getLogger(__name__)
from sat_frontends.tools import xmlui as xmlui_base
from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A
from sat.core.i18n import _
from functools import partial

# workflow constants

SUBMIT = "SUBMIT"  # submit form


## Widgets ##


class Base(object):
    """Base for Widget and Container"""

    type = None
    _root = None

    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent
        self.host = self.xmlui_parent.host

    @property
    def root(self):
        """retrieve main XMLUI parent class"""
        if self._root is not None:
            return self._root
        root = self
        while not isinstance(root, xmlui_base.XMLUIBase):
            root = root.xmlui_parent
        self._root = root
        return root

    def disp(self, *args, **kwargs):
        self.host.disp(*args, **kwargs)


class Widget(Base):
    category = u"widget"
    enabled = True

    @property
    def name(self):
        return self._xmlui_name

    def show(self):
        """display current widget

        must be overriden by subclasses
        """
        raise NotImplementedError(self.__class__)

    def verboseName(self, elems=None, value=None):
        """add name in color to the elements

        helper method to display name which can then be used to automate commands
        elems is only modified if verbosity is > 0
        @param elems(list[unicode], None): elements to display
            None to display name directly
        @param value(unicode, None): value to show
            use self.name if None
        """
        if value is None:
            value = self.name
        if self.host.verbosity:
            to_disp = [
                A.FG_MAGENTA,
                u" " if elems else u"",
                u"({})".format(value),
                A.RESET,
            ]
            if elems is None:
                self.host.disp(A.color(*to_disp))
            else:
                elems.extend(to_disp)


class ValueWidget(Widget):
    def __init__(self, xmlui_parent, value):
        super(ValueWidget, self).__init__(xmlui_parent)
        self.value = value

    @property
    def values(self):
        return [self.value]


class InputWidget(ValueWidget):
    def __init__(self, xmlui_parent, value, read_only=False):
        super(InputWidget, self).__init__(xmlui_parent, value)
        self.read_only = read_only

    def _xmluiGetValue(self):
        return self.value


class OptionsWidget(Widget):
    def __init__(self, xmlui_parent, options, selected, style):
        super(OptionsWidget, self).__init__(xmlui_parent)
        self.options = options
        self.selected = selected
        self.style = style

    @property
    def values(self):
        return self.selected

    @values.setter
    def values(self, values):
        self.selected = values

    @property
    def value(self):
        return self.selected[0]

    @value.setter
    def value(self, value):
        self.selected = [value]

    def _xmluiSelectValue(self, value):
        self.value = value

    def _xmluiSelectValues(self, values):
        self.values = values

    def _xmluiGetSelectedValues(self):
        return self.values

    @property
    def labels(self):
        """return only labels from self.items"""
        for value, label in self.items:
            yield label

    @property
    def items(self):
        """return suitable items, according to style"""
        no_select = self.no_select
        for value, label in self.options:
            if no_select or value in self.selected:
                yield value, label

    @property
    def inline(self):
        return u"inline" in self.style

    @property
    def no_select(self):
        return u"noselect" in self.style


class EmptyWidget(xmlui_base.EmptyWidget, Widget):

    def __init__(self, xmlui_parent):
        Widget.__init__(self, xmlui_parent)

    def show(self):
        self.host.disp(u'')


class TextWidget(xmlui_base.TextWidget, ValueWidget):
    type = u"text"

    def show(self):
        self.host.disp(self.value)


class LabelWidget(xmlui_base.LabelWidget, ValueWidget):
    type = u"label"

    @property
    def for_name(self):
        try:
            return self._xmlui_for_name
        except AttributeError:
            return None

    def show(self, no_lf=False, ansi=u""):
        """show label

        @param no_lf(bool): same as for [JP.disp]
        @param ansi(unicode): ansi escape code to print before label
        """
        self.disp(A.color(ansi, self.value), no_lf=no_lf)


class JidWidget(xmlui_base.JidWidget, TextWidget):
    type = u"jid"

class StringWidget(xmlui_base.StringWidget, InputWidget):
    type = u"string"

    def show(self):
        if self.read_only or self.root.read_only:
            self.disp(self.value)
        else:
            elems = []
            self.verboseName(elems)
            if self.value:
                elems.append(_(u"(enter: {default})").format(default=self.value))
            elems.extend([C.A_HEADER, u"> "])
            value = raw_input(A.color(*elems).encode('utf-8'))
            if value:
                #  TODO: empty value should be possible
                #       an escape key should be used for default instead of enter with empty value
                self.value = value


class JidInputWidget(xmlui_base.JidInputWidget, StringWidget):
    type = u"jid_input"


class TextBoxWidget(xmlui_base.TextWidget, StringWidget):
    type = u"textbox"
    # TODO: use a more advanced input method

    def show(self):
        self.verboseName()
        if self.read_only or self.root.read_only:
            self.disp(self.value)
        else:
            if self.value:
                self.disp(A.color(C.A_HEADER, u"↓ current value ↓\n", A.FG_CYAN, self.value,
                                  ""))

            values = []
            while True:
                try:
                    if not values:
                        line = raw_input(A.color(C.A_HEADER, u"[Ctrl-D to finish]> "))
                    else:
                        line = raw_input()
                    values.append(line)
                except EOFError:
                   break

            self.value = u'\n'.join(values).rstrip()


class XHTMLBoxWidget(xmlui_base.XHTMLBoxWidget, StringWidget):
    type = u"xhtmlbox"

    def show(self):
        # FIXME: we use bridge in a blocking way as permitted by python-dbus
        #        this only for now to make it simpler, it must be refactored
        #        to use async when jp will be fully async (expected for 0.8)
        self.value = self.host.bridge.syntaxConvert(
            self.value, C.SYNTAX_XHTML, "markdown", False, self.host.profile)
        super(XHTMLBoxWidget, self).show()


class ListWidget(xmlui_base.ListWidget, OptionsWidget):
    type = u"list"
    # TODO: handle flags, notably multi

    def show(self):
        if self.root.values_only:
            for value in self.values:
                self.disp(self.value)
                return
        if not self.options:
            return

        # list display
        self.verboseName()

        for idx, (value, label) in enumerate(self.options):
            elems = []
            if not self.root.read_only:
                elems.extend([C.A_SUBHEADER, unicode(idx), A.RESET, u": "])
            elems.append(label)
            self.verboseName(elems, value)
            self.disp(A.color(*elems))

        if self.root.read_only:
            return

        if len(self.options) == 1:
            # we have only one option, no need to ask
            self.value = self.options[0][0]
            return

        #  we ask use to choose an option
        choice = None
        limit_max = len(self.options) - 1
        while choice is None or choice < 0 or choice > limit_max:
            choice = raw_input(
                A.color(C.A_HEADER, _(u"your choice (0-{max}): ").format(max=limit_max))
            )
            try:
                choice = int(choice)
            except ValueError:
                choice = None
        self.value = self.options[choice][0]
        self.disp("")


class BoolWidget(xmlui_base.BoolWidget, InputWidget):
    type = u"bool"

    def show(self):
        disp_true = A.color(A.FG_GREEN, u"TRUE")
        disp_false = A.color(A.FG_RED, u"FALSE")
        if self.read_only or self.root.read_only:
            self.disp(disp_true if self.value else disp_false)
        else:
            self.disp(A.color(C.A_HEADER, u"0: ",
                              disp_false, A.RESET,
                              u" *" if not self.value else u""))
            self.disp(A.color(C.A_HEADER, u"1: ",
                              disp_true, A.RESET,
                              u" *" if self.value else u""))
            choice = None
            while choice not in ("0", "1"):
                elems = [C.A_HEADER, _(u"your choice (0,1): ")]
                self.verboseName(elems)
                choice = raw_input(A.color(*elems))
            self.value = bool(int(choice))
            self.disp("")

    def _xmluiGetValue(self):
        return C.boolConst(self.value)


## Containers ##


class Container(Base):
    category = u"container"

    def __init__(self, xmlui_parent):
        super(Container, self).__init__(xmlui_parent)
        self.children = []

    def __iter__(self):
        return iter(self.children)

    def _xmluiAppend(self, widget):
        self.children.append(widget)

    def _xmluiRemove(self, widget):
        self.children.remove(widget)

    def show(self):
        for child in self.children:
            child.show()


class VerticalContainer(xmlui_base.VerticalContainer, Container):
    type = u"vertical"


class PairsContainer(xmlui_base.PairsContainer, Container):
    type = u"pairs"


class LabelContainer(xmlui_base.PairsContainer, Container):
    type = u"label"

    def show(self):
        for child in self.children:
            no_lf = False
            # we check linked widget type
            # to see if we want the label on the same line or not
            if child.type == u"label":
                for_name = child.for_name
                if for_name:
                    for_widget = self.root.widgets[for_name]
                    wid_type = for_widget.type
                    if self.root.values_only or wid_type in (
                        "text",
                        "string",
                        "jid_input",
                    ):
                        no_lf = True
                    elif wid_type == "bool" and for_widget.read_only:
                        no_lf = True
                child.show(no_lf=no_lf, ansi=A.FG_CYAN)
            else:
                child.show()


## Dialogs ##


class Dialog(object):
    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent
        self.host = self.xmlui_parent.host

    def disp(self, *args, **kwargs):
        self.host.disp(*args, **kwargs)

    def show(self):
        """display current dialog

        must be overriden by subclasses
        """
        raise NotImplementedError(self.__class__)


class NoteDialog(xmlui_base.NoteDialog, Dialog):
    def show(self):
        # TODO: handle title and level
        self.disp(self.message)

    def __init__(self, xmlui_parent, title, message, level):
        Dialog.__init__(self, xmlui_parent)
        xmlui_base.NoteDialog.__init__(self, xmlui_parent)
        self.title, self.message, self.level = title, message, level


## Factory ##


class WidgetFactory(object):
    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = globals()[attr[6:]]
            return cls


class XMLUIPanel(xmlui_base.XMLUIPanel):
    widget_factory = WidgetFactory()
    _actions = 0  # use to keep track of bridge's launchAction calls
    read_only = False
    values_only = False
    workflow = None
    _submit_cb = None

    def __init__(self, host, parsed_dom, title=None, flags=None, callback=None,
                 ignore=None, whitelist=None, profile=None):
        xmlui_base.XMLUIPanel.__init__(
            self,
            host,
            parsed_dom,
            title=title,
            flags=flags,
            ignore=ignore,
            whitelist=whitelist,
            profile=host.profile,
        )
        self.submitted = False

    @property
    def command(self):
        return self.host.command

    def show(self, workflow=None, read_only=False, values_only=False):
        """display the panel

        @param workflow(list, None): command to execute if not None
            put here for convenience, the main workflow is the class attribute
            (because workflow can continue in subclasses)
            command are a list of consts or lists:
                - SUBMIT is the only constant so far, it submits the XMLUI
                - list must contain widget name/widget value to fill
        @param read_only(bool): if True, don't request values
        @param values_only(bool): if True, only show select values (imply read_only)
        """
        self.read_only = read_only
        self.values_only = values_only
        if self.values_only:
            self.read_only = True
        if workflow:
            XMLUIPanel.workflow = workflow
        if XMLUIPanel.workflow:
            self.runWorkflow()
        else:
            self.main_cont.show()

    def runWorkflow(self):
        """loop into workflow commands and execute commands

        SUBMIT will interrupt workflow (which will be continue on callback)
        @param workflow(list): same as [show]
        """
        workflow = XMLUIPanel.workflow
        while True:
            try:
                cmd = workflow.pop(0)
            except IndexError:
                break
            if cmd == SUBMIT:
                self.onFormSubmitted()
                self.submit_id = None  # avoid double submit
                return
            elif isinstance(cmd, list):
                name, value = cmd
                widget = self.widgets[name]
                if widget.type == "bool":
                    value = C.bool(value)
                widget.value = value
        self.show()

    def submitForm(self, callback=None):
        XMLUIPanel._submit_cb = callback
        self.onFormSubmitted()

    def onFormSubmitted(self, ignore=None):
        #  self.submitted is a Q&D workaround to avoid
        # double submit when a workflow is set
        if self.submitted:
            return
        self.submitted = True
        super(XMLUIPanel, self).onFormSubmitted(ignore)

    def _xmluiClose(self):
        pass

    def _launchActionCb(self, data):
        XMLUIPanel._actions -= 1
        assert XMLUIPanel._actions >= 0
        if u"xmlui" in data:
            xmlui_raw = data["xmlui"]
            xmlui = create(self.host, xmlui_raw)
            xmlui.show()
            if xmlui.submit_id:
                xmlui.onFormSubmitted()
        # TODO: handle data other than XMLUI
        if not XMLUIPanel._actions:
            if self._submit_cb is None:
                self.host.quit()
            else:
                self._submit_cb()

    def _xmluiLaunchAction(self, action_id, data):
        XMLUIPanel._actions += 1
        self.host.bridge.launchAction(
            action_id,
            data,
            self.profile,
            callback=self._launchActionCb,
            errback=partial(
                self.command.errback,
                msg=_(u"can't launch XMLUI action: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class XMLUIDialog(xmlui_base.XMLUIDialog):
    type = "dialog"
    dialog_factory = WidgetFactory()
    read_only = False

    def show(self, __=None):
        self.dlg.show()

    def _xmluiClose(self):
        pass


create = partial(xmlui_base.create, class_map={
    xmlui_base.CLASS_PANEL: XMLUIPanel,
    xmlui_base.CLASS_DIALOG: XMLUIDialog})
