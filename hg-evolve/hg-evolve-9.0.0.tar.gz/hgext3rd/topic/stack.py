# stack.py - code related to stack workflow
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
from mercurial.i18n import _
from mercurial import (
    destutil,
    error,
    node,
    phases,
    obsolete,
    util,
)
from .evolvebits import (
    _singlesuccessor,
    MultipleSuccessorsError,
    builddependencies,
)

short = node.short

def parseusername(user):
    """parses the ctx user and returns the username without email ID if
    possible, otherwise returns the mail address from that"""
    username = None
    if user:
        # user is of form "abc <abc@xyz.com>"
        username = user.split('<')[0]
        if not username:
            # assuming user is of form "<abc@xyz.com>"
            if len(user) > 1:
                username = user[1:-1]
            else:
                username = user
        username = username.strip()

    return username

def _stackcandidates(repo):
    """build the smaller set of revs that might be part of a stack.

    The intend is to build something more efficient than what revsets do in
    this area.
    """
    phasesets = repo._phasecache._phasesets
    if not phasesets or None in phasesets[phases.draft:]:
        return repo.revs('(not public()) - obsolete()')

    result = set.union(*phasesets[phases.draft:])
    result -= obsolete.getrevs(repo, 'obsolete')
    return result

class stack(object):
    """object represent a stack and common logic associated to it."""

    def __init__(self, repo, branch=None, topic=None):
        self._repo = repo
        self.branch = branch
        self.topic = topic
        self.behinderror = None

        subset = _stackcandidates(repo)

        if topic is not None and branch is not None:
            raise error.ProgrammingError('both branch and topic specified (not defined yet)')
        elif topic is not None:
            trevs = repo.revs("%ld and topic(%s)", subset, topic)
        elif branch is not None:
            trevs = repo.revs("%ld and branch(%s) - topic()", subset, branch)
        else:
            raise error.ProgrammingError('neither branch and topic specified (not defined yet)')
        self._revs = trevs

    def __iter__(self):
        return iter(self.revs)

    def __getitem__(self, index):
        return self.revs[index]

    def __nonzero__(self):
        return bool(self._revs)

    __bool__ = __nonzero__

    def index(self, item):
        return self.revs.index(item)

    @util.propertycache
    def _dependencies(self):
        deps, rdeps = builddependencies(self._repo, self._revs)

        repo = self._repo
        srcpfunc = repo.changelog.parentrevs

        ### post process to skip over possible gaps in the stack
        #
        # For example in the following situation, we need to detect that "t3"
        # indirectly depends on t2.
        #
        #  o t3
        #  |
        #  o other
        #  |
        #  o t2
        #  |
        #  o t1

        pmap = {}

        def pfuncrev(repo, rev):
            """a special "parent func" that also consider successors"""
            parents = pmap.get(rev)
            if parents is None:
                parents = [repo[_singlesuccessor(repo, repo[p])].rev()
                           for p in srcpfunc(rev) if 0 <= p]
                pmap[rev] = parents
            return parents

        revs = self._revs
        stackrevs = set(self._revs)
        for root in [r for r in revs if not deps[r]]:
            seen = set()
            stack = [root]
            while stack:
                current = stack.pop()
                for p in pfuncrev(repo, current):
                    if p in seen:
                        continue
                    seen.add(p)
                    if p in stackrevs:
                        rdeps[p].add(root)
                        deps[root].add(p)
                    elif phases.public < repo[p].phase():
                        # traverse only if we did not found a proper candidate
                        stack.append(p)

        return deps, rdeps

    @util.propertycache
    def revs(self):
        # some duplication/change from _orderrevs because we use a post
        # processed dependency graph.

        # Step 1: compute relation of revision with each other
        dependencies, rdependencies = self._dependencies
        dependencies = dependencies.copy()
        rdependencies = rdependencies.copy()
        # Step 2: Build the ordering
        # Remove the revisions with no dependency(A) and add them to the ordering.
        # Removing these revisions leads to new revisions with no dependency (the
        # one depending on A) that we can remove from the dependency graph and add
        # to the ordering. We progress in a similar fashion until the ordering is
        # built
        solvablerevs = [r for r in sorted(dependencies.keys())
                        if not dependencies[r]]
        revs = []
        while solvablerevs:
            rev = solvablerevs.pop()
            for dependent in rdependencies[rev]:
                dependencies[dependent].remove(rev)
                if not dependencies[dependent]:
                    solvablerevs.append(dependent)
            del dependencies[rev]
            revs.append(rev)

        revs.extend(sorted(dependencies))
        # step 3: add t0
        if revs:
            pt1 = self._repo[revs[0]].p1()
        else:
            pt1 = self._repo['.']

        if pt1.obsolete():
            pt1 = self._repo[_singlesuccessor(self._repo, pt1)]
        revs.insert(0, pt1.rev())
        return revs

    @util.propertycache
    def changesetcount(self):
        return len(self._revs)

    @util.propertycache
    def unstablecount(self):
        return len([r for r in self._revs if self._repo[r].isunstable()])

    @util.propertycache
    def heads(self):
        revs = self.revs[1:]
        deps, rdeps = self._dependencies
        return [r for r in revs if not rdeps[r]]

    @util.propertycache
    def behindcount(self):
        revs = self.revs[1:]
        deps, rdeps = self._dependencies
        if revs:
            minroot = [min(r for r in revs if not deps[r])]
            try:
                dest = destutil.destmerge(self._repo, action='rebase',
                                          sourceset=minroot,
                                          onheadcheck=False)
                return len(self._repo.revs("only(%d, %ld)", dest, minroot))
            except error.NoMergeDestAbort:
                return 0
            except error.ManyMergeDestAbort as exc:
                # XXX we should make it easier for upstream to provide the information
                self.behinderror = str(exc).split('-', 1)[0].rstrip()
                return -1
        return 0

    @util.propertycache
    def branches(self):
        branches = sorted(set(self._repo[r].branch() for r in self._revs))
        if not branches:
            branches = set([self._repo[None].branch()])
        return branches

