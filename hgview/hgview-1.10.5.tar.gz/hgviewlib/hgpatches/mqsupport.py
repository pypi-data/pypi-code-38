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
The main goal of this module is to create fake mercurial change context classes from
data information available in mq patch files.

Only methods that are required by hgview had been implemented.
They may have special features to help hgview, So use it with care.

The main differences are:

* node, rev, hex are all strings (patch name)
* files within patches are always displayed as modified files
* manifest only shows files modified by the mq patch.
* data may be empty (date, description, status, tags, branch, etc.)
* the parent of a patch may by the last applied on or previous patch or nullid
* the child of a patch is the next patch
* patches are hidden
"""

from __future__ import with_statement

import re
import os
import os.path as osp
from operator import or_
from itertools import chain

from mercurial import error, node, patch, context, manifest
from hgext.mq import patchheader

from hgviewlib.hgpatches import phases

MODIFY, ADD, REMOVE, DELETE, UNKNOWN, RENAME = range(6) # order is important for status

class PatchMetaData(object):
    def __init__(self, path, oldpath, op):
        self.path = path
        self.oldpath = oldpath
        self.op = op

class MqLookupError(error.LookupError):
    """Specific exception dedicated to mq patches"""

class MqCtx(context.changectx):
    """Base class of mq patch context (changectx, filectx, etc.)"""
    def __init__(self, repo, patch_name):
        self.name = patch_name
        self._rev = self.name
        self._repo = repo
        self._queue = self._repo.mq

        self.path = self._queue.join(self.name)

    @property
    def applied(self):
        return bool(self._queue.isapplied(self.name))

    def __contains__(self, filename):
        return filename in self.files()

    def __iter__(self):
        for filename in self.files():
            yield filename

    def __getitem__(self, filename):
        return self.filectx(filename)

    def files(self):
        """Return the list of related files"""
        raise NotImplementedError

    def filectx(self, path, **kwargs):
        """Return the context related to the filename"""
        raise NotImplementedError

class MqChangeCtx(MqCtx):
    """
    A Mercurial change context fake for unapplied mq patch.
    Use with care as methods may be missing or have special features.
    """

    def __init__(self, repo, patch_name):
        super(MqChangeCtx, self).__init__(repo, patch_name)
        if patch_name is None:
            raise ValueError
        self._header_cache = None
        self._diffs_cache = None
        self._files_cache = None

    def __repr__(self):
        return '<MqChangeCtx (unapplied) %s>' % self.name

    @property
    def _header(self):
        if self._header_cache is not None:
            return self._header_cache
        self._header_cache = patchheader(self.path) 
        return self._header_cache

    @property
    def _diffs(self):
        # cache on first access only to speed up the process
        if self._diffs_cache is not None:
            return self._diffs_cache
        self._diffs_cache = []
        hunks = None
        meta = None
        data = None
        with open(self.path) as fid:
            for event, data in patch.iterhunks(fid):
                if event == 'file':
                    if hunks:
                        self._diffs_cache.append(MqFileCtx(hunks, meta, self))
                    hunks = []
                    meta = data[-1]
                    if not hasattr(meta, 'path'):
                        new, old = data[:2]
                        meta = PatchMetaData(new[2:], old[2:], 'UNKNOWN') # [2:] = remove a/
                elif event == 'hunk' and data:
                    hunks.append(data)
            if hunks:
                self._diffs_cache.append(MqFileCtx(hunks, meta, self))
        return self._diffs_cache

    def branch(self):
        return getattr(self._header, 'branch', '')

    def children(self):
        series = self._queue.series
        try:
            idx = series.index(self.name)
            return [self._repo[series[idx + 1]] if idx else self._repo[None]]
        except IndexError:
            return [self._repo[node.nullid]]

    def date(self):
        date = self._header.date
        if not date:
            return ()
        date, timezone = date.split()
        return float(date), int(timezone)

    def description(self):
        return '\n'.join(self._header.message)

    def filectx(self, filename, _cache=[], **kwargs):
        for diff in self._diffs:
            if diff.path == filename:
                return diff
        raise MqLookupError(self.name, filename, 'file not in manifest.')

    def files(self):
        if self._files_cache is not None:
            return self._files_cache
        out = list(set(chain(*(diff.files() for diff in self._diffs))))
        self._files_cache = out
        return out

    def flags(self, path):
        return ''

    def hex(self):
        return self.name

    def hidden(self):
        return True

    def phase(self):
        return phases.secret

    def manifest(self):
        return manifest.manifestdict.fromkeys(self.files(), '=')

    def node(self):
        '''Return the name of the patch'''
        return self.name
    @property
    def _node(self):
        return self.node() # in that way to support old hg

    def parents(self):
        if self._header.parent:
            try:
                return [self._repo[self._header.parent]]
            except error.RepoLookupError:
                pass
        series = self._queue.series
        if not self.name in series:
            return []
        idx = series.index(self.name)
        return [self._repo[series[idx - 1]] if idx else self._repo[None]]

    def rev(self):
        return self.name

    def status(self):
        return ()

    def tags(self):
        return [self.name]

    def user(self):
        return self._header.user or ''

class _MqMissingPatch_Header(object):
    """Patch header fake for missing file"""
    message = (':ERROR: patch file is missing !!!',)
    date, breanch, user, parent = ('',) * 4

class MqMissingChangeCtx(MqChangeCtx):
    """Changeset class for patch in series without file."""
    def __init__(self, repo, patch_name):
        super(MqMissingChangeCtx, self).__init__(repo, patch_name)
        self._header_cache = _MqMissingPatch_Header()
        self._diffs_cache = ()
        self._files_cache = ()

    def __repr__(self):
        return '<MqChangeCtx (missing file) %s>' % self.name

class MqFileCtx(context.filectx):
    """Mq Fake for file context"""

    def __init__(self, hunks, meta, changectx):
        self._changectx = changectx
        self._repo = changectx._repo
        self._path = meta.path
        self._oldpath = meta.oldpath
        self._operation = meta.op
        self._data = '\n\n\n'
        self._data += ''.join(l for h in hunks for l in h.hunk if h)
        # XXX how to deal diff encodings?
        try:
            self._data = unicode(self._data, "utf-8")
        except UnicodeError:
            # XXX use a default encoding from config?
            self._data = unicode(self._data, "iso-8859-15", 'ignore')

    @property
    def path(self):
        return self._path

    @property
    def oldpath(self):
        return self._oldpath

    def files(self):
        """List of modified files"""
        return tuple(path for path in (self._path, self._oldpath)
                     if path and not os.devnull.endswith(path))
    # note endswith is used as the complete path have been cut
    # (expecting ``a/`` at the beginning of path)

    def data(self):
        """ return the patch hunks"""
        return self._data
    __str__ = data

    def isexec(self):
        return False #  XXX

    def __repr__(self):
        return ('<MqFileCtx (unapplied) %s@%s>' %
                (self._path, self._changectx.name))

    def flags(self):
        return ''

    def renamed(self):
        if self.state == 'RENAME':
            return self._oldpath, self._path
        return False

    def parents(self):
        try:
            return [self._changectx._repo[self._changectx._header.parent].filectx(self.path)]
        except error.RepoLookupError:
            return [self]

    def size(self):
        return len(self._data)

    @property
    def state(self):
        return self._operation or 'UNKNOWN'

    def filelog(self):
        return None

# ___________________________________________________________________________
def reposetup(ui, repo):
    """
    extend repo class with special mq logic
    """
    if (not repo.local()) or (not hasattr(repo, "mq")):
        return

    repo.unapplieds = filter(repo.mq.unapplied, repo.mq.series)

    getitem_orig = repo.__getitem__
    status_orig = repo.status
    lookup_orig = repo.lookup

    class MqRepository(repo.__class__):
        __hgview__ = True

        def __getitem__(self, changeid):
            if changeid not in self.unapplieds: #pylint: disable=E1101
                return getitem_orig(changeid)
            patch = MqChangeCtx(repo, changeid)
            if os.path.exists(patch.path):
                return patch
            return MqMissingChangeCtx(repo, changeid)

        def status(self, node1='.', node2=None, match=None, *args, **kwargs):
            if isinstance(node1, context.changectx):
                ctx1 = node1
            else:
                ctx1 = self[node1]
            if isinstance(node2, context.changectx):
                ctx2 = node2
            else:
                ctx2 = self[node2]

            if not (isinstance(ctx1, MqCtx) or isinstance(ctx2, MqCtx)):
                return super(MqRepository, self).status(ctx1, ctx2, match, *args, **kwargs)
            # modified, added, removed, deleted, unknown
            status = ([], [], [], [], [], [], [])
            if match is None:
                match = lambda x: x
            # force patch content as MODIFY which is close to what a patch is :D
            status[MODIFY][:] = [path for path in ctx2.files() if match(path)]
            return status

        def lookup(self, key):
            if isinstance(key, MqCtx):
                return key.node()
            if key in repo.unapplieds:
                return key
            return lookup_orig(key)
    # common way for hg extensions
    repo.__class__ = MqRepository
