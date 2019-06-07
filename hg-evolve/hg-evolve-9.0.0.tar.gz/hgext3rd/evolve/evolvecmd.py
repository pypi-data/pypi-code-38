# Copyright 2011 Peter Arrenbrecht <peter.arrenbrecht@gmail.com>
#                Logilab SA        <contact@logilab.fr>
#                Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#                Patrick Mezard <patrick@mezard.eu>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

"""logic related to hg evolve command"""

import collections
import re

from mercurial import (
    bookmarks as bookmarksmod,
    cmdutil,
    commands,
    context,
    copies,
    error,
    encoding,
    hg,
    merge,
    mergeutil,
    node as nodemod,
    obsolete,
    obsutil,
    phases,
    repair,
    scmutil,
    simplemerge,
    util,
)

from mercurial.i18n import _

from . import (
    cmdrewrite,
    compat,
    exthelper,
    rewriteutil,
    state,
    utility,
)

TROUBLES = compat.TROUBLES
shorttemplate = utility.shorttemplate
stacktemplate = utility.stacktemplate
_bookmarksupdater = rewriteutil.bookmarksupdater
sha1re = re.compile(r'\b[0-9a-f]{6,40}\b')

eh = exthelper.exthelper()
mergetoolopts = commands.mergetoolopts

abortmessage = _("see `hg help evolve.interrupted`\n")

def _solveone(ui, repo, ctx, evolvestate, dryrun, confirm,
              progresscb, category, lastsolved=None, stacktmplt=False):
    """Resolve the troubles affecting one revision

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    tr = repo.currenttransaction()
    assert tr is not None
    displayer = None
    if stacktmplt:
        displayer = compat.changesetdisplayer(ui, repo,
                                              {'template': stacktemplate})
    else:
        displayer = compat.changesetdisplayer(ui, repo,
                                              {'template': shorttemplate})
    if 'orphan' == category:
        result = _solveunstable(ui, repo, ctx, evolvestate, displayer,
                                dryrun, confirm, progresscb,
                                lastsolved=lastsolved)
    elif 'phasedivergent' == category:
        result = _solvephasedivergence(ui, repo, ctx, evolvestate,
                                       displayer, dryrun, confirm,
                                       progresscb)
    elif 'contentdivergent' == category:
        result = _solvedivergent(ui, repo, ctx, evolvestate, displayer,
                                 dryrun, confirm, progresscb)
    else:
        assert False, "unknown trouble category: %s" % (category)
    return result

def _solveunstable(ui, repo, orig, evolvestate, displayer, dryrun=False,
                   confirm=False, progresscb=None, lastsolved=None):
    """ Tries to stabilize the changeset orig which is orphan.

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    pctx = orig.p1()
    keepbranch = orig.p1().branch() != orig.branch()
    if len(orig.parents()) == 2:
        p1obs = orig.p1().obsolete()
        p2obs = orig.p2().obsolete()
        if not p1obs and p2obs:
            pctx = orig.p2()  # second parent is obsolete ?
            keepbranch = orig.p2().branch() != orig.branch()
        elif not p2obs and p1obs:
            pass
        else:
            # store that we are resolving an orphan merge with both parents
            # obsolete and proceed with first parent
            evolvestate['orphanmerge'] = True
            # we should process the second parent first, so that in case of
            # no-conflicts the first parent is processed later and preserved as
            # first parent
            pctx = orig.p2()
            keepbranch = orig.p2().branch() != orig.branch()

    if not pctx.obsolete():
        ui.warn(_("cannot solve instability of %s, skipping\n") % orig)
        return (False, ".")
    obs = pctx
    newer = obsutil.successorssets(repo, obs.node())
    # search of a parent which is not killed
    while not newer or newer == [()]:
        ui.debug("stabilize target %s is plain dead,"
                 " trying to stabilize on its parent\n" %
                 obs)
        obs = obs.parents()[0]
        newer = obsutil.successorssets(repo, obs.node())
    if len(newer) > 1:
        msg = _("skipping %s: divergent rewriting. can't choose "
                "destination\n") % obs
        ui.write_err(msg)
        return (False, ".")
    targets = newer[0]
    assert targets
    if len(targets) > 1:
        # split target, figure out which one to pick, are they all in line?
        targetrevs = [repo[r].rev() for r in targets]
        roots = repo.revs('roots(%ld)', targetrevs)
        heads = repo.revs('heads(%ld)', targetrevs)
        if len(roots) > 1 or len(heads) > 1:
            cheader = _("ancestor '%s' split over multiple topological"
                        " branches.\nchoose an evolve destination:") % orig
            selectedrev = utility.revselectionprompt(ui, repo, list(heads),
                                                     cheader)
            if selectedrev is None:
                msg = _("could not solve instability, "
                        "ambiguous destination: "
                        "parent split across two branches\n")
                ui.write_err(msg)
                return (False, ".")
            target = repo[selectedrev]
        else:
            target = repo[heads.first()]
    else:
        target = targets[0]
    target = repo[target]
    if not ui.quiet or confirm:
        repo.ui.write(_('move:'), label='evolve.operation')
        displayer.show(orig)
        if lastsolved is None or target != repo[lastsolved]:
            repo.ui.write(_('atop:'))
            displayer.show(target)
    if confirm and ui.prompt('perform evolve? [Ny]', 'n') != 'y':
        raise error.Abort(_('evolve aborted by user'))
    todo = 'hg rebase -r %s -d %s\n' % (orig, target)
    if dryrun:
        if progresscb:
            progresscb()
        repo.ui.write(todo)
        return (False, ".")
    else:
        repo.ui.note(todo)
        if progresscb:
            progresscb()
        try:
            newid = relocate(repo, orig, target, evolvestate, pctx,
                             keepbranch, 'orphan')
            return (True, newid)
        except error.InterventionRequired:
            ops = {'current': orig.node()}
            evolvestate.addopts(ops)
            evolvestate.save()
            raise

