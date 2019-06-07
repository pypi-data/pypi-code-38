# Module dedicated to host history rewriting commands
#
# Copyright 2017 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# Status: Stabilization of the API in progress
#
#   The final set of command should go into core.

from __future__ import absolute_import

import contextlib
import random

from mercurial import (
    bookmarks as bookmarksmod,
    cmdutil,
    commands,
    context,
    copies,
    error,
    hg,
    lock as lockmod,
    merge,
    node,
    obsolete,
    obsutil,
    patch,
    phases,
    scmutil,
    util,
)

from mercurial.i18n import _

try:
    from mercurial.utils.dateutil import datestr
except ImportError: # hg <= 4.5
    from mercurial.util import datestr

from . import (
    compat,
    state,
    exthelper,
    rewriteutil,
    utility,
)

eh = exthelper.exthelper()

walkopts = commands.walkopts
commitopts = commands.commitopts
commitopts2 = commands.commitopts2
mergetoolopts = commands.mergetoolopts
stringio = util.stringio

# option added by evolve

def _checknotesize(ui, opts):
    """ make sure note is of valid format """

    note = opts.get('note')
    if not note:
        return

    if not compat.isobsnotesupported():
        ui.warn(_("current hg version does not support storing"
                  " note in obsmarker\n"))
    if len(note) > 255:
        raise error.Abort(_("cannot store a note of more than 255 bytes"))
    if '\n' in note:
        raise error.Abort(_("note cannot contain a newline"))

def _resolveoptions(ui, opts):
    """modify commit options dict to handle related options

    For now, all it does is figure out the commit date: respect -D unless
    -d was supplied.
    """
    # N.B. this is extremely similar to setupheaderopts() in mq.py
    if not opts.get('date') and opts.get('current_date'):
        opts['date'] = '%d %d' % compat.makedate()
    if not opts.get('user') and opts.get('current_user'):
        opts['user'] = ui.username()

commitopts3 = [
    ('D', 'current-date', None,
     _('record the current date as commit date')),
    ('U', 'current-user', None,
     _('record the current user as committer')),
]

interactiveopt = [['i', 'interactive', None, _('use interactive mode')]]

@eh.command(
    'amend|refresh',
    [('A', 'addremove', None,
      _('mark new/missing files as added/removed before committing')),
     ('a', 'all', False, _("match all files")),
     ('e', 'edit', False, _('invoke editor on commit messages')),
     ('', 'extract', False, _('extract changes from the commit to the working copy')),
     ('', 'patch', False, _('make changes to wdir parent by editing patch')),
     ('', 'close-branch', None,
      _('mark a branch as closed, hiding it from the branch list')),
     ('s', 'secret', None, _('use the secret phase for committing')),
     ('n', 'note', '', _('store a note on amend'), _('TEXT')),
    ] + walkopts + commitopts + commitopts2 + commitopts3 + interactiveopt,
    _('[OPTION]... [FILE]...'),
    helpbasic=True)
def amend(ui, repo, *pats, **opts):
    """combine a changeset with updates and replace it with a new one

    Commits a new changeset incorporating both the changes to the given files
    and all the changes from the current parent changeset into the repository.

    See :hg:`commit` for details about committing changes.

    If you don't specify -m, the parent's message will be reused.

    If --extract is specified, the behavior of `hg amend` is reversed: Changes
    to selected files in the checked out revision appear again as uncommitted
    changed in the working directory.

    Returns 0 on success, 1 if nothing changed.
    """
    _checknotesize(ui, opts)
    opts = opts.copy()
    if opts.get('patch'):
        return amendpatch(ui, repo, *pats, **opts)
    if opts.get('extract'):
        return uncommit(ui, repo, *pats, **opts)
    else:
        if opts.pop('all', False):
            # add an include for all
            include = list(opts.get('include'))
            include.append('re:.*')
        edit = opts.pop('edit', False)
        log = opts.get('logfile')
        opts['amend'] = True
        _resolveoptions(ui, opts)
        _alias, commitcmd = cmdutil.findcmd('commit', commands.table)
        with repo.wlock(), repo.lock():
            if not (edit or opts['message'] or log):
                opts['message'] = repo['.'].description()
            rewriteutil.precheck(repo, [repo['.'].rev()], action='amend')
            return commitcmd[0](ui, repo, *pats, **opts)

def amendpatch(ui, repo, *pats, **opts):
    """logic for --patch flag of `hg amend` command."""
    with repo.wlock(), repo.lock(), repo.transaction('amend') as tr:
        cmdutil.bailifchanged(repo)
        # first get the patch
        old = repo['.']
        p1 = old.p1()
        rewriteutil.precheck(repo, [old.rev()], 'amend')
        diffopts = patch.difffeatureopts(repo.ui, whitespace=True)
        diffopts.nodates = True
        diffopts.git = True
        fp = stringio()
        _writectxmetadata(repo, old, fp)
        matcher = scmutil.match(old, pats, opts)
        for chunk, label in patch.diffui(repo, p1.node(), old.node(),
                                         match=matcher,
                                         opts=diffopts):
            fp.write(chunk)
        newnode = _editandapply(ui, repo, pats, old, p1, fp, diffopts)
        if newnode == old.node():
            raise error.Abort(_("nothing changed"))
        metadata = {}
        if opts.get('note'):
            metadata['note'] = opts['note']
        replacements = {old.node(): [newnode]}
        scmutil.cleanupnodes(repo, replacements, operation='amend',
                             metadata=metadata)
        phases.retractboundary(repo, tr, old.phase(), [newnode])
        hg.updaterepo(repo, newnode, True)

def _editandapply(ui, repo, pats, old, p1, fp, diffopts):
    newnode = None
    while newnode is None:
        fp.seek(0)
        previous_patch = fp.getvalue()
        if 5 <= len(ui.edit.im_func.func_defaults):
            newpatch = ui.edit(fp.getvalue(), old.user(), action="diff")
        else:
            newpatch = ui.edit(fp.getvalue(), old.user())

        afp = stringio()
        afp.write(newpatch)
        if pats:
            # write rest of the files in the patch
            restmatcher = scmutil.match(old, [], opts={'exclude': pats})
            for chunk, label in patch.diffui(repo, p1.node(), old.node(),
                                             match=restmatcher,
                                             opts=diffopts):
                afp.write(chunk)

        user_patch = afp.getvalue()
        if not user_patch:
            raise error.Abort(_("empty patch file, amend aborted"))
        if user_patch == previous_patch:
            raise error.Abort(_("patch unchanged"))
        afp.seek(0)
        # write the patch to repo and get the newnode
        try:
            newnode = _writepatch(ui, repo, old, afp)
        except patch.PatchError as err:
            ui.write_err(_("failed to apply edited patch: %s\n") % err)
            defaultchoice = 0 # yes
            if not ui.interactive:
                defaultchoice = 1 # no
            retrychoice = _('try to fix the patch (yn)?$$ &Yes $$ &No')
            if ui.promptchoice(retrychoice, default=defaultchoice):
                raise error.Abort(_("Could not apply amended path"))
            else:
                # consider a third choice where we restore the original patch
                fp = stringio()
                fp.write(user_patch)
    return newnode

