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
'''
Contains a listbox definition that walk the repo log and display an ascii graph
'''

try:
    from itertools import izip_longest as zzip
    zzip(()) # force check over lazy import
except (ImportError, TypeError): # python2.5 support
    from itertools import repeat, chain
    class ZipExhausted(Exception):
        pass
    def zzip(*args, **kwds):
        # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        fillvalue = kwds.get('fillvalue')
        counter = [len(args) - 1]
        def sentinel():
            if not counter[0]:
                raise ZipExhausted
            counter[0] -= 1
            yield fillvalue
        fillers = repeat(fillvalue)
        iterators = [chain(it, sentinel(), fillers) for it in args]
        try:
            while iterators:
                yield tuple(iterator.next() for iterator in iterators)
        except ZipExhausted:
            pass

from logging import warn

from mercurial.node import short
from urwid import AttrMap, Text, ListWalker, Columns, WidgetWrap, emit_signal

from hgviewlib.hgpatches.graphmod import (_fixlongrightedges,
                                          _getnodelineedgestail,
                                          _drawedges, _getpaddingline)

from hgviewlib.util import tounicode
from hgviewlib.hggraph import getlog, gettags, getdate, HgRepoListWalker
from hgviewlib.curses import connect_command, SelectableText

# __________________________________________________________________ constants

COLORS = ["brown", "dark red", "dark magenta", "dark blue", "dark cyan",
          "dark green", "yellow", "light red", "light magenta", "light blue",
          "light cyan", "light green"]


_COLUMNMAP = {
    'ID': lambda m, c, g: c.rev() is not None and str(c.rev()) or "",
    'Log': getlog,
    'Author': lambda m, c, g: tounicode((c.user() if c.node() else '').split('<',1)[0]),
    'Date': getdate,
    'Tags': gettags,
    'Bookmarks': lambda m, c, g: ', '.join(c.bookmarks() or ()),
    'Branch': lambda m, c, g: c.branch() != 'default' and c.branch(),
    'Filename': lambda m, c, g: g.extra[0],
    'Phase': lambda model, ctx, gnode: ctx.phasestr(),
    }
GRAPH_MIN_WIDTH = 6

# ____________________________________________________________________ classes