def _solvephasedivergence(ui, repo, bumped, evolvestate, displayer,
                          dryrun=False, confirm=False, progresscb=None):
    """Stabilize a phase divergent changeset

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    repo = repo.unfiltered()
    bumped = repo[bumped.rev()]
    # For now we deny bumped merge
    if len(bumped.parents()) > 1:
        msg = _('skipping %s : we do not handle merge yet\n') % bumped
        ui.write_err(msg)
        return (False, ".")
    prec = repo.set('last(allpredecessors(%d) and public())', bumped.rev()).next()
    # For now we deny target merge
    if len(prec.parents()) > 1:
        msg = _('skipping: %s: public version is a merge, '
                'this is not handled yet\n') % prec
        ui.write_err(msg)
        return (False, ".")

    if not ui.quiet or confirm:
        repo.ui.write(_('recreate:'), label='evolve.operation')
        displayer.show(bumped)
        repo.ui.write(_('atop:'))
        displayer.show(prec)
    if confirm and ui.prompt('perform evolve? [Ny]', 'n') != 'y':
        raise error.Abort(_('evolve aborted by user'))
    if dryrun:
        todo = 'hg rebase --rev %s --dest %s;\n' % (bumped, prec.p1())
        repo.ui.write(todo)
        repo.ui.write(('hg update %s;\n' % prec))
        repo.ui.write(('hg revert --all --rev %s;\n' % bumped))
        repo.ui.write(('hg commit --msg "%s update to %s"\n' %
                       (TROUBLES['PHASEDIVERGENT'], bumped)))
        return (False, ".")
    if progresscb:
        progresscb()

    # Checking for whether the phase-divergent changeset has common parents as
    # it's precursors. Phase-divergent changeset and precursor having different
    # parents is a result of when the changeset is rebased, picked, histedit or
    # evolved or any other operation which can change parent. In such cases,
    # when parents are not same, we first rebase the divergent changeset onto
    # parent or precursor and then perform later steps
    if not list(repo.set('parents(%d) and parents(%d)', bumped.rev(), prec.rev())):
        # Need to rebase the changeset at the right place
        repo.ui.status(
            _('rebasing to destination parent: %s\n') % prec.p1())
        try:
            newnode = relocate(repo, bumped, prec.p1(), evolvestate,
                               category='phasedivergent')
            if newnode is not None:
                new = repo[newnode]
                obsolete.createmarkers(repo, [(bumped, (new,))],
                                       operation='evolve')
                bumped = new
                evolvestate['temprevs'].append(newnode)
        except error.InterventionRequired:
            evolvestate['current'] = bumped.hex()
            evolvestate['precursor'] = prec.hex()
            evolvestate.save()
            raise

    return _resolvephasedivergent(ui, repo, prec, bumped)

def _resolvephasedivergent(ui, repo, prec, bumped):
    """final step of a phase divergence resolution

    This will create a new changesets (or nothing when applicable), the two
    changesets needs to be on the same parents.
    """
    tr = repo.currenttransaction()
    assert tr is not None

    cl = repo.changelog
    prec_parent = cl.parentrevs(prec.rev())
    bump_parent = cl.parentrevs(bumped.rev())
    assert prec_parent == bump_parent, (prec_parent, bump_parent)

    bmupdate = _bookmarksupdater(repo, bumped.node(), tr)
    newid = None
    replacementnode = None

    # Create the new commit context. This is done by applying the changes from
    # the precursor to the bumped node onto the precursor. This is effectively
    # like reverting to the bumped node.
    wctx = context.overlayworkingctx(repo)
    wctx.setbase(prec)
    merge.update(repo, bumped.node(), ancestor=prec, mergeancestor=True,
                 branchmerge=True, force=False, wc=wctx)
    if not wctx.isempty():
        text = '%s update to %s:\n\n' % (TROUBLES['PHASEDIVERGENT'], prec)
        text += bumped.description()
        memctx = wctx.tomemctx(text,
                               parents=(prec.node(), nodemod.nullid),
                               date=bumped.date(),
                               extra=bumped.extra(),
                               user=bumped.user())
        newid = repo.commitctx(memctx)
        replacementnode = newid
    if newid is None:
        repo.ui.status(_('no changes to commit\n'))
        obsolete.createmarkers(repo, [(bumped, ())], operation='evolve')
        newid = prec.node()
    else:
        repo.ui.status(_('committed as %s\n') % nodemod.short(newid))
        phases.retractboundary(repo, tr, bumped.phase(), [newid])
        obsolete.createmarkers(repo, [(bumped, (repo[newid],))],
                               flag=obsolete.bumpedfix, operation='evolve')
    bmupdate(newid)
    # reroute the working copy parent to the new changeset
    with repo.dirstate.parentchange():
        repo.dirstate.setparents(newid, nodemod.nullid)
    return (True, replacementnode)

def _solvedivergent(ui, repo, divergent, evolvestate, displayer, dryrun=False,
                    confirm=False, progresscb=None):
    """tries to solve content-divergence of a changeset

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    repo = repo.unfiltered()
    divergent = repo[divergent.rev()]
    evolvestate['divergent'] = divergent.node()
    evolvestate['orig-divergent'] = divergent.node()
    # sometimes we will relocate a node in case of different parents and we can
    # encounter conflicts after relocation is done while solving
    # content-divergence and if the user calls `hg evolve --stop`, we need to
    # strip that relocated commit. However if `--all` is passed, we need to
    # reset this value for each content-divergence resolution which we are doing
    # below.
    evolvestate['relocated'] = None
    evolvestate['relocating'] = False
    # in case or relocation we get a new other node, we need to store the old
    # other for purposes like `--abort` or `--stop`
    evolvestate['old-other'] = None
    base, others = divergentdata(divergent)

    # we don't handle split in content-divergence yet
    if len(others) > 1:
        othersstr = "[%s]" % (','.join([str(i) for i in others]))
        msg = _("skipping %s: %s with a changeset that got split"
                " into multiple ones:\n"
                "|[%s]\n"
                "| This is not handled by automatic evolution yet\n"
                "| You have to fallback to manual handling with commands "
                "such as:\n"
                "| - hg touch -D\n"
                "| - hg prune\n"
                "| \n"
                "| You should contact your local evolution Guru for help.\n"
                ) % (divergent, TROUBLES['CONTENTDIVERGENT'], othersstr)
        ui.write_err(msg)
        return (False, ".")
    other = others[0]
    evolvestate['other-divergent'] = other.node()
    evolvestate['base'] = base.node()

    def swapnodes(div, other):
        div, other = other, div
        evolvestate['divergent'] = div.node()
        evolvestate['other-divergent'] = other.node()
        return div, other
    # haspubdiv: to keep track if we are solving public content-divergence
    haspubdiv = False
    if not (divergent.mutable() and other.mutable()):
        haspubdiv = True
        # for simplicity, we keep public one to local side while merging
        # (as divergent is kept at local side, pinning public -> divergent)
        if divergent.mutable():
            publicdiv = other
            divergent, other = swapnodes(divergent, other)
        else:
            publicdiv = divergent
        evolvestate['public-divergent'] = publicdiv.node()
    # we don't handle merge content-divergent changesets yet
    if len(other.parents()) > 1:
        msg = _("skipping %s: %s changeset can't be "
                "a merge (yet)\n") % (divergent, TROUBLES['CONTENTDIVERGENT'])
        ui.write_err(msg)
        hint = _("You have to fallback to solving this by hand...\n"
                 "| This probably means redoing the merge and using \n"
                 "| `hg prune` to kill older version.\n")
        ui.write_err(hint)
        return (False, ".")

    otherp1 = other.p1().rev()
    divp1 = divergent.p1().rev()

    # finding single successors of otherp1 and divp1
    try:
        otherp1 = utility._singlesuccessor(repo, other.p1())
    except utility.MultipleSuccessorsError:
        pass

    try:
        divp1 = utility._singlesuccessor(repo, divergent.p1())
    except utility.MultipleSuccessorsError:
        pass

    # the changeset on which resolution changeset will be based on
    resolutionparent = repo[divp1].node()

    gca = repo.revs("ancestor(%d, %d)" % (otherp1, divp1))
    # divonly: non-obsolete csets which are topological ancestor of "divergent"
    # but not "other"
    divonly = repo.revs("only(%d, %d) - obsolete()" % (divergent.rev(),
                                                       other.rev()))
    # otheronly: non-obsolete csets which are topological ancestor of "other"
    # but not "div"
    otheronly = repo.revs("only(%d, %d) - obsolete()" % (other.rev(),
                                                         divergent.rev()))
    # make it exclusive set
    divonly = set(divonly) - {divergent.rev()}
    otheronly = set(otheronly) - {other.rev()}
    # is relocation of one of the changeset required
    relocatereq = False

    # testing how both the divergent changesets are arranged, there can be 4
    # possible cases here:
    #
    # 1) both have the same parents
    # 2) both have different parents but greatest common anscestor of them is
    #    parent of one of them
    # 3) both have different parents and gca is not parent of any of them
    # 4) one of them is parent of other
    #
    # we are handling 1) very good now.
    # for 2) we will relocate one which is behind to the parent of ahead one and
    # then solve the content-divergence the way we solve 1)
    # for 3) and 4), we still have to decide
    if otherp1 in gca and divp1 in gca:
        if otherp1 == other.p1().rev() and divp1 == divergent.p1().rev():
            # both are on the same parents
            pass
        else:
            # both are not on the same parent but have same parents's succs.
            if otheronly and divonly:
                # case: we have visible csets on both side diverging from
                # tca of "divergent" and "other". We still need to decide what
                # to do in this case
                pass
            if otheronly:
                relocatereq = True
                if not haspubdiv:
                    # can't swap when public divergence, as public can't move
                    divergent, other = swapnodes(divergent, other)
                    resolutionparent = repo[otherp1].node()
            elif divonly:
                relocatereq = True
            else:
                # no extra cset on either side; so not considering relocation
                pass
    elif otherp1 in gca and divp1 not in gca:
        relocatereq = True
        pass
    elif divp1 in gca and otherp1 not in gca:
        relocatereq = True

        # When public branch is behind to the mutable branch, for now we
        # relocate mutable cset to public one's side in every case.
        #
        # This behaviour might be sub optimal when ancestors of mutable
        # cset has changes its relocated descendant rely on.
        #
        # Otherwise, we are going to rebase the "behind" branch up to the new
        # brancmap level.
        if not haspubdiv:
            divergent, other = swapnodes(divergent, other)
            resolutionparent = divergent.p1().node()
    else:
        msg = _("skipping %s: have a different parent than %s "
                "(not handled yet)\n") % (divergent, other)
        hint = _("| %(d)s, %(o)s are not based on the same changeset.\n"
                 "| With the current state of its implementation, \n"
                 "| evolve does not work in that case.\n"
                 "| rebase one of them next to the other and run \n"
                 "| this command again.\n"
                 "| - either: hg rebase --dest 'p1(%(d)s)' -r %(o)s\n"
                 "| - or:     hg rebase --dest 'p1(%(o)s)' -r %(d)s\n"
                 ) % {'d': divergent, 'o': other}
        ui.write_err(msg)
        ui.write_err(hint)
        return (False, ".")

    if not ui.quiet or confirm:
        ui.write(_('merge:'), label='evolve.operation')
        displayer.show(divergent)
        ui.write(_('with: '))
        displayer.show(other)
        ui.write(_('base: '))
        displayer.show(base)
    if confirm and ui.prompt(_('perform evolve? [Ny]'), 'n') != 'y':
        raise error.Abort(_('evolve aborted by user'))
    if dryrun:
        ui.write(('hg update -c %s &&\n' % divergent))
        ui.write(('hg merge %s &&\n' % other))
        ui.write(('hg commit -m "auto merge resolving conflict between '
                 '%s and %s"&&\n' % (divergent, other)))
        ui.write(('hg up -C %s &&\n' % base))
        ui.write(('hg revert --all --rev tip &&\n'))
        ui.write(('hg commit -m "`hg log -r %s --template={desc}`";\n'
                 % divergent))
        return (False, ".")

    evolvestate['resolutionparent'] = resolutionparent
    # relocate the other divergent if required
    if relocatereq:
        # relocating will help us understand during the time of conflicts that
        # whether conflicts occur at reloacting or they occured at merging
        # content divergent changesets
        evolvestate['relocating'] = True
        ui.status(_('rebasing "other" content-divergent changeset %s on'
                    ' %s\n' % (other, divergent.p1())))
        try:
            newother = relocate(repo, other, divergent.p1(), evolvestate,
                                keepbranch=True)
        except error.InterventionRequired:
            evolvestate['current'] = other.node()
            evolvestate.save()
            raise
        evolvestate['old-other'] = other.node()
        other = repo[newother]
        evolvestate['relocating'] = False
        evolvestate['relocated'] = other.node()
        evolvestate['temprevs'].append(other.node())
        evolvestate['other-divergent'] = other.node()

    _mergecontentdivergents(repo, progresscb, divergent, other, base,
                            evolvestate)
    res, newnode = _completecontentdivergent(ui, repo, progresscb, divergent,
                                             other, base, evolvestate)
    if not haspubdiv:
        return (res, newnode)
    else:
        # we have content-divergence with a public cset:
        # after performing content divergence resolution steps, possbile cases:
        # 1) merging results in a new node:
        #       we need to perform phase divergence resolution
        # 2) merging leads to same content as public cset:
        #       divergence has been resolved by creating markers
        if not res:
            # resolution was not successful, return
            return (res, newnode)
        if newnode == publicdiv.node():
            # case 2)
            pubstr = str(publicdiv)
            othstr = str(other)
            msg = _('content divergence resolution between %s '
                    '(public) and %s has same content as %s, '
                    'discarding %s\n')
            msg %= (pubstr, othstr, pubstr, othstr)
            repo.ui.status(msg)
            return (res, newnode)
        # case 1)
        prec = publicdiv
        bumped = repo[newnode]
        return _resolvephasedivergent(ui, repo, prec=prec, bumped=bumped)

