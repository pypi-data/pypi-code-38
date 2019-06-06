#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Controller that manage data and connect widgets."""
import asyncio
from collections import defaultdict
from functools import partial

import urwid

from . import commands, config, mixin, open_popup, process, widgets
from .config import (
    GRAPHNODETEMPLATE, SUMMARY_EXTRA_TEMPLATE, SUMMARY_TEMPLATE, TEMPLATE)
from .mixin import ensurable, multilist, paginatedlist, waitable
from .utils import (
    ParseError, ensure_one, nodestr, parse_colored_line, popup_error,
    shelvestr)
from .widgets import dialog, mainwidget


class _multiwalker(
        ensurable, waitable, multilist, urwid.SimpleFocusListWalker):
    """Waitable multiwalker.

    All sub walkers are ensured/delayed/cancelled all together.

    Signals:

    - 'completed': fired when the output of the hg sub command as been fully
                   loaded.
    """

    signals = ['completed']

    def __init__(self, walkers):
        self.__sequences__ = walkers
        for walker in walkers:
            urwid.signals.connect_signal(walker, 'modified', self._modified)
        super().__init__([])

    async def _wait(self):
        await super()._wait()
        await asyncio.gather(*(walker.wait() for walker in self.__sequences__))
        urwid.emit_signal(self, 'completed')


class _hgwalker(ensurable, waitable, urwid.SimpleFocusListWalker):
    """An waitable walker though stdout of an async hg process.

    Signals:

    - 'completed': fired when the output of the hg sub command as been fully
                   loaded.
    """

    cmd = ('--verbose', 'help')

    signals = ['completed']

    class line_widget(mixin.focusable_widget, urwid.Text):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__([urwid.Text('LOADING …')], *args, **kwargs)

    def get_cmd(self):
        return self.cmd

    async def __aiter__(self):
        async for line in self.aiterlines():
            widget = self._get_widget(line)
            if widget:
                yield widget

    async def aiterlines(self):
        cmd = self.get_cmd()
        if not cmd:
            return
        self.hgproc = process.hg(*cmd)
        await self.hgproc.start()
        try:
            async for line in self.hgproc:
                yield line
        except asyncio.CancelledError as error:
            # raised when the task is interrupted
            pass

    def _get_widget(self, line):
        content = self._parse_line(line)
        if not content:
            return None
        return self._make_widget(content)

    def _parse_line(self, line):
        return parse_colored_line(line.rstrip())

    def _make_widget(self, content):
        return self.line_widget(content)

    async def _wait(self):
        await super()._wait()
        first = True
        async for widget in self:
            if first:
                self.clear(full=True)
                first = False
            self.append(widget)
        if first:               # nothing fetched
            self.clear(full=True)
            # we need at least one content
            self.append(urwid.Text(''))
        urwid.emit_signal(self, 'completed')

    def clear(self, full=False):
        self.cancel()
        super().clear()
        if not full:
            self.append(urwid.Text('LOADING …'))


class _listbox(ensurable, waitable, mixin.mouse_up_down, urwid.ListBox):
    """An waitable listbox that handle waitable walkers."""

    def __init__(self, walker, *walkers, **kwargs):
        if walkers:
            walker = _multiwalker((walker,) + walkers)
        super().__init__(walker, **kwargs)
        self._connect_all()

    def _connect_all(self):
        urwid.signals.connect_signal(
            self.body, 'modified', self._on_modified)

    def _on_modified(self):
        # reset the view when the first line arrived
        return

    async def _wait(self):
        self.body.set_focus(0)
        self.set_focus(0)
        await self.body._wait()

    def cancel(self):
        self.body.cancel()


class _graphtreewalker(urwid.SimpleFocusListWalker):

    class line_widget(
            mixin.selectable_widget,
            mixin.focusable_widget,
            mixin.one_line_widget,
            mixin.highlightable_widget,
            urwid.Text):
        pass


class cwdwalker(ensurable, waitable, _graphtreewalker):

    def __init__(self):
        widget = self.line_widget([('', '@  CWD')])
        widget.node = None
        widget.p1 = -1
        super().__init__([widget, urwid.Text([('', '| ')])])

    def clear(self):
        pass  # static content

    def ensure(self):
        pass  # static content

    def cancel(self):
        pass  # static content