def _writepatch(ui, repo, old, fp):
    """utility function to use filestore and patchrepo to apply a patch to the
    repository with metadata being extracted from the patch"""
    metadata = patch.extract(ui, fp)
    if util.safehasattr(metadata, 'get'): # < hg-4.6
        @contextlib.contextmanager
        def patchcontext():
            yield metadata
        patchcontext = patchcontext()
    else:
        patchcontext = metadata
    pold = old.p1()

    with patchcontext as metadata:
        # store the metadata from the patch to variables
        parents = (metadata.get('p1'), metadata.get('p2'))
        date = metadata.get('date') or old.date()
        branch = metadata.get('branch') or old.branch()
        user = metadata.get('user') or old.user()
        # XXX: we must extract extras from the patchfile too
        extra = old.extra()
        message = metadata.get('message') or old.description()
        store = patch.filestore()
        fp.seek(0)
        try:
            files = set()
            # beware: next line may raise a PatchError to be handled by the caller
            # of this function
            patch.patchrepo(ui, repo, pold, store, fp, 1, '',
                            files=files, eolmode=None)

            memctx = context.memctx(repo, parents, message, files=files,
                                    filectxfn=store,
                                    user=user,
                                    date=date,
                                    branch=branch,
                                    extra=extra)
            newcm = memctx.commit()
        finally:
            store.close()
    return newcm

def _writectxmetadata(repo, ctx, fp):
    nodeval = scmutil.binnode(ctx)
    parents = [p.node() for p in ctx.parents() if p]
    branch = ctx.branch()
    if parents:
        prev = parents[0]
    else:
        prev = node.nullid

    fp.write("# HG changeset patch\n")
    fp.write("# User %s\n" % ctx.user())
    fp.write("# Date %d %d\n" % ctx.date())
    fp.write("#      %s\n" % datestr(ctx.date()))
    if branch and branch != 'default':
        fp.write("# Branch %s\n" % branch)
    fp.write("# Node ID %s\n" % node.hex(nodeval))
    fp.write("# Parent  %s\n" % node.hex(prev))
    if len(parents) > 1:
        fp.write("# Parent  %s\n" % node.hex(parents[1]))

    for headerid in cmdutil.extraexport:
        header = cmdutil.extraexportmap[headerid](1, ctx)
        if header is not None:
            fp.write('# %s\n' % header)
    fp.write(ctx.description().rstrip())
    fp.write("\n\n")

def _touchedbetween(repo, source, dest, match=None):
    touched = set()
    for files in repo.status(source, dest, match=match)[:3]:
        touched.update(files)
    return touched

def _commitfiltered(repo, ctx, match, target=None, message=None, user=None,
                    date=None):
    """Recommit ctx with changed files not in match. Return the new
    node identifier, or None if nothing changed.
    """
    base = ctx.p1()
    if target is None:
        target = base
    # ctx
    initialfiles = _touchedbetween(repo, base, ctx)
    if base == target:
        affected = set(f for f in initialfiles if match(f))
        newcontent = set()
    else:
        affected = _touchedbetween(repo, target, ctx, match=match)
        newcontent = _touchedbetween(repo, target, base, match=match)
    # The commit touchs all existing files
    # + all file that needs a new content
    # - the file affected bny uncommit with the same content than base.
    files = (initialfiles - affected) | newcontent
    if not newcontent and files == initialfiles:
        return None

    # Filter copies
    copied = copies.pathcopies(target, ctx)
    copied = dict((dst, src) for dst, src in copied.iteritems()
                  if dst in files)

    def filectxfn(repo, memctx, path, contentctx=ctx, redirect=newcontent):
        if path in redirect:
            return filectxfn(repo, memctx, path, contentctx=target, redirect=())
        if path not in contentctx:
            return None
        fctx = contentctx[path]
        flags = fctx.flags()
        mctx = compat.memfilectx(repo, memctx, fctx, flags, copied, path)
        return mctx

    if message is None:
        message = ctx.description()
    if not user:
        user = ctx.user()
    if not date:
        date = ctx.date()
    new = context.memctx(repo,
                         parents=[base.node(), node.nullid],
                         text=message,
                         files=files,
                         filectxfn=filectxfn,
                         user=user,
                         date=date,
                         extra=ctx.extra())
    # commitctx always create a new revision, no need to check
    newid = repo.commitctx(new)
    return newid

