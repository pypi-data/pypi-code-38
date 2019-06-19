# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from sympathy.platform import qt_compat
from . import parameter_helper_gui as gui
from sympathy.utils.context import trim_doc
from sympathy.utils.context import indent_doc

QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


class IParameterVisitor(object):
    def visit_root(self, root):
        pass

    def visit_group(self, group):
        pass

    def visit_page(self, page):
        pass

    def visit_integer(self, value):
        pass

    def visit_float(self, value):
        pass

    def visit_string(self, value):
        pass

    def visit_boolean(self, value):
        pass

    def visit_list(self, plist):
        pass

    def visit_custom(self, custom):
        pass


class ShowParameterVisitor(object):
    """
    Builds a string of all visited parameter leaf entities, the string result
    is available in instance.result. The format of the string compatible with
    the documentation format used, and is valid Restructured Text.

    This useful for generating the documentation for the configuration options.
    """
    def __init__(self):
        self.result = None

    def visit_root(self, root):
        self.visit_group(root)

    def visit_group(self, group):
        results = []
        for item in group.children():
            visitor = ShowParameterVisitor()
            item.accept(visitor)
            results.append(visitor.result)
        self.result = u'\n'.join(results)

    def visit_page(self, page):
        self.visit_group(page)

    def visit_integer(self, value):
        self.visit_value(value)

    def visit_float(self, value):
        self.visit_value(value)

    def visit_string(self, value):
        self.visit_value(value)

    def visit_boolean(self, value):
        self.visit_value(value)

    def visit_list(self, plist):
        self.visit_value(plist)

    def visit_custom(self, custom):
        self.visit_value(custom)

    def visit_value(self, value):
        self.result = u'**{}**\n{}'.format(
            value.name or value.label,
            indent_doc(
                trim_doc(value.description or '(no description)'), 4))


class ReorderVisitor(IParameterVisitor):
    """Order elements."""
    def visit_root(self, root):
        self.visit_group(root)

    def visit_group(self, group):
        group.reorder()
        for item in group.children():
            item.accept(self)

    def visit_page(self, page):
        self.visit_group(page)


class NullParameterWidget(object):
    def add_group(self, widget):
        pass

    def add_page(self, widget, label):
        pass

    def add_widget(self, widget):
        pass


class WidgetBuildingVisitor(IParameterVisitor):
    def __init__(self, validator=None):
        self._validator = validator
        self._widget_stack = []
        self._flat_widget_dict = {}
        self._null_root = NullParameterWidget()

    def gui(self):
        return self._parent()

    def widget_dict(self):
        return self._flat_widget_dict

    def visit_root(self, root):
        widget = gui.ParameterGroupWidget(root, validator=self._validator)
        self._push_parent(widget)
        children = root.children()
        for child in children:
            child.accept(self)
        if widget.needs_stretch():
            widget.group_layout().addStretch()

    def visit_group(self, group):
        group_widget = gui.ParameterGroupWidget(group)
        if group.type == 'page':
            self._parent().add_page(group_widget, group.label)
        else:
            self._parent().add_group(group_widget)
        self._flat_widget_dict[group.name] = group_widget
        self._push_parent(group_widget)
        children = group.children()
        for child in children:
            child.accept(self)
        if group_widget.needs_stretch():
            group_widget.group_layout().addStretch()
        self._pop_parent()

    def visit_page(self, page):
        self.visit_group(page)

    def visit_integer(self, value):
        integer_widget = None
        if value.editor is None:
            integer_widget = gui.ParameterNumericValueWidget(value)
        else:
            integer_widget = gui.ParameterNumericValueWidget(
                value, gui.editor_factory(
                    value.editor['type'],
                    value.editor,
                    value))
        self._flat_widget_dict[value.name] = integer_widget
        self._parent().add_widget(integer_widget)

    def visit_float(self, value):
        float_widget = None
        if value.editor is None:
            float_widget = gui.ParameterNumericValueWidget(value)
        else:
            float_widget = gui.ParameterNumericValueWidget(
                value, gui.editor_factory(
                    value.editor['type'],
                    value.editor,
                    value))
        self._flat_widget_dict[value.name] = float_widget
        self._parent().add_widget(float_widget)

    def visit_string(self, value):
        string_widget = None
        if value.editor is None:
            string_widget = gui.ParameterStringWidget(value)
        else:
            string_widget = gui.ParameterStringWidget(
                value, gui.editor_factory(
                    value.editor['type'],
                    value.editor,
                    value))
        self._flat_widget_dict[value.name] = string_widget
        self._parent().add_widget(string_widget)

    def visit_boolean(self, value):
        boolean_widget = gui.ParameterBooleanWidget(value)
        self._flat_widget_dict[value.name] = boolean_widget
        self._parent().add_widget(boolean_widget)

    def visit_list(self, plist):
        if plist.editor is None:
            widget = gui.ParameterListWidget(plist)
        else:
            widget = gui.ParameterListWidget(
                plist, gui.editor_factory(
                    plist.editor.get('type', None),
                    plist.editor,
                    plist))
        self._flat_widget_dict[plist.name] = widget
        self._parent().add_widget(widget)

    def visit_custom(self, custom):
        pass

    def _parent(self):
        try:
            return self._widget_stack[-1]
        except IndexError:
            return self._null_root

    def _push_parent(self, widget):
        self._widget_stack.append(widget)

    def _pop_parent(self):
        if len(self._widget_stack) > 1:
            return self._widget_stack.pop()


class MyCustomWidgetBuildingVisitor(WidgetBuildingVisitor):
    def __init__(self):
        super(MyCustomWidgetBuildingVisitor, self).__init__()

    def visit_custom(self, custom):
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtGui.QLabel("Hello")
        layout.addWidget(label)
        widget.setLayout(layout)
        self._parent().add_widget(widget)