class shelvewalker(_graphtreewalker, _hgwalker):

    cmd = ('--config', 'extensions.shelve=', 'shelve', '--list')

    def _make_widget(self, content):
        name = content[0][-1]
        content = [('', '|  ')] + [
            (style or 'shelve.description', txt) for style, txt in content]
        widget = super()._make_widget(content)
        widget.node = shelvestr(name)
        return widget

    async def _wait(self):
        await super()._wait()
        self.append(urwid.Text([('| ')]))


class changesetwalker(_graphtreewalker, paginatedlist, _hgwalker):

    _sep = '\0\0'
    _template = r'\0\0' + r'\0\0'.join([
        '{node}', '{rev}', '{graphnode}', '{p1rev}', '{children}', TEMPLATE])

    class graph_line_widget(
            mixin.focusable_widget,
            mixin.highlightable_widget,
            urwid.Text):
        pass

    def __init__(self, rev, *args, **kwargs):
        self.rev = rev
        super().__init__(*args, **kwargs)

    def get_cmd(self):
        cmd = ['--config', 'ui.graphnodetemplate=%s' % GRAPHNODETEMPLATE,
               'debuglairucremgraphlog',
               '--template', self._template]
        if self.rev:
            cmd += ['--rev', self.rev]
        return cmd

    def _get_widget(self, line):
        line = line.rstrip()
        if line.count(self._sep) == 6:
            data = line.split(self._sep)
            try:
                graph, node, rev, graphnode, p1, children, content = data
            except ValueError:
                raise ParseError(f'Unexpected output: {data}')
            if set(node) == {'f'}:
                return
            iscwd = graphnode == '@'
            style = 'log.cwd' if iscwd else ''
            content = parse_colored_line(graph) + parse_colored_line(content)
            widget = self._make_widget(content)
            widget = urwid.AttrWrap(widget, style, style + '.focus')
            widget.node = nodestr(node)
            widget.rev = int(rev)
            widget.p1 = int(p1)
            widget.cwd = iscwd
            widget.children = [
                int(child.split(':')[0]) for child in children.split()]
            return widget
        else:
            if not (set(line) - set(' |:')):
                return
            return self.graph_line_widget(parse_colored_line(line))

    async def find_widget(self, matcher):
        """Return (widget, position) of the cset with the given rev."""
        # search in already loaded csets
        async for widget, position in self.iter_widgets():
            if matcher(widget):
                return widget, position
        else:
            raise mixin.NotFound(f'Not Found')

    async def get_rev(self, rev):
        """Return (widget, position) of the cset with the given rev."""
        # search in already loaded csets
        return await self.find_widget(partial(self._is_widget_match_rev, rev))

    @staticmethod
    def _is_widget_match_rev(rev, widget):
        return ((rev == -1 and getattr(widget, 'cwd', None))
                or (getattr(widget, 'rev', None) == rev))

    async def _wait(self):
        async with popup_error(OSError, donotraise=True):
            await super()._wait()


class _patchdetailwalker(_hgwalker):

    class line_widget(
            mixin.highlightable_widget,
            mixin.focusable_widget,
            urwid.Text):
        pass

    def __init__(self, node=None, *args, **kwargs):
        self.node = node
        super().__init__(*args, **kwargs)


class diffstatwalker(_patchdetailwalker):
    """Manage diff content."""

    signals = ['link']
    filename = None

    class line_widget(
            mixin.link,
            mixin.selectable_widget,
            mixin.highlightable_widget,
            mixin.focusable_widget,
            urwid.Text):
        pass

    def get_cmd(self):
        if self.node is None:
            cmd = ['diff', '--stat']
        elif isinstance(self.node, nodestr):
            cmd = ['--hidden', 'diff', '--stat', '--change', self.node]
        elif isinstance(self.node, shelvestr):
            return ['shelve', '--stat', self.node]
        else:
            return None
        if self.filename:
            cmd.append(self.filename)
        return cmd

    def _parse_line(self, line):
        if '|' not in line:     # skip the summary
            return
        return parse_colored_line(line.rstrip())

    def _make_widget(self, content):
        widget = super()._make_widget(content)
        widget.fname = fname = content[0][1].split('|')[0].strip()
        # propagate signal
        urwid.connect_signal(
            widget, 'link', lambda w: urwid.emit_signal(self, 'link', fname))
        return widget