def _mergecontentdivergents(repo, progresscb, divergent, other, base,
                            evolvestate):
    if divergent not in repo[None].parents():
        repo.ui.note(_("updating to \"local\" side of the conflict: %s\n") %
                     divergent.hex()[:12])
        hg.updaterepo(repo, divergent.node(), False)
    # merging the two content-divergent changesets
    repo.ui.note(_("merging \"other\" %s changeset '%s'\n") %
                 (TROUBLES['CONTENTDIVERGENT'], other.hex()[:12]))
    if progresscb:
        progresscb()
    mergeancestor = repo.changelog.isancestor(divergent.node(), other.node())
    stats = merge.update(repo,
                         other.node(),
                         branchmerge=True,
                         force=False,
                         ancestor=base.node(),
                         mergeancestor=mergeancestor)
    hg._showstats(repo, stats)

    # conflicts while merging content-divergent changesets
    if compat.hasconflict(stats):
        evolvestate.save()
        raise error.InterventionRequired(_("fix conflicts and see `hg help "
                                           "evolve.interrupted`"))

def _completecontentdivergent(ui, repo, progresscb, divergent, other,
                              base, evolvestate):
    """completes the content-divergence resolution"""
    # no conflicts were there in merging content divergent changesets, let's
    # resume resolution
    if progresscb:
        progresscb()
    emtpycommitallowed = repo.ui.backupconfig('ui', 'allowemptycommit')
    tr = repo.currenttransaction()
    assert tr is not None
    # whether to store the obsmarker in the evolvestate
    storemarker = False
    resparent = evolvestate['resolutionparent']

    # whether we are solving public divergence
    haspubdiv = False
    if evolvestate.get('public-divergent'):
        haspubdiv = True
        publicnode = evolvestate['public-divergent']
        publicdiv = repo[publicnode]
        othernode = evolvestate['other-divergent']
        otherdiv = repo[othernode]

        with repo.dirstate.parentchange():
            repo.dirstate.setparents(publicnode, nodemod.nullid)
            dirstatedance(repo, divergent, publicnode, None)
        # check if node to be committed has changes same as public one
        s = publicdiv.status()
        if not (s.added or s.removed or s.deleted or s.modified):
            # warn user if metadata is being lost
            warnmetadataloss(repo, publicdiv, otherdiv)
            # no changes, create markers to resolve divergence
            obsolete.createmarkers(repo, [(otherdiv, (publicdiv,))],
                                   operation='evolve')
            return (True, publicnode)
    try:
        with repo.dirstate.parentchange():
            repo.dirstate.setparents(resparent, nodemod.nullid)

        dirstatedance(repo, divergent, resparent, None)

        # merge the branches
        mergebranches(repo, divergent, other, base)
        # merge the commit messages
        desc = mergecommitmessages(ui, base.description(),
                                   divergent.description(),
                                   other.description())
        user = utility.mergeusers(ui, base, divergent, other)

        # new node if any formed as the replacement
        newnode = None

        mergehook(repo, base, divergent, other)

        newnode = repo.commit(text=desc, user=user)
        if newnode == divergent.node() or newnode is None:
            # no changes
            new = divergent
            storemarker = True
            repo.ui.status(_("nothing changed\n"))
            hg.updaterepo(repo, divergent.rev(), False)
        else:
            new = repo[newnode]
            newnode = new.node()
            hg.updaterepo(repo, new.rev(), False)
            if haspubdiv and publicdiv == divergent:
                bypassphase(repo, (divergent, new), operation='evolve')
            else:
                obsolete.createmarkers(repo, [(divergent, (new,))],
                                       operation='evolve')

        # creating markers and moving phases post-resolution
        if haspubdiv and publicdiv == other:
            bypassphase(repo, (other, new), operation='evolve')
        else:
            obsolete.createmarkers(repo, [(other, (new,))], operation='evolve')
        if storemarker:
            # storing the marker in the evolvestate
            # we just store the precursors and successor pair for now, we might
            # want to store more data and serialize obsmarker in a better way in
            # future
            evolvestate['obsmarkers'].append((other.node(), new.node()))

        phases.retractboundary(repo, tr, other.phase(), [new.node()])
        return (True, newnode)
    finally:
        repo.ui.restoreconfig(emtpycommitallowed)

def warnmetadataloss(repo, local, other):
    """warn the user for the metadata being lost while resolving
    public content-divergence"""

    # needtowarn: aspects where we need to warn user
    needtowarn = ['branch', 'topic', 'close']
    aspects = set()
    localextra = local.extra()
    otherextra = other.extra()

    for asp in needtowarn:
        otherasp = otherextra.get(asp)
        localasp = localextra.get(asp)
        if otherasp and otherasp != localasp:
            aspects.add(asp)

    if other.description() != local.description():
        aspects.add('description')

    if aspects:
        # warn user
        locstr = str(local)
        othstr = str(other)
        if 'close' in aspects:
            filteredasp = aspects - {'close'}
            if filteredasp:
                msg = _('other divergent changeset %s is a closed branch head '
                        'and differs from local %s by "%s" only,' %
                        (othstr, locstr, ', '.join(sorted(filteredasp))))
            else:
                msg = _('other divergent changeset %s is a closed branch head '
                        'and has same content as local %s,' % (othstr, locstr))
        else:
            msg = _('other divergent changeset %s has same content as local %s'
                    ' and differs by "%s" only,' %
                    (othstr, locstr, ', '.join(sorted(aspects))))
        msg += _(' discarding %s\n' % othstr)
        repo.ui.warn(msg)

def bypassphase(repo, relation, flag=0, metadata=None, operation='evolve'):
    """function to create a single obsmarker relation even for public csets
    where relation should be a single pair (prec, succ)"""

    # prepare metadata
    if metadata is None:
        metadata = {}
    if 'user' not in metadata:
        luser = repo.ui.config('devel', 'user.obsmarker') or repo.ui.username()
        metadata['user'] = encoding.fromlocal(luser)
    # Operation metadata handling
    useoperation = repo.ui.configbool('experimental',
                                      'evolution.track-operation')
    if useoperation and operation:
        metadata['operation'] = operation

    # Effect flag metadata handling
    saveeffectflag = repo.ui.configbool('experimental',
                                        'evolution.effect-flags')
    with repo.transaction('add-obsolescence-marker') as tr:
        prec, succ = relation
        nprec = prec.node()
        npare = None
        nsucs = [succ.node()]
        if not nsucs:
            npare = tuple(p.node() for p in prec.parents())
        if nprec in nsucs:
            raise error.Abort(_("changeset %s cannot obsolete itself") % prec)

        if saveeffectflag:
            # The effect flag is saved in a versioned field name for
            # future evolution
            try:
                effectflag = obsutil.geteffectflag(prec, (succ,))
            except TypeError:
                # hg <= 4.7
                effectflag = obsutil.geteffectflag((prec, (succ,)))
            metadata[obsutil.EFFECTFLAGFIELD] = "%d" % effectflag

        # create markers
        repo.obsstore.create(tr, nprec, nsucs, flag, parents=npare,
                             metadata=metadata, ui=repo.ui)
        repo.filteredrevcache.clear()

def dirstatedance(repo, oldparent, newparent, match):
    """utility function to fix the dirstate when we change parents from
    oldparent to newparent with a dirty working directory using
    repo.dirstate.setparents()

    Lets refer oldparent as Pold
               newparent as Pnew

    Now when we are on oldparent with a dirty working directory, there are three
    types of files which we are concerned about. They are files having modified,
    added and removed status.

    Lets refer modified files as Fm
               added files as Fa
               removed files as Fr

    Now, between Pold and Pnew, files can be modified, files can be added, files
    can be removed.

    Lets refer modification of a file between Pold to Pnew as Cm
               addition of a file between Pold to Pnew as Ca
               removal of a file between Pold to Pnew as Cr

    Now let's play combinations and permutations:

    |---------------------------------------------------------------|
    | Type of file |  Changes between |   End status with Pnew as   |
    |   in wdir    |    Pold -> Pnew  |       wdir parent           |
    |--------------|------------------|-----------------------------|
    |              |                  |                             |
    |   Fm         |      Cm          |       Modified or clean     |
    |--------------|------------------|-----------------------------|
    |   Fm         |      Cr          |           Added             |
    |--------------|------------------|-----------------------------|
    |   Fm         |      Ca          |       Not possible (1)      |
    |--------------|------------------|-----------------------------|
    |   Fa         |      Ca          |       Modified or clean     |
    |--------------|------------------|-----------------------------|
    |   Fa         |      Cm          |       Not possible (2)      |
    |--------------|------------------|-----------------------------|
    |   Fa         |      Cr          |       Not possible (2)      |
    |--------------|------------------|-----------------------------|
    |   Fr         |      Cr          | File should be untracked (3)|
    |--------------|------------------|-----------------------------|
    |   Fr         |      Ca          |       Not possible (4)      |
    |--------------|------------------|-----------------------------|
    |   Fr         |      Cm          |           Removed           |
    |--------------|------------------|-----------------------------|

    (1): File is modified in wdir, it means file was present in Pold, so
         addition of that file between Pold to Pnew is not possible

    (2): File was added in wdir, it means file was not present in Pold, so
         deletion or modification of that file from Pold to Pnew is not possible

    (3): File should be dropped from the dirstate, Pnew has it removed, so no
         need to mark that removed again

    (4): File was removed in wdir, it means file was present in Pold, so
         addition of that file between Pold to Pnew is not possible

    """

    # falling back to an existing function, in future we should have logic in
    # this function only
    cmdrewrite._uncommitdirstate(repo, oldparent, match, True)

