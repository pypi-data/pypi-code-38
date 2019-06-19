# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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

"""Sympathy Plugin"""

# pylint: disable=C0103
# pylint: disable=R0903
# pylint: disable=R0911
# pylint: disable=R0201

# Local imports
import types
import inspect
import sqlite3
import tempfile
import os
import six
from spyderlib.baseconfig import get_translation
from spyderlib.utils.qthelpers import get_icon, create_action
from spyderlib.plugins import SpyderPluginMixin

from spyderplugins.widgets.sympathygui import SympathyWidget
_ = get_translation("p_sympathy", dirname="spyderplugins")


class Sympathy(SympathyWidget, SpyderPluginMixin):
    """Sympathy"""

    CONF_SECTION = 'sympathy'
    GLOBAL = {}
#    CONFIGWIDGET_CLASS = SympathyConfigPage

    def __init__(self, parent=None):
        SympathyWidget.__init__(self, parent=parent)
        SpyderPluginMixin.__init__(self, parent)

        # Initialize plugin
        self.initialize_plugin()
        self.set_data()
        self._unleash_monkey_mayhem()

    def _unleash_monkey_mayhem(self):

        def get_dst(src):
            try:
                db = os.path.join(tempfile.gettempdir(),
                                  'sympathy_1.1.dbg.sqlite3')
                conn = sqlite3.connect(db)
                return six.next(conn.execute(
                    'SELECT dst from dbg where src = ?', (src, )))[0]
            except (sqlite3.OperationalError, StopIteration):
                pass
            finally:
                conn.close()
            return src

        def editor_get_current_filename_monkey(instance):
            fname = type(instance).get_current_filename(instance)
            stack = inspect.stack()

            if stack[1][3] == 'run_file':
                return get_dst(fname)

            return fname

        self.get_current_filename = self.main.editor.get_current_filename
        self.main.editor.get_current_filename = types.MethodType(
            editor_get_current_filename_monkey, self.main.editor)

    # ------ SpyderPluginWidget API -------------------------------------------

    def get_plugin_title(self):
        return _("Sympathy")

    def get_plugin_icon(self):
        return get_icon('bug.png')

    def get_focus_widget(self):
        return self

    def get_plugin_actions(self):
        return []

    def on_first_registration(self):
        self.main.tabify_plugins(self.main.inspector, self)

    def register_plugin(self):
        self.main.add_dockwidget(self)
        list_action = create_action(self, _("Sympathy"),
                                    triggered=self.show)
        list_action.setEnabled(True)
        self.register_shortcut(list_action, context="Editor",
                               name="Sympathy", default="Ctrl+Y")
        self.main.editor.pythonfile_dependent_actions += [list_action]

    def refresh_plugin(self):
        pass

    def closing_plugin(self, cancelable=False):
        return True

    def apply_plugin_settings(self, options):
        pass

    def show(self):
        if self.dockwidget and not self.ismaximized:
            self.dockwidget.setVisible(True)
            self.dockwidget.setFocus()
            self.dockwidget.raise_()


# =============================================================================
# The following statements are required to register this 3rd party plugin:
# =============================================================================
PLUGIN_CLASS = Sympathy
