# Extension to provide automatic caching of bundle server for pull
#
# Copyright 2018 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""pullbundle: automatic server side bundle caching

General principle
=================

This extension provides a means for server to use pre-computed bundle for
serving arbitrary pulls. If missing, the necessary pre-computed bundle will be
generated on demand.

To maximize usage of existing cached bundle, each pull will be served through
multiple bundles. The bundle will be created using "standard range" from the
"stablerange" principle. The "stablerange" concept if already used for
obsmarkers discovery in the evolve extensions.

Using pull Bundle
=================

All configuration is only required server side.

The "stablerange" code currently still live in the evolve extensions, so for
now enabling that extensions is required:

You need at minimum the following configuration:

    [extensions]
    evolve=yes
    pullbundle=yes
    [experimental]
    obshashrange.warm-cache = yes

If you do not want to use evolution server side, you should disable obsmarkers exchange:

    [experimental]
    evolution.exchange=no

Extra Configuration
===================

  [pullbundle]
  # By default bundles are stored `.hg/cache/pullbundles/.
  # This can be changed with the following config:
  cache-directory=/absolute/path

Implementation status
=====================

Both for stablerange and pullbundle use "simple" initial implementations.
Theses implemenations focus on testing the algorithms and proving the features
works. Yet they are already useful and used in production.

Performances are expected to greatly improved in the final implementation,
especially if some of it end up being compiled code.

This first implementation lacks the ability to server the cached bundle from a
CDN. We'll want this limitation to be lifted quickly.

The way mercurial core report progress is designed for the receival of a single
changegroup. So currently using pullbundle means flooding the user with output.
This will have to be fixed.

Why is does this live in the same repository as evolve
======================================================