def mergehook(repo, base, divergent, other):
    """function which extensions can wrap and merge data introduced by them
    while resolving content-divergence"""
    pass

def mergebranches(repo, divergent, other, base):
    """merges the branch information for content-divergent changesets and sets
    the dirstate branch accordingly
    If unable to merge, prompts user to select a branch

    If the branch name is different from the branch of divergent changeset, it
    sets the current branch using repo.dirstate.setbranch()
    """
    divbranch = divergent.branch()
    basebranch = base.branch()
    othbranch = other.branch()
    # content divergent changes were on different branches, ask user to
    # select one
    if divbranch != othbranch:

        if basebranch == othbranch and basebranch != divbranch:
            # we will be amending the divergent changeset so branch will be
            # preserved
            pass
        elif basebranch == divbranch and basebranch != othbranch:
            repo.dirstate.setbranch(othbranch)
        else:
            # all the three branches are different
            index = repo.ui.promptchoice(_("content divergent changesets on "
                                           "different branches.\nchoose branch"
                                           " for the resolution changeset. (a) "
                                           "%s or (b) %s or (c) %s? $$ &a $$ &b"
                                           " $$ &c") %
                                         (basebranch, divbranch, othbranch), 0)

            if index == 0:
                repo.dirstate.setbranch(basebranch)
            elif index == 1:
                pass
            elif index == 2:
                repo.dirstate.setbranch(othbranch)

def mergecommitmessages(ui, basedesc, divdesc, othdesc):
    """merges the commit messages and return the new merged message and whether
    there were conflicts or not while merging the messages"""

    merger = simplemerge.Merge3Text(basedesc, divdesc, othdesc)
    mdesc = []
    kwargs = {}
    kwargs['name_base'] = 'base'
    kwargs['base_marker'] = '|||||||'
    for line in merger.merge_lines(name_a='divergent', name_b='other',
                                   **kwargs):
        mdesc.append(line)

    desc = ''.join(mdesc)
    if merger.conflicts:

        prefixes = ("HG: Conflicts while merging changeset description of"
                    " content-divergent changesets.\nHG: Resolve conflicts"
                    " in commit messages to continue.\n\n")

        resolveddesc = ui.edit(prefixes + desc, ui.username(), action='desc')
        # make sure we remove the prefixes part from final commit message
        if prefixes in resolveddesc:
            # hack, we should find something better
            resolveddesc = resolveddesc[len(prefixes):]
        desc = resolveddesc

    return desc

def _orderrevs(repo, revs):
    """Compute an ordering to solve instability for the given revs

    revs is a list of unstable revisions.

    Returns the same revisions ordered to solve their instability from the
    bottom to the top of the stack that the stabilization process will produce
    eventually.

    This ensures the minimal number of stabilizations, as we can stabilize each
    revision on its final stabilized destination.
    """
    # Step 1: Build the dependency graph
    dependencies, rdependencies = utility.builddependencies(repo, revs)
    # Step 2: Build the ordering
    # Remove the revisions with no dependency(A) and add them to the ordering.
    # Removing these revisions leads to new revisions with no dependency (the
    # one depending on A) that we can remove from the dependency graph and add
    # to the ordering. We progress in a similar fashion until the ordering is
    # built
    solvablerevs = collections.deque([r for r in sorted(dependencies.keys())
                                      if not dependencies[r]])
    ordering = []
    while solvablerevs:
        rev = solvablerevs.popleft()
        for dependent in rdependencies[rev]:
            dependencies[dependent].remove(rev)
            if not dependencies[dependent]:
                solvablerevs.append(dependent)
        del dependencies[rev]
        ordering.append(rev)

    ordering.extend(sorted(dependencies))
    return ordering

def relocate(repo, orig, dest, evolvestate, pctx=None, keepbranch=False,
             category=None):
    """rewrites the orig rev on dest rev

    returns the node of new commit which is formed
    """
    if orig.rev() == dest.rev():
        msg = _('tried to relocate a node on top of itself')
        hint = _("This shouldn't happen. If you still need to move changesets, "
                 "please do so manually with nothing to rebase - working "
                 "directory parent is also destination")
        raise error.ProgrammingError(msg, hint=hint)

    if pctx is None:
        if len(orig.parents()) == 2:
            msg = _("tried to relocate a merge commit without specifying which "
                    "parent should be moved")
            hint = _("Specify the parent by passing in pctx")
            raise error.ProgrammingError(msg, hint)
        pctx = orig.p1()

    commitmsg = orig.description()

    cache = {}
    sha1s = re.findall(sha1re, commitmsg)
    unfi = repo.unfiltered()
    for sha1 in sha1s:
        if util.safehasattr(scmutil, 'resolvehexnodeidprefix'): # > hg-4.6
            fullnode = scmutil.resolvehexnodeidprefix(unfi, sha1)
        else:
            fullnode = unfi.changelog.index.partialmatch(sha1)
        if fullnode is None:
            continue
        ctx = unfi[fullnode]
        if not ctx.obsolete():
            continue

        successors = obsutil.successorssets(repo, ctx.node(), cache)

        # We can't make any assumptions about how to update the hash if the
        # cset in question was split or diverged.
        if len(successors) == 1 and len(successors[0]) == 1:
            newsha1 = nodemod.hex(successors[0][0])
            commitmsg = commitmsg.replace(sha1, newsha1[:len(sha1)])
        else:
            repo.ui.note(_('The stale commit message reference to %s could '
                           'not be updated\n') % sha1)

    tr = repo.currenttransaction()
    assert tr is not None
    r = _evolvemerge(repo, orig, dest, pctx, keepbranch)
    if compat.hasconflict(r): # some conflict
        with repo.dirstate.parentchange():
            repo.setparents(dest.node(), orig.node())
            repo.dirstate.write(tr)
            # fix up dirstate for copies and renames
            copies.duplicatecopies(repo, repo[None], dest.rev(),
                                   orig.p1().rev())
            dirstatedance(repo, dest, orig.node(), None)
        raise error.InterventionRequired(_("fix conflicts and see `hg help "
                                           "evolve.interrupted`"))
    nodenew = _relocatecommit(repo, orig, commitmsg)
    _finalizerelocate(repo, orig, dest, nodenew, tr, category, evolvestate)
    return nodenew

def _relocatecommit(repo, orig, commitmsg):
    if commitmsg is None:
        commitmsg = orig.description()
    extra = dict(orig.extra())
    if 'branch' in extra:
        del extra['branch']
    extra['rebase_source'] = orig.hex()

    backup = repo.ui.backupconfig('phases', 'new-commit')
    try:
        targetphase = max(orig.phase(), phases.draft)
        repo.ui.setconfig('phases', 'new-commit', targetphase, 'evolve')
        # Commit might fail if unresolved files exist
        nodenew = repo.commit(text=commitmsg, user=orig.user(),
                              date=orig.date(), extra=extra)
    finally:
        repo.ui.restoreconfig(backup)
    return nodenew

def _finalizerelocate(repo, orig, dest, nodenew, tr, category, evolvestate):
    destbookmarks = repo.nodebookmarks(dest.node())
    nodesrc = orig.node()
    oldbookmarks = repo.nodebookmarks(nodesrc)
    bmchanges = []

    if nodenew is not None:
        obsolete.createmarkers(repo, [(repo[nodesrc], (repo[nodenew],))],
                               operation='evolve')
        for book in oldbookmarks:
            bmchanges.append((book, nodenew))
            evolvestate['bookmarkchanges'].append((book, nodesrc))
    else:
        if category == 'orphan':
            repo.ui.status(_("evolution of %d:%s created no changes "
                             "to commit\n") % (orig.rev(), orig))
        obsolete.createmarkers(repo, [(repo[nodesrc], ())], operation='evolve')
        # Behave like rebase, move bookmarks to dest
        for book in oldbookmarks:
            evolvestate['bookmarkchanges'].append((book, nodesrc))
            bmchanges.append((book, dest.node()))
    for book in destbookmarks: # restore bookmark that rebase move
        bmchanges.append((book, dest.node()))
    if bmchanges:
        repo._bookmarks.applychanges(repo, tr, bmchanges)

def _evolvemerge(repo, orig, dest, pctx, keepbranch):
    """Used by the evolve function to merge dest on top of pctx.
    return the same tuple as merge.graft"""
    if repo['.'].rev() != dest.rev():
        merge.update(repo,
                     dest,
                     branchmerge=False,
                     force=True)
    if repo._activebookmark:
        repo.ui.status(_("(leaving bookmark %s)\n") % repo._activebookmark)
    bookmarksmod.deactivate(repo)
    if keepbranch:
        repo.dirstate.setbranch(orig.branch())
    if util.safehasattr(repo, 'currenttopic'):
        # uurrgs
        # there no other topic setter yet
        if not orig.topic() and repo.vfs.exists('topic'):
            repo.vfs.unlink('topic')
        else:
            with repo.vfs.open('topic', 'w') as f:
                f.write(orig.topic())

    return merge.graft(repo, orig, pctx, ['destination', 'evolving'], True)

instabilities_map = {
    'contentdivergent': "content-divergent",
    'phasedivergent': "phase-divergent"
}

def _selectrevs(repo, allopt, revopt, anyopt, targetcat):
    """select troubles in repo matching according to given options"""
    revs = set()
    if allopt or revopt:
        revs = repo.revs("%s()" % targetcat)
        if revopt:
            revs = scmutil.revrange(repo, revopt) & revs
        elif not anyopt:
            topic = getattr(repo, 'currenttopic', '')
            if topic:
                revs = repo.revs('topic(%s)', topic) & revs
            elif targetcat == 'orphan':
                revs = _aspiringdescendant(repo,
                                           repo.revs('(.::) - obsolete()::'))
                revs = set(revs)
        if targetcat == 'contentdivergent':
            # Pick one divergent per group of divergents
            revs = _dedupedivergents(repo, revs)
    elif anyopt:
        revs = repo.revs('first(%s())' % (targetcat))
    elif targetcat == 'orphan':
        revs = set(_aspiringchildren(repo, repo.revs('(.::) - obsolete()::')))
        if 1 < len(revs):
            msg = "multiple evolve candidates"
            hint = (_("select one of %s with --rev")
                    % ', '.join([str(repo[r]) for r in sorted(revs)]))
            raise error.Abort(msg, hint=hint)
    elif instabilities_map.get(targetcat, targetcat) in repo['.'].instabilities():
        revs = set([repo['.'].rev()])
    return revs