class RevisionsWalker(ListWalker):
    """ListWalker-compatible class for browsing log changeset.
    """

    signals = ['focus changed']
    _columns = HgRepoListWalker._columns

    _allfields = (('Bookmarks', 'Branch', 'Tags', 'Log'),)
    _allcolumns = (('Date', 16), ('Author', 20), ('ID', 6),)

    def __init__(self, walker, branch='', fromhead=None, follow=False,
                 *args, **kwargs):
        self._data_cache = {}
        self._focus = 0
        self.walker = walker
        super(RevisionsWalker, self).__init__(*args, **kwargs)
        self.asciistate = [0, 0] # graphlog.asciistate()

    def connect_commands(self):
        """Connect usefull commands to callbacks"""
        connect_command('goto', self.set_rev)

    def _modified(self):
        """obsolete widget content"""
        super(RevisionsWalker, self)._modified()

    def _invalidate(self):
        """obsolete rendering cache"""
        self._data_cache.clear()
        super(RevisionsWalker, self)._modified()

    @staticmethod
    def get_color(idx, ignore=()):
        """
        Return a color at index 'n' rotating in the available
        colors. 'ignore' is a list of colors not to be chosen.
        """
        colors = [x for x in COLORS if x not in ignore]
        if not colors: # ghh, no more available colors...
            colors = COLORS
        return colors[idx % len(colors)]

    def data(self, pos):
        """Return a widget and the position passed."""
        # cache may be very huge on very big repo
        # (cpython for instance: >1.5GB)
        if pos in self._data_cache: # speed up rendering
            return self._data_cache[pos], pos
        widget = self.get_widget(pos)
        if widget is None:
            return None, None
        self._data_cache[pos] = widget
        return widget, pos

    def get_widget(self, pos):
        """Return a widget for the node"""
        if pos in self._data_cache: # speed up rendering
            return self._data_cache[pos], pos

        try:
            self.walker.ensureBuilt(row=pos)
        except ValueError:
            return None
        gnode = self.walker.graph[pos]
        ctx = self.walker.repo[gnode.rev]
        # prepare the last columns content
        txts = []
        for graph, fields in zzip(self.graphlog(gnode, ctx), self._allfields):
            graph = graph or ''
            fields = fields or ()
            txts.append(graph)
            txts.append(' ')
            for field in fields:
                if field not in self._columns:
                    continue
                txt = _COLUMNMAP[field](self.walker, ctx, gnode)
                if not txt:
                    continue
                txts.append((field, txt))
                txts.append(('default', ' '))
            txts.pop() # remove pending space
            txts.append('\n')
        txts.pop() # remove pending newline
        # prepare other columns
        txter = lambda col, sz: Text(
                 (col, _COLUMNMAP[col](self.walker, ctx, gnode)[:sz]),
                                       align='right', wrap='clip')
        columns = [('fixed', sz, txter(col, sz))
                   for col, sz in self._allcolumns
                   if col in self._columns]
        columns.append(SelectableText(txts, wrap='clip'))
        # tune style
        spec_style = {} # style modifier for normal
        foc_style = {} # style modifier for focused
        all_styles = set(self._columns) | set(['GraphLog', 'GraphLog.node', None])
        important_styles = set(['ID', 'GraphLog.node'])
        if ctx.obsolete():
            spec_style.update(dict.fromkeys(all_styles, 'obsolete'))
        # normal style: use special styles for working directory and tip
        style = None
        if gnode.rev is None:
            style = 'modified' # pending changes
        elif gnode.rev in self.walker.wd_revs:
            style = 'current'
        if style is not None:
            spec_style.update(dict.fromkeys(important_styles, style))
        # focused style: use special styles for working directory and tip
        foc_style.update(dict.fromkeys(all_styles, style or 'focus'))
        foc_style.update(dict.fromkeys(important_styles, 'focus.alternate'))
        # wrap widget with style modified
        widget = AttrMap(Columns(columns, 1), spec_style, foc_style)
        return widget

    def graphlog(self, gnode, ctx):
        """Return a generator that get lines of graph log for the node
        """
        # define node symbol
        if gnode.rev is None:
            char = '!' # pending changes
        elif not getattr(ctx, 'applied', True):
            char = ' '
        elif set(ctx.tags()).intersection(self.walker.mqueues):
            char = '*'
        else:
            phase = ctx.phase()
            try:
                char = 'o#^'[phase]
            except IndexError:
                warn('"%(node)s" has an unknown phase: %(phase)i',
                     {'node':short(ctx.node()), 'phase':phase})
                char = '?'

        # build the column data for the graphlogger from data given by hgview
        curcol = gnode.x
        curedges = [(start, end)
                    for start, end, color, fill in gnode.bottomlines
                    if start == curcol]
        try:
            prv, nxt, _, _ = zip(*gnode.bottomlines)
            prv, nxt = len(set(prv)), len(set(nxt))
        except ValueError: # last
            prv, nxt = 1, 0
        coldata = (curcol, curedges, prv, nxt - prv)
        self.asciistate = self.asciistate or [0, 0]
        return hgview_ascii(self.asciistate, char, len(self._allfields),
                            coldata)

    def get_focus(self):
        """Get focused widget"""
        try:
            return self.data(self._focus)
        except IndexError:
            if self._focus > 0:
                self._focus = 0
            else:
                self._focus = 0
        try:
            return self.data(self._focus)
        except:
            return None, None

    def set_focus(self, focus=None):
        """change focused widget"""
        self._focus = focus or 0
        emit_signal(self, 'focus changed', self.get_ctx())

    focus = property(lambda self: self._focus, set_focus, None,
                     'focused widget index')

    def get_rev(self):
        """Return revision of the focused changeset"""
        if self._focus >= 0:
            return self.walker.graph[self._focus].rev

    def set_rev(self, rev=None):
        """change focused widget to the given revision ``rev``."""
        if rev is None:
            self.set_focus(0)
        else:
            self.set_focus(self.walker.graph.index(rev or 0))
        self._invalidate()

    rev = property(get_rev, set_rev, None, 'current revision')

    def get_ctx(self):
        """return context of the focused changeset"""
        if self.focus >= 0:
            return self.walker.repo[self.rev]

    def get_next(self, start_from):
        """get the next widget to display"""
        focus = start_from + 1
        try:
            return self.data(focus)
        except IndexError:
            return None, None

    def get_prev(self, start_from):
        """get the previous widget to display"""
        focus = start_from - 1
        if focus < 0:
            return None, None
        try:
            return self.data(focus)
        except IndexError:
            return None, None

