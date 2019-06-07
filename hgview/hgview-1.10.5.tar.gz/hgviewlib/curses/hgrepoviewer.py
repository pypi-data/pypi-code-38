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
"""
Main curses application for hgview
"""

try:
    import pygments
    from pygments import lexers
except ImportError:
    # pylint: enable=C0103
    pygments = None

import urwid
from urwid import AttrWrap, Pile, Columns, SolidFill, signals
from urwid.util import is_mouse_press

from mercurial.error import RepoError

from hgviewlib.config import HgConfig
from hgviewlib.hggraph import HgRepoListWalker
from hgviewlib.util import exec_flag_changed, isbfile, tounicode

from hgviewlib.curses.exceptions import CommandError
from hgviewlib.curses.graphlog import RevisionsWalker
from hgviewlib.curses.manifest import ManifestWalker
from hgviewlib.curses import (Body, SourceText, ScrollableListBox,
                              register_command, unregister_command,
                              connect_command, emit_command, CommandArg as CA,
                              hg_command_map)

class GraphlogViewer(Body):
    """Graphlog body"""

    def __init__(self, walker, *args, **kwargs):
        self.walker = walker
        self.graphlog_walker = RevisionsWalker(walker=walker)
        body = ScrollableListBox(self.graphlog_walker)
        super(GraphlogViewer, self).__init__(body=body, *args, **kwargs)
        self.title = walker.repo.root
        signals.connect_signal(self.graphlog_walker, 'focus changed',
                               self.update_title)
        wc = walker.repo[None]
        rev = None
        if not wc.dirty() and wc.p1().rev() >= 0:
            # parent of working directory is not nullrev
            rev = wc.p1().rev()
        self.graphlog_walker.rev = rev

    def update_title(self, ctx):
        """update title depending on the given context ``ctx``."""
        if ctx.node() is None:
            hex_ = 'WORKING DIRECTORY'
        else:
            hex_ = str(ctx)
        self.title = '%(root)s [%(hex)s] %(phase)s' % {
            'root':self.walker.repo.root,
            'hex':hex_,
            'phase':ctx.phasestr()}

    def register_commands(self):
        '''Register commands and connect commands for bodies'''
        cnvt = lambda entry: self.walker.repo[entry].rev()
        register_command(
                ('goto', 'g'), 'Set focus on a particular revision',
                CA('revision', cnvt,
                'The revision number to focus on (default to last)'))
        register_command(
                ('toggle-hidden',), 'Show/hide hidden changesets',)
        connect_command('toggle-hidden', self.toggle_hidden)
        self.graphlog_walker.connect_commands()

    def unregister_commands(self):
        '''Unregister commands'''
        unregister_command('goto')
        unregister_command('g')

    def toggle_hidden(self, _current=[]):
        self.walker.show_hidden = not self.walker.show_hidden
        emit_command('refresh')

    def render(self, size, focus=True):
        '''Render the widget. Always use the focus style.'''
        return super(GraphlogViewer, self).render(size, True)

    def mouse_event(self, size, event, button, col, row, focus):
        """Scroll content and show context"""
        if urwid.util.is_mouse_press(event):
            if button == 1:
                emit_command('show-context')
        return super(GraphlogViewer, self).mouse_event(size, event, button,
                                                       col, row, True)

class ManifestViewer(Body):
    """Manifest viewer"""

    def __init__(self, walker, ctx, *args, **kwargs):
        self.manifest_walker = ManifestWalker(walker=walker, ctx=ctx,
                                              manage_description=True,
                                              *args, **kwargs)
        body = ScrollableListBox(self.manifest_walker)
        super(ManifestViewer, self).__init__(body=body, *args, **kwargs)
        signals.connect_signal(self.manifest_walker, 'focus changed',
                               self.update_title)
        self.title = 'Manifest'

    def update_title(self, filename):
        '''update the body title.'''
        tot = len(self.manifest_walker)
        if self.manifest_walker.focus < 0:
            self.title = '%i file%s' % (tot, 's' * (tot > 1))
            return
        cur = self.manifest_walker.focus + 1
        self.title = '%i/%i [%i%%]' % (cur, tot, cur*100/tot)

    def render(self, size, focus=True):
        '''Render the manifest viewer. Always use the focus style.'''
        return super(ManifestViewer, self).render(size, True)