def _dedupedivergents(repo, revs):
    """Dedupe the divergents revs in revs to get one from each group with the
    lowest revision numbers
    """
    repo = repo.unfiltered()
    res = set()
    # To not reevaluate divergents of the same group once one is encountered
    discarded = set()
    for rev in revs:
        if rev in discarded:
            continue
        divergent = repo[rev]
        base, others = divergentdata(divergent)
        othersrevs = [o.rev() for o in others]
        res.add(min([divergent.rev()] + othersrevs))
        discarded.update(othersrevs)
    return res

def divergentdata(ctx):
    """return base, other part of a conflict

    This only return the first one.

    XXX this woobly function won't survive XXX
    """
    repo = ctx._repo.unfiltered()
    for base in repo.set('reverse(allpredecessors(%d))', ctx.rev()):
        newer = obsutil.successorssets(ctx._repo, base.node())
        # drop filter and solution including the original ctx
        newer = [n for n in newer if n and ctx.node() not in n]
        if newer:
            return base, tuple(ctx._repo[o] for o in newer[0])
    raise error.Abort(_("base of divergent changeset %s not found") % ctx,
                      hint=_('this case is not yet handled'))

def _aspiringdescendant(repo, revs):
    """Return a list of changectx which can be stabilized on top of pctx or
    one of its descendants recursively. Empty list if none can be found."""
    target = set(revs)
    result = set(target)
    paths = collections.defaultdict(set)
    for r in repo.revs('orphan() - %ld', revs):
        for d in _possibledestination(repo, r):
            paths[d].add(r)

    result = set(target)
    tovisit = list(revs)
    while tovisit:
        base = tovisit.pop()
        for unstable in paths[base]:
            if unstable not in result:
                tovisit.append(unstable)
                result.add(unstable)
    return sorted(result - target)

def _aspiringchildren(repo, revs):
    """Return a list of changectx which can be stabilized on top of pctx or
    one of its descendants. Empty list if none can be found."""
    target = set(revs)
    result = []
    for r in repo.revs('orphan() - %ld', revs):
        dest = _possibledestination(repo, r)
        if target & dest:
            result.append(r)
    return result

def _possibledestination(repo, rev):
    """return all changesets that may be a new parent for REV"""
    tonode = repo.changelog.node
    parents = repo.changelog.parentrevs
    torev = repo.changelog.rev
    dest = set()
    tovisit = list(parents(rev))
    while tovisit:
        r = tovisit.pop()
        if r == -1:
            continue
        succsets = obsutil.successorssets(repo, tonode(r))
        if not succsets:
            tovisit.extend(parents(r))
        else:
            # We should probably pick only one destination from split
            # (case where '1 < len(ss)'), This could be the currently tipmost
            # but logic is less clear when result of the split are now on
            # multiple branches.
            for ss in succsets:
                for n in ss:
                    dest.add(torev(n))
    return dest

def _handlenotrouble(ui, repo, allopt, revopt, anyopt, targetcat):
    """Used by the evolve function to display an error message when
    no troubles can be resolved"""
    troublecategories = ['phasedivergent', 'contentdivergent', 'orphan']
    unselectedcategories = [c for c in troublecategories if c != targetcat]
    msg = None
    hint = None
    retoverride = None

    troubled = {
        "orphan": repo.revs("orphan()"),
        "contentdivergent": repo.revs("contentdivergent()"),
        "phasedivergent": repo.revs("phasedivergent()"),
        "all": repo.revs("unstable()"),
    }

    hintmap = {
        'phasedivergent': _("do you want to use --phase-divergent"),
        'phasedivergent+contentdivergent': _("do you want to use "
                                             "--phase-divergent or"
                                             " --content-divergent"),
        'phasedivergent+orphan': _("do you want to use --phase-divergent"
                                   " or --orphan"),
        'contentdivergent': _("do you want to use --content-divergent"),
        'contentdivergent+orphan': _("do you want to use --content-divergent"
                                     " or --orphan"),
        'orphan': _("do you want to use --orphan"),
        'any+phasedivergent': _("do you want to use --any (or --rev) and"
                                " --phase-divergent"),
        'any+phasedivergent+contentdivergent': _("do you want to use --any"
                                                 " (or --rev) and"
                                                 " --phase-divergent or"
                                                 " --content-divergent"),
        'any+phasedivergent+orphan': _("do you want to use --any (or --rev)"
                                       " and --phase-divergent or --orphan"),
        'any+contentdivergent': _("do you want to use --any (or --rev) and"
                                  " --content-divergent"),
        'any+contentdivergent+orphan': _("do you want to use --any (or --rev)"
                                         " and --content-divergent or "
                                         "--orphan"),
        'any+orphan': _("do you want to use --any (or --rev)"
                        "and --orphan"),
    }

    if revopt:
        revs = scmutil.revrange(repo, revopt)
        if not revs:
            msg = _("set of specified revisions is empty")
        else:
            msg = _("no %s changesets in specified revisions") % targetcat
            othertroubles = []
            for cat in unselectedcategories:
                if revs & troubled[cat]:
                    othertroubles.append(cat)
            if othertroubles:
                hint = hintmap['+'.join(othertroubles)]

    elif anyopt:
        msg = _("no %s changesets to evolve") % targetcat
        othertroubles = []
        for cat in unselectedcategories:
            if troubled[cat]:
                othertroubles.append(cat)
        if othertroubles:
            hint = hintmap['+'.join(othertroubles)]

    else:
        # evolve without any option = relative to the current wdir
        if targetcat == 'orphan':
            msg = _("nothing to evolve on current working copy parent")
        else:
            msg = _("current working copy parent is not %s") % targetcat

        p1 = repo['.'].rev()
        othertroubles = []
        for cat in unselectedcategories:
            if p1 in troubled[cat]:
                othertroubles.append(cat)
        if othertroubles:
            hint = hintmap['+'.join(othertroubles)]
        else:
            length = len(troubled[targetcat])
            if length:
                hint = _("%d other %s in the repository, do you want --any "
                         "or --rev") % (length, targetcat)
            else:
                othertroubles = []
                for cat in unselectedcategories:
                    if troubled[cat]:
                        othertroubles.append(cat)
                if othertroubles:
                    hint = hintmap['any+' + ('+'.join(othertroubles))]
                else:
                    msg = _("no troubled changesets")
                    # Exit with a 0 (success) status in this case.
                    retoverride = 0

    assert msg is not None
    ui.write_err("%s\n" % msg)
    if hint:
        ui.write_err("(%s)\n" % hint)
        ret = 2
    else:
        ret = 1

    if retoverride is not None:
        return retoverride
    return ret

def _preparelistctxs(items, condition):
    return [item.hex() for item in items if condition(item)]

def _formatctx(fm, ctx):
    fm.data(node=ctx.hex())
    fm.data(desc=ctx.description())
    fm.data(date=ctx.date())
    fm.data(user=ctx.user())

def listtroubles(ui, repo, troublecategories, **opts):
    """Print all the troubles for the repo (or given revset)"""
    troublecategories = troublecategories or ['contentdivergent', 'orphan', 'phasedivergent']
    showunstable = 'orphan' in troublecategories
    showbumped = 'phasedivergent' in troublecategories
    showdivergent = 'contentdivergent' in troublecategories

    revs = repo.revs('+'.join("%s()" % t for t in troublecategories))
    if opts.get('rev'):
        revs = scmutil.revrange(repo, opts.get('rev'))

    fm = ui.formatter('evolvelist', opts)
    for rev in revs:
        ctx = repo[rev]
        unpars = _preparelistctxs(ctx.parents(), lambda p: p.orphan())
        obspars = _preparelistctxs(ctx.parents(), lambda p: p.obsolete())
        imprecs = _preparelistctxs(repo.set("allpredecessors(%n)", ctx.node()),
                                   lambda p: not p.mutable())
        dsets = divergentsets(repo, ctx)

        fm.startitem()
        # plain formatter section
        hashlen, desclen = 12, 60
        desc = ctx.description()
        if desc:
            desc = desc.splitlines()[0]
        desc = (desc[:desclen] + '...') if len(desc) > desclen else desc
        fm.plain('%s: ' % ctx.hex()[:hashlen])
        fm.plain('%s\n' % desc)
        fm.data(node=ctx.hex(), rev=ctx.rev(), desc=desc, phase=ctx.phasestr())

        for unpar in unpars if showunstable else []:
            fm.plain('  %s: %s (%s parent)\n' % (TROUBLES['ORPHAN'],
                                                 unpar[:hashlen],
                                                 TROUBLES['ORPHAN']))
        for obspar in obspars if showunstable else []:
            fm.plain('  %s: %s (obsolete parent)\n' % (TROUBLES['ORPHAN'],
                                                       obspar[:hashlen]))
        for imprec in imprecs if showbumped else []:
            fm.plain('  %s: %s (immutable precursor)\n' %
                     (TROUBLES['PHASEDIVERGENT'], imprec[:hashlen]))

        if dsets and showdivergent:
            for dset in dsets:
                fm.plain('  %s: ' % TROUBLES['CONTENTDIVERGENT'])
                first = True
                for n in dset['divergentnodes']:
                    t = "%s (%s)" if first else " %s (%s)"
                    first = False
                    fm.plain(t % (nodemod.hex(n)[:hashlen], repo[n].phasestr()))
                comprec = nodemod.hex(dset['commonprecursor'])[:hashlen]
                fm.plain(" (precursor %s)\n" % comprec)
        fm.plain("\n")

        # templater-friendly section
        _formatctx(fm, ctx)
        troubles = []
        for unpar in unpars:
            troubles.append({'troubletype': TROUBLES['ORPHAN'],
                             'sourcenode': unpar, 'sourcetype': 'orphanparent'})
        for obspar in obspars:
            troubles.append({'troubletype': TROUBLES['ORPHAN'],
                             'sourcenode': obspar,
                             'sourcetype': 'obsoleteparent'})
        for imprec in imprecs:
            troubles.append({'troubletype': TROUBLES['PHASEDIVERGENT'],
                             'sourcenode': imprec,
                             'sourcetype': 'immutableprecursor'})
        for dset in dsets:
            divnodes = [{'node': nodemod.hex(n),
                         'phase': repo[n].phasestr(),
                        } for n in dset['divergentnodes']]
            troubles.append({'troubletype': TROUBLES['CONTENTDIVERGENT'],
                             'commonprecursor': nodemod.hex(dset['commonprecursor']),
                             'divergentnodes': divnodes})
        fm.data(troubles=troubles)

    fm.end()

