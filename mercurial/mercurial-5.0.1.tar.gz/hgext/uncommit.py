# uncommit - undo the actions of a commit
#
# Copyright 2011 Peter Arrenbrecht <peter.arrenbrecht@gmail.com>
#                Logilab SA        <contact@logilab.fr>
#                Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#                Patrick Mezard <patrick@mezard.eu>
# Copyright 2016 Facebook, Inc.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

"""uncommit part or all of a local changeset (EXPERIMENTAL)

This command undoes the effect of a local commit, returning the affected
files to their uncommitted state. This means that files modified, added or
removed in the changeset will be left unchanged, and so will remain modified,
added and removed in the working directory.
"""

from __future__ import absolute_import

from mercurial.i18n import _

from mercurial import (
    cmdutil,
    commands,
    context,
    copies as copiesmod,
    error,
    node,
    obsutil,
    pycompat,
    registrar,
    rewriteutil,
    scmutil,
    util,
)

cmdtable = {}
command = registrar.command(cmdtable)

configtable = {}
configitem = registrar.configitem(configtable)

configitem('experimental', 'uncommitondirtywdir',
    default=False,
)
configitem('experimental', 'uncommit.keep',
    default=False,
)

# Note for extension authors: ONLY specify testedwith = 'ships-with-hg-core' for
# extensions which SHIP WITH MERCURIAL. Non-mainline extensions should
# be specifying the version(s) of Mercurial they are tested with, or
# leave the attribute unspecified.
testedwith = 'ships-with-hg-core'

def _commitfiltered(repo, ctx, match, keepcommit):
    """Recommit ctx with changed files not in match. Return the new
    node identifier, or None if nothing changed.
    """
    base = ctx.p1()
    # ctx
    initialfiles = set(ctx.files())
    exclude = set(f for f in initialfiles if match(f))

    # No files matched commit, so nothing excluded
    if not exclude:
        return None

    # return the p1 so that we don't create an obsmarker later
    if not keepcommit:
        return ctx.p1().node()

    files = (initialfiles - exclude)
    # Filter copies
    copied = copiesmod.pathcopies(base, ctx)
    copied = dict((dst, src) for dst, src in copied.iteritems()
                  if dst in files)
    def filectxfn(repo, memctx, path, contentctx=ctx, redirect=()):
        if path not in contentctx:
            return None
        fctx = contentctx[path]
        mctx = context.memfilectx(repo, memctx, fctx.path(), fctx.data(),
                                  fctx.islink(),
                                  fctx.isexec(),
                                  copysource=copied.get(path))
        return mctx

    if not files:
        repo.ui.status(_("note: keeping empty commit\n"))

    new = context.memctx(repo,
                         parents=[base.node(), node.nullid],
                         text=ctx.description(),
                         files=files,
                         filectxfn=filectxfn,
                         user=ctx.user(),
                         date=ctx.date(),
                         extra=ctx.extra())
    return repo.commitctx(new)

@command('uncommit',
    [('', 'keep', None, _('allow an empty commit after uncommiting')),
     ('', 'allow-dirty-working-copy', False,
    _('allow uncommit with outstanding changes'))
    ] + commands.walkopts,
    _('[OPTION]... [FILE]...'),
    helpcategory=command.CATEGORY_CHANGE_MANAGEMENT)
