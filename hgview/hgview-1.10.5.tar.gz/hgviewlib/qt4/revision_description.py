# Copyright (c) 2009-2012 LOGILAB S.A. (Paris, FRANCE).
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
Qt4 high level widgets for hg repo changelogs and filelogs
"""
from collections import defaultdict

from mercurial.node import short as short_hex

from mercurial.error import RepoError

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, pyqtSignal

from hgviewlib.config import HgConfig
from hgviewlib.util import format_desc, xml_escape, tounicode
from hgviewlib.util import first_known_precursors, first_known_successors
from hgviewlib.qt4.mixins import ActionsMixin

# Re-Structured Text support
raw2html = lambda x: u'<pre>%s</pre>' % xml_escape(x)
try:
    from docutils.core import publish_string
    import docutils.utils
    def rst2html(text, stylesheet_path=None):
        if stylesheet_path is None:
            stylesheet_path = 'qrc:/resources/description.css'
        try:
            # halt_level allows the parser to raise errors
            # report_level cleans the standard output
            out = publish_string(text, writer_name='html', settings_overrides={
                'halt_level':docutils.utils.Reporter.WARNING_LEVEL,
                'report_level':docutils.utils.Reporter.SEVERE_LEVEL + 1,
                'stylesheet_path': stylesheet_path,
                'embed_stylesheet': False,
            })
        except:
            # docutils is not always reliable (or reliably packaged)
            out = raw2html(text)
        if not isinstance(out, unicode):
            # if the docutils call did not fail, we likely got an str ...
            out = tounicode(out)
        return out
except ImportError:
    rst2html = None

TROUBLE_EXPLANATIONS = defaultdict(lambda:u'unknown trouble')
TROUBLE_EXPLANATIONS['unstable']  = "Based on obsolete ancestor"
TROUBLE_EXPLANATIONS['bumped']    = "Hopeless successors of a public changeset"
TROUBLE_EXPLANATIONS['divergent'] = "Another changeset are also a successors "\
                                    "of one of your precursor"
# temporary compat with older evolve version
TROUBLE_EXPLANATIONS['latecomer'] = TROUBLE_EXPLANATIONS['bumped']
TROUBLE_EXPLANATIONS['conflicting'] = TROUBLE_EXPLANATIONS['divergent']
class RevisionDescriptionView(ActionsMixin, QtGui.QTextBrowser):
    """
    Display metadata for one revision (rev, author, description, etc.)
    using a TextBrowser.
    """

    parent_revision_selected = pyqtSignal([], [int])
    revision_selected = pyqtSignal([], [int])

    def __init__(self, parent=None):
        super(RevisionDescriptionView, self).__init__(parent)
        self.excluded = ()
        self.descwidth = 60 # number of chars displayed for parent/child descriptions

        self.add_action(
            'rst', self.tr("Fancy description"),
            menu=self.tr("Display"),
            tip=self.tr('Interpret ReST comments'),
            callback=self.refreshDisplay,
            checked=bool(rst2html),
            enabled=bool(rst2html),
            )
        self.anchorClicked.connect(self.on_anchor_clicked)

    def on_anchor_clicked(self, qurl):
        """
        Callback called when a link is clicked in the text browser
        """
        rev = qurl.toString()
        diff = False
        if rev.startswith('diff_'):
            rev = int(rev[5:])
            diff = True

        try:
            rev = self.ctx._repo[rev].rev()
        except RepoError:
            QtGui.QDesktopServices.openUrl(qurl)
            self.refreshDisplay()

        if diff:
            self.diffrev = rev
            self.refreshDisplay()
            # TODO: emit a signal to recompute the diff
            if self.diffrev is None:
                self.parent_revision_selected.emit()
            else:
                self.parent_revision_selected[int].emit(self.diffrev)
        else:
            if rev is None:
                self.revision_selected.emit()
            else:
                self.revision_selected[int].emit(rev)

    def setDiffRevision(self, rev):
        if rev != self.diffrev:
            self.diffrev = rev
            self.refreshDisplay()

    def displayRevision(self, ctx):
        self.ctx = ctx
        self.diffrev = ctx.parents()[0].rev()
        if hasattr(self.ctx._repo, "mq"):
            self.mqseries = self.ctx._repo.mq.series[:]
            self.mqunapplied = [x[1] for x in self.ctx._repo.mq.unapplied(self.ctx._repo)]
            mqpatch = set(self.ctx.tags()).intersection(self.mqseries)
            if mqpatch:
                self.mqpatch = mqpatch.pop()
            else:
                self.mqpatch = None
        else:
            self.mqseries = []
            self.mqunapplied = []
            self.mqpatch = None

        self.refreshDisplay()

    def selectNone(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        cursor.setPosition(0)
        self.setTextCursor(cursor)
        self.setExtraSelections([])

    def searchString(self, text):
        self.selectNone()
        if text in self.toPlainText():
            clist = []
            while self.find(text):
                eselect = self.ExtraSelection()
                eselect.cursor = self.textCursor()
                eselect.format.setBackground(QtGui.QColor('#ffffbb'))
                clist.append(eselect)
            self.selectNone()
            self.setExtraSelections(clist)
            def finditer(self, text):
                if text:
                    while True:
                        if self.find(text):
                            yield self.ctx.rev(), None
                        else:
                            break
            return finditer(self, text)

    def refreshDisplay(self):
        ctx = self.ctx
        rev = ctx.rev()
        cfg = HgConfig(ctx._repo.ui)
        buf = u"<table width=100%>\n"
        if self.mqpatch:
            buf += u'<tr bgcolor=%s>' % cfg.getMQFGColor()
            buf += u'<td colspan=4 width=100%><b>Patch queue:</b>&nbsp;'
            for p in self.mqseries:
                if p in self.mqunapplied:
                    p = u"<i>%s</i>" % tounicode(p)
                elif p == self.mqpatch:
                    p = u"<b>%s</b>" % tounicode(p)
                buf += u'&nbsp;%s&nbsp;' % tounicode(p)
            buf += u'</td></tr>\n'

        buf += u'<tr>'
        if rev is None:
            buf += u"<td><b>Working Directory</b></td>\n"
        else:
            buf += u'<td title="Revision"><b>'\
                   u'<span class="rev_number">%s</span>:'\
                   u'<span class="rev_hash">%s</span>'\
                   u'</b></td>\n' % (ctx.rev(), short_hex(ctx.node()))

        user = tounicode(ctx.user()) if ctx.node() else u''
        buf += '<td title="Author">%s</td>\n' % user
        buf += '<td title="Branch name">%s</td>\n' % tounicode(ctx.branch())
        buf += '<td title="Phase name">%s</td>\n' % tounicode(ctx.phasestr())
        buf += '</tr>'
        buf += "</table>\n"

        buf += "<table width=100%>\n"
        parents = [p for p in ctx.parents() if p]
        for p in parents:
            if p.rev() > -1:
                buf += self._html_ctx_info(p, 'Parent', 'Direct ancestor of this changeset')
        if len(parents) == 2:
            p = parents[0].ancestor(parents[1])
            buf += self._html_ctx_info(p, 'Ancestor', 'Direct ancestor of this changeset')

        for p in ctx.children():
            r = p.rev()
            if r > -1 and r not in self.excluded:
                buf += self._html_ctx_info(p, 'Child', 'Direct descendant of this changeset')
        for prec in first_known_precursors(ctx, self.excluded):
            buf += self._html_ctx_info(prec, 'Precursor',
                'Previous version obsolete by this changeset')
        for suc in first_known_successors(ctx, self.excluded):
            buf += self._html_ctx_info(suc, 'Successors',
                'Updated version that make this changeset obsolete')
        bookmarks = ', '.join(tounicode(bookmark) for bookmark in ctx.bookmarks())
        if bookmarks:
            buf += '<tr><td width=50 class="label"><b>Bookmarks:</b></td>'\
                   '<td colspan=5>&nbsp;'\
                   '<span class="short_desc">%s</span></td></tr>'\
                   '\n' % bookmarks
        troubles = ctx.instabilities()
        if troubles:
            span = u'<span title="%s"  style="color: red;">%s</span>'
            content = u', '.join([span % (TROUBLE_EXPLANATIONS[troub], troub)
                                 for troub in troubles])
            buf += '<tr><td width=50 class="label"><b>Troubles:</b></td>'\
                   '<td colspan=5>&nbsp;'\
                   '<span class="short_desc" >%s</span></td></tr>'\
                   '\n' % ''.join(content)
        buf += u"</table>\n"
        desc = tounicode(ctx.description())
        if self.get_action('rst').isChecked():
            replace = cfg.getFancyReplace()
            if replace:
                desc = replace(desc)
            desc = rst2html(desc, cfg.getDescriptionStylePath())
        else:
            desc = raw2html(desc)
        buf += u'<div class="diff_desc">%s</div>\n' % desc
        self.setHtml(buf)

    def _html_ctx_info(self, ctx, title, tooltip=None):
        isdiffrev = ctx.rev() == self.diffrev
        if not tooltip:
            tooltip = title
        short = short_hex(ctx.node()) if getattr(ctx, 'applied', True) else ctx.node()
        descr = format_desc(ctx.description(), self.descwidth)
        rev = ctx.rev()
        out = '<tr>'\
              '<td width=60 class="label" title="%(tooltip)s"><b>%(title)s:</b></td>'\
              '<td colspan=5>' % locals()
        if isdiffrev:
            out += '<b>'
        out += '<span class="rev_number">'\
               '<a href="diff_%(rev)s" class="rev_diff" title="display diff from there">%(rev)s</a>'\
               '</span>:'\
               '<a title="go to there" href="%(rev)s" class="rev_hash">%(short)s</a>&nbsp;'\
               '<span class="short_desc"><i>%(descr)s</i></span>' % locals()
        if isdiffrev:
            out += '</b>'
        out += '</td></tr>\n'
        return out