def _uncommitdirstate(repo, oldctx, match, interactive):
    """Fix the dirstate after switching the working directory from
    oldctx to a copy of oldctx not containing changed files matched by
    match.
    """
    ctx = repo['.']
    ds = repo.dirstate
    copies = dict(ds.copies())
    if interactive:
        # In interactive cases, we will find the status between oldctx and ctx
        # and considering only the files which are changed between oldctx and
        # ctx, and the status of what changed between oldctx and ctx will help
        # us in defining the exact behavior
        m, a, r = repo.status(oldctx, ctx, match=match)[:3]
        for f in m:
            # These are files which are modified between oldctx and ctx which
            # contains two cases: 1) Were modified in oldctx and some
            # modifications are uncommitted
            # 2) Were added in oldctx but some part is uncommitted (this cannot
            # contain the case when added files are uncommitted completely as
            # that will result in status as removed not modified.)
            # Also any modifications to a removed file will result the status as
            # added, so we have only two cases. So in either of the cases, the
            # resulting status can be modified or clean.
            if ds[f] == 'r':
                # But the file is removed in the working directory, leaving that
                # as removed
                continue
            ds.normallookup(f)

        for f in a:
            # These are the files which are added between oldctx and ctx(new
            # one), which means the files which were removed in oldctx
            # but uncommitted completely while making the ctx
            # This file should be marked as removed if the working directory
            # does not adds it back. If it's adds it back, we do a normallookup.
            # The file can't be removed in working directory, because it was
            # removed in oldctx
            if ds[f] == 'a':
                ds.normallookup(f)
                continue
            ds.remove(f)

        for f in r:
            # These are files which are removed between oldctx and ctx, which
            # means the files which were added in oldctx and were completely
            # uncommitted in ctx. If a added file is partially uncommitted, that
            # would have resulted in modified status, not removed.
            # So a file added in a commit, and uncommitting that addition must
            # result in file being stated as unknown.
            if ds[f] == 'r':
                # The working directory say it's removed, so lets make the file
                # unknown
                ds.drop(f)
                continue
            ds.add(f)
    else:
        m, a, r = repo.status(oldctx.p1(), oldctx, match=match)[:3]
        for f in m:
            if ds[f] == 'r':
                # modified + removed -> removed
                continue
            ds.normallookup(f)

        for f in a:
            if ds[f] == 'r':
                # added + removed -> unknown
                ds.drop(f)
            elif ds[f] != 'a':
                ds.add(f)

        for f in r:
            if ds[f] == 'a':
                # removed + added -> normal
                ds.normallookup(f)
            elif ds[f] != 'r':
                ds.remove(f)

    # Merge old parent and old working dir copies
    oldcopies = {}
    if interactive:
        # Interactive had different meaning of the variables so restoring the
        # original meaning to use them
        m, a, r = repo.status(oldctx.p1(), oldctx, match=match)[:3]
    for f in (m + a):
        src = oldctx[f].renamed()
        if src:
            oldcopies[f] = src[0]
    oldcopies.update(copies)
    copies = dict((dst, oldcopies.get(src, src))
                  for dst, src in oldcopies.iteritems())
    # Adjust the dirstate copies
    for dst, src in copies.iteritems():
        if (src not in ctx or dst in ctx or ds[dst] != 'a'):
            src = None
        ds.copy(src, dst)

@eh.command(
    'uncommit',
    [('a', 'all', None, _('uncommit all changes when no arguments given')),
     ('i', 'interactive', False, _('interactive mode to uncommit (EXPERIMENTAL)')),
     ('r', 'rev', '', _('revert commit content to REV instead'), _('REV')),
     ('', 'revert', False, _('discard working directory changes after uncommit')),
     ('n', 'note', '', _('store a note on uncommit'), _('TEXT')),
     ] + commands.walkopts + commitopts + commitopts2 + commitopts3,
    _('[OPTION]... [NAME]'))
def uncommit(ui, repo, *pats, **opts):
    """move changes from parent revision to working directory

    Changes to selected files in the checked out revision appear again as
    uncommitted changed in the working directory. A new revision
    without the selected changes is created, becomes the checked out
    revision, and obsoletes the previous one.

    The --include option specifies patterns to uncommit.
    The --exclude option specifies patterns to keep in the commit.

    The --rev argument let you change the commit file to a content of another
    revision. It still does not change the content of your file in the working
    directory.

    .. container:: verbose

       The --interactive option lets you select hunks interactively to uncommit.
       You can uncommit parts of file using this option.

    Return 0 if changed files are uncommitted.
    """

    _checknotesize(ui, opts)
    _resolveoptions(ui, opts) # process commitopts3
    interactive = opts.get('interactive')
    wlock = lock = tr = None
    try:
        wlock = repo.wlock()
        lock = repo.lock()
        wctx = repo[None]
        if len(wctx.parents()) <= 0:
            raise error.Abort(_("cannot uncommit null changeset"))
        if len(wctx.parents()) > 1:
            raise error.Abort(_("cannot uncommit while merging"))
        old = repo['.']
        rewriteutil.precheck(repo, [repo['.'].rev()], action='uncommit')
        if len(old.parents()) > 1:
            raise error.Abort(_("cannot uncommit merge changeset"))
        oldphase = old.phase()

        rev = None
        if opts.get('rev'):
            rev = scmutil.revsingle(repo, opts.get('rev'))
            ctx = repo[None]
            if ctx.p1() == rev or ctx.p2() == rev:
                raise error.Abort(_("cannot uncommit to parent changeset"))

        onahead = old.rev() in repo.changelog.headrevs()
        disallowunstable = not obsolete.isenabled(repo,
                                                  obsolete.allowunstableopt)
        if disallowunstable and not onahead:
            raise error.Abort(_("cannot uncommit in the middle of a stack"))

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
                badfiles -= set([f for f in util.dirs(eligible)])

            try:
                uipathfn = scmutil.getuipathfn(repo)
            except AttributeError:
                uipathfn = match.rel   # <= 4.9

            for f in sorted(badfiles):
                if f in s.clean:
                    hint = _(b"file was not changed in working directory "
                             b"parent")
                elif repo.wvfs.exists(f):
                    hint = _(b"file was untracked in working directory parent")
                else:
                    hint = _(b"file does not exist")

                raise error.Abort(_(b'cannot uncommit "%s"')
                                  % uipathfn(f), hint=hint)

        # Recommit the filtered changeset
        tr = repo.transaction('uncommit')
        if interactive:
            opts['all'] = True
            newid = _interactiveuncommit(ui, repo, old, match)
        else:
            newid = None
            includeorexclude = opts.get('include') or opts.get('exclude')
            if (pats or includeorexclude or opts.get('all')):
                if not (opts['message'] or opts['logfile']):
                    opts['message'] = old.description()
                message = cmdutil.logmessage(ui, opts)
                newid = _commitfiltered(repo, old, match, target=rev,
                                        message=message, user=opts.get('user'),
                                        date=opts.get('date'))
            if newid is None:
                raise error.Abort(_('nothing to uncommit'),
                                  hint=_("use --all to uncommit all files"))

        # metadata to be stored in obsmarker
        metadata = {}
        if opts.get('note'):
            metadata['note'] = opts['note']

        replacements = {old.node(): [newid]}
        scmutil.cleanupnodes(repo, replacements, operation="uncommit",
                             metadata=metadata)
        phases.retractboundary(repo, tr, oldphase, [newid])
        if opts.get('revert'):
            hg.updaterepo(repo, newid, True)
        else:
            with repo.dirstate.parentchange():
                repo.dirstate.setparents(newid, node.nullid)
                _uncommitdirstate(repo, old, match, interactive)
        if not repo[newid].files():
            ui.warn(_("new changeset is empty\n"))
            ui.status(_("(use 'hg prune .' to remove it)\n"))
        tr.close()
    finally:
        lockmod.release(tr, lock, wlock)