class diffwalker(_patchdetailwalker):
    """Manage diff content."""

    filename = None

    def get_cmd(self):
        if self.node is None:
            cmd = ['--verbose', 'diff']
        elif isinstance(self.node, nodestr):
            cmd = [
                '--verbose', '--hidden',
                'diff',
                '--git', '--nodates', '--noprefix',
                '--show-function', '--change', self.node
            ]
        elif isinstance(self.node, shelvestr):
            return ['--verbose', 'shelve', '--patch', self.node]
        else:
            return None
        if self.filename:
            cmd.append(self.filename)
        return cmd

    def _parse_line(self, line):
        return parse_colored_line(line.rstrip(), default_style='diff.context')

    def _make_widget(self, content):
        widget = super()._make_widget(content)
        try:
            if content[0][0] == 'diff.diffline':
                widget = urwid.AttrWrap(
                    widget, 'diff.diffline', 'diff.diffline.focus')
        finally:
            return widget


class summarywalker(_patchdetailwalker):
    """Manage the cset summary content."""

    def get_cmd(self):
        if self.node is None:
            return ('--verbose', 'summary')
        elif isinstance(self.node, nodestr):
            return ('--verbose', '--hidden', 'log', '--template', SUMMARY_TEMPLATE,
                    '-r', self.node)
        else:
            return None


class summaryextrawalker(_patchdetailwalker):
    """Manage the cset summary extras content."""

    def get_cmd(self):
        if isinstance(self.node, nodestr):
            return ('--verbose', '--hidden', 'log', '--template', SUMMARY_EXTRA_TEMPLATE,
                    '-r', self.node)
        else:
            return None


class descriptionwalker(_patchdetailwalker):
    """Manage the cset description content."""

    def get_cmd(self):
        if isinstance(self.node, nodestr):
            return ('--hidden', 'log', '--template', r'\n{desc}\n\n', '--rev', self.node)
        else:
            return None

    def _make_widget(self, content):
        content = [(style or 'log.description', text)
                   for style, text in content]
        widget = super()._make_widget(content)
        return urwid.AttrWrap(
            widget, 'log.description', 'log.description.focus')


