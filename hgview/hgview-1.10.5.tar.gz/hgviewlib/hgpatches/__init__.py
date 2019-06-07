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
This modules contains monkey patches for Mercurial allowing hgview to support
older versions
"""

from functools import partial
from mercurial import changelog, filelog, patch, context, localrepo
from hgviewlib import add_demandimport_ignore

# for CPython > 2.7 (see pkg_resources) module [loaded by pygments])
add_demandimport_ignore("_frozen_importlib")

# from pyinotify which try from functools import reduce
add_demandimport_ignore("functools")

if not hasattr(changelog.changelog, '__len__'):
    changelog.changelog.__len__ = changelog.changelog.count
if not hasattr(filelog.filelog, '__len__'):
    filelog.filelog.__len__ = filelog.filelog.count

# mercurial ~< 1.8.4
if patch.iterhunks.func_code.co_varnames[0] == 'ui':
    iterhunks_orig = patch.iterhunks
    ui = type('UI', (), {'debug':lambda *x: None})()
    iterhunks = partial(iterhunks_orig, ui)
    patch.iterhunks = iterhunks

# mercurial ~< 1.8.3
if not hasattr(context.filectx, 'p1'):
    context.filectx.p1 = lambda self: self.parents()[0]

# mercurial < 2.1
if not hasattr(context.changectx, 'phase'):
    from hgviewlib.hgpatches.phases import phasenames
    context.changectx.phase = lambda self: 0
    context.changectx.phasestr = lambda self: phasenames[self.phase()]
    context.workingctx.phase = lambda self: 1

# note: use dir(...) has localrepo.localrepository.hiddenrevs always raises
#       an attribute error - because the repo is not set yet
if 'hiddenrevs' not in dir(localrepo.localrepository):
    def hiddenrevs(self):
        return getattr(self.changelog, 'hiddenrevs', ())
    localrepo.localrepository.hiddenrevs = property(hiddenrevs, None, None)
try:
    from mercurial.repoview import filterrevs
    def hiddenrevs(repo):
        return filterrevs(repo, 'visible')
except ImportError:
    def hiddenrevs(repo):
        # mercurial < 2.5 has no filteredrevs
        # mercurial < 2.3 has hiddenrevs on changelog
        # mercurial < 1.9 has no hiddenrevs
        return getattr(repo, 'hiddenrevs',
                       getattr(repo.changelog, 'hiddenrevs', ()))

# obsolete feature
if getattr(context.changectx, 'obsolete', None) is None:
    context.changectx.obsolete = lambda self: False
if getattr(context.changectx, 'unstable', None) is None:
    context.changectx.unstable = lambda self: False


### unofficial API implemented by mutable extension
# They will probably because official, but maybe with a different name
has_conflicting = True
if getattr(context.changectx, 'conflicting', None) is None:
    has_conflicting = False
    context.changectx.conflicting = lambda self: False
if getattr(context.changectx, 'divergent', None) is None:
    if has_conflicting:
        # older version with real conflicting support. rely on this for divergent.
        context.changectx.divergent = lambda self: self.conflicting()
    else:
        context.changectx.divergent = lambda self: False

has_latecomer = True
if getattr(context.changectx, 'latecomer', None) is None:
    has_latecomer = False
    context.changectx.latecomer = lambda self: self.bumped()
if getattr(context.changectx, 'bumped', None) is None:
    if has_latecomer:
        # older version with real latecomer support. rely on this for bumped.
        context.changectx.bumped = lambda self: self.latecomer()
    else:
        context.changectx.bumped = lambda self: False

if getattr(context.changectx, 'instabilities', None) is None:
    if getattr(context.changectx, 'troubles', None) is None:
        def instabilities(ctx):
            troubles = []
            if ctx.unstable():
                troubles.append('unstable')
            if ctx.bumped(): # rename
                troubles.append('bumped')
            if ctx.divergent():
                troubles.append('divergent')
            return tuple(troubles)
        context.changectx.instabilities = instabilities
    else:
        context.changectx.instabilities = context.changectx.troubles

try:
    # meaning of obsstore attribute have been flipped between mercurial 2.3 and
    # mercurial 2.4
    import mercurial.obsolete
    mercurial.obsolete.getrevs
except (ImportError, AttributeError):
    # pre Mercurial 2.4
    def precursorsmarkers(obsstore, node):
        return obsstore.successors.get(node, ())

    def successorsmarkers(obsstore, node):
        return obsstore.precursors.get(node, ())
else:
    def precursorsmarkers(obsstore, node):
        if not hasattr(obsstore, 'predecessors'):
            return obsstore.precursors.get(node, ())
        else:
            return obsstore.predecessors.get(node, ())

    def successorsmarkers(obsstore, node):
        return obsstore.successors.get(node, ())