There is no fundamental reasons for live in the same repository. However, the
stablerange data-structure lives in evolve, so it was simpler to put this new
extensions next to it. As soon as stable range have been upstreamed, we won't
need the dependency to the evolve extension anymore.
"""

import collections
import errno
import random
import os

from mercurial import (
    changegroup,
    discovery,
    error,
    exchange,
    narrowspec,
    node as nodemod,
    registrar,
    scmutil,
    util,
)

from mercurial.i18n import _

__version__ = '0.1.1'
testedwith = '4.4 4.5 4.6 4.7.1'
minimumhgversion = '4.4'
buglink = 'https://bz.mercurial-scm.org/'

cmdtable = {}
command = registrar.command(cmdtable)

configtable = {}
configitem = registrar.configitem(configtable)

configitem('pullbundle', 'cache-directory',
           default=None,
)

# generic wrapping

def uisetup(ui):
    exchange.getbundle2partsmapping['changegroup'] = _getbundlechangegrouppart

def _getbundlechangegrouppart(bundler, repo, source, bundlecaps=None,
                              b2caps=None, heads=None, common=None, **kwargs):
    """add a changegroup part to the requested bundle"""
    if not kwargs.get(r'cg', True):
        return

    version = '01'
    cgversions = b2caps.get('changegroup')
    if cgversions:  # 3.1 and 3.2 ship with an empty value
        cgversions = [v for v in cgversions
                      if v in changegroup.supportedoutgoingversions(repo)]
        if not cgversions:
            raise ValueError(_('no common changegroup version'))
        version = max(cgversions)

    outgoing = exchange._computeoutgoing(repo, heads, common)
    if not outgoing.missing:
        return

    if kwargs.get(r'narrow', False):
        include = sorted(filter(bool, kwargs.get(r'includepats', [])))
        exclude = sorted(filter(bool, kwargs.get(r'excludepats', [])))
        filematcher = narrowspec.match(repo.root, include=include,
                                       exclude=exclude)
    else:
        filematcher = None

    # START OF ALTERED PART
    makeallcgpart(bundler.newpart, repo, outgoing, version, source, bundlecaps,
                  filematcher, cgversions)
    # END OF ALTERED PART

    if kwargs.get(r'narrow', False) and (include or exclude):
        narrowspecpart = bundler.newpart('narrow:spec')
        if include:
            narrowspecpart.addparam(
                'include', '\n'.join(include), mandatory=True)
        if exclude:
            narrowspecpart.addparam(
                'exclude', '\n'.join(exclude), mandatory=True)

def makeallcgpart(newpart, repo, outgoing, version, source,
                  bundlecaps, filematcher, cgversions):

    pullbundle = not filematcher
    if pullbundle and not util.safehasattr(repo, 'stablerange'):
        repo.ui.warn('pullbundle: required extension "evolve" are missing, skipping pullbundle\n')
        pullbundle = False
    if filematcher:
        makeonecgpart(newpart, repo, None, outgoing, version, source, bundlecaps,
                      filematcher, cgversions)
    else:
        start = util.timer()
        slices = sliceoutgoing(repo, outgoing)
        end = util.timer()
        msg = _('pullbundle-cache: "missing" set sliced into %d subranges '
                'in %s seconds\n')
        repo.ui.write(msg % (len(slices), end - start))
        for sliceid, sliceout in slices:
            makeonecgpart(newpart, repo, sliceid, sliceout, version, source, bundlecaps,
                          filematcher, cgversions)

# stable range slicing

DEBUG = False

def sliceoutgoing(repo, outgoing):
    cl = repo.changelog
    rev = cl.nodemap.get
    node = cl.node
    revsort = repo.stablesort

    missingrevs = set(rev(n) for n in outgoing.missing)
    if DEBUG:
        ms = missingrevs.copy()
        ss = []
    allslices = []
    missingheads = [rev(n) for n in sorted(outgoing.missingheads, reverse=True)]
    for head in missingheads:
        localslices = []
        localmissing = set(repo.revs('%ld and ::%d', missingrevs, head))
        thisrunmissing = localmissing.copy()
        while localmissing:
            slicerevs = []
            for r in revsort.walkfrom(repo, head):
                if r not in thisrunmissing:
                    break
                slicerevs.append(r)
            slicenodes = [node(r) for r in slicerevs]
            localslices.append(canonicalslices(repo, slicenodes))
            if DEBUG:
                ss.append(slicerevs)
            missingrevs.difference_update(slicerevs)
            localmissing.difference_update(slicerevs)
            if localmissing:
                heads = list(repo.revs('heads(%ld)', localmissing))
                heads.sort(key=node)
                head = heads.pop()
                if heads:
                    thisrunmissing = repo.revs('%ld and only(%d, %ld)',
                                               localmissing,
                                               head,
                                               heads)
                else:
                    thisrunmissing = localmissing.copy()
        if DEBUG:
            for s in reversed(ss):
                ms -= set(s)
                missingbase = repo.revs('parents(%ld) and %ld', s, ms)
                if missingbase:
                    repo.ui.write_err('!!! rev bundled while parents missing\n')
                    repo.ui.write_err('    parent: %s\n' % list(missingbase))
                    pb = repo.revs('%ld and children(%ld)', s, missingbase)
                    repo.ui.write_err('    children: %s\n' % list(pb))
                    h = repo.revs('heads(%ld)', s)
                    repo.ui.write_err('    heads: %s\n' % list(h))
                    raise error.ProgrammingError('issuing a range before its parents')

        for s in reversed(localslices):
            allslices.extend(s)
    # unknown subrange might had to be computed
    repo.stablerange.save(repo)
    return [(rangeid, outgoingfromnodes(repo, nodes))
            for rangeid, nodes in allslices]

def canonicalslices(repo, nodes):
    depth = repo.depthcache.get
    stablerange = repo.stablerange
    rangelength = lambda x: stablerange.rangelength(repo, x)
    headrev = repo.changelog.rev(nodes[0])
    nbrevs = len(nodes)
    headdepth = depth(headrev)
    skipped = headdepth - nbrevs
    rangeid = (headrev, skipped)

    subranges = canonicalsubranges(repo, stablerange, rangeid)
    idx = 0
    slices = []
    nodes.reverse()
    for rangeid in subranges:
        size = rangelength(rangeid)
        slices.append((rangeid, nodes[idx:idx + size]))
        idx += size
    ### slow code block to validate ranges content
    # rev = repo.changelog.nodemap.get
    # for ri, ns in slices:
    #     a = set(rev(n) for n in ns)
    #     b = set(repo.stablerange.revsfromrange(repo, ri))
    #     l = repo.stablerange.rangelength(repo, ri)
    #     repo.ui.write('range-length: %d-%d %s %s\n' % (ri[0], ri[1], l, len(a)))
    #     if a != b:
    #         d =  (ri[0], ri[1], b - a, a - b)
    #         repo.ui.write("mismatching content: %d-%d -%s +%s\n" % d)
    return slices

def canonicalsubranges(repo, stablerange, rangeid):
    """slice a size of nodes into most reusable subranges

    We try to slice a range into a set of "largest" and "canonical" stable
    range.

    It might make sense to move this function as a 'stablerange' method.
    """
    headrev, skip = rangeid
    rangedepth = stablerange.depthrev(repo, rangeid[0])
    canonicals = []

    # 0. find the first power of 2 higher than this range depth
    cursor = 1
    while cursor <= rangedepth:
        cursor *= 2

    # 1. find first cupt
    precut = cut = 0
    while True:
        if skip <= cut:
            break
        if cut + cursor < rangedepth:
            precut = cut
            cut += cursor
        if cursor == 1:
            break
        cursor //= 2

    # 2. optimise, bottom part
    if skip != cut:
        currentsize = tailsize = cut - skip
        assert 0 < tailsize, tailsize

        # we need to take several "standard cut" in the bottom part
        #
        # This is similar to what we will do for the top part, we reusing the
        # existing structure is a bit more complex.
        allcuts = list(reversed(standardcut(tailsize)))
        prerange = (headrev, precut)
        ### slow code block to check we operate on the right data
        # rev = repo.changelog.nodemap.get
        # allrevs = [rev(n) for n in nodes]
        # allrevs.reverse()
        # prerevs = repo.stablerange.revsfromrange(repo, prerange)
        # assert allrevs == prerevs[(len(prerevs) - len(allrevs)):]
        # end of check
        sub = list(stablerange.subranges(repo, prerange)[:-1])

        bottomranges = []
        # XXX we might be able to reuse core stable-range logic instead of
        # redoing this manually
        currentrange = sub.pop()
        currentsize = stablerange.rangelength(repo, currentrange)
        currentcut = None
        while allcuts or currentcut is not None:
            # get the next cut if needed
            if currentcut is None:
                currentcut = allcuts.pop()
            # deal attemp a cut
            if currentsize == currentcut:
                bottomranges.append(currentrange)
                currentcut = None
            elif currentsize < currentcut:
                bottomranges.append(currentrange)
                currentcut -= currentsize
            else: # currentsize > currentcut
                newskip = currentrange[1] + (currentsize - currentcut)
                currentsub = stablerange._slicesrangeat(repo, currentrange, newskip)
                bottomranges.append(currentsub.pop())
                sub.extend(currentsub)
                currentcut = None
            currentrange = sub.pop()
            currentsize = stablerange.rangelength(repo, currentrange)
        bottomranges.reverse()
        canonicals.extend(bottomranges)

    # 3. take recursive subrange until we get to a power of two size?
    current = (headrev, cut)
    while not poweroftwo(stablerange.rangelength(repo, current)):
        sub = stablerange.subranges(repo, current)
        canonicals.extend(sub[:-1])
        current = sub[-1]
    canonicals.append(current)

    return canonicals

def standardcut(size):
    assert 0 < size
    # 0. find the first power of 2 higher than this range depth
    cut = 1
    while cut <= size:
        cut *= 2

    allcuts = []
    # 1. find all standard expected cut
    while 1 < cut and size:
        cut //= 2
        if cut <= size:
            allcuts.append(cut)
            size -= cut
    return allcuts

def poweroftwo(num):
    return num and not num & (num - 1)

def outgoingfromnodes(repo, nodes):
    return discovery.outgoing(repo,
                              missingroots=nodes,
                              missingheads=nodes)

# changegroup part construction

def _changegroupinfo(repo, nodes, source):
    if repo.ui.verbose or source == 'bundle':
        repo.ui.status(_("%d changesets found\n") % len(nodes))

def _makenewstream(newpart, repo, outgoing, version, source,
                   bundlecaps, filematcher, cgversions):
    old = changegroup._changegroupinfo
    try:
        changegroup._changegroupinfo = _changegroupinfo
        if filematcher is not None:
            cgstream = changegroup.makestream(repo, outgoing, version, source,
                                              bundlecaps=bundlecaps,
                                              filematcher=filematcher)
        else:
            cgstream = changegroup.makestream(repo, outgoing, version, source,
                                              bundlecaps=bundlecaps)
    finally:
        changegroup._changegroupinfo = old

    nbchanges = len(outgoing.missing)
    pversion = None
    if cgversions:
        pversion = version
    return (cgstream, nbchanges, pversion)

def _makepartfromstream(newpart, repo, cgstream, nbchanges, version):
    # same as upstream code

    part = newpart('changegroup', data=cgstream)
    if version:
        part.addparam('version', version)

    part.addparam('nbchanges', '%d' % nbchanges,
                  mandatory=False)

    if 'treemanifest' in repo.requirements:
        part.addparam('treemanifest', '1')

# cache management

def cachedir(repo):
    cachedir = repo.ui.config('pullbundle', 'cache-directory')
    if cachedir is not None:
        return cachedir
    return repo.cachevfs.join('pullbundles')

def getcache(repo, bundlename):
    cdir = cachedir(repo)
    bundlepath = os.path.join(cdir, bundlename)
    if not os.path.exists(bundlepath):
        return None
    # delay file opening as much as possible this introduce a small race
    # condition if someone remove the file before we actually use it. However
    # opening too many file will not work.

    def data():
        with open(bundlepath, 'rb') as fd:
            for chunk in util.filechunkiter(fd):
                yield chunk
    return data()

def cachewriter(repo, bundlename, stream):
    cdir = cachedir(repo)
    bundlepath = os.path.join(cdir, bundlename)
    try:
        os.makedirs(cdir)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
    with util.atomictempfile(bundlepath) as cachefile:
        for chunk in stream:
            cachefile.write(chunk)
            yield chunk

BUNDLEMASK = "%s-%s-%010iskip-%010isize.hg"

def makeonecgpart(newpart, repo, rangeid, outgoing, version, source,
                  bundlecaps, filematcher, cgversions):
    bundlename = cachedata = None
    if rangeid is not None:
        nbchanges = repo.stablerange.rangelength(repo, rangeid)
        headnode = nodemod.hex(repo.changelog.node(rangeid[0]))
        # XXX do we need to use cgversion in there?
        bundlename = BUNDLEMASK % (version, headnode, rangeid[1], nbchanges)
        cachedata = getcache(repo, bundlename)
    if cachedata is None:
        partdata = _makenewstream(newpart, repo, outgoing, version, source,
                                  bundlecaps, filematcher, cgversions)
        if bundlename is not None:
            cgstream = cachewriter(repo, bundlename, partdata[0])
            partdata = (cgstream,) + partdata[1:]
    else:
        if repo.ui.verbose or source == 'bundle':
            repo.ui.status(_("%d changesets found in caches\n") % nbchanges)
        pversion = None
        if cgversions:
            pversion = version
        partdata = (cachedata, nbchanges, pversion)
    return _makepartfromstream(newpart, repo, *partdata)

@command('debugpullbundlecacheoverlap',
         [('', 'count', 100, _('of "client" pulling')),
          ('', 'min-cache', 1, _('minimum size of cached bundle')),
         ],
         _('hg debugpullbundlecacheoverlap [--client 100] REVSET'))
def debugpullbundlecacheoverlap(ui, repo, *revs, **opts):
    '''Display statistic on bundle cache hit

    This command "simulate pulls from multiple clients. Each using a random
    subset of revisions defined by REVSET. And display statistic about the
    overlap in bundle necessary to serve them.
    '''
    actionrevs = scmutil.revrange(repo, revs)
    if not revs:
        raise error.Abort('No revision selected')
    count = opts['count']
    min_cache = opts['min_cache']

    bundlehits = collections.defaultdict(lambda: 0)
    pullstats = []

    rlen = lambda rangeid: repo.stablerange.rangelength(repo, rangeid)

    repo.ui.write("gathering %d sample pulls within %d revisions\n"
                  % (count, len(actionrevs)))
    if 1 < min_cache:
        repo.ui.write("  not caching ranges smaller than %d changesets\n" % min_cache)
    for i in xrange(count):
        repo.ui.progress('gathering data', i, total=count)
        outgoing = takeonesample(repo, actionrevs)
        ranges = sliceoutgoing(repo, outgoing)
        hitranges = 0
        hitchanges = 0
        totalchanges = 0
        largeranges = []
        for rangeid, __ in ranges:
            length = rlen(rangeid)
            totalchanges += length
            if bundlehits[rangeid]:
                hitranges += 1
                hitchanges += rlen(rangeid)
            if min_cache <= length:
                bundlehits[rangeid] += 1
                largeranges.append(rangeid)

        stats = (len(outgoing.missing),
                 totalchanges,
                 hitchanges,
                 len(largeranges),
                 hitranges,
                 )
        pullstats.append(stats)
    repo.ui.progress('gathering data', None)

    sizes = []
    changesmissing = []
    totalchanges = 0
    totalcached = 0
    changesratio = []
    rangesratio = []
    bundlecount = []
    for entry in pullstats:
        sizes.append(entry[0])
        changesmissing.append(entry[1] - entry[2])
        changesratio.append(entry[2] / float(entry[1]))
        if entry[3]:
            rangesratio.append(entry[4] / float(entry[3]))
        else:
            rangesratio.append(1)
        bundlecount.append(entry[3])
        totalchanges += entry[1]
        totalcached += entry[2]

    cachedsizes = []
    cachedhits = []
    for rangeid, hits in bundlehits.items():
        if hits <= 0:
            continue
        length = rlen(rangeid)
        cachedsizes.append(length)
        cachedhits.append(hits)

    sizesdist = distribution(sizes)
    repo.ui.write(fmtdist('pull size', sizesdist))

    changesmissingdist = distribution(changesmissing)
    repo.ui.write(fmtdist('non-cached changesets', changesmissingdist))

    changesratiodist = distribution(changesratio)
    repo.ui.write(fmtdist('ratio of cached changesets', changesratiodist))

    bundlecountdist = distribution(bundlecount)
    repo.ui.write(fmtdist('bundle count', bundlecountdist))

    rangesratiodist = distribution(rangesratio)
    repo.ui.write(fmtdist('ratio of cached bundles', rangesratiodist))

    repo.ui.write('changesets served:\n')
    repo.ui.write('  total:      %7d\n' % totalchanges)
    repo.ui.write('  from cache: %7d (%2d%%)\n'
                  % (totalcached, (totalcached * 100 // totalchanges)))
    repo.ui.write('  bundle:     %7d\n' % sum(bundlecount))

    cachedsizesdist = distribution(cachedsizes)
    repo.ui.write(fmtdist('size of cached bundles', cachedsizesdist))

    cachedhitsdist = distribution(cachedhits)
    repo.ui.write(fmtdist('hit on cached bundles', cachedhitsdist))

def takeonesample(repo, revs):
    node = repo.changelog.node
    pulled = random.sample(revs, max(4, len(revs) // 1000))
    pulled = repo.revs('%ld::%ld', pulled, pulled)
    nodes = [node(r) for r in pulled]
    return outgoingfromnodes(repo, nodes)

def distribution(data):
    data.sort()
    length = len(data)
    return {
        'min': data[0],
        '10%': data[length // 10],
        '25%': data[length // 4],
        '50%': data[length // 2],
        '75%': data[(length // 4) * 3],
        '90%': data[(length // 10) * 9],
        '95%': data[(length // 20) * 19],
        'max': data[-1],
    }

STATSFORMAT = """{name}:
  min: {min}
  10%: {10%}
  25%: {25%}
  50%: {50%}
  75%: {75%}
  90%: {90%}
  95%: {95%}
  max: {max}
"""

def fmtdist(name, data):
    return STATSFORMAT.format(name=name, **data)