class graphlistbox(
        mixin.changeable_listbox,
        mixin.filterable_listbox,
        mixin.searchable_listbox,
        mixin.commandable_listbox,
        mixin.refreshable_listbox,
        _listbox):
    """Manage the cset tree."""

    def __init__(self, rev, *args):
        self._commands_selectors = commands.selection()
        self._cwd = cwdwalker()
        self._changeset = changesetwalker(rev)
        self._shelve = shelvewalker()  # shelvewalker()
        self.on_filter = ensure_one(self._on_filter)
        self.on_commandlist = ensure_one(self._on_commandlist)
        self.reset_commands_selectors = ensure_one(self._reset_commands_selectors)
        self.on_focus_rev = ensure_one(self._on_focus_rev)
        super().__init__(self._cwd, self._shelve, self._changeset)

    def _connect_all(self):
        super()._connect_all()
        urwid.connect_signal(self, 'filter', self.on_filter.ensure)
        # 1) Delay reset_commands_selector to prevent starting processes while
        # quickly browsing the history.
        # 2) IMPORTANT: 'on_commandlist' callback must be called after 'reset_commands_selector'
        # callback to ensure displaying the menu of the currently focused node.
        urwid.connect_signal(self, 'changed', partial(self.reset_commands_selectors.delay, duration=0.4))
        urwid.connect_signal(self, 'commandlist', partial(self.on_commandlist.delay, duration=0.5))
        urwid.signals.connect_signal(self, 'refresh', lambda *a: self.ensure())

    @property
    def current_widget(self):
        try:
            return self.get_focus_widgets()[0]
        except IndexError:
            return None

    @property
    def current_node(self):
        wd = self.current_widget
        if wd is None:
            return None
        node = getattr(wd, 'node', None)
        if not node or set(node) == {'f'}:
            return None
        else:
            return node

    async def _wait(self, *args):
        position = self.get_focus()[-1]
        rev = getattr(self.current_widget, 'rev', None)
        if rev is None:
            return await super()._wait()
        # Maybe the current_node was obsoleted
        try:
            _rev = await process.hg_plain(
                'log', '--hidden', '--rev', f'last(allsuccessors({rev}))', '--template', '{rev}')
            if _rev:
                rev = _rev
        except OSError:
            # cwd was stripped. Doing more complicated stuff would be not useful.
            return await super()._wait()
        try:
            await asyncio.gather(
                super()._wait(),
                dialog.popup_processing(
                    self._on_focus_rev(rev),
                    'Searching for the previous changeset... Close this popup to cancel.'
                ))
        except mixin.NotFound:
            self.set_focus(position)

    async def _reset_commands_selectors(self, *args):
        try:
            await self._commands_selectors.fetch(self.current_node)
        except OSError:
            # Happen sometime when browsing the tree. This is not a big deal
            # because we're just prefilling caches. So let ignore it.
            pass

    async def _on_commandlist(self, *args):
        tasks = [getter(self.current_node, selectors=self._commands_selectors)
                 for getter in commands.cset_command_getters]
        cmd = await dialog.async_choices(tasks)
        if not cmd:
            return
        exctype = OSError if not config.DEBUG else Exception
        async with popup_error(exctype, donotraise=True):
            await cmd()
        self.ensure()

    async def _on_filter(self, *args):
        edit = widgets.edit(
            [('ui.label', 'revset: ')], self._changeset.rev or '')
        choice = await dialog.ask(edit, title='FILTER TREE', focus_content=True)
        if choice:
            self.reset_rev(edit.get_edit_text().strip() or None)

    def reset_rev(self, rev):
        """Reset the view with the given revision set."""
        self._changeset.rev = rev
        self.ensure()

    async def _on_focus_rev(self, rev):
        """Set the focus focus to cset with the given `rev` (-1 == cwd)."""
        widget, position = await self._changeset.get_rev(rev)
        if position is not None:
            self.set_focus(position + len(self._cwd) + len(self._shelve))
            self._invalidate()

    def focus_p1(self):
        """Set focus on the first parent of the current cset."""
        widget, position = self.get_focus()
        if getattr(widget, 'p1', None) is None:
            return
        task = self.on_focus_rev.ensure(widget.p1)
        # delaying popup_processing prevents popup if the cset already fetched
        dialog.popup_processing.delay(task, duration=0.1)

    def focus_c1(self):
        """Set focus on the first child of the current cset."""
        widget, position = self.get_focus()
        if not getattr(widget, 'children', None) or not widget.children[0]:
            return
        task = self.on_focus_rev.ensure(widget.children[0])
        # delaying popup_processing prevents popup if the cset already fetched
        dialog.popup_processing.delay(task, duration=0.1)

    def set_focus(self, position, *args, **kwargs):
        super().set_focus(position, *args, **kwargs)
        urwid.emit_signal(self, 'changed')  # ensure other panes sync

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key is None:
            return None
        if self._command_map[key] == config.CMD_NEXT_RELATED:
            self.focus_p1()
            return
        if self._command_map[key] == config.CMD_PREV_RELATED:
            self.focus_c1()
            return
        return key


