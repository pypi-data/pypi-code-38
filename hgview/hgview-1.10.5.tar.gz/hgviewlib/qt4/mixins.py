# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

#
# make sure the Qt rc files are converted into python modules, then load them
# this must be done BEFORE other hgview qt4 modules are loaded.
import os
import os.path as osp
import sys

from PyQt4 import uic
from PyQt4.QtCore import QTimer, Qt
from PyQt4.QtGui import QAction, QActionGroup, QMenu, QShortcut

from hgviewlib.config import HgConfig
from hgviewlib.qt4 import should_rebuild
from hgviewlib.qt4 import icon as geticon
from hgviewlib.qt4.config import get_font

class ActionsMixin(object):
    """
    A Mixin for Hgview widgets containing a simple way to create and register Qt
    actions.
    """

    def __init__(self, *args, **kwargs):
        super(ActionsMixin, self).__init__(*args, **kwargs)
        self._actions = {}
        self._action_groups = {}
        self._action_groups_order = []

    def _set_action(self, name, **parameters):
        """Set the registred At action named ``name``.
        ``parameters`` are optional arguments given to ``add_action``.
        """
        action = self._actions[name]

        if parameters.get('icon'):
            action.setIcon(geticon(parameters['icon']))

        if parameters.get('tip'):
            action.setStatusTip(parameters['tip'])

        if parameters.get('keys'):
            action.setShortcuts(parameters['keys'])

        if parameters.get('checked') is not None:
            action.setCheckable(True)
            action.setChecked(parameters['checked'])

        action.setEnabled(parameters.get('enabled', True))

        if parameters.get('callback'):
            if parameters.get('checked') is not None:
                signal = action.toggled[bool]
            else:
                signal = action.triggered
            signal.connect(parameters['callback'])

        menu = parameters.get('menu', None)
        if menu is not None:
            if menu not in self._action_groups:
                group = QActionGroup(self)
                self._action_groups[unicode(menu)] = group
                self._action_groups_order.append(menu)
                group.addAction(menu).setSeparator(True)
            else:
                group = self._action_groups[unicode(menu)]
            group.setExclusive(False)
            group.addAction(action)

    def set_action(self, name, **parameters):
        """Set the registred At action named ``name``.
        ``parameters`` are optional arguments given to ``add_action``.
        """
        # delayed to not append after add_action
        QTimer.singleShot(0, lambda: self._set_action(name, **parameters))

    def set_actions(self, *names, **parameters):
        """Same as set_actions but accept multiple registred actions names
        as positioned arguments.
        """
        for name in names:
            self.set_action(name, **parameters)

    def add_action(self, name, action, **options):
        """Add and attach an action to the widget.

        The action setup is finalized in a dedicated thread in order to speed
        up the hgview start up.

        .. note:: the action is added to the context menu of the widget
                  if the ``menu`` option is specified.

        Arguments
        ---------

        :name: action name
        :action: a QAction object or a short desciption string.

        Optional arguments
        ------------------

        :menu: a string containing the group name of the action in the context
               menu. The action is not added to context menu if set to None
               (default).

        :checked: A boolean to set the action as checkable or None.
                  The boolean value is used for the action checked status.
                  (default: None == non checkable).

        :enabled: A boolean value used for the enabled status (default True)

        :callback: a slot called on the ``triggered()`` signal (or
                   ``toggled[bool]`` if ``checkable is True)

        :icon: registred icon name as expected by ``hgviewlib.qt4.icon(icon)``

        :keys: a single keybinding or a list of keybindings (see Qt bindings definition)

        :tip: extended desciption string

        """
        if not isinstance(action, QAction):
            action = QAction(action, self)
        self._actions[name] = action
        self.addAction(action)
        QTimer.singleShot(0, lambda: self._set_action(name, **options))
        return action

    def get_action(self, name):
        """Return the registred qt action object named ``name``."""
        return self._actions[name]

    def get_actions(self, *names):
        """Return a tuple of registred qt actions named ``names``."""
        return tuple(self.get_action(name) for name in names)

    def contextMenuEvent(self, event):
        """Overwritte context menu event  to add registred actions."""
        try:
            menu = self.createStandardContextMenu()
        except AttributeError:
            menu = QMenu(self)
        for name in  self._action_groups_order:
            group = self._action_groups[name]
            menu.addActions(group.actions())
        menu.exec_(event.globalPos())

def ui2cls(ui_name):
    """Compile the .ui file named ``ui_name`` into a python class en return it.

    Also tyr to comvert the .ui file into a .py file in order to generate the
    python code only once. This allow to speed up the hgview start up as the
    python module can be imported directly on next start up.

    """
    _path = osp.dirname(__file__)
    uifile = osp.join(_path, ui_name)
    pyfile = uifile.replace(".ui", "_ui.py")
    if should_rebuild(uifile, pyfile):
        os.system('pyuic4 %s -o %s' % (uifile, pyfile))
    try:
        modname = osp.splitext(osp.basename(uifile))[0] + "_ui"
        modname = "hgviewlib.qt4.%s" % modname
        mod = __import__(modname, fromlist=['*'])
        classnames = [x for x in dir(mod) if x.startswith('Ui_')]
        if len(classnames) == 1:
            ui_class = getattr(mod, classnames[0])
        elif 'Ui_MainWindow' in classnames:
            ui_class = getattr(mod, 'Ui_MainWindow')
        else:
            raise ValueError("Can't determine which main class to use in %s" % modname)
    except ImportError:
        ui_class, base_class = uic.loadUiType(uifile)
    return ui_class

class HgDialogMixin(object):
    """
    Mixin for QDialogs defined from a .ui file, which automates the
    setup of the UI from the ui file, and the loading of user
    preferences.
    The main class must define a '_uifile' class attribute.
    """
    def __init__(self, *args, **kwargs):
        self._cfg = None
        self._font = None
        super(HgDialogMixin, self).__init__(*args, **kwargs)

    def load_ui(self):
        self.setupUi(self)
        # we explicitly create a QShortcut so we can disable it
        # when a "helper context toolbar" is activated (which can be
        # closed by hitting the Esc shortcut)
        self.esc_shortcut = QShortcut(self)
        self.esc_shortcut.setKey(Qt.Key_Escape)
        self.esc_shortcut.activated.connect(self.maybeClose)
        self._quickbars = []
        self.disab_shortcuts = []

    def attachQuickBar(self, qbar):
        qbar.setParent(self)
        self._quickbars.append(qbar)
        qbar.esc_shortcut_disabled[bool].connect(self.setShortcutsEnabled)
        self.addToolBar(Qt.BottomToolBarArea, qbar)
        qbar.unhidden.connect(self.ensureOneQuickBar)

    def setShortcutsEnabled(self, enabled=True):
        for sh in self.disab_shortcuts:
            sh.setEnabled(enabled)

    def ensureOneQuickBar(self):
        tb = self.sender()
        for w in self._quickbars:
            if w is not tb:
                w.hide()

    def maybeClose(self):
        for w in self._quickbars:
            if w.isVisible():
                w.cancel()
                break
        else:
            self.close()

    def load_config(self, repo):
        self.cfg = HgConfig(repo.ui)
        self._font = get_font(self.cfg)
        self.rowheight = self.cfg.getRowHeight()
        self.users, self.aliases = self.cfg.getUsers()

    def accept(self):
        self.close()
    def reject(self):
        self.close()