class SourceViewer(Body):
    """Source Viewer"""

    signals = ['translated']

    def __init__(self, text, *args, **kwargs):
        self.text = SourceText(text, wrap='clip')
        self.position = 0
        body = ScrollableListBox([self.text])
        super(SourceViewer, self).__init__(body=body, *args, **kwargs)

    def update_position(self, size, isdown):
        curr, fullheight = self.body.inset_fraction
        _, displayedheight = size
        stroke = fullheight - displayedheight
        if stroke <= 0: # fully displayed
            self.position = 100 if isdown else 0
        else:
            self.position = max(min(curr * 100 / stroke, 100), 0)
        signals.emit_signal(self, 'translated')

    def keypress(self, size, key):
        super(SourceViewer, self).keypress(size, key)
        if key.endswith(('up', 'down')):
            self.update_position(size, key.endswith('down'))

    def mouse_event(self, size, event, button, col, row, focus):
        """Scroll content"""
        if is_mouse_press(event) and button in (4, 5):
            self.update_position(size)
        return super(SourceViewer, self).mouse_event(size, event, button,
                                                     col, row, focus)
class ContextViewer(Columns):
    """Context viewer (manifest and source)"""
    signals = ['update source title']
    MANIFEST_SIZE = 0.3
    def __init__(self, walker, *args, **kwargs):
        self._walker = walker
        self._filename = None
        self._size_cache = (0, 0)
        self.cfg = HgConfig(walker.repo.ui)
        self.manifest = ManifestViewer(walker=walker, ctx=None)
        self.manifest_walker = self.manifest.manifest_walker
        self.source = SourceViewer('')
        self.source_text = self.source.text
        self._source_title_cache = ''

        widget_list = [('weight', 1 - self.MANIFEST_SIZE, self.source),
                       ('fixed', 1, AttrWrap(SolidFill(' '), 'banner')),
                       ('weight', self.MANIFEST_SIZE, self.manifest),
                       ]
        super(ContextViewer, self).__init__(widget_list=widget_list,
                                            *args, **kwargs)

        signals.connect_signal(self.manifest_walker, 'focus changed',
                               self.update_source)
        signals.connect_signal(self, 'update source title',
                               self.update_source_title_cache)
        signals.connect_signal(self.source, 'translated', self.update_source_title)

    def register_commands(self):
        """Register commands and commands of bodies"""
        register_command('set-max-file-size',
                         'max size of handled file for diff computation, and so on.',
                         CA('size', int, 'octets (-1 means no max size)'))
        connect_command('set-max-file-size', self.modify_max_file_size)

    def unregister_commands(self):
        """Unregister commands and commands of bodies"""
        unregister_command('set-max-file-size')

    def modify_max_file_size(self, size):
        """Modify the max handled file size and update the source content."""
        self._walker.graph.maxfilesize = size
        self.update_source(self._filename)

    def update_source_title_cache(self, filename, flag):
        """
        Display information about the file in the title of the source body.
        """
        ctx = self.manifest_walker.ctx
        title = []
        if filename is None:
            title.append(' Description')
        elif flag == '' or flag == '-':
            title += [' Removed file: ', ('focus', filename)]
        else:
            filectx = ctx.filectx(filename)
            flag = exec_flag_changed(filectx)
            if flag:
                title += [' Exec mode: ', ('focus', flag)]
            if isbfile(filename):
                title.append('bfile tracked')
            renamed = filectx.renamed()
            if renamed:
                title += [' Renamed from: ', ('focus', renamed[0])]
            title += [' File name: ', ('focus', filename)]
        self._source_title_cache = title
        self.update_source_title()

    def update_source_title(self):
        self.source.title = ['[% 3s%%]' % self.source.position] + self._source_title_cache

    def update_source(self, filename):
        """Update the source content."""
        ctx = self.manifest_walker.ctx
        if ctx is None:
            return
        self._filename = filename
        numbering = False
        flag = ''
        if filename is None: # source content is the changeset description
            wrap = 'space' # Do not cut description and wrap content
            data = tounicode(ctx.description())
            if pygments:
                lexer = lexers.get_lexer_by_name('reStructuredText')
        else: # source content is a file
            wrap = 'clip' # truncate lines
            flag, data = self.manifest_walker.filedata(filename)
            lexer = None # default to inspect filename and/or content
            if flag == '=' and pygments: # modified => display diff
                lexer = lexers.get_lexer_by_name('diff') if flag == '=' else None
            elif flag == '-' or flag == '': # removed => just say it
                if pygments:
                    lexer = lexers.lexer_by_name('diff')
                data = '- Removed file'
            elif flag == '+': # Added => display content
                numbering = True
                lexer = None
        signals.delay_emit_signal(self, 'update source title', 0.05,
                                  filename, flag)
        self.source_text.set_wrap_mode(wrap)
        self.source_text.set_text(data or '')
        if pygments:
            self.source_text.lexer = lexer
        self.source_text.numbering = numbering
        self.source.body.set_focus_valign('top') # reset offset
        self.source.position = 0

    def keypress(self, size, key):
        self._size_cache = size
        try:
            self._keypress(hg_command_map[key])
        except CommandError:
            return key

    def _keypress(self, command):
        "allow subclasses to intercept keystrokes"
        widths = self.column_widths(self._size_cache)
        maxrow = self._size_cache[1]
        if command.startswith('source'):
            self._previous_source_position = self.source.position
        if command  == 'manifest up':
            _size = widths[2], maxrow
            self.manifest.keypress(_size, 'up')
        elif command == 'manifest down':
            _size = widths[2], maxrow
            self.manifest.keypress(_size, 'down')
        if command  == 'source up':
            _size = widths[0], maxrow
            self.source.keypress(_size, 'up')
        elif command == 'source down':
            _size = widths[0], maxrow
            self.source.keypress(_size, 'down')

        elif command  == 'manifest page up':
            _size = widths[2], maxrow
            self.manifest.keypress(_size, 'page up')
        elif command == 'manifest page down':
            _size = widths[2], maxrow
            self.manifest.keypress(_size, 'page down')
        if command  == 'source page up':
            _size = widths[0], maxrow
            self.source.keypress(_size, 'page up')
        elif command == 'source page down':
            _size = widths[0], maxrow
            self.source.keypress(_size, 'page down')
        else:
            CommandError('unknown command: %r' % command)

    def clear(self):
        """Clear content"""
        self.manifest_walker.clear()
        self.source_text.set_text('')