def uncommit(ui, repo, *pats, **opts):
    """uncommit part or all of a local changeset

    This command undoes the effect of a local commit, returning the affected
    files to their uncommitted state. This means that files modified or
    deleted in the changeset will be left unchanged, and so will remain
    modified in the working directory.

    If no files are specified, the commit will be pruned, unless --keep is
    given.
    """
    opts = pycompat.byteskwargs(opts)

    with repo.wlock(), repo.lock():

        m, a, r, d = repo.status()[:4]
        isdirtypath = any(set(m + a + r + d) & set(pats))
        allowdirtywcopy = (opts['allow_dirty_working_copy'] or
                    repo.ui.configbool('experimental', 'uncommitondirtywdir'))
        if not allowdirtywcopy and (not pats or isdirtypath):
            cmdutil.bailifchanged(repo, hint=_('requires '
                                '--allow-dirty-working-copy to uncommit'))
        old = repo['.']
        rewriteutil.precheck(repo, [old.rev()], 'uncommit')
        if len(old.parents()) > 1:
            raise error.Abort(_("cannot uncommit merge changeset"))

        match = scmutil.match(old, pats, opts)

        # Check all explicitly given files; abort if there's a problem.
        if match.files():
            s = old.status(old.p1(), match, listclean=True)
            eligible = set(s.added) | set(s.modified) | set(s.removed)

            badfiles = set(match.files()) - eligible

            # Naming a parent directory of an eligible file is OK, even
            # if not everything tracked in that directory can be
            # uncommitted.
            if badfiles:
                badfiles -= {f for f in util.dirs(eligible)}

            for f in sorted(badfiles):
                if f in s.clean:
                    hint = _(b"file was not changed in working directory "
                             b"parent")
                elif repo.wvfs.exists(f):
                    hint = _(b"file was untracked in working directory parent")
                else:
                    hint = _(b"file does not exist")

                raise error.Abort(_(b'cannot uncommit "%s"')
                                  % scmutil.getuipathfn(repo)(f), hint=hint)

        with repo.transaction('uncommit'):
            keepcommit = pats
            if not keepcommit:
                if opts.get('keep') is not None:
                    keepcommit = opts.get('keep')
                else:
                    keepcommit = ui.configbool('experimental', 'uncommit.keep')
            newid = _commitfiltered(repo, old, match, keepcommit)
            if newid is None:
                ui.status(_("nothing to uncommit\n"))
                return 1

            mapping = {}
            if newid != old.p1().node():
                # Move local changes on filtered changeset
                mapping[old.node()] = (newid,)
            else:
                # Fully removed the old commit
                mapping[old.node()] = ()

            with repo.dirstate.parentchange():
                scmutil.movedirstate(repo, repo[newid], match)

            scmutil.cleanupnodes(repo, mapping, 'uncommit', fixphase=True)

def predecessormarkers(ctx):
    """yields the obsolete markers marking the given changeset as a successor"""
    for data in ctx.repo().obsstore.predecessors.get(ctx.node(), ()):
        yield obsutil.marker(ctx.repo(), data)

@command('unamend', [], helpcategory=command.CATEGORY_CHANGE_MANAGEMENT,
         helpbasic=True)
def unamend(ui, repo, **opts):
    """undo the most recent amend operation on a current changeset

    This command will roll back to the previous version of a changeset,
    leaving working directory in state in which it was before running
    `hg amend` (e.g. files modified as part of an amend will be
    marked as modified `hg status`)
    """

    unfi = repo.unfiltered()
    with repo.wlock(), repo.lock(), repo.transaction('unamend'):

        # identify the commit from which to unamend
        curctx = repo['.']

        rewriteutil.precheck(repo, [curctx.rev()], 'unamend')

        # identify the commit to which to unamend
        markers = list(predecessormarkers(curctx))
        if len(markers) != 1:
            e = _("changeset must have one predecessor, found %i predecessors")
            raise error.Abort(e % len(markers))

        prednode = markers[0].prednode()
        predctx = unfi[prednode]

        # add an extra so that we get a new hash
        # note: allowing unamend to undo an unamend is an intentional feature
        extras = predctx.extra()
        extras['unamend_source'] = curctx.hex()

        def filectxfn(repo, ctx_, path):
            try:
                return predctx.filectx(path)
            except KeyError:
                return None

        # Make a new commit same as predctx
        newctx = context.memctx(repo,
                                parents=(predctx.p1(), predctx.p2()),
                                text=predctx.description(),
                                files=predctx.files(),
                                filectxfn=filectxfn,
                                user=predctx.user(),
                                date=predctx.date(),
                                extra=extras)
        newprednode = repo.commitctx(newctx)
        newpredctx = repo[newprednode]
        dirstate = repo.dirstate

        with dirstate.parentchange():
            scmutil.movedirstate(repo, newpredctx)

        mapping = {curctx.node(): (newprednode,)}
        scmutil.cleanupnodes(repo, mapping, 'unamend', fixphase=True)