def _checkevolveopts(repo, opts):
    """ check the options passed to `hg evolve` and warn for deprecation warning
    if any """

    if opts['continue']:
        if opts['any']:
            raise error.Abort(_('cannot specify both "--any" and "--continue"'))
        if opts['all']:
            raise error.Abort(_('cannot specify both "--all" and "--continue"'))
        if opts['rev']:
            raise error.Abort(_('cannot specify both "--rev" and "--continue"'))
        if opts['stop']:
            raise error.Abort(_('cannot specify both "--stop" and'
                                ' "--continue"'))
        if opts['abort']:
            raise error.Abort(_('cannot specify both "--abort" and'
                                ' "--continue"'))

    if opts['stop']:
        if opts['any']:
            raise error.Abort(_('cannot specify both "--any" and "--stop"'))
        if opts['all']:
            raise error.Abort(_('cannot specify both "--all" and "--stop"'))
        if opts['rev']:
            raise error.Abort(_('cannot specify both "--rev" and "--stop"'))
        if opts['abort']:
            raise error.Abort(_('cannot specify both "--abort" and "--stop"'))

    if opts['abort']:
        if opts['any']:
            raise error.Abort(_('cannot specify both "--any" and "--abort"'))
        if opts['all']:
            raise error.Abort(_('cannot specify both "--all" and "--abort"'))
        if opts['rev']:
            raise error.Abort(_('cannot specify both "--rev" and "--abort"'))

    if opts['rev']:
        if opts['any']:
            raise error.Abort(_('cannot specify both "--rev" and "--any"'))
        if opts['all']:
            raise error.Abort(_('cannot specify both "--rev" and "--all"'))

    # Backward compatibility
    if opts['unstable']:
        msg = ("'evolve --unstable' is deprecated, "
               "use 'evolve --orphan'")
        repo.ui.deprecwarn(msg, '4.4')

        opts['orphan'] = opts['divergent']

    if opts['divergent']:
        msg = ("'evolve --divergent' is deprecated, "
               "use 'evolve --content-divergent'")
        repo.ui.deprecwarn(msg, '4.4')

        opts['content_divergent'] = opts['divergent']

    if opts['bumped']:
        msg = ("'evolve --bumped' is deprecated, "
               "use 'evolve --phase-divergent'")
        repo.ui.deprecwarn(msg, '4.4')

        opts['phase_divergent'] = opts['bumped']

    return opts

def _cleanup(ui, repo, startnode, shouldupdate):
    if not shouldupdate:
        # Move back to startnode, or to its successor if the start node is
        # obsolete (perhaps made obsolete by the current `hg evolve`)
        unfi = repo.unfiltered()
        succ = utility._singlesuccessor(repo, unfi[startnode])
        hg.updaterepo(repo, repo[succ].node(), False)
    if repo['.'].node() != startnode:
        ui.status(_('working directory is now at %s\n') % repo['.'])

def divergentsets(repo, ctx):
    """Compute sets of commits divergent with a given one"""
    cache = {}
    base = {}
    for n in obsutil.allpredecessors(repo.obsstore, [ctx.node()]):
        if n == ctx.node():
            # a node can't be a base for divergence with itself
            continue
        nsuccsets = obsutil.successorssets(repo, n, cache)
        for nsuccset in nsuccsets:
            if ctx.node() in nsuccset:
                # we are only interested in *other* successor sets
                continue
            if tuple(nsuccset) in base:
                # we already know the latest base for this divergency
                continue
            base[tuple(nsuccset)] = n
    divergence = []
    for divset, b in base.iteritems():
        divergence.append({
            'divergentnodes': divset,
            'commonprecursor': b
        })

    return divergence