class patchlistbox(
        mixin.filterable_listbox,
        mixin.searchable_listbox, mixin.refreshable_listbox, _listbox):
    """Manage the patch content, a.k.a. summary and diff."""

    def __init__(self):
        self._search_pattern = ''
        self._summary = summarywalker()
        self._summaryextra = summaryextrawalker()
        self._description = descriptionwalker()
        self._diffstat = diffstatwalker()
        self._diff = diffwalker()
        self.on_jump_to_diffline = ensure_one(self._on_jump_to_diffline)
        self.on_filter = ensure_one(self._on_filter)
        super().__init__(
            self._summary, self._summaryextra, self._description,
            self._diffstat, self._diff)

    def _connect_all(self):
        super()._connect_all()
        urwid.connect_signal(self, 'filter', self.on_filter.ensure)
        urwid.signals.connect_signal(
            self._diffstat, 'link', self.on_jump_to_diffline.ensure)
        urwid.signals.connect_signal(self, 'refresh', lambda *a: self.ensure())

    def change_focus(self, *args, **kwargs):
        # workaround urwid bug: just don't focus on selectable if we can't
        try:
            return super().change_focus(*args, **kwargs)
        except urwid.ListBoxError:
            pass

    def reset_node(self, node):
        # resetonly if not CWD and changed. We always reset on cwd as
        # the user evently want to view changes while cset is expected
        # not to be modified outside the application.
        if node is not None and node == self._summary.node:
            return
        self.body.cancel()
        self._summary.node = node
        self._summaryextra.node = node
        self._description.node = node
        self._diffstat.node = node
        self._diff.node = node
        self.ensure()

    def _iter_widgets(self, startpos=None, forward=True):
        pos = self.focus_position if startpos is None else startpos
        nextgetter = self.body.get_next if forward else self.body.get_prev
        widget = self.body[pos]
        while widget:
            yield widget, pos
            widget, pos = nextgetter(pos)

    def _goto(self, matcher, startpos=None, forward=True):
        for widget, pos in self._iter_widgets(startpos, forward):
            if matcher(widget, pos):
                self.set_focus(pos)
                self._invalidate()
                break

    async def _on_jump_to_diffline(self, fname):
        assert self.wait.task
        await self.wait.task    # wait until all loaded
        self._goto(
            lambda w, p: fname in w.text,
            self.body.startof(self._diff))

    async def _on_filter(self, *args):
        edit = widgets.edit(
            [('ui.label', 'file: ')], self._diff.filename or '')
        choice = await dialog.ask(edit, title='FILTER PATCH', focus_content=True)
        if choice:
            val = edit.get_edit_text().strip() or None
            self._diff.filename = val
            self._diffstat.filename = val
            self.ensure()

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key is None:
            return
        command = self._command_map[key]
        if command in (config.CMD_PREV_RELATED, config.CMD_NEXT_RELATED):
            forward = command == config.CMD_NEXT_RELATED
            self._goto(
                lambda w, p: w.text.startswith(('diff --git', '@@ ')),
                startpos=self.focus_position + (1 if forward else -1),
                forward=forward,
            )
            return
        return key


class maincontroler(ensurable):

    def __init__(self, rev=None):
        self._graph = graphlistbox(rev=rev)
        self._patch = patchlistbox()
        self._grep_pattern = ''
        self.on_focus_patch = ensure_one(self._on_focus_patch)
        self.on_grep = ensure_one(self._on_grep)
        self._connect_all()

    def _connect_all(self):
        urwid.signals.connect_signal(
            self._graph, 'changed', self.on_focus_patch.delay)

    def get_widget(self):
        return mainwidget.mainwidget(mainwidget.packer([
            mainwidget.pane(self._graph, 'TREE'),
            mainwidget.pane(self._patch, 'PATCH'),
        ]))

    def _on_focus_patch(self, *args):
        self._patch.reset_node(self._graph.current_node)

    def ensure(self):
        self._graph.ensure()
        self._patch.ensure()

    def cancel(self):
        self._graph.cancel()
        self._patch.cancel()

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key == '?':
            open_popup(dialog.simple(mainwidget.thehelp(), 'HELP'))
        elif key == 'G':
            self.on_grep.ensure()

    async def _on_grep(self):
        edit = widgets.edit([('ui.label', 'pattern: ')], self._grep_pattern)
        answer = await dialog.ask(edit, title='Grep', focus_content=True)
        if not answer:
            return
        pattern = edit.get_edit_text()
        if pattern:
            revset = await dialog.popup_processing(self._grep_revset(pattern))
        else:
            revset = ''
        self._graph.reset_rev(revset)
        self._patch.search_pattern(pattern),

    async def _grep_revset(self, pattern):
        self._grep_pattern = pattern
        csets = defaultdict(set)
        async for line in process.hg('grep', '--all', '-l', pattern):
            try:
                data = dict(parse_colored_line(line))
            except ValueError:
                pass
            csets[data['grep.rev']].add(data['grep.filename'])
        revset = ' or '.join(csets)
        return f'({revset})'