# __________________________________________________________________ functions

def hgview_ascii(state, char, height, coldata):
    """prints an ASCII graph of the DAG

    takes the following arguments (one call per node in the graph):

    :param state: Somewhere to keep the needed state in (init to [0, 0])
    :param char: character to use as node's symbol.
    :param height: minimal line number to use for this node
    :param coldata: (idx, edges, ncols, coldiff)
        * idx: column index for the current changeset
        * edges: a list of (col, next_col) indicating the edges between
          the current node and its parents.
        * ncols: number of columns (ongoing edges) in the current revision.
        * coldiff: the difference between the number of columns (ongoing edges)
          in the next revision and the number of columns (ongoing edges)
          in the current revision. That is: -1 means one column removed;
          0 means no columns added or removed; 1 means one column added.


    :note: it is a Modified version of Joel Rosdahl <joel@rosdahl.net> 
           graphlog extension for mercurial
    """
    idx, edges, ncols, coldiff = coldata
    # graphlog is broken with multiple parent. But we have ignore that to allow
    # some support of obsolete relation display
    # assert -2 < coldiff < 2
    assert height > 0
    if coldiff == -1:
        _fixlongrightedges(edges)
    # add_padding_line says whether to rewrite
    add_padding_line = (height > 2 and coldiff == -1 and
                        [x for (x, y) in edges if x + 1 < y])
    # fix_nodeline_tail says whether to rewrite
    fix_nodeline_tail = height <= 2 and not add_padding_line

    # nodeline is the line containing the node character (typically o)
    nodeline = ["|", " "] * idx
    nodeline.extend([('GraphLog.node', char), " "])
    nodeline.extend(_getnodelineedgestail(idx, state[1], ncols, coldiff,
                                            state[0], fix_nodeline_tail))
    # shift_interline is the line containing the non-vertical
    # edges between this entry and the next
    shift_interline = ["|", " "] * idx
    if coldiff == -1:
        n_spaces = 1
        edge_ch = "/"
    elif coldiff == 0:
        n_spaces = 2
        edge_ch = "|"
    else:
        n_spaces = 3
        edge_ch = "\\"
    shift_interline.extend(n_spaces * [" "])
    shift_interline.extend([edge_ch, " "] * (ncols - idx - 1))
    # draw edges from the current node to its parents
    _drawedges(edges, nodeline, shift_interline)
    # lines is the list of all graph lines to print
    lines = [nodeline]
    if add_padding_line:
        lines.append(_getpaddingline(idx, ncols, edges))
    if not set(shift_interline).issubset(set([' ', '|'])): # compact
        lines.append(shift_interline)
    # make sure that there are as many graph lines as there are
    # log strings
    if len(lines) < height:
        extra_interline = ["|", " "] * (ncols + coldiff)
        while len(lines) < height:
            lines.append(extra_interline)
    # print lines
    indentation_level = max(ncols, ncols + coldiff)
    for line in lines:
        # justify to GRAPH_MIN_WIDTH for convenience
        if len(line) < GRAPH_MIN_WIDTH:
            line.append(' ' * (GRAPH_MIN_WIDTH - len(line)))
        yield [('GraphLog', item) if isinstance(item, basestring) else item for item in line]
    # ... and start over
    state[0] = coldiff
    state[1] = idx