@eh.command(
    'evolve|stabilize|solve',
    [('n', 'dry-run', False,
      _('do not perform actions, just print what would be done')),
     ('', 'confirm', False,
      _('ask for confirmation before performing the action')),
     ('A', 'any', False,
      _('also consider troubled changesets unrelated to current working '
        'directory')),
     ('r', 'rev', [], _('solves troubles of these revisions'), _('REV')),
     ('', 'bumped', False, _('solves only bumped changesets (DEPRECATED)')),
     ('', 'phase-divergent', False, _('solves only phase-divergent changesets')),
     ('', 'divergent', False, _('solves only divergent changesets (DEPRECATED)')),
     ('', 'content-divergent', False, _('solves only content-divergent changesets')),
     ('', 'unstable', False, _('solves only unstable changesets (DEPRECATED)')),
     ('', 'orphan', False, _('solves only orphan changesets (default)')),
     ('a', 'all', None, _('evolve all troubled changesets related to the current'
                          ' working directory and its descendants (default)')),
     ('', 'update', False, _('update to the head of evolved changesets')),
     ('c', 'continue', False, _('continue an interrupted evolution')),
     ('', 'stop', False, _('stop the interrupted evolution')),
     ('', 'abort', False, _('abort the interrupted evolution')),
     ('l', 'list', False, _('provide details on troubled changesets'
                            ' in the repo')),
    ] + mergetoolopts,
    _('[OPTIONS]...'),
    helpbasic=True
)
def evolve(ui, repo, **opts):
    """solve troubled changesets in your repository

    Modifying history can lead to various types of troubled changesets:
    orphan, phase-divergent, or content-divergent. The evolve command resolves
    your troubles by executing one of the following actions:

    - update working copy to a successor
    - rebase an orphan changeset
    - extract the desired changes from a phase-divergent changeset
    - fuse content-divergent changesets back together

    If you pass no arguments, evolve works in automatic mode: it will execute a
    single action to reduce instability related to your working copy. There are
    two cases for this action. First, if the parent of your working copy is
    obsolete, evolve updates to the parent's successor. Second, if the working
    copy parent is not obsolete but has obsolete predecessors, then evolve
    determines if there is an orphan changeset that can be rebased onto the
    working copy parent in order to reduce instability.
    If so, evolve rebases that changeset. If not, evolve refuses to guess your
    intention, and gives a hint about what you might want to do next.

    Any time evolve creates a changeset, it updates the working copy to the new
    changeset. Using ``--update`` will make evolve perform an update after any
    successful evolve operation.

    Automatic mode only handles common use cases. For example, it avoids taking
    action in the case of ambiguity, and it ignores orphan changesets that are
    not related to your working copy.
    It also refuses to solve phase-divergent or content-divergent changesets
    unless you explicitly request such behavior (see below).

    Eliminating all instability around your working copy may require multiple
    invocations of :hg:`evolve` if you use ``--rev`` or ``--no-all``. Use
    ``--all`` (which is the default behavior) to recursively select and evolve
    all orphan changesets that can be rebased onto the working copy parent.
    This is more powerful than successive invocations, since ``--all`` handles
    ambiguous cases (e.g. orphan changesets with multiple children) by evolving
    all branches.

    When your repository cannot be handled by automatic mode, you might need to
    use ``--rev`` to specify a changeset to evolve. For example, if you have
    an orphan changeset that is not related to the working copy parent,
    you could use ``--rev`` to evolve it. Or, if some changeset has multiple
    orphan children, evolve in automatic mode refuses to guess which one to
    evolve; you have to use ``--rev`` in that case.

    Alternately, ``--any`` makes evolve search for the next evolvable changeset
    regardless of whether it is related to the working copy parent.

    You can supply multiple revisions to evolve multiple troubled changesets
    in a single invocation. In revset terms, ``--any`` is equivalent to ``--rev
    first(orphan())``. ``--rev`` and ``--all`` are mutually exclusive, as are
    ``--rev`` and ``--any``.

    ``hg evolve --any --all`` is useful for cleaning up instability across all
    branches, letting evolve figure out the appropriate order and destination.

    When you have troubled changesets that are not orphan, :hg:`evolve` refuses
    to consider them unless you specify the category of trouble you
    wish to resolve, with ``--phase-divergent`` or ``--content-divergent``.
    These options are currently mutually exclusive with each other and with
    ``--orphan`` (the default). You can combine ``--phase-divergent`` or
    ``--content-divergent`` with ``--rev``, ``--all``, or ``--any``.

    You can also use the evolve command to list the troubles affecting your
    repository by using the --list flag. You can choose to display only some
    categories of troubles with the --orphan, --content-divergent or
    --phase-divergent flags.

    Interrupted
    ===========

    The `hg evolve` command is an all purpose tool that solve all kind of
    instabilities in your repository. Sometimes, instability resolution will lead
    to merge conflict that cannot be solved without a human intervention (same as
    `hg merge`). This can lead to an "interrupted state" where human assistance is
    requested. There are three things which you can do when you face a similar
    situation:

      - `hg evolve --continue`:
         fix all the conflicts using `hg resolve` and then run this to continue the
         interrupted evolve

      - `hg evolve --stop`:
         stops the current interrupted evolve, keeping all the successful steps,
         but delaying to resolution of the remaining step for later.

      - `hg evolve --abort`:
         aborts the interrupted evolve and undoes all the resolution which have
         happened
    """

    opts = _checkevolveopts(repo, opts)
    # Options
    contopt = opts['continue']
    anyopt = opts['any']
    allopt = opts['all']
    if allopt is None:
        allopt = True
    startnode = repo['.'].node()
    dryrunopt = opts['dry_run']
    confirmopt = opts['confirm']
    revopt = opts['rev']
    stopopt = opts['stop']
    abortopt = opts['abort']
    shouldupdate = opts['update']

    troublecategories = ['phase_divergent', 'content_divergent', 'orphan']
    specifiedcategories = [t.replace('_', '')
                           for t in troublecategories
                           if opts[t]]
    if opts['list']:
        ui.pager('evolve')
        listtroubles(ui, repo, specifiedcategories, **opts)
        return

    targetcat = 'orphan'
    has_some_opts = bool(revopt or anyopt or allopt or contopt or stopopt or abortopt)
    if 1 < len(specifiedcategories):
        msg = _('cannot specify more than one trouble category to solve (yet)')
        raise error.Abort(msg)
    elif len(specifiedcategories) == 1:
        targetcat = specifiedcategories[0]
    elif repo['.'].obsolete() and not has_some_opts:
        # if no args and parent is obsolete, update to successors
        return solveobswdp(ui, repo, opts)

    ui.setconfig('ui', 'forcemerge', opts.get('tool', ''), 'evolve')

    evolvestate = state.cmdstate(repo)
    # Continuation handling
    if contopt:
        if not evolvestate:
            raise error.Abort(_('no interrupted evolve to continue'))
        evolvestate.load()
        continueevolve(ui, repo, evolvestate)
        if evolvestate['command'] != 'evolve':
            evolvestate.delete()
            return
        startnode = repo.unfiltered()[evolvestate['startnode']]
        if 'update' in evolvestate:
            shouldupdate = evolvestate['update']
        evolvestate.delete()
    elif stopopt:
        if not evolvestate:
            raise error.Abort(_('no interrupted evolve to stop'))
        evolvestate.load()
        stopevolve(ui, repo, evolvestate)
        evolvestate.delete()
        return
    elif abortopt:
        if not evolvestate:
            raise error.Abort(_('no interrupted evolve to stop'))
        evolvestate.load()
        # `hg next --evolve` in play
        if evolvestate['command'] != 'evolve':
            pctx = repo['.']
            hg.updaterepo(repo, pctx.node(), True)
            ui.status(_('evolve aborted\n'))
            ui.status(_('working directory is now at %s\n')
                      % pctx.hex()[:12])
            evolvestate.delete()
            return 0
        return abortevolve(ui, repo, evolvestate)
    else:
        cmdutil.bailifchanged(repo)

        revs = _selectrevs(repo, allopt, revopt, anyopt, targetcat)

        # Case: when wdir parent is obsolete and args passed.
        # Handling it here otherwise `revs` set would change, after
        # performing update to successor of obsolete wdir parent.
        # (in case when user passes a revset related to wdir parent '.::')
        if repo['.'].obsolete():
            result = solveobswdp(ui, repo, opts)
            if result != 0 or result is True:
                return result

        if not revs:
            return _handlenotrouble(ui, repo, allopt, revopt, anyopt, targetcat)

        # Progress handling
        seen = 1
        showprogress = allopt or revopt
        count = len(revs)

        def progresscb():
            if showprogress:
                compat.progress(ui, _('evolve'), seen, unit=_('changesets'),
                                total=count)

        # Order the revisions
        revs = _orderrevs(repo, revs)

        # cbor does not know how to serialize sets, using list for skippedrevs
        stateopts = {'category': targetcat, 'replacements': {},
                     'revs': list(revs), 'confirm': confirmopt,
                     'startnode': startnode, 'skippedrevs': [],
                     'command': 'evolve', 'orphanmerge': False,
                     'bookmarkchanges': [], 'temprevs': [], 'obsmarkers': [],
                     'update': shouldupdate}
        evolvestate.addopts(stateopts)
        # lastsolved: keep track of successor of last troubled cset we evolved
        # to confirm that if atop msg should be suppressed to remove redundancy
        lastsolved = None

        activetopic = getattr(repo, 'currenttopic', '')
        with repo.wlock(), repo.lock():
            tr = repo.transaction("evolve")
            with util.acceptintervention(tr):
                for rev in revs:
                    lastsolved = _solveonerev(ui, repo, rev, evolvestate,
                                              activetopic, dryrunopt,
                                              confirmopt, progresscb,
                                              targetcat, lastsolved)
                    seen += 1

        if showprogress:
            compat.progress(ui, _('evolve'), None)

    _cleanup(ui, repo, startnode, shouldupdate)

def _solveonerev(ui, repo, rev, evolvestate, activetopic, dryrunopt, confirmopt,
                 progresscb, targetcat, lastsolved):
    """solves one trouble, including orphan merges

    Like _solveone(), this solves one trouble. Unlike _solveone(), it
    stabilizes for both parents of orphan merges.
    """
    curctx = repo[rev]
    revtopic = getattr(curctx, 'topic', lambda: '')()
    topicidx = getattr(curctx, 'topicidx', lambda: None)()
    stacktmplt = False
    # check if revision being evolved is in active topic to make sure
    # that we can use stack aliases s# in evolve msgs.
    if activetopic and (activetopic == revtopic) and topicidx is not None:
        stacktmplt = True
    progresscb()
    ret = _solveone(ui, repo, curctx, evolvestate, dryrunopt,
                    confirmopt, progresscb, targetcat,
                    lastsolved=lastsolved, stacktmplt=stacktmplt)
    if ret[0]:
        evolvestate['replacements'][curctx.node()] = ret[1]
        lastsolved = ret[1]
    else:
        evolvestate['skippedrevs'].append(curctx.node())

    if evolvestate['orphanmerge']:
        # we were processing an orphan merge with both parents obsolete,
        # stabilized for second parent, re-stabilize for the first parent
        ret = _solveone(ui, repo, repo[ret[1]], evolvestate, dryrunopt,
                        confirmopt, progresscb, targetcat,
                        stacktmplt=stacktmplt)
        if ret[0]:
            evolvestate['replacements'][curctx.node()] = ret[1]
            lastsolved = ret[1]
        else:
            evolvestate['skippedrevs'].append(curctx.node())

        evolvestate['orphanmerge'] = False
    return lastsolved

def solveobswdp(ui, repo, opts):
    """this function updates to the successor of obsolete wdir parent"""
    oldid = repo['.'].node()
    startctx = repo['.']
    dryrunopt = opts.get('dry_run', False)
    displayer = compat.changesetdisplayer(ui, repo,
                                          {'template': shorttemplate})
    try:
        ctx = repo[utility._singlesuccessor(repo, repo['.'])]
    except utility.MultipleSuccessorsError as exc:
        repo.ui.write_err(_('parent is obsolete with multiple'
                            ' successors:\n'))
        for ln in exc.successorssets:
            for n in ln:
                displayer.show(repo[n])
        return 2

    ui.status(_('update:'))
    if not ui.quiet:
        displayer.show(ctx)

    if dryrunopt:
        return 0
    res = hg.update(repo, ctx.rev())
    newid = ctx.node()

    if ctx != startctx:
        with repo.wlock(), repo.lock(), repo.transaction('evolve') as tr:
            bmupdater = rewriteutil.bookmarksupdater(repo, oldid, tr)
            bmupdater(newid)
        ui.status(_('working directory is now at %s\n') % ctx)
    return res

def stopevolve(ui, repo, evolvestate):
    """logic for handling of `hg evolve --stop`"""
    updated = False
    pctx = None
    if (evolvestate['command'] == 'evolve'
        and evolvestate['category'] == 'contentdivergent'
        and evolvestate['relocated']):
        oldother = evolvestate['old-other']
        if oldother:
            with repo.wlock(), repo.lock():
                repo = repo.unfiltered()
                hg.updaterepo(repo, oldother, True)
                strips = [evolvestate['relocated']]
                repair.strip(ui, repo, strips, False)
                updated = True
                pctx = repo[oldother]
    if not updated:
        pctx = repo['.']
        hg.updaterepo(repo, pctx.node(), True)
    ui.status(_('stopped the interrupted evolve\n'))
    ui.status(_('working directory is now at %s\n') % pctx)

