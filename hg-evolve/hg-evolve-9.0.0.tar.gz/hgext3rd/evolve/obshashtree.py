#############################
### Tree Hash computation ###
#############################

# Status: dropable
#
# This module don't need to be upstreamed and can be dropped if its maintenance
# become a burden

import hashlib

from mercurial import (
    error,
    node,
    obsolete,
)

from mercurial.i18n import _

from . import (
    compat,
    exthelper,
)

eh = exthelper.exthelper()

# Dash computed from a given changesets using all markers relevant to it and
# the obshash of its parents.  This is similar to what happend for changeset
# node where the parent is used in the computation
@eh.command(
    'debugobsrelsethashtree',
    [('', 'v0', None, 'hash on marker format "0"'),
     ('', 'v1', None, 'hash on marker format "1" (default)')], _(''))
def debugobsrelsethashtree(ui, repo, v0=False, v1=False):
    """display Obsolete markers, Relevant Set, Hash Tree
    changeset-node obsrelsethashtree-node

    It computed form the "obs-hash-tree" value of its parent and markers
    relevant to the changeset itself.

    The obs-hash-tree is no longer used for any user facing logic. However the
    debug command stayed as an inspection tool. It does not seem supseful to
    upstream the command with the rest of evolve. We can safely drop it."""
    if v0 and v1:
        raise error.Abort('cannot only specify one format')
    elif v0:
        treefunc = _obsrelsethashtreefm0
    else:
        treefunc = _obsrelsethashtreefm1

    for chg, obs in treefunc(repo):
        ui.status('%s %s\n' % (node.hex(chg), node.hex(obs)))

def _obsrelsethashtreefm0(repo):
    return _obsrelsethashtree(repo, obsolete._fm0encodeonemarker)

def _obsrelsethashtreefm1(repo):
    return _obsrelsethashtree(repo, obsolete._fm1encodeonemarker)

def _obsrelsethashtree(repo, encodeonemarker):
    cache = []
    unfi = repo.unfiltered()
    markercache = {}
    compat.progress(repo.ui, _("preparing locally"), 0, total=len(unfi),
                    unit=_("changesets"))
    for i in unfi:
        ctx = unfi[i]
        entry = 0
        sha = hashlib.sha1()
        # add data from p1
        for p in ctx.parents():
            p = p.rev()
            if p < 0:
                p = node.nullid
            else:
                p = cache[p][1]
            if p != node.nullid:
                entry += 1
                sha.update(p)
        tmarkers = repo.obsstore.relevantmarkers([ctx.node()])
        if tmarkers:
            bmarkers = []
            for m in tmarkers:
                if m not in markercache:
                    markercache[m] = encodeonemarker(m)
                bmarkers.append(markercache[m])
            bmarkers.sort()
            for m in bmarkers:
                entry += 1
                sha.update(m)
        if entry:
            cache.append((ctx.node(), sha.digest()))
        else:
            cache.append((ctx.node(), node.nullid))
        compat.progress(repo.ui, _("preparing locally"), i, total=len(unfi),
                        unit=_("changesets"))
    compat.progress(repo.ui, _("preparing locally"), None)
    return cache
