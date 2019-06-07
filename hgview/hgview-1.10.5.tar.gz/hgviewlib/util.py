# -*- coding: utf-8 -*-
# util functions
#
# Copyright (C) 2009-2012 Logilab. All rights reserved.
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.
"""
Several helper functions
"""
import os
import os.path as osp
import string
from functools import partial
from mercurial import hg, config, error

from hgviewlib.hgpatches.scmutil import match
from hgviewlib.hgpatches import precursorsmarkers, successorsmarkers

try:
    from mercurial.utils.stringutil import binary  # noqa
except ImportError:  # hg < 4.7
    from mercurial.util import binay  # noqa


def tounicode(text):
    """
    Tries to convert ``text`` into a unicode string.
    If ``text`` is already a unicode object return it.
    """
    if isinstance(text, unicode):
        return text
    else:
        text = str(text)
    for encoding in ('utf-8', 'iso-8859-15', 'cp1252'):
        try:
            return text.decode(encoding)
        except (UnicodeError, UnicodeDecodeError):
            pass
    return text.decode('utf-8', 'replace')

def isexec(filectx):
    """
    Return True is the file at filectx revision is executable
    """
    if hasattr(filectx, "isexec"):
        return filectx.isexec()
    return "x" in filectx.flags()

def exec_flag_changed(filectx):
    """
    Return True if the file referenced by filectx has changed its exec
    flag
    """
    flag = isexec(filectx)
    parents = filectx.parents()
    if not parents:
        return ""

    pflag = isexec(parents[0])
    if flag != pflag:
        if flag:
            return "set"
        else:
            return "unset"
    return ""

def isbfile(filename):
    return filename and filename.startswith('.hgbfiles' + os.sep)

def bfilepath(filename):
    return filename and filename.replace('.hgbfiles' + os.sep, '')

def find_repository(path):
    """returns <path>'s mercurial repository

    None if <path> is not under hg control
    """
    path = os.path.abspath(path)
    while not os.path.isdir(os.path.join(path, ".hg")):
        oldpath = path
        path = os.path.dirname(path)
        if path == oldpath:
            return None
    return path

def rootpath(repo, rev, path):
    """return the path name of 'path' relative to repo's root at
    revision rev;
    path is relative to cwd
    """
    ctx = repo[rev]
    filenames = list(ctx.walk(match(ctx, [path], {})))
    if len(filenames) != 1 or filenames[0] not in ctx.manifest():
        return None
    else:
        return filenames[0]

# XXX duplicates logilab.mtconverter.__init__ code
CONTROL_CHARS = [chr(ci) for ci in range(32)]
TR_CONTROL_CHARS = [' '] * len(CONTROL_CHARS)
for c in ('\n', '\r', '\t'):
    TR_CONTROL_CHARS[ord(c)] = c
TR_CONTROL_CHARS[ord('\f')] = '\n'
TR_CONTROL_CHARS[ord('\v')] = '\n'
ESC_CAR_TABLE = string.maketrans(''.join(CONTROL_CHARS),
                                 ''.join(TR_CONTROL_CHARS))
ESC_UCAR_TABLE = unicode(ESC_CAR_TABLE, 'latin1')

def xml_escape(data):
    """escapes XML forbidden characters in attributes and CDATA"""
    if isinstance(data, unicode):
        data = data.translate(ESC_UCAR_TABLE)
    else:
        data = data.translate(ESC_CAR_TABLE)
    return (data.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            .replace('"','&quot;').replace("'",'&#39;'))

def format_desc(desc, width):
    """ format a ctx description for oneliner
    representation (summary view) """
    udesc = tounicode(desc)
    udesc = xml_escape(udesc.split('\n', 1)[0])
    if len(udesc) > width:
        udesc = udesc[:width] + '...'
    return udesc


def allbranches(repo, include_closed=False):
    """Return the list of branches in a repo

    Closed branch are excluded unless `include_closed=True`."""
    if getattr(repo, 'branchtags', None) is None:
        # mercurial 2.9 and above. branchtags is gone but we have cached value
        # to know if a branch is closed or not.
        clbranches = []
        branches = []
        for tag, heads, tip, closed in repo.branchmap().iterbranches():
            if closed:
                clbranches.append(tag)
            else:
                branches.append(tag)
    else:
        allbranches = sorted(repo.branchtags().items())

        openbr = []
        for branch, brnode in allbranches:
            openbr.extend(repo.branchheads(branch, closed=False))
        clbranches = [br for br, node in allbranches if node not in openbr]
        branches = [br for br, node in allbranches if node in openbr]
    if include_closed:
        branches = branches + clbranches
    return branches