def abortevolve(ui, repo, evolvestate):
    """ logic for handling of `hg evolve --abort`"""

    with repo.wlock(), repo.lock():
        repo = repo.unfiltered()
        evolvedctx = []
        # boolean value to say whether we should strip or not
        cleanup = True
        startnode = evolvestate['startnode']
        for old, new in evolvestate['replacements'].iteritems():
            if new:
                evolvedctx.append(repo[new])
        for temp in evolvestate['temprevs']:
            if temp:
                evolvedctx.append(repo[temp])
        evolvedrevs = [c.rev() for c in evolvedctx]

        # checking if phase changed of any of the evolved rev
        immutable = [c for c in evolvedctx if not c.mutable()]
        if immutable:
            repo.ui.warn(_("cannot clean up public changesets: %s\n")
                         % ', '.join(str(c) for c in immutable),
                         hint=_("see 'hg help phases' for details"))
            cleanup = False

        # checking no new changesets are created on evolved revs
        descendants = set()
        if evolvedrevs:
            descendants = set(repo.changelog.descendants(evolvedrevs))
        if descendants - set(evolvedrevs):
            repo.ui.warn(_("warning: new changesets detected on destination "
                           "branch\n"))
            cleanup = False

        # finding the indices of the obsmarkers to be stripped and stripping
        # them
        if evolvestate['obsmarkers']:
            stripmarkers = set()
            for m in evolvestate['obsmarkers']:
                m = (m[0], m[1])
                stripmarkers.add(m)
            indices = []
            allmarkers = obsutil.getmarkers(repo)
            for i, m in enumerate(allmarkers):
                marker = (m.prednode(), m.succnodes()[0])
                if marker in stripmarkers:
                    indices.append(i)

            repair.deleteobsmarkers(repo.obsstore, indices)
            repo.ui.debug('deleted %d obsmarkers\n' % len(indices))

        if cleanup:
            if evolvedrevs:
                strippoints = [c.node()
                               for c in repo.set('roots(%ld)', evolvedrevs)]

            # updating the working directory
            hg.updaterepo(repo, startnode, True)

            # Strip from the first evolved revision
            if evolvedrevs:
                # no backup of evolved cset versions needed
                repair.strip(repo.ui, repo, strippoints, False)

            with repo.transaction('evolve') as tr:
                # restoring bookmarks at there original place
                bmchanges = evolvestate['bookmarkchanges']
                if bmchanges:
                    repo._bookmarks.applychanges(repo, tr, bmchanges)

            evolvestate.delete()
            ui.status(_('evolve aborted\n'))
            ui.status(_('working directory is now at %s\n')
                      % nodemod.hex(startnode)[:12])
        else:
            raise error.Abort(_("unable to abort interrupted evolve, use 'hg "
                                "evolve --stop' to stop evolve"))

def continueevolve(ui, repo, evolvestate):
    """logic for handling of `hg evolve --continue`"""

    with repo.wlock(), repo.lock():
        ms = merge.mergestate.read(repo)
        mergeutil.checkunresolved(ms)
        if (evolvestate['command'] == 'next'
            or evolvestate['category'] == 'orphan'):
            _completeorphan(ui, repo, evolvestate)
        elif evolvestate['category'] == 'phasedivergent':
            _completephasedivergent(ui, repo, evolvestate)
        elif evolvestate['category'] == 'contentdivergent':
            _continuecontentdivergent(ui, repo, evolvestate, None)
        else:
            repo.ui.status(_("continuing interrupted '%s' resolution is not yet"
                             " supported\n") % evolvestate['category'])
            return

        # make sure we are continuing evolve and not `hg next --evolve`
        if evolvestate['command'] != 'evolve':
            return

        # Progress handling
        seen = 1
        count = len(evolvestate['revs'])

        def progresscb():
            compat.progress(ui, _('evolve'), seen, unit=_('changesets'),
                            total=count)

        category = evolvestate['category']
        confirm = evolvestate['confirm']
        unfi = repo.unfiltered()
        # lastsolved: keep track of successor of last troubled cset we
        # evolved to confirm that if atop msg should be suppressed to remove
        # redundancy
        lastsolved = None
        activetopic = getattr(repo, 'currenttopic', '')
        tr = repo.transaction("evolve")
        with util.acceptintervention(tr):
            for rev in evolvestate['revs']:
                # XXX: prevent this lookup by storing nodes instead of revnums
                curctx = unfi[rev]

                # check if we can use stack template
                revtopic = getattr(curctx, 'topic', lambda: '')()
                topicidx = getattr(curctx, 'topicidx', lambda: None)()
                stacktmplt = False
                if (activetopic and (activetopic == revtopic)
                    and topicidx is not None):
                    stacktmplt = True

                if (curctx.node() not in evolvestate['replacements']
                    and curctx.node() not in evolvestate['skippedrevs']):
                    newnode = _solveone(ui, repo, curctx, evolvestate, False,
                                        confirm, progresscb, category,
                                        lastsolved=lastsolved,
                                        stacktmplt=stacktmplt)
                    if newnode[0]:
                        evolvestate['replacements'][curctx.node()] = newnode[1]
                        lastsolved = newnode[1]
                    else:
                        evolvestate['skippedrevs'].append(curctx.node())
                seen += 1

def _continuecontentdivergent(ui, repo, evolvestate, progresscb):
    """function to continue the interrupted content-divergence resolution."""
    tr = repo.transaction('evolve')
    with util.acceptintervention(tr):
        divergent = evolvestate['divergent']
        base = evolvestate['base']
        repo = repo.unfiltered()
        if evolvestate['relocating']:
            newother = _completerelocation(ui, repo, evolvestate)
            current = repo[evolvestate['current']]
            obsolete.createmarkers(repo, [(current, (repo[newother],))],
                                   operation='evolve')
            evolvestate['relocating'] = False
            evolvestate['relocated'] = newother
            evolvestate['temprevs'].append(newother)
            evolvestate['other-divergent'] = newother
            # continue the resolution by merging the content-divergence
            _mergecontentdivergents(repo, progresscb,
                                    repo[divergent],
                                    repo[newother],
                                    repo[base],
                                    evolvestate)

        other = evolvestate['other-divergent']
        ret = _completecontentdivergent(ui, repo, progresscb,
                                        repo[divergent],
                                        repo[other],
                                        repo[base],
                                        evolvestate)
        origdivergent = evolvestate['orig-divergent']
        evolvestate['replacements'][origdivergent] = ret[1]
        # logic to continue the public content-divergent
        publicnode = evolvestate.get('public-divergent')
        if publicnode:
            res, newnode = ret
            if not res:
                # no need to proceed for phase divergence resolution step
                pass
            elif newnode == publicnode:
                # merging had the same changes as public changeset and
                # divergence has been resolved by creating markers
                pass
            else:
                prec = repo[publicnode]
                bumped = repo[newnode]
                ret = _resolvephasedivergent(ui, repo, prec=prec, bumped=bumped)
        return ret

def _completephasedivergent(ui, repo, evolvestate):
    """function to complete the interrupted phase-divergence resolution.

    First completes the relocation of the commit and then process resolving
    phase-divergence"""

    # need to start transaction for bookmark changes
    with repo.transaction('evolve'):
        node = _completerelocation(ui, repo, evolvestate)
        evolvestate['temprevs'].append(node)
        # resolving conflicts can lead to empty wdir and node can be None in
        # those cases
        ctx = repo[evolvestate['current']]
        newctx = repo[node] if node is not None else repo['.']
        obsolete.createmarkers(repo, [(ctx, (newctx,))], operation='evolve')

        # now continuing the phase-divergence resolution part
        prec = repo[evolvestate['precursor']]
        retvalue = _resolvephasedivergent(ui, repo, prec, newctx)
        evolvestate['replacements'][ctx.node()] = retvalue[1]

def _completeorphan(ui, repo, evolvestate):
    """function to complete the interrupted orphan resolution"""

    node = _completerelocation(ui, repo, evolvestate)
    # resolving conflicts can lead to empty wdir and node can be None in
    # those cases
    ctx = repo[evolvestate['current']]
    if node is None:
        repo.ui.status(_("evolution of %d:%s created no changes"
                         " to commit\n") % (ctx.rev(), ctx))
    newctx = repo[node] if node is not None else repo['.']
    obsolete.createmarkers(repo, [(ctx, (newctx,))], operation='evolve')

    # make sure we are continuing evolve and not `hg next --evolve`
    if evolvestate['command'] == 'evolve':
        evolvestate['replacements'][ctx.node()] = node
        if evolvestate['orphanmerge']:
            # processing a merge changeset with both parents obsoleted,
            # stabilized on second parent, insert in front of list to
            # re-process to stabilize on first parent
            evolvestate['revs'].insert(0, repo[node].rev())
            evolvestate['orphanmerge'] = False

def _completerelocation(ui, repo, evolvestate):
    """function to complete the interrupted relocation of a commit
    return the new node formed
    """

    orig = repo[evolvestate['current']]
    ctx = orig
    source = ctx.extra().get('source')
    extra = {}
    if source:
        extra['source'] = source
        extra['intermediate-source'] = ctx.hex()
    else:
        extra['source'] = ctx.hex()
    user = ctx.user()
    date = ctx.date()
    message = ctx.description()
    ui.status(_('evolving %d:%s "%s"\n') % (ctx.rev(), ctx,
                                            message.split('\n', 1)[0]))
    targetphase = max(ctx.phase(), phases.draft)
    overrides = {('phases', 'new-commit'): targetphase}

    ctxparents = orig.parents()
    if len(ctxparents) == 2:
        currentp1 = repo.dirstate.parents()[0]
        p1obs = ctxparents[0].obsolete()
        p2obs = ctxparents[1].obsolete()
        # asumming that the parent of current wdir is successor of one
        # of p1 or p2 of the original changeset
        if p1obs and not p2obs:
            # p1 is obsolete and p2 is not obsolete, current working
            # directory parent should be successor of p1, so we should
            # set dirstate parents to (succ of p1, p2)
            with repo.dirstate.parentchange():
                repo.dirstate.setparents(currentp1,
                                         ctxparents[1].node())
        elif p2obs and not p1obs:
            # p2 is obsolete and p1 is not obsolete, current working
            # directory parent should be successor of p2, so we should
            # set dirstate parents to (succ of p2, p1)
            with repo.dirstate.parentchange():
                repo.dirstate.setparents(ctxparents[0].node(),
                                         currentp1)

        else:
            # both the parents were obsoleted, if orphanmerge is set, we
            # are processing the second parent first (to keep parent order)
            if evolvestate.get('orphanmerge'):
                with repo.dirstate.parentchange():
                    repo.dirstate.setparents(ctxparents[0].node(),
                                             currentp1)
            pass
    else:
        with repo.dirstate.parentchange():
            repo.dirstate.setparents(repo.dirstate.parents()[0], nodemod.nullid)

    with repo.ui.configoverride(overrides, 'evolve-continue'):
        node = repo.commit(text=message, user=user,
                           date=date, extra=extra)
    return node