def _interactiveuncommit(ui, repo, old, match):
    """ The function which contains all the logic for interactively uncommiting
    a commit. This function makes a temporary commit with the chunks which user
    selected to uncommit. After that the diff of the parent and that commit is
    applied to the working directory and committed again which results in the
    new commit which should be one after uncommitted.
    """

    # create a temporary commit with hunks user selected
    tempnode = _createtempcommit(ui, repo, old, match)

    diffopts = patch.difffeatureopts(repo.ui, whitespace=True)
    diffopts.nodates = True
    diffopts.git = True
    fp = stringio()
    for chunk, label in patch.diffui(repo, tempnode, old.node(), None,
                                     opts=diffopts):
        fp.write(chunk)

    fp.seek(0)
    newnode = _patchtocommit(ui, repo, old, fp)
    # creating obs marker temp -> ()
    obsolete.createmarkers(repo, [(repo[tempnode], ())], operation="uncommit")
    return newnode

def _createtempcommit(ui, repo, old, match):
    """ Creates a temporary commit for `uncommit --interative` which contains
    the hunks which were selected by the user to uncommit.
    """

    pold = old.p1()
    # The logic to interactively selecting something copied from
    # cmdutil.revert()
    diffopts = patch.difffeatureopts(repo.ui, whitespace=True)
    diffopts.nodates = True
    diffopts.git = True
    diff = patch.diff(repo, pold.node(), old.node(), match, opts=diffopts)
    originalchunks = patch.parsepatch(diff)
    # XXX: The interactive selection is buggy and does not let you
    # uncommit a removed file partially.
    # TODO: wrap the operations in mercurial/patch.py and mercurial/crecord.py
    # to add uncommit as an operation taking care of BC.
    try:
        chunks, opts = cmdutil.recordfilter(repo.ui, originalchunks, match,
                                            operation='discard')
    except TypeError:
        # hg <= 4.9 (db72f9f6580e)
        chunks, opts = cmdutil.recordfilter(repo.ui, originalchunks,
                                            operation='discard')
    if not chunks:
        raise error.Abort(_("nothing selected to uncommit"))
    fp = stringio()
    for c in chunks:
        c.write(fp)

    fp.seek(0)
    oldnode = node.hex(old.node())[:12]
    message = 'temporary commit for uncommiting %s' % oldnode
    tempnode = _patchtocommit(ui, repo, old, fp, message, oldnode)
    return tempnode

def _patchtocommit(ui, repo, old, fp, message=None, extras=None):
    """ A function which will apply the patch to the working directory and
    make a commit whose parents are same as that of old argument. The message
    argument tells us whether to use the message of the old commit or a
    different message which is passed. Returns the node of new commit made.
    """
    pold = old.p1()
    parents = (old.p1().node(), old.p2().node())
    date = old.date()
    branch = old.branch()
    user = old.user()
    extra = old.extra()
    if extras:
        extra['uncommit_source'] = extras
    if not message:
        message = old.description()
    store = patch.filestore()
    try:
        files = set()
        try:
            patch.patchrepo(ui, repo, pold, store, fp, 1, '',
                            files=files, eolmode=None)
        except patch.PatchError as err:
            raise error.Abort(str(err))

        finally:
            del fp

        memctx = context.memctx(repo, parents, message, files=files,
                                filectxfn=store,
                                user=user,
                                date=date,
                                branch=branch,
                                extra=extra)
        newcm = memctx.commit()
    finally:
        store.close()
    return newcm

@eh.command(
    'fold|squash',
    [('r', 'rev', [], _("revision to fold"), _('REV')),
     ('', 'exact', None, _("only fold specified revisions")),
     ('', 'from', None, _("fold revisions linearly to working copy parent")),
     ('n', 'note', '', _('store a note on fold'), _('TEXT')),
    ] + commitopts + commitopts2 + commitopts3,
    _('hg fold [OPTION]... [-r] REV'),
    helpbasic=True)
def fold(ui, repo, *revs, **opts):
    """fold multiple revisions into a single one

    With --from, folds all the revisions linearly between the given revisions
    and the parent of the working directory.

    With --exact, folds only the specified revisions while ignoring the
    parent of the working directory. In this case, the given revisions must
    form a linear unbroken chain.

    .. container:: verbose

     Some examples:

     - Fold the current revision with its parent::

         hg fold --from .^

     - Fold all draft revisions with working directory parent::

         hg fold --from 'draft()'

       See :hg:`help phases` for more about draft revisions and
       :hg:`help revsets` for more about the `draft()` keyword

     - Fold revisions between 3 and 6 with the working directory parent::

         hg fold --from 3::6

     - Fold revisions 3 and 4::

        hg fold "3 + 4" --exact

     - Only fold revisions linearly between foo and @::

         hg fold foo::@ --exact
    """
    _checknotesize(ui, opts)
    _resolveoptions(ui, opts)
    revs = list(revs)
    revs.extend(opts['rev'])
    if not revs:
        raise error.Abort(_('no revisions specified'))

    revs = scmutil.revrange(repo, revs)

    if opts['from'] and opts['exact']:
        raise error.Abort(_('cannot use both --from and --exact'))
    elif opts['from']:
        # Try to extend given revision starting from the working directory
        extrevs = repo.revs('(%ld::.) or (.::%ld)', revs, revs)
        discardedrevs = [r for r in revs if r not in extrevs]
        if discardedrevs:
            msg = _("cannot fold non-linear revisions")
            hint = _("given revisions are unrelated to parent of working"
                     " directory")
            raise error.Abort(msg, hint=hint)
        revs = extrevs
    elif opts['exact']:
        # Nothing to do; "revs" is already set correctly
        pass
    else:
        raise error.Abort(_('must specify either --from or --exact'))

    if not revs:
        raise error.Abort(_('specified revisions evaluate to an empty set'),
                          hint=_('use different revision arguments'))
    elif len(revs) == 1:
        ui.write_err(_('single revision specified, nothing to fold\n'))
        return 1

    # Sort so combined commit message of `hg fold --exact -r . -r .^` is
    # in topological order.
    revs.sort()

    wlock = lock = None
    try:
        wlock = repo.wlock()
        lock = repo.lock()

        root, head = rewriteutil.foldcheck(repo, revs)

        tr = repo.transaction('fold')
        try:
            commitopts = opts.copy()
            allctx = [repo[r] for r in revs]
            targetphase = max(c.phase() for c in allctx)

            if commitopts.get('message') or commitopts.get('logfile'):
                commitopts['edit'] = False
            else:
                msgs = ["HG: This is a fold of %d changesets." % len(allctx)]
                msgs += ["HG: Commit message of changeset %s.\n\n%s\n" %
                         (c.rev(), c.description()) for c in allctx]
                commitopts['message'] = "\n".join(msgs)
                commitopts['edit'] = True

            metadata = {}
            if opts.get('note'):
                metadata['note'] = opts['note']

            newid, unusedvariable = rewriteutil.rewrite(repo, root, allctx,
                                                        head,
                                                        [root.p1().node(),
                                                         root.p2().node()],
                                                        commitopts=commitopts)
            phases.retractboundary(repo, tr, targetphase, [newid])
            replacements = {ctx.node(): [newid] for ctx in allctx}
            scmutil.cleanupnodes(repo, replacements, operation="fold",
                                 metadata=metadata)
            tr.close()
        finally:
            tr.release()
        ui.status('%i changesets folded\n' % len(revs))
        if repo['.'].rev() in revs:
            hg.update(repo, newid)
    finally:
        lockmod.release(lock, wlock)