def first_known_precursors(ctx, excluded=()):
    obsstore = getattr(ctx._repo, 'obsstore', None)
    startnode = ctx.node()
    nm = ctx._repo.changelog.nodemap
    if obsstore is not None:
        markers = precursorsmarkers(obsstore, startnode)
        # consider all precursors
        candidates = set(mark[0] for mark in markers)
        seen = set(candidates)
        if startnode in candidates:
            candidates.remove(startnode)
        else:
            seen.add(startnode)
        while candidates:
            current = candidates.pop()
            # is this changeset in the displayed set ?
            crev = nm.get(current)
            if crev is not None and crev not in excluded:
                yield ctx._repo[crev]
            else:
                for mark in precursorsmarkers(obsstore, current):
                    if mark[0] not in seen:
                        candidates.add(mark[0])
                        seen.add(mark[0])

def first_known_successors(ctx, excluded=()):
    obsstore = getattr(ctx._repo, 'obsstore', None)
    startnode = ctx.node()
    nm = ctx._repo.changelog.nodemap
    if obsstore is not None:
        markers = successorsmarkers(obsstore, startnode)
        # consider all precursors
        candidates = set()
        for mark in markers:
            candidates.update(mark[1])
        seen = set(candidates)
        if startnode in candidates:
            candidates.remove(startnode)
        else:
            seen.add(startnode)
        while candidates:
            current = candidates.pop()
            # is this changeset in the displayed set ?
            crev = nm.get(current)
            if crev is not None and crev not in excluded:
                yield ctx._repo[crev]
            else:
                for mark in successorsmarkers(obsstore, current):
                    for succ in mark[1]:
                        if succ not in seen:
                            candidates.add(succ)
                            seen.add(succ)

def build_repo(ui, path):
    """build a repo like hg.repository

    But ensure it is not filtered whatever the version used"""
    if isinstance(path, unicode):
        path = path.encode('utf-8')
    repo = hg.repository(ui, path)
    return getattr(repo, 'unfiltered', lambda: repo)()

def upward_path(path):
    """A generator function that upward path

    >>> for path in upward_path('/tmp/jungle/elephants/babar/head/'):
    ...    print path
    ...
    /tmp/jungle/elephants/babar/head
    /tmp/jungle/elephants/babar
    /tmp/jungle/elephants
    /tmp/jungle
    /tmp
    /
    """
    path = path.rstrip(os.path.sep)
    yield path
    while path != osp.dirname(path): # root folder reached?
        path = osp.dirname(path)
        yield osp.normpath(path)


def _get_conf(repo_path, conf_file):
    """Read a configuratio inside a repo"""
    # We do not ask to the extension api (there is no public
    # api). Because setting up hg to use the extension is merely more
    # complicated than a naive approach.

    # they all have the same kind of settings: a file on the root
    # folder in rc-style.
    confpath = osp.join(repo_path, conf_file)
    if not osp.exists(confpath):
        return None
    conf = config.config()
    try:
        conf.read(confpath)
        out = conf
    except error.ParseError:
        out = None
    return out

def _get_subrepo(repo_path):
    """Get subrepo style nested repo"""
    config = _get_conf(repo_path, '.hgsub')
    if config is None:
        return None
    return ((path, path) for path in config[''].keys())


def _get_guestrepo(repo_path):
    """Get guestrepo style nested repo"""
    config = _get_conf(repo_path, '.hgguestrepo')
    if config is None:
        return None
    return ((value.split(None, 1)[0], path)
            for path, value in config[''].iteritems())

SUBREPO_GETTERS = [_get_subrepo, _get_guestrepo]


def read_nested_repo_paths(repopath):
    '''Return a list of pairs ``(name, path)``.

    They describe sub-repositories managed by *subrepo*, and *guestrepo* within
    the master repository located at ``repopath``'''
    repopath = osp.abspath(repopath)
    subpath = partial(osp.join, repopath)
    for helper in SUBREPO_GETTERS:
        data = helper(repopath)
        if data is not None:
            return [(name, osp.normpath(subpath(path))) for (name, path) in data]
    return []

def compose(f, g):
    """Return the functions composition ``f o g``.

    >>> foo = compose(str, float)
    >>> foo(1)
    '1.0'
    """
    composed = lambda *args, **kwargs: f(g(*args, **kwargs))
    names = (getattr(f, '__name__', 'unknown'),
             getattr(g, '__name__', 'unknown'))
    composed.__doc__ = 'functions composition (%s o %s)' % names
    composed.__name__ = '(%s o %s)' % names
    return composed