def labelsgen(prefix, parts):
    fmt = prefix + '.%s'
    return prefix + ' ' + ' '.join(fmt % p.replace(' ', '-') for p in parts)

def showstack(ui, repo, branch=None, topic=None, opts=None):
    if opts is None:
        opts = {}

    if topic is not None and branch is not None:
        msg = 'both branch and topic specified [%s]{%s}(not defined yet)'
        msg %= (branch, topic)
        raise error.ProgrammingError(msg)
    elif topic is not None:
        prefix = 's'
        if topic not in repo.topics:
            raise error.Abort(_('cannot resolve "%s": no such topic found') % topic)
    elif branch is not None:
        prefix = 's'
    else:
        raise error.ProgrammingError('neither branch and topic specified (not defined yet)')

    fm = ui.formatter('topicstack', opts)
    prev = None
    entries = []
    idxmap = {}

    label = 'topic'
    if topic == repo.currenttopic:
        label = 'topic.active'

    st = stack(repo, branch, topic)
    if topic is not None:
        fm.plain(_('### topic: %s')
                 % ui.label(topic, label),
                 label='stack.summary.topic')

        if 1 < len(st.heads):
            fm.plain(' (')
            fm.plain('%d heads' % len(st.heads),
                     label='stack.summary.headcount.multiple')
            fm.plain(')')
        fm.plain('\n')
    fm.plain(_('### target: %s (branch)')
             % '+'.join(st.branches), # XXX handle multi branches
             label='stack.summary.branches')
    if topic is None:
        if 1 < len(st.heads):
            fm.plain(' (')
            fm.plain('%d heads' % len(st.heads),
                     label='stack.summary.headcount.multiple')
            fm.plain(')')
    else:
        if st.behindcount == -1:
            fm.plain(', ')
            fm.plain('ambiguous rebase destination - %s' % st.behinderror,
                     label='stack.summary.behinderror')
        elif st.behindcount:
            fm.plain(', ')
            fm.plain('%d behind' % st.behindcount, label='stack.summary.behindcount')
    fm.plain('\n')

    if not st:
        fm.plain(_("(stack is empty)\n"))

    st = stack(repo, branch=branch, topic=topic)
    for idx, r in enumerate(st, 0):
        ctx = repo[r]
        # special case for t0, b0 as it's hard to plugin into rest of the logic
        if idx == 0:
            # t0, b0 can be None
            if r == -1:
                continue
            entries.append((idx, False, ctx))
            prev = ctx.rev()
            continue
        p1 = ctx.p1()
        p2 = ctx.p2()
        if p1.obsolete():
            try:
                p1 = repo[_singlesuccessor(repo, p1)]
            except MultipleSuccessorsError as e:
                successors = e.successorssets
                if len(successors) > 1:
                    # case of divergence which we don't handle yet
                    raise
                p1 = repo[successors[0][-1]]

        if p2.node() != node.nullid:
            entries.append((idxmap.get(p1.rev()), False, p1))
            entries.append((idxmap.get(p2.rev()), False, p2))
        elif p1.rev() != prev and p1.node() != node.nullid:
            entries.append((idxmap.get(p1.rev()), False, p1))
        entries.append((idx, True, ctx))
        idxmap[ctx.rev()] = idx
        prev = r

    # super crude initial version
    for idx, isentry, ctx in entries[::-1]:

        symbol = None
        states = []
        if opts.get('children'):
            expr = 'children(%d) and merge() - %ld'
            revisions = repo.revs(expr, ctx.rev(), st._revs)
            if len(revisions) > 0:
                states.append('external-children')

        if ctx.orphan():
            symbol = '$'
            states.append('orphan')

        if ctx.contentdivergent():
            symbol = '$'
            states.append('content divergent')

        if ctx.phasedivergent():
            symbol = '$'
            states.append('phase divergent')

        iscurrentrevision = repo.revs('%d and parents()', ctx.rev())
        if iscurrentrevision:
            symbol = '@'
            states.append('current')

        if not isentry:
            symbol = '^'
            # "base" is kind of a "ghost" entry
            states.append('base')

        # none of the above if statments get executed
        if not symbol:
            symbol = ':'

        if not states:
            states.append('clean')

        states.sort()

        fm.startitem()
        fm.context(ctx=ctx)
        fm.data(isentry=isentry)

        if idx is None:
            spacewidth = 0
            if ui.verbose:
                # parentheses plus short node hash
                spacewidth = 2 + 12
            if ui.debugflag:
                # parentheses plus full node hash
                spacewidth = 2 + 40
            # s# alias width
            spacewidth += 2
            fm.plain(' ' * spacewidth)
        else:
            fm.write('stack_index', '%s%%d' % prefix, idx,
                     label=labelsgen('stack.index', states))
            if ui.verbose:
                fm.write('node', '(%s)', fm.hexfunc(ctx.node()),
                         label=labelsgen('stack.shortnode', states))
            else:
                fm.data(node=fm.hexfunc(ctx.node()))
        fm.write('symbol', '%s', symbol,
                 label=labelsgen('stack.state', states))
        fm.plain(' ')
        fm.write('desc', '%s', ctx.description().splitlines()[0],
                 label=labelsgen('stack.desc', states))
        fm.condwrite(states != ['clean'] and idx is not None, 'state',
                     ' (%s)', fm.formatlist(states, 'stack.state'),
                     label=labelsgen('stack.state', states))
        fm.plain('\n')
    fm.end()