@eh.command(
    'metaedit',
    [('r', 'rev', [], _("revision to edit"), _('REV')),
     ('', 'fold', None, _("also fold specified revisions into one")),
     ('n', 'note', '', _('store a note on metaedit'), _('TEXT')),
    ] + commitopts + commitopts2 + commitopts3,
    _('hg metaedit [OPTION]... [-r] [REV]'))
def metaedit(ui, repo, *revs, **opts):
    """edit commit information

    Edits the commit information for the specified revisions. By default, edits
    commit information for the working directory parent.

    With --fold, also folds multiple revisions into one if necessary. In this
    case, the given revisions must form a linear unbroken chain.

    .. container:: verbose

     Some examples:

     - Edit the commit message for the working directory parent::

         hg metaedit

     - Change the username for the working directory parent::

         hg metaedit --user 'New User <new-email@example.com>'

     - Combine all draft revisions that are ancestors of foo but not of @ into
       one::

         hg metaedit --fold 'draft() and only(foo,@)'

       See :hg:`help phases` for more about draft revisions, and
       :hg:`help revsets` for more about the `draft()` and `only()` keywords.
    """
    _checknotesize(ui, opts)
    _resolveoptions(ui, opts)
    revs = list(revs)
    revs.extend(opts['rev'])
    if not revs:
        if opts['fold']:
            raise error.Abort(_('revisions must be specified with --fold'))
        revs = ['.']

    with repo.wlock(), repo.lock():
        revs = scmutil.revrange(repo, revs)
        if not opts['fold'] and len(revs) > 1:
            # TODO: handle multiple revisions. This is somewhat tricky because
            # if we want to edit a series of commits:
            #
            #   a ---- b ---- c
            #
            # we need to rewrite a first, then directly rewrite b on top of the
            # new a, then rewrite c on top of the new b. So we need to handle
            # revisions in topological order.
            raise error.Abort(_('editing multiple revisions without --fold is '
                                'not currently supported'))

        if opts['fold']:
            root, head = rewriteutil.foldcheck(repo, revs)
        else:
            if repo.revs("%ld and public()", revs):
                raise error.Abort(_('cannot edit commit information for public '
                                    'revisions'))
            newunstable = rewriteutil.disallowednewunstable(repo, revs)
            if newunstable:
                msg = _('cannot edit commit information in the middle'
                        ' of a stack')
                hint = _('%s will become unstable and new unstable changes'
                         ' are not allowed')
                hint %= repo[newunstable.first()]
                raise error.Abort(msg, hint=hint)
            root = head = repo[revs.first()]

        wctx = repo[None]
        p1 = wctx.p1()
        tr = repo.transaction('metaedit')
        newp1 = None
        try:
            commitopts = opts.copy()
            allctx = [repo[r] for r in revs]
            targetphase = max(c.phase() for c in allctx)

            if commitopts.get('message') or commitopts.get('logfile'):
                commitopts['edit'] = False
            else:
                if opts['fold']:
                    msgs = ["HG: This is a fold of %d changesets." % len(allctx)]
                    msgs += ["HG: Commit message of changeset %s.\n\n%s\n" %
                             (c.rev(), c.description()) for c in allctx]
                else:
                    msgs = [head.description()]
                commitopts['message'] = "\n".join(msgs)
                commitopts['edit'] = True

            # TODO: if the author and message are the same, don't create a new
            # hash. Right now we create a new hash because the date can be
            # different.
            newid, created = rewriteutil.rewrite(repo, root, allctx, head,
                                                 [root.p1().node(),
                                                  root.p2().node()],
                                                 commitopts=commitopts)
            if created:
                if p1.rev() in revs:
                    newp1 = newid
                # metadata to be stored on obsmarker
                metadata = {}
                if opts.get('note'):
                    metadata['note'] = opts['note']

                phases.retractboundary(repo, tr, targetphase, [newid])
                obsolete.createmarkers(repo, [(ctx, (repo[newid],))
                                              for ctx in allctx],
                                       metadata=metadata, operation="metaedit")
            else:
                ui.status(_("nothing changed\n"))
            tr.close()
        finally:
            tr.release()

        if opts['fold']:
            ui.status('%i changesets folded\n' % len(revs))
        if newp1 is not None:
            hg.update(repo, newp1)

metadataopts = [
    ('d', 'date', '',
     _('record the specified date in metadata'), _('DATE')),
    ('u', 'user', '',
     _('record the specified user in metadata'), _('USER')),
]

def _getmetadata(**opts):
    metadata = {}
    date = opts.get('date')
    user = opts.get('user')
    if date:
        metadata['date'] = '%i %i' % compat.parsedate(date)
    if user:
        metadata['user'] = user
    return metadata

@eh.command(
    'prune|obsolete',
    [('n', 'new', [], _("successor changeset (DEPRECATED)")),
     ('s', 'succ', [], _("successor changeset"), _('REV')),
     ('r', 'rev', [], _("revisions to prune"), _('REV')),
     ('k', 'keep', None, _("does not modify working copy during prune")),
     ('n', 'note', '', _('store a note on prune'), _('TEXT')),
     ('', 'pair', False, _("record a pairing, such as a rebase or divergence resolution "
                           "(pairing multiple precursors to multiple successors)")),
     ('', 'biject', False, _("alias to --pair (DEPRECATED)")),
     ('', 'fold', False,
      _("record a fold (multiple precursors, one successors)")),
     ('', 'split', False,
      _("record a split (on precursor, multiple successors)")),
     ('B', 'bookmark', [], _("remove revs only reachable from given"
                             " bookmark"), _('BOOKMARK'))] + metadataopts,
    _('[OPTION] [-r] REV...'),
    helpbasic=True)
