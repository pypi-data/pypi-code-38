# Copyright 2017 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""
Compatibility module
"""

import inspect

from mercurial import (
    context,
    copies,
    encoding,
    mdiff,
    obsolete,
    obsutil,
    repair,
    scmutil,
    util,
    ui as uimod,
)
from mercurial.hgweb import hgweb_mod

# hg < 4.6 compat (c8e2d6ed1f9e)
try:
    from mercurial import logcmdutil
    changesetdisplayer = logcmdutil.changesetdisplayer
    changesetprinter = logcmdutil.changesetprinter
    displaygraph = logcmdutil.displaygraph
    changesetdiffer = logcmdutil.changesetdiffer
except (AttributeError, ImportError):
    from mercurial import cmdutil
    changesetdisplayer = cmdutil.show_changeset
    changesetprinter = cmdutil.changeset_printer
    displaygraph = cmdutil.displaygraph
    changesetdiffer = None

from . import (
    exthelper,
)

eh = exthelper.exthelper()

def isobsnotesupported():
    # hack to know obsnote is supported. The patches for obsnote support was
    # pushed before the obsfateprinter patches, so this will serve as a good
    # check
    if not obsutil:
        return False
    return util.safehasattr(obsutil, 'obsfateprinter')

# Evolution renaming compat

TROUBLES = {
    'ORPHAN': 'orphan',
    'CONTENTDIVERGENT': 'content-divergent',
    'PHASEDIVERGENT': 'phase-divergent',
}

if util.safehasattr(uimod.ui, 'makeprogress'):
    def progress(ui, topic, pos, item="", unit="", total=None):
        progress = ui.makeprogress(topic, unit, total)
        if pos is not None:
            progress.update(pos, item=item)
        else:
            progress.complete()
else:
    def progress(ui, topic, pos, item="", unit="", total=None):
        ui.progress(topic, pos, item, unit, total)

# XXX: Better detection of property cache
if 'predecessors' not in dir(obsolete.obsstore):
    @property
    def predecessors(self):
        return self.precursors

    obsolete.obsstore.predecessors = predecessors

def memfilectx(repo, ctx, fctx, flags, copied, path):
    # XXX Would it be better at the module level?
    varnames = context.memfilectx.__init__.__code__.co_varnames

    if "copysource" in varnames:
        mctx = context.memfilectx(repo, ctx, fctx.path(), fctx.data(),
                                  islink='l' in flags,
                                  isexec='x' in flags,
                                  copysource=copied.get(path))
    # compat with hg <- 4.9
    elif varnames[2] == "changectx":
        mctx = context.memfilectx(repo, ctx, fctx.path(), fctx.data(),
                                  islink='l' in flags,
                                  isexec='x' in flags,
                                  copied=copied.get(path))
    else:
        mctx = context.memfilectx(repo, fctx.path(), fctx.data(),
                                  islink='l' in flags,
                                  isexec='x' in flags,
                                  copied=copied.get(path))
    return mctx

def strdiff(a, b, fn1, fn2):
    """ A version of mdiff.unidiff for comparing two strings
    """
    args = [a, '', b, '', fn1, fn2]

    # hg < 4.6 compat 8b6dd3922f70
    argspec = inspect.getargspec(mdiff.unidiff)

    if 'binary' in argspec.args:
        args.append(False)

    return mdiff.unidiff(*args)

# date related

try:
    import mercurial.utils.dateutil
    makedate = mercurial.utils.dateutil.makedate
    parsedate = mercurial.utils.dateutil.parsedate
except ImportError:
    import mercurial.util
    makedate = mercurial.util.makedate
    parsedate = mercurial.util.parsedate

def wireprotocommand(exthelper, name, args='', permission='pull'):
    try:
        # Since b4d85bc1
        from mercurial.wireprotov1server import wireprotocommand
        return wireprotocommand(name, args, permission=permission)
    except (ImportError, AttributeError):
        from mercurial import wireproto

    if 3 <= len(wireproto.wireprotocommand.func_defaults):
        return wireproto.wireprotocommand(name, args, permission=permission)

    # <= hg-4.5 permission must be registered in dictionnary
    def decorator(func):
        @eh.extsetup
        def install(ui):
            hgweb_mod.perms[name] = permission
            wireproto.commands[name] = (func, args)
    return decorator

# mercurial <= 4.5 do not have the updateresult object
try:
    from mercurial.merge import updateresult
except (ImportError, AttributeError):
    updateresult = None

# 46c2b19a1263f18a5829a21b7a5053019b0c5a31 in hg moved repair.stripbmrevset to
# scmutil.bookmarkrevs
# This change is a part of 4.7 cycle, so drop this when we drop support for 4.6
try:
    bmrevset = repair.stripbmrevset
except AttributeError:
    bmrevset = scmutil.bookmarkrevs

def hasconflict(upres):
    if updateresult is None:
        return bool(upres[-1])
    return bool(upres.unresolvedcount)

hg48 = util.safehasattr(copies, 'stringutil')
# code imported from Mercurial core at ae17555ef93f + patch
def fixedcopytracing(repo, c1, c2, base):
    """A complete copy-patse of copies._fullcopytrace with a one line fix to
    handle when the base is not parent of both c1 and c2. This should be
    converted in a compat function once https://phab.mercurial-scm.org/D3896
    gets in and once we drop support for 4.7, this should be removed."""

    from mercurial import pathutil

    # In certain scenarios (e.g. graft, update or rebase), base can be
    # overridden We still need to know a real common ancestor in this case We
    # can't just compute _c1.ancestor(_c2) and compare it to ca, because there
    # can be multiple common ancestors, e.g. in case of bidmerge.  Because our
    # caller may not know if the revision passed in lieu of the CA is a genuine
    # common ancestor or not without explicitly checking it, it's better to
    # determine that here.
    #
    # base.isancestorof(wc) is False, work around that
    _c1 = c1.p1() if c1.rev() is None else c1
    _c2 = c2.p1() if c2.rev() is None else c2
    # an endpoint is "dirty" if it isn't a descendant of the merge base
    # if we have a dirty endpoint, we need to trigger graft logic, and also
    # keep track of which endpoint is dirty
    if util.safehasattr(base, 'isancestorof'):
        dirtyc1 = not base.isancestorof(_c1)
        dirtyc2 = not base.isancestorof(_c2)
    else: # hg <= 4.6
        dirtyc1 = not base.descendant(_c1)
        dirtyc2 = not base.descendant(_c2)
    graft = dirtyc1 or dirtyc2
    tca = base
    if graft:
        tca = _c1.ancestor(_c2)

    # hg < 4.8 compat (dc50121126ae)
    try:
        limit = copies._findlimit(repo, c1, c2)
    except (AttributeError, TypeError):
        limit = copies._findlimit(repo, c1.rev(), c2.rev())
    if limit is None:
        # no common ancestor, no copies
        return {}, {}, {}, {}, {}
    repo.ui.debug("  searching for copies back to rev %d\n" % limit)

    m1 = c1.manifest()
    m2 = c2.manifest()
    mb = base.manifest()

    # gather data from _checkcopies:
    # - diverge = record all diverges in this dict
    # - copy = record all non-divergent copies in this dict
    # - fullcopy = record all copies in this dict
    # - incomplete = record non-divergent partial copies here
    # - incompletediverge = record divergent partial copies here
    diverge = {} # divergence data is shared
    incompletediverge = {}
    data1 = {'copy': {},
             'fullcopy': {},
             'incomplete': {},
             'diverge': diverge,
             'incompletediverge': incompletediverge,
            }
    data2 = {'copy': {},
             'fullcopy': {},
             'incomplete': {},
             'diverge': diverge,
             'incompletediverge': incompletediverge,
            }

    # find interesting file sets from manifests
    if hg48:
        addedinm1 = m1.filesnotin(mb, repo.narrowmatch())
        addedinm2 = m2.filesnotin(mb, repo.narrowmatch())
    else:
        addedinm1 = m1.filesnotin(mb)
        addedinm2 = m2.filesnotin(mb)
    bothnew = sorted(addedinm1 & addedinm2)
    if tca == base:
        # unmatched file from base
        u1r, u2r = copies._computenonoverlap(repo, c1, c2, addedinm1, addedinm2)
        u1u, u2u = u1r, u2r
    else:
        # unmatched file from base (DAG rotation in the graft case)
        u1r, u2r = copies._computenonoverlap(repo, c1, c2, addedinm1, addedinm2,
                                             baselabel='base')
        # unmatched file from topological common ancestors (no DAG rotation)
        # need to recompute this for directory move handling when grafting
        mta = tca.manifest()
        if hg48:
            m1f = m1.filesnotin(mta, repo.narrowmatch())
            m2f = m2.filesnotin(mta, repo.narrowmatch())
            baselabel = 'topological common ancestor'
            u1u, u2u = copies._computenonoverlap(repo, c1, c2, m1f, m2f,
                                                 baselabel=baselabel)
        else:
            u1u, u2u = copies._computenonoverlap(repo, c1, c2, m1.filesnotin(mta),
                                                 m2.filesnotin(mta),
                                                 baselabel='topological common ancestor')

    for f in u1u:
        copies._checkcopies(c1, c2, f, base, tca, dirtyc1, limit, data1)

    for f in u2u:
        copies._checkcopies(c2, c1, f, base, tca, dirtyc2, limit, data2)

    copy = dict(data1['copy'])
    copy.update(data2['copy'])
    fullcopy = dict(data1['fullcopy'])
    fullcopy.update(data2['fullcopy'])

    if dirtyc1:
        copies._combinecopies(data2['incomplete'], data1['incomplete'], copy, diverge,
                              incompletediverge)
    else:
        copies._combinecopies(data1['incomplete'], data2['incomplete'], copy, diverge,
                              incompletediverge)

    renamedelete = {}
    renamedeleteset = set()
    divergeset = set()
    for of, fl in list(diverge.items()):
        if len(fl) == 1 or of in c1 or of in c2:
            del diverge[of] # not actually divergent, or not a rename
            if of not in c1 and of not in c2:
                # renamed on one side, deleted on the other side, but filter
                # out files that have been renamed and then deleted
                renamedelete[of] = [f for f in fl if f in c1 or f in c2]
                renamedeleteset.update(fl) # reverse map for below
        else:
            divergeset.update(fl) # reverse map for below

    if bothnew:
        repo.ui.debug("  unmatched files new in both:\n   %s\n"
                      % "\n   ".join(bothnew))
    bothdiverge = {}
    bothincompletediverge = {}
    remainder = {}
    both1 = {'copy': {},
             'fullcopy': {},
             'incomplete': {},
             'diverge': bothdiverge,
             'incompletediverge': bothincompletediverge
            }
    both2 = {'copy': {},
             'fullcopy': {},
             'incomplete': {},
             'diverge': bothdiverge,
             'incompletediverge': bothincompletediverge
            }
    for f in bothnew:
        copies._checkcopies(c1, c2, f, base, tca, dirtyc1, limit, both1)
        copies._checkcopies(c2, c1, f, base, tca, dirtyc2, limit, both2)

    if dirtyc1 and dirtyc2:
        pass
    elif dirtyc1:
        # incomplete copies may only be found on the "dirty" side for bothnew
        assert not both2['incomplete']
        remainder = copies._combinecopies({}, both1['incomplete'], copy, bothdiverge,
                                          bothincompletediverge)
    elif dirtyc2:
        assert not both1['incomplete']
        remainder = copies._combinecopies({}, both2['incomplete'], copy, bothdiverge,
                                          bothincompletediverge)
    else:
        # incomplete copies and divergences can't happen outside grafts
        assert not both1['incomplete']
        assert not both2['incomplete']
        assert not bothincompletediverge
    for f in remainder:
        assert f not in bothdiverge
        ic = remainder[f]
        if ic[0] in (m1 if dirtyc1 else m2):
            # backed-out rename on one side, but watch out for deleted files
            bothdiverge[f] = ic
    for of, fl in bothdiverge.items():
        if len(fl) == 2 and fl[0] == fl[1]:
            copy[fl[0]] = of # not actually divergent, just matching renames

    if fullcopy and repo.ui.debugflag:
        repo.ui.debug("  all copies found (* = to merge, ! = divergent, "
                      "% = renamed and deleted):\n")
        for f in sorted(fullcopy):
            note = ""
            if f in copy:
                note += "*"
            if f in divergeset:
                note += "!"
            if f in renamedeleteset:
                note += "%"
            repo.ui.debug("   src: '%s' -> dst: '%s' %s\n" % (fullcopy[f], f,
                                                              note))
    del divergeset

    if not fullcopy:
        return copy, {}, diverge, renamedelete, {}

    repo.ui.debug("  checking for directory renames\n")

    # generate a directory move map
    d1, d2 = c1.dirs(), c2.dirs()
    # Hack for adding '', which is not otherwise added, to d1 and d2
    d1.addpath('/')
    d2.addpath('/')
    invalid = set()
    dirmove = {}

    # examine each file copy for a potential directory move, which is
    # when all the files in a directory are moved to a new directory
    for dst, src in fullcopy.iteritems():
        dsrc, ddst = pathutil.dirname(src), pathutil.dirname(dst)
        if dsrc in invalid:
            # already seen to be uninteresting
            continue
        elif dsrc in d1 and ddst in d1:
            # directory wasn't entirely moved locally
            invalid.add(dsrc + "/")
        elif dsrc in d2 and ddst in d2:
            # directory wasn't entirely moved remotely
            invalid.add(dsrc + "/")
        elif dsrc + "/" in dirmove and dirmove[dsrc + "/"] != ddst + "/":
            # files from the same directory moved to two different places
            invalid.add(dsrc + "/")
        else:
            # looks good so far
            dirmove[dsrc + "/"] = ddst + "/"

    for i in invalid:
        if i in dirmove:
            del dirmove[i]
    del d1, d2, invalid

    if not dirmove:
        return copy, {}, diverge, renamedelete, {}

    for d in dirmove:
        repo.ui.debug("   discovered dir src: '%s' -> dst: '%s'\n" %
                      (d, dirmove[d]))

    movewithdir = {}
    # check unaccounted nonoverlapping files against directory moves
    for f in u1r + u2r:
        if f not in fullcopy:
            for d in dirmove:
                if f.startswith(d):
                    # new file added in a directory that was moved, move it
                    df = dirmove[d] + f[len(d):]
                    if df not in copy:
                        movewithdir[f] = df
                        repo.ui.debug(("   pending file src: '%s' -> "
                                       "dst: '%s'\n") % (f, df))
                    break

    return copy, movewithdir, diverge, renamedelete, dirmove

# hg <= 4.9 compat (7694b685bb10)
fixupstreamed = util.safehasattr(scmutil, 'movedirstate')
if not fixupstreamed:
    copies._fullcopytracing = fixedcopytracing

if not util.safehasattr(obsutil, "_succs"):
    class _succs(list):
        """small class to represent a successors with some metadata about it"""

        def __init__(self, *args, **kwargs):
            super(_succs, self).__init__(*args, **kwargs)
            self.markers = set()

        def copy(self):
            new = _succs(self)
            new.markers = self.markers.copy()
            return new

        @util.propertycache
        def _set(self):
            # immutable
            return set(self)

        def canmerge(self, other):
            return self._set.issubset(other._set)
else:
    from mercurial.obsutil import _succs

def wrap_succs(succs):
    """ Wrap old data format of successorsets (tuple) only if if's not yet a
    _succs instance
    """

    if not util.safehasattr(succs, "markers"):
        return _succs(succs)
    else:
        return succs

if not util.safehasattr(obsutil, "markersdates"):
    MARKERS_DATE_COMPAT = True
else:
    MARKERS_DATE_COMPAT = False

def markersdates(markers):
    """returns the list of dates for a list of markers
    """
    if MARKERS_DATE_COMPAT is False:
        return obsutil.markersdates(markers)

    return [m[4] for m in markers]

if not util.safehasattr(obsutil, "markersusers"):
    MARKERS_USERS_COMPAT = True
else:
    MARKERS_USERS_COMPAT = False

def markersusers(markers):
    """ Returns a sorted list of markers users without duplicates
    """
    if MARKERS_USERS_COMPAT is False:
        return obsutil.markersusers(markers)

    markersmeta = [dict(m[3]) for m in markers]
    users = set(encoding.tolocal(meta['user']) for meta in markersmeta
                if meta.get('user'))

    return sorted(users)

if not util.safehasattr(obsutil, "markersoperations"):
    MARKERS_OPERATIONS_COMPAT = True
else:
    MARKERS_OPERATIONS_COMPAT = False

def markersoperations(markers):
    """ Returns a sorted list of markers operations without duplicates
    """
    if MARKERS_OPERATIONS_COMPAT is False:
        return obsutil.markersoperations(markers)

    markersmeta = [dict(m[3]) for m in markers]
    operations = set(meta.get('operation') for meta in markersmeta
                     if meta.get('operation'))

    return sorted(operations)