class RepoViewer(Pile):
    """Repository viewer (graphlog and context)"""

    CONTEXT_SIZE = 0.5

    def __init__(self, repo, *args, **kwargs):
        if repo.root is None:
            raise RepoError("There is no Mercurial repository here (.hg not found)!")
        self.repo = repo
        self.cfg = HgConfig(repo.ui)
        self._show_context = 0 # O:hide, 1:half, 2:maximized
        self.refreshing = False # flag to now if the repo is refreshing

        self._walker = HgRepoListWalker(repo)
        self.graphlog = GraphlogViewer(walker=self._walker)
        self.context = ContextViewer(walker=self._walker)

        widget_list = [('weight', 1 - self.CONTEXT_SIZE, self.graphlog),]

        super(RepoViewer, self).__init__(widget_list=widget_list, focus_item=0,
                                         *args, **kwargs)
        if self.cfg.getContentAtStartUp():
            self.show_context()

    def update_context(self, ctx):
        """Change the current displayed context"""
        self.context.manifest_walker.set_ctx(ctx, reset_focus=(not self.refreshing))

    def register_commands(self):
        """Register commands and commands of bodies"""
        register_command('hide-context', 'Hide context pane.')
        register_command('show-context', 'Show context pane.',
                         CA('height', float,
                         'Relative height [0-1] of the context pane.'))
        register_command('maximize-context', 'Maximize context pane.')
        self.graphlog.register_commands()
        self.context.register_commands()
        connect_command('hide-context', self.hide_context)
        connect_command('show-context', self.show_context)
        connect_command('maximize-context', self.maximize_context)
        connect_command('refresh', self.refresh)

    def unregister_commands(self):
        """Unregister commands and commands of bodies"""
        self.graphlog.unregister_commands()
        self.context.unregister_commands()

    def refresh(self):
        graphlog_walker = self.graphlog.graphlog_walker
        manifest_walker = self.context.manifest_walker
        self.refreshing = True
        rev = graphlog_walker.rev
        filename = manifest_walker.filename
        self._walker.setRepo()
        try:
            graphlog_walker.set_rev(rev) # => focus changed => update_context
        except AttributeError: # rev stripped
            graphlog_walker.rev = None
        manifest_walker.filename = filename
        self.refreshing = False

    def hide_context(self):
        ''' hide the context widget'''
        if self._show_context == 0: # already hidden
            return
        self._deactivate_context()
        self.item_types[:] = [('weight', 1)]
        self.widget_list[:] = [self.graphlog]
        self._show_context = 0

    def maximize_context(self):
        '''hide the graphlog widget'''
        if self._show_context == 2: # already maximized
            return
        self._activate_context()
        self.item_types[:] = [('weight', 1)]
        self.widget_list[:] = [self.context]
        self._show_context = 2

    def show_context(self, height=None):
        '''show context and graphlog widgets'''
        if self._show_context == 1: # already half
            return
        self._activate_context()
        if height is None:
            height = self.CONTEXT_SIZE
        self.item_types[:] = [('weight', 1 - height),
                              ('weight', height),]
        self.widget_list[:] = [self.graphlog, self.context]
        self._show_context = 1

    def _activate_context(self):
        context_walker = self.context.manifest_walker
        graphlog_ctx = self.graphlog.graphlog_walker.get_ctx()
        if context_walker.ctx != graphlog_ctx:
            self.update_context(graphlog_ctx)
        signals.connect_signal(self.graphlog.graphlog_walker, 'focus changed',
                               self.update_context)

    def _deactivate_context(self):
        signals.disconnect_signal(self.graphlog.graphlog_walker,
                                  'focus changed', self.update_context)

    def keypress(self, size, key):
        "allow subclasses to intercept keystrokes"
        if self._show_context == 0 and hg_command_map[key] == 'validate':
            self.show_context()
            return
        if hg_command_map[key] == 'close pane' and self._show_context > 0:
            # allows others to catch 'close pane'
            self.hide_context()
            return
        if  self._show_context < 2:
            if hg_command_map[key]  == 'graphlog up':
                _size = self.get_item_size(size, 0, True)
                self.graphlog.keypress(_size, 'up')
                return
            if hg_command_map[key]  == 'graphlog down':
                _size = self.get_item_size(size, 0, True)
                self.graphlog.keypress(_size, 'down')
                return
            if hg_command_map[key]  == 'graphlog page up':
                _size = self.get_item_size(size, 0, True)
                self.graphlog.keypress(_size, 'page up')
                return
            if hg_command_map[key]  == 'graphlog page down':
                _size = self.get_item_size(size, 0, True)
                self.graphlog.keypress(_size, 'page down')
                return
        if self._show_context > 0:
            idx = 1 if self._show_context == 1 else 0
            _size = self.get_item_size(size, idx, True)
            return self.context.keypress(_size, key)
        return key

    def mouse_event(self, size, event, button, col, row, focus):
        """Hide context"""
        if urwid.util.is_mouse_press(event):
            if button == 3:
                emit_command('hide-context')
                return
        return super(RepoViewer, self).mouse_event(size, event, button, col,
                                                   row, focus)