# XXX -U  --noupdate option to prevent wc update and or bookmarks update ?
def cmdprune(ui, repo, *revs, **opts):
    """mark changesets as obsolete or succeeded by another changeset

    Pruning changesets marks them obsolete, hiding them from the
    history log, provided they have no descendants. Otherwise, all
    such descendants that aren't themselves obsolete become
    "unstable". Use :hg:`evolve` to handle this situation.

    When you prune the parent of your working copy, Mercurial updates the working
    copy to a non-obsolete parent.

    You can use ``-s/--succ`` to tell Mercurial that a newer version (successor) of the
    pruned changeset exists. Mercurial records successor revisions in obsolescence
    markers.

    If you prune a single revision and specify multiple revisions in
    ``-s/--succ``, you are recording a "split" and must acknowledge it by
    passing ``--split``. Similarly, when you prune multiple changesets with a
    single successor, you must pass the ``--fold`` option.

    If you want to supersede multiple revisions at the same time, use
    ``--pair`` option to pair the pruned precursor and successor changesets.
    This is commonly useful for resolving history divergence, or when someone
    else does edits history without obsolescence enabled.
    """
    _checknotesize(ui, opts)
    revs = scmutil.revrange(repo, list(revs) + opts.get('rev'))
    succs = opts['new'] + opts['succ']
    bookmarks = set(opts.get('bookmark'))
    metadata = _getmetadata(**opts)
    biject = opts.get('pair') or opts.get('biject')
    fold = opts.get('fold')
    split = opts.get('split')

    options = [o for o in ('pair', 'fold', 'split') if opts.get(o)]
    if 1 < len(options):
        raise error.Abort(_("can only specify one of %s") % ', '.join(options))

    if bookmarks:
        reachablefrombookmark = rewriteutil.reachablefrombookmark
        repomarks, revs = reachablefrombookmark(repo, revs, bookmarks)
        if not revs:
            # no revisions to prune - delete bookmark immediately
            rewriteutil.deletebookmark(repo, repomarks, bookmarks)

    if not revs:
        raise error.Abort(_('nothing to prune'))

    wlock = lock = tr = None
    try:
        wlock = repo.wlock()
        lock = repo.lock()
        rewriteutil.precheck(repo, revs, 'prune')
        tr = repo.transaction('prune')
        # defines pruned changesets
        precs = []
        revs.sort()
        for p in revs:
            cp = repo[p]
            precs.append(cp)
        if not precs:
            raise error.Abort('nothing to prune')

        # defines successors changesets
        sucs = scmutil.revrange(repo, succs)
        sucs.sort()
        sucs = tuple(repo[n] for n in sucs)
        if not biject and len(sucs) > 1 and len(precs) > 1:
            msg = "Can't use multiple successors for multiple precursors"
            hint = _("use --pair to mark a series as a replacement"
                     " for another")
            raise error.Abort(msg, hint=hint)
        elif biject and len(sucs) != len(precs):
            msg = "Can't use %d successors for %d precursors" \
                % (len(sucs), len(precs))
            raise error.Abort(msg)
        elif (len(precs) == 1 and len(sucs) > 1) and not split:
            msg = "please add --split if you want to do a split"
            raise error.Abort(msg)
        elif len(sucs) == 1 and len(precs) > 1 and not fold:
            msg = "please add --fold if you want to do a fold"
            raise error.Abort(msg)
        elif biject:
            replacements = {p.node(): [s.node()] for p, s in zip(precs, sucs)}
        else:
            replacements = {p.node(): [s.node() for s in sucs] for p in precs}

        wdp = repo['.']

        if len(sucs) == 1 and len(precs) == 1 and wdp in precs:
            # '.' killed, so update to the successor
            newnode = sucs[0]
        else:
            # update to an unkilled parent
            newnode = wdp

            while newnode in precs or newnode.obsolete():
                newnode = newnode.parents()[0]

        if newnode.node() != wdp.node():
            if opts.get('keep', False):
                # This is largely the same as the implementation in
                # strip.stripcmd(). We might want to refactor this somewhere
                # common at some point.

                # only reset the dirstate for files that would actually change
                # between the working context and uctx
                descendantrevs = repo.revs("%d::." % newnode.rev())
                changedfiles = []
                for rev in descendantrevs:
                    # blindly reset the files, regardless of what actually
                    # changed
                    changedfiles.extend(repo[rev].files())

                # reset files that only changed in the dirstate too
                dirstate = repo.dirstate
                dirchanges = [f for f in dirstate if dirstate[f] != 'n']
                changedfiles.extend(dirchanges)
                repo.dirstate.rebuild(newnode.node(), newnode.manifest(),
                                      changedfiles)
                dirstate.write(tr)
            else:
                bookactive = repo._activebookmark
                # Active bookmark that we don't want to delete (with -B option)
                # we deactivate and move it before the update and reactivate it
                # after
                movebookmark = bookactive and not bookmarks
                if movebookmark:
                    bookmarksmod.deactivate(repo)
                    bmchanges = [(bookactive, newnode.node())]
                    repo._bookmarks.applychanges(repo, tr, bmchanges)
                commands.update(ui, repo, newnode.hex())
                ui.status(_('working directory is now at %s\n')
                          % ui.label(str(newnode), 'evolve.node'))
                if movebookmark:
                    bookmarksmod.activate(repo, bookactive)

        # update bookmarks
        if bookmarks:
            rewriteutil.deletebookmark(repo, repomarks, bookmarks)

        # store note in metadata
        if opts.get('note'):
            metadata['note'] = opts['note']

        precrevs = (precursor.rev() for precursor in precs)
        moves = {}
        for ctx in repo.unfiltered().set('bookmark() and %ld', precrevs):
            # used to be:
            #
            #   ldest = list(repo.set('max((::%d) - obsolete())', ctx))
            #   if ldest:
            #      c = ldest[0]
            #
            # but then revset took a lazy arrow in the knee and became much
            # slower. The new forms makes as much sense and a much faster.
            for dest in ctx.ancestors():
                if not dest.obsolete() and dest.node() not in replacements:
                    moves[ctx.node()] = dest.node()
                    break
        scmutil.cleanupnodes(repo, replacements, operation="prune", moves=moves,
                             metadata=metadata)

        # informs that changeset have been pruned
        ui.status(_('%i changesets pruned\n') % len(precs))

        tr.close()
    finally:
        lockmod.release(tr, lock, wlock)

@eh.command(
    'split',
    [('i', 'interactive', True, _('use interactive mode')),
     ('r', 'rev', [], _("revision to split"), _('REV')),
     ('n', 'note', '', _("store a note on split"), _('TEXT')),
    ] + commitopts + commitopts2 + commitopts3,
    _('hg split [OPTION] [-r REV] [FILES]'),
    helpbasic=True)
def cmdsplit(ui, repo, *pats, **opts):
    """split a changeset into smaller changesets

    By default, split the current revision by prompting for all its hunks to be
    redistributed into new changesets.

    Use --rev to split a given changeset instead.

    If file patterns are specified only files matching these patterns will be
    considered to be split in earlier changesets. The files that doesn't match
    will be gathered in the last changeset.
    """
    _checknotesize(ui, opts)
    _resolveoptions(ui, opts)
    tr = wlock = lock = None
    newcommits = []
    iselect = opts.pop('interactive')

    revs = opts.get('rev') or '.'
    if not revs:
        revarg = '.'
    elif len(revs) == 1:
        revarg = revs[0]
    else:
        # XXX --rev often accept multiple value, it seems safer to explicitly
        # complains here instead of just taking the last value.
        raise error.Abort(_('more than one revset is given'))

    # Save the current branch to restore it in the end
    savedbranch = repo.dirstate.branch()

    try:
        wlock = repo.wlock()
        lock = repo.lock()
        ctx = scmutil.revsingle(repo, revarg)
        rev = ctx.rev()
        cmdutil.bailifchanged(repo)
        rewriteutil.precheck(repo, [rev], action='split')
        tr = repo.transaction('split')
        # make sure we respect the phase while splitting
        overrides = {('phases', 'new-commit'): ctx.phase()}

        if len(ctx.parents()) > 1:
            raise error.Abort(_("cannot split merge commits"))
        prev = ctx.p1()
        bmupdate = rewriteutil.bookmarksupdater(repo, ctx.node(), tr)
        bookactive = repo._activebookmark
        if bookactive is not None:
            repo.ui.status(_("(leaving bookmark %s)\n") % repo._activebookmark)
        bookmarksmod.deactivate(repo)

        # Prepare the working directory
        rewriteutil.presplitupdate(repo, ui, prev, ctx)

        def haschanges(matcher=None):
            modified, added, removed, deleted = repo.status(match=matcher)[:4]
            return modified or added or removed or deleted
        msg = ("HG: This is the original pre-split commit message. "
               "Edit it as appropriate.\n\n")
        msg += ctx.description()
        opts['message'] = msg
        opts['edit'] = True
        if not opts['user']:
            opts['user'] = ctx.user()

        # Set the right branch
        # XXX-TODO: Find a way to set the branch without altering the dirstate
        repo.dirstate.setbranch(ctx.branch())

        if pats:
            # refresh the wctx used for the matcher
            matcher = scmutil.match(repo[None], pats)
        else:
            matcher = scmutil.matchall(repo)

        while haschanges():

            if haschanges(matcher):
                if iselect:
                    with repo.ui.configoverride(overrides, 'split'):
                        cmdutil.dorecord(ui, repo, commands.commit, 'commit',
                                         False, cmdutil.recordfilter, *pats,
                                         **opts)
                    # TODO: Does no seem like the best way to do this
                    # We should make dorecord return the newly created commit
                    newcommits.append(repo['.'])
                elif not pats:
                    msg = _("no files of directories specified")
                    hint = _("do you want --interactive")
                    raise error.Abort(msg, hint=hint)
                else:
                    with repo.ui.configoverride(overrides, 'split'):
                        commands.commit(ui, repo, *pats, **opts)
                    newcommits.append(repo['.'])
            if pats:
                # refresh the wctx used for the matcher
                matcher = scmutil.match(repo[None], pats)
            else:
                matcher = scmutil.matchall(repo)

            if haschanges(matcher):
                nextaction = None
                while nextaction is None:
                    nextaction = ui.prompt('continue splitting? [Ycdq?]', default='y')
                    if nextaction == 'c':
                        with repo.ui.configoverride(overrides, 'split'):
                            commands.commit(ui, repo, **opts)
                        newcommits.append(repo['.'])
                        break
                    elif nextaction == 'q':
                        raise error.Abort(_('user quit'))
                    elif nextaction == 'd':
                        # TODO: We should offer a way for the user to confirm
                        # what is the remaining changes, either via a separate
                        # diff action or by showing the remaining and
                        # prompting for confirmation
                        ui.status(_('discarding remaining changes\n'))
                        target = newcommits[0]
                        if pats:
                            status = repo.status(match=matcher)[:4]
                            dirty = set()
                            for i in status:
                                dirty.update(i)
                            dirty = sorted(dirty)
                            cmdutil.revert(ui, repo, repo[target],
                                           (target, node.nullid), *dirty)
                        else:
                            cmdutil.revert(ui, repo, repo[target],
                                           (target, node.nullid), all=True)
                    elif nextaction == '?':
                        nextaction = None
                        ui.write(_("y - yes, continue selection\n"))
                        ui.write(_("c - commit, select all remaining changes\n"))
                        ui.write(_("d - discard, discard remaining changes\n"))
                        ui.write(_("q - quit, abort the split\n"))
                        ui.write(_("? - ?, display help\n"))
                else:
                    continue
                break # propagate the previous break
            else:
                ui.status(_("no more change to split\n"))
                if haschanges():
                    # XXX: Should we show a message for informing the user
                    # that we create another commit with remaining changes?
                    with repo.ui.configoverride(overrides, 'split'):
                        commands.commit(ui, repo, **opts)
                    newcommits.append(repo['.'])
        if newcommits:
            tip = repo[newcommits[-1]]
            bmupdate(tip.node())
            if bookactive is not None:
                bookmarksmod.activate(repo, bookactive)
            metadata = {}
            if opts.get('note'):
                metadata['note'] = opts['note']
            obsolete.createmarkers(repo, [(repo[rev], newcommits)],
                                   metadata=metadata, operation="split")
        tr.close()
    finally:
        # Restore the old branch
        repo.dirstate.setbranch(savedbranch)

        lockmod.release(tr, lock, wlock)

@eh.command(
    'touch',
    [('r', 'rev', [], _('revision to update'), _('REV')),
     ('n', 'note', '', _('store a note on touch'), _('TEXT')),
     ('D', 'duplicate', False,
      'do not mark the new revision as successor of the old one'),
     ('A', 'allowdivergence', False,
      'mark the new revision as successor of the old one potentially creating '
      'divergence')],
    # allow to choose the seed ?
    _('[-r] revs'))
def touch(ui, repo, *revs, **opts):
    """create successors identical to their predecessors but the changeset ID

    This is used to "resurrect" changesets
    """
    _checknotesize(ui, opts)
    revs = list(revs)
    revs.extend(opts['rev'])
    if not revs:
        revs = ['.']
    revs = scmutil.revrange(repo, revs)
    if not revs:
        ui.write_err('no revision to touch\n')
        return 1

    duplicate = opts['duplicate']
    if not duplicate:
        rewriteutil.precheck(repo, revs, 'touch')
    tmpl = utility.shorttemplate
    displayer = compat.changesetdisplayer(ui, repo, {'template': tmpl})
    with repo.wlock(), repo.lock():
        tr = repo.transaction('touch')
        with util.acceptintervention(tr):
            touchnodes(ui, repo, revs, displayer, **opts)

def touchnodes(ui, repo, revs, displayer, **opts):
    duplicate = opts['duplicate']
    allowdivergence = opts['allowdivergence']
    revs.sort() # ensure parent are run first
    newmapping = {}
    for r in revs:
        ctx = repo[r]
        extra = ctx.extra().copy()
        extra['__touch-noise__'] = random.randint(0, 0xffffffff)
        # search for touched parent
        p1 = ctx.p1().node()
        p2 = ctx.p2().node()
        p1 = newmapping.get(p1, p1)
        p2 = newmapping.get(p2, p2)

        if not (duplicate or allowdivergence):
            # The user hasn't yet decided what to do with the revived
            # cset, let's ask
            sset = obsutil.successorssets(repo, ctx.node())
            nodivergencerisk = (len(sset) == 0
                                or (len(sset) == 1
                                    and len(sset[0]) == 1
                                    and repo[sset[0][0]].rev() == ctx.rev()
                                ))
            if nodivergencerisk:
                duplicate = False
            else:
                displayer.show(ctx)
                index = ui.promptchoice(
                    _("reviving this changeset will create divergence"
                      " unless you make a duplicate.\n(a)llow divergence or"
                      " (d)uplicate the changeset? $$ &Allowdivergence $$ "
                      "&Duplicate"), 0)
                choice = ['allowdivergence', 'duplicate'][index]
                if choice == 'allowdivergence':
                    duplicate = False
                else:
                    duplicate = True

        extradict = {'extra': extra}
        new, unusedvariable = rewriteutil.rewrite(repo, ctx, [], ctx,
                                                  [p1, p2],
                                                  commitopts=extradict)
        # store touched version to help potential children
        newmapping[ctx.node()] = new

        if not duplicate:
            metadata = {}
            if opts.get('note'):
                metadata['note'] = opts['note']
            obsolete.createmarkers(repo, [(ctx, (repo[new],))],
                                   metadata=metadata, operation="touch")
        tr = repo.currenttransaction()
        phases.retractboundary(repo, tr, ctx.phase(), [new])
        if ctx in repo[None].parents():
            with repo.dirstate.parentchange():
                repo.dirstate.setparents(new, node.nullid)

@eh.command(
    'pick|grab',
    [('r', 'rev', '', _('revision to pick'), _('REV')),
     ('c', 'continue', False, 'continue interrupted pick'),
     ('a', 'abort', False, 'abort interrupted pick'),
    ] + mergetoolopts,
    _('[-r] rev'))
def cmdpick(ui, repo, *revs, **opts):
    """move a commit on the top of working directory parent and updates to it."""

    cont = opts.get('continue')
    abort = opts.get('abort')

    if cont and abort:
        raise error.Abort(_("cannot specify both --continue and --abort"))

    revs = list(revs)
    if opts.get('rev'):
        revs.append(opts['rev'])

    overrides = {('ui', 'forcemerge'): opts.get('tool', '')}
    with repo.wlock(), repo.lock(), repo.transaction('pick'), ui.configoverride(overrides, 'pick'):
        pickstate = state.cmdstate(repo, path='pickstate')
        pctx = repo['.']

        if not cont and not abort:
            cmdutil.bailifchanged(repo)
            revs = scmutil.revrange(repo, revs)
            if len(revs) > 1:
                raise error.Abort(_("specify just one revision"))
            elif not revs:
                raise error.Abort(_("empty revision set"))

            origctx = repo[revs.first()]

            if origctx in pctx.ancestors() or origctx.node() == pctx.node():
                raise error.Abort(_("cannot pick an ancestor revision"))

            rewriteutil.precheck(repo, [origctx.rev()], 'pick')

            ui.status(_('picking %d:%s "%s"\n') %
                      (origctx.rev(), origctx,
                       origctx.description().split("\n", 1)[0]))
            stats = merge.graft(repo, origctx, origctx.p1(), ['local',
                                                              'destination'])
            if compat.hasconflict(stats):
                pickstate.addopts({'orignode': origctx.node(),
                                   'oldpctx': pctx.node()})
                pickstate.save()
                raise error.InterventionRequired(_("unresolved merge conflicts"
                                                   " (see hg help resolve)"))

        elif abort:
            if not pickstate:
                raise error.Abort(_("no interrupted pick state exists"))
            pickstate.load()
            pctxnode = pickstate['oldpctx']
            ui.status(_("aborting pick, updating to %s\n") %
                      node.hex(pctxnode)[:12])
            hg.updaterepo(repo, pctxnode, True)
            return 0

        else:
            if revs:
                raise error.Abort(_("cannot specify both --continue and "
                                    "revision"))
            if not pickstate:
                raise error.Abort(_("no interrupted pick state exists"))

            pickstate.load()
            orignode = pickstate['orignode']
            origctx = repo[orignode]

        overrides = {('phases', 'new-commit'): origctx.phase()}
        with repo.ui.configoverride(overrides, 'pick'):
            newnode = repo.commit(text=origctx.description(),
                                  user=origctx.user(),
                                  date=origctx.date(), extra=origctx.extra())
        repo.dirstate.setbranch(origctx.branch())

        if pickstate:
            pickstate.delete()
        newctx = repo[newnode] if newnode else pctx
        replacements = {origctx.node(): [newctx.node()]}
        scmutil.cleanupnodes(repo, replacements, operation="pick")

        if newnode is None:
            ui.warn(_("note: picking %d:%s created no changes to commit\n") %
                    (origctx.rev(), origctx))
            return 0

        return 0
