# Code dedicated to the discovery of obsolescence marker "over the wire"
#
# Copyright 2017 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# Status: Experiment in progress // open question
#
#   The final discovery algorithm and protocol will go into core when we'll be
#   happy with it.
#
#   Some of the code in this module is for compatiblity with older version
#   of evolve and will be eventually dropped.

from __future__ import absolute_import

import hashlib
import heapq
import sqlite3
import struct
import weakref

from mercurial import (
    error,
    exchange,
    extensions,
    localrepo,
    node,
    obsolete,
    scmutil,
    util,
)
from mercurial.i18n import _

from . import (
    compat,
    exthelper,
    obscache,
    utility,
    stablerange,
    stablerangecache,
)

try:
    from mercurial import wireprototypes, wireprotov1server
    from mercurial.wireprotov1peer import wirepeer
    from mercurial.wireprototypes import encodelist, decodelist
except (ImportError, AttributeError): # <= hg-4.5
    from mercurial import wireproto as wireprototypes
    wireprotov1server = wireprototypes
    from mercurial.wireproto import wirepeer, encodelist, decodelist

_pack = struct.pack
_unpack = struct.unpack
_calcsize = struct.calcsize

eh = exthelper.exthelper()
obsexcmsg = utility.obsexcmsg

# Config
eh.configitem('experimental', 'evolution.obsdiscovery', True)
eh.configitem('experimental', 'obshashrange', True)
eh.configitem('experimental', 'obshashrange.warm-cache', 'auto')
eh.configitem('experimental', 'obshashrange.max-revs', None)
eh.configitem('experimental', 'obshashrange.lru-size', 2000)

##################################
###  Code performing discovery ###
##################################

def findmissingrange(ui, local, remote, probeset,
                     initialsamplesize=100,
                     fullsamplesize=200):
    missing = set()
    starttime = util.timer()

    heads = local.revs('heads(%ld)', probeset)
    local.stablerange.warmup(local)

    rangelength = local.stablerange.rangelength
    subranges = local.stablerange.subranges
    # size of slice ?
    heappop = heapq.heappop
    heappush = heapq.heappush
    heapify = heapq.heapify

    tested = set()

    sample = []
    samplesize = initialsamplesize

    def addentry(entry):
        if entry in tested:
            return False
        sample.append(entry)
        tested.add(entry)
        return True

    for h in heads:
        entry = (h, 0)
        addentry(entry)

    local.obsstore.rangeobshashcache.update(local)
    querycount = 0
    compat.progress(ui, _("comparing obsmarker with other"), querycount,
                    unit=_("queries"))
    overflow = []
    while sample or overflow:
        if overflow:
            sample.extend(overflow)
            overflow = []

        if samplesize < len(sample):
            # too much sample already
            overflow = sample[samplesize:]
            sample = sample[:samplesize]
        elif len(sample) < samplesize:
            ui.debug("query %i; add more sample (target %i, current %i)\n"
                     % (querycount, samplesize, len(sample)))
            # we need more sample !
            needed = samplesize - len(sample)
            sliceme = []
            heapify(sliceme)
            for entry in sample:
                if 1 < rangelength(local, entry):
                    heappush(sliceme, (-rangelength(local, entry), entry))

            while sliceme and 0 < needed:
                _key, target = heappop(sliceme)
                for new in subranges(local, target):
                    # XXX we could record hierarchy to optimise drop
                    if addentry(new):
                        if 1 < len(new):
                            heappush(sliceme, (-rangelength(local, new), new))
                        needed -= 1
                        if needed <= 0:
                            break

        # no longer the first interation
        samplesize = fullsamplesize

        nbsample = len(sample)
        maxsize = max([rangelength(local, r) for r in sample])
        ui.debug("query %i; sample size is %i, largest range %i\n"
                 % (querycount, nbsample, maxsize))
        nbreplies = 0
        replies = list(_queryrange(ui, local, remote, sample))
        sample = []
        n = local.changelog.node
        for entry, remotehash in replies:
            nbreplies += 1
            if remotehash == _obshashrange(local, entry):
                continue
            elif 1 == rangelength(local, entry):
                missing.add(n(entry[0]))
            else:
                for new in subranges(local, entry):
                    addentry(new)
        assert nbsample == nbreplies
        querycount += 1
        compat.progress(ui, _("comparing obsmarker with other"), querycount,
                        unit=_("queries"))
    compat.progress(ui, _("comparing obsmarker with other"), None)
    local.obsstore.rangeobshashcache.save(local)
    duration = util.timer() - starttime
    logmsg = ('obsdiscovery, %d/%d mismatch'
              ' - %d obshashrange queries in %.4f seconds\n')
    logmsg %= (len(missing), len(probeset), querycount, duration)
    ui.log('evoext-obsdiscovery', logmsg)
    ui.debug(logmsg)
    return sorted(missing)

def _queryrange(ui, repo, remote, allentries):
    #  question are asked with node
    n = repo.changelog.node
    noderanges = [(n(entry[0]), entry[1]) for entry in allentries]
    replies = remote.evoext_obshashrange_v1(noderanges)
    result = []
    for idx, entry in enumerate(allentries):
        result.append((entry, replies[idx]))
    return result

##############################
### Range Hash computation ###
##############################

@eh.command(
    'debugobshashrange',
    [
        ('', 'rev', [], 'display obshash for all (rev, 0) range in REVS'),
        ('', 'subranges', False, 'display all subranges'),
    ],
    _(''))
def debugobshashrange(ui, repo, **opts):
    """display the ::REVS set topologically sorted in a stable way
    """
    s = node.short
    revs = scmutil.revrange(repo, opts['rev'])
    # prewarm depth cache
    if revs:
        repo.stablerange.warmup(repo, max(revs))
    cl = repo.changelog
    rangelength = repo.stablerange.rangelength
    depthrev = repo.stablerange.depthrev
    if opts['subranges']:
        ranges = stablerange.subrangesclosure(repo, repo.stablerange, revs)
    else:
        ranges = [(r, 0) for r in revs]
    headers = ('rev', 'node', 'index', 'size', 'depth', 'obshash')
    linetemplate = '%12d %12s %12d %12d %12d %12s\n'
    headertemplate = linetemplate.replace('d', 's')
    ui.status(headertemplate % headers)
    repo.obsstore.rangeobshashcache.update(repo)
    for r in ranges:
        d = (r[0],
             s(cl.node(r[0])),
             r[1],
             rangelength(repo, r),
             depthrev(repo, r[0]),
             node.short(_obshashrange(repo, r)))
        ui.status(linetemplate % d)
    repo.obsstore.rangeobshashcache.save(repo)

def _obshashrange(repo, rangeid):
    """return the obsolete hash associated to a range"""
    cache = repo.obsstore.rangeobshashcache
    cl = repo.changelog
    obshash = cache.get(rangeid)
    if obshash is not None:
        return obshash
    pieces = []
    nullid = node.nullid
    if repo.stablerange.rangelength(repo, rangeid) == 1:
        rangenode = cl.node(rangeid[0])
        tmarkers = repo.obsstore.relevantmarkers([rangenode])
        pieces = []
        for m in tmarkers:
            mbin = obsolete._fm1encodeonemarker(m)
            pieces.append(mbin)
        pieces.sort()
    else:
        for subrange in repo.stablerange.subranges(repo, rangeid):
            obshash = _obshashrange(repo, subrange)
            if obshash != nullid:
                pieces.append(obshash)

    sha = hashlib.sha1()
    # note: if there is only one subrange with actual data, we'll just
    # reuse the same hash.
    if not pieces:
        obshash = node.nullid
    elif len(pieces) != 1 or obshash is None:
        sha = hashlib.sha1()
        for p in pieces:
            sha.update(p)
        obshash = sha.digest()
    cache[rangeid] = obshash
    return obshash

### sqlite caching

_sqliteschema = [
    """CREATE TABLE obshashrange(rev     INTEGER NOT NULL,
                                 idx     INTEGER NOT NULL,
                                 obshash BLOB    NOT NULL,
                                 PRIMARY KEY(rev, idx));""",
    "CREATE INDEX range_index ON obshashrange(rev, idx);",
    """CREATE TABLE meta(schemaversion INTEGER NOT NULL,
                         tiprev        INTEGER NOT NULL,
                         tipnode       BLOB    NOT NULL,
                         nbobsmarker   INTEGER NOT NULL,
                         obssize       BLOB    NOT NULL,
                         obskey        BLOB    NOT NULL
                        );""",
]
_queryexist = "SELECT name FROM sqlite_master WHERE type='table' AND name='meta';"
_clearmeta = """DELETE FROM meta;"""
_newmeta = """INSERT INTO meta (schemaversion, tiprev, tipnode, nbobsmarker, obssize, obskey)
            VALUES (?,?,?,?,?,?);"""
_updateobshash = "INSERT INTO obshashrange(rev, idx, obshash) VALUES (?,?,?);"
_querymeta = "SELECT schemaversion, tiprev, tipnode, nbobsmarker, obssize, obskey FROM meta;"
_queryobshash = "SELECT obshash FROM obshashrange WHERE (rev = ? AND idx = ?);"
_query_max_stored = "SELECT MAX(rev) FROM obshashrange"

_reset = "DELETE FROM obshashrange;"
_delete = "DELETE FROM obshashrange WHERE (rev = ? AND idx = ?);"

def _affectedby(repo, markers):
    """return all nodes whose relevant set is affected by this changeset

    This is a reversed version of obsstore.relevantmarkers
    """
    affected_nodes = set()
    known_markers = set(markers)
    node_to_proceed = set()
    marker_to_proceed = set(known_markers)

    obsstore = repo.obsstore

    while node_to_proceed or marker_to_proceed:
        while marker_to_proceed:
            m = marker_to_proceed.pop()
            # check successors and parent
            if m[1]:
                relevant = (m[1], )
            else: # prune case
                relevant = ((m[0], ), m[5])
            for l in relevant:
                if l is None:
                    continue
                for n in l:
                    if n not in affected_nodes:
                        node_to_proceed.add(n)
                    affected_nodes.add(n)
        # marker_to_proceed is now empty:
        if node_to_proceed:
            n = node_to_proceed.pop()
            markers = set()
            markers.update(obsstore.successors.get(n, ()))
            markers.update(obsstore.predecessors.get(n, ()))
            markers -= known_markers
            marker_to_proceed.update(markers)
            known_markers.update(markers)

    return affected_nodes

# if there is that many new obsmarkers, reset without analysing them
RESET_ABOVE = 10000

class _obshashcache(obscache.dualsourcecache):

    _schemaversion = 3

    _cachename = 'evo-ext-obshashrange' # used for error message
    _filename = 'evoext_obshashrange_v2.sqlite'

    def __init__(self, repo):
        super(_obshashcache, self).__init__()
        self._vfs = repo.vfs
        self._path = repo.cachevfs.join(self._filename)
        self._new = set()
        self._valid = True
        self._repo = weakref.ref(repo.unfiltered())
        # cache status
        self._ondiskcachekey = None
        self._data = {}

    def clear(self, reset=False):
        super(_obshashcache, self).clear(reset=reset)
        self._data.clear()
        self._new.clear()
        if reset:
            self._valid = False
        if '_con' in vars(self):
            del self._con

    def get(self, rangeid):
        # revision should be covered by the tiprev
        #
        # XXX there are issue with cache warming, we hack around it for now
        if not getattr(self, '_updating', False):
            if self._cachekey[0] < rangeid[0]:
                msg = ('using unwarmed obshashrangecache (%s %s)'
                       % (rangeid[0], self._cachekey[0]))
                raise error.ProgrammingError(msg)

        value = self._data.get(rangeid)
        if value is None and self._con is not None:
            nrange = (rangeid[0], rangeid[1])
            try:
                obshash = self._con.execute(_queryobshash, nrange).fetchone()
                if obshash is not None:
                    value = obshash[0]
                self._data[rangeid] = value
            except (sqlite3.DatabaseError, sqlite3.OperationalError):
                # something is wrong with the sqlite db
                # Since this is a cache, we ignore it.
                if '_con' in vars(self):
                    del self._con
                self._new.clear()
        return value

    def __setitem__(self, rangeid, obshash):
        self._new.add(rangeid)
        self._data[rangeid] = obshash

    def _updatefrom(self, repo, revs, obsmarkers):
        """override this method to update your cache data incrementally

        revs:      list of new revision in the changelog
        obsmarker: list of new obsmarkers in the obsstore
        """
        # XXX for now, we'll not actually update the cache, but we'll be
        # smarter at invalidating it.
        #
        # 1) new revisions does not get their entry updated (not update)
        # 2) if we detect markers affecting non-new revision we reset the cache

        self._updating = True

        con = self._con
        if con is not None:
            reset = False
            affected = []
            if RESET_ABOVE < len(obsmarkers):
                # lots of new obsmarkers, probably smarter to reset the cache
                repo.ui.log('evoext-cache', 'obshashcache reset - '
                            'many new markers (%d)\n'
                            % len(obsmarkers))
                reset = True
            elif obsmarkers:
                max_stored = con.execute(_query_max_stored).fetchall()[0][0]
                affected_nodes = _affectedby(repo, obsmarkers)

                rev = repo.changelog.nodemap.get
                affected = [rev(n) for n in affected_nodes]
                affected = [r for r in affected
                            if r is not None and r <= max_stored]

            if RESET_ABOVE < len(affected):
                repo.ui.log('evoext-cache', 'obshashcache reset - '
                            'new markers affect many changeset (%d)\n'
                            % len(affected))
                reset = True

            if affected or reset:
                if not reset:
                    repo.ui.log('evoext-cache', 'obshashcache clean - '
                                'new markers affect %d changeset and cached ranges\n'
                                % len(affected))
                if con is not None:
                    # always reset for now, the code detecting affect is buggy
                    # so we need to reset more broadly than we would like.
                    try:
                        if repo.stablerange._con is None:
                            repo.ui.log('evoext-cache', 'obshashcache reset - '
                                        'underlying stablerange cache unavailable\n')
                            reset = True
                        if reset:
                            con.execute(_reset)
                            self._data.clear()
                        else:
                            ranges = repo.stablerange.contains(repo, affected)
                            con.executemany(_delete, ranges)
                            for r in ranges:
                                self._data.pop(r, None)
                    except (sqlite3.DatabaseError, sqlite3.OperationalError) as exc:
                        repo.ui.log('evoext-cache', 'error while updating obshashrange cache: %s' % exc)
                        del self._updating
                        return

                # rewarm key revisions
                #
                # (The current invalidation is too wide, but rewarming every
                # single revision is quite costly)
                newrevs = []
                stop = self._cachekey[0] # tiprev
                for h in repo.filtered('immutable').changelog.headrevs():
                    if h <= stop and h in affected:
                        newrevs.append(h)
                newrevs.extend(revs)
                revs = newrevs

        repo.depthcache.update(repo)
        total = len(revs)

        def progress(pos, rev):
            compat.progress(repo.ui, 'updating obshashrange cache',
                            pos, 'rev %s' % rev, unit='revision', total=total)
        # warm the cache for the new revs
        progress(0, '')
        for idx, r in enumerate(revs):
            _obshashrange(repo, (r, 0))
            progress(idx, r)
        progress(None, '')

        del self._updating

    @property
    def _fullcachekey(self):
        return (self._schemaversion, ) + self._cachekey

    def load(self, repo):
        if self._con is None:
            self._cachekey = self.emptykey
            self._ondiskcachekey = self.emptykey
        assert self._cachekey is not None

    def _db(self):
        try:
            util.makedirs(self._vfs.dirname(self._path))
        except OSError:
            return None
        con = sqlite3.connect(self._path, timeout=30, isolation_level="IMMEDIATE")
        con.text_factory = str
        return con

    @util.propertycache
    def _con(self):
        if not self._valid:
            return None
        repo = self._repo()
        if repo is None:
            return None
        con = self._db()
        if con is None:
            return None
        cur = con.execute(_queryexist)
        if cur.fetchone() is None:
            self._valid = False
            return None
        meta = con.execute(_querymeta).fetchone()
        if meta is None or meta[0] != self._schemaversion:
            self._valid = False
            return None
        self._cachekey = self._ondiskcachekey = meta[1:]
        return con

    def save(self, repo):
        if self._cachekey is None:
            return
        if self._cachekey == self._ondiskcachekey and not self._new:
            return
        repo = repo.unfiltered()
        try:
            with repo.lock():
                if 'stablerange' in vars(repo):
                    repo.stablerange.save(repo)
                self._save(repo)
        except error.LockError:
            # Exceptionnally we are noisy about it since performance impact
            # is large We should address that before using this more
            # widely.
            msg = _('obshashrange cache: skipping save unable to lock repo\n')
            repo.ui.warn(msg)

    def _save(self, repo):
        if not self._new:
            return
        try:
            return self._trysave(repo)
        except (IOError, OSError, sqlite3.DatabaseError, sqlite3.OperationalError, sqlite3.IntegrityError) as exc:
            # Catch error that may arise under stress
            #
            # operational error catch read-only and locked database
            # IntegrityError catch Unique constraint error that may arise
            if '_con' in vars(self):
                del self._con
            self._new.clear()
            repo.ui.log('evoext-cache', 'error while saving new data: %s' % exc)
            repo.ui.debug('evoext-cache: error while saving new data: %s' % exc)

    def _trysave(self, repo):
        if self._con is None:
            util.unlinkpath(self._path, ignoremissing=True)
            if '_con' in vars(self):
                del self._con

            con = self._db()
            if con is None:
                repo.ui.log('evoext-cache', 'unable to write obshashrange cache'
                            ' - cannot create database')
                return
            with con:
                for req in _sqliteschema:
                    con.execute(req)

                meta = [self._schemaversion] + list(self.emptykey)
                con.execute(_newmeta, meta)
                self._ondiskcachekey = self.emptykey
        else:
            con = self._con
        with con:
            meta = con.execute(_querymeta).fetchone()
            if meta[1:] != self._ondiskcachekey:
                # drifting is currently an issue because this means another
                # process might have already added the cache line we are about
                # to add. This will confuse sqlite
                msg = _('obshashrange cache: skipping write, '
                        'database drifted under my feet\n')
                repo.ui.warn(msg)
                self._new.clear()
                self._valid = False
                if '_con' in vars(self):
                    del self._con
                self._valid = False
                return
            data = ((rangeid[0], rangeid[1], self.get(rangeid)) for rangeid in self._new)
            con.executemany(_updateobshash, data)
            cachekey = self._fullcachekey
            con.execute(_clearmeta) # remove the older entry
            con.execute(_newmeta, cachekey)
            self._new.clear()
            self._valid = True
            self._ondiskcachekey = self._cachekey
@eh.wrapfunction(obsolete.obsstore, '_addmarkers')
def _addmarkers(orig, obsstore, *args, **kwargs):
    obsstore.rangeobshashcache.clear()
    return orig(obsstore, *args, **kwargs)

obsstorefilecache = localrepo.localrepository.obsstore


# obsstore is a filecache so we have do to some spacial dancing
@eh.wrapfunction(obsstorefilecache, 'func')
def obsstorewithcache(orig, repo):
    obsstore = orig(repo)
    obsstore.rangeobshashcache = _obshashcache(repo.unfiltered())
    return obsstore

@eh.reposetup
def setupcache(ui, repo):

    class obshashrepo(repo.__class__):
        @localrepo.unfilteredmethod
        def destroyed(self):
            if 'obsstore' in vars(self):
                self.obsstore.rangeobshashcache.clear()
            toplevel = not util.safehasattr(self, '_destroying')
            if toplevel:
                self._destroying = True
            try:
                super(obshashrepo, self).destroyed()
            finally:
                if toplevel:
                    del self._destroying

        @localrepo.unfilteredmethod
        def updatecaches(self, tr=None, **kwargs):
            if utility.shouldwarmcache(self, tr):
                self.obsstore.rangeobshashcache.update(self)
                self.obsstore.rangeobshashcache.save(self)
            super(obshashrepo, self).updatecaches(tr, **kwargs)

    repo.__class__ = obshashrepo

### wire protocol commands

def _obshashrange_v0(repo, ranges):
    """return a list of hash from a list of range

    The range have the id encoded as a node

    return 'wdirid' for unknown range"""
    nm = repo.changelog.nodemap
    ranges = [(nm.get(n), idx) for n, idx in ranges]
    if ranges:
        maxrev = max(r for r, i in ranges)
        if maxrev is not None:
            repo.stablerange.warmup(repo, upto=maxrev)
    result = []
    repo.obsstore.rangeobshashcache.update(repo)
    for r in ranges:
        if r[0] is None:
            result.append(node.wdirid)
        else:
            result.append(_obshashrange(repo, r))
    repo.obsstore.rangeobshashcache.save(repo)
    return result

@eh.addattr(localrepo.localpeer, 'evoext_obshashrange_v1')
def local_obshashrange_v0(peer, ranges):
    return _obshashrange_v0(peer._repo, ranges)


_indexformat = '>I'
_indexsize = _calcsize(_indexformat)
def _encrange(node_rangeid):
    """encode a (node) range"""
    headnode, index = node_rangeid
    return headnode + _pack(_indexformat, index)

def _decrange(data):
    """encode a (node) range"""
    assert _indexsize < len(data), len(data)
    headnode = data[:-_indexsize]
    index = _unpack(_indexformat, data[-_indexsize:])[0]
    return (headnode, index)

@eh.addattr(wirepeer, 'evoext_obshashrange_v1')
def peer_obshashrange_v0(self, ranges):
    binranges = [_encrange(r) for r in ranges]
    encranges = encodelist(binranges)
    d = self._call("evoext_obshashrange_v1", ranges=encranges)
    try:
        return decodelist(d)
    except ValueError:
        self._abort(error.ResponseError(_("unexpected response:"), d))

@compat.wireprotocommand(eh, 'evoext_obshashrange_v1', 'ranges')
def srv_obshashrange_v1(repo, proto, ranges):
    ranges = decodelist(ranges)
    ranges = [_decrange(r) for r in ranges]
    hashes = _obshashrange_v0(repo, ranges)
    return encodelist(hashes)

def _useobshashrange(repo):
    base = repo.ui.configbool('experimental', 'obshashrange')
    if base:
        maxrevs = repo.ui.configint('experimental', 'obshashrange.max-revs')
        if maxrevs is not None and maxrevs < len(repo.unfiltered()):
            base = False
    return base

def _canobshashrange(local, remote):
    return (_useobshashrange(local)
            and remote.capable('_evoext_obshashrange_v1'))

def _obshashrange_capabilities(orig, repo, proto):
    """wrapper to advertise new capability"""
    caps = orig(repo, proto)
    enabled = _useobshashrange(repo)
    if obsolete.isenabled(repo, obsolete.exchangeopt) and enabled:

        # Compat hg 4.6+ (2f7290555c96)
        bytesresponse = False
        if util.safehasattr(caps, 'data'):
            bytesresponse = True
            caps = caps.data

        caps = caps.split()
        caps.append(b'_evoext_obshashrange_v1')
        caps.sort()
        caps = b' '.join(caps)

        # Compat hg 4.6+ (2f7290555c96)
        if bytesresponse:
            caps = wireprototypes.bytesresponse(caps)
    return caps

@eh.extsetup
def obshashrange_extsetup(ui):
    ###
    extensions.wrapfunction(wireprotov1server, 'capabilities',
                            _obshashrange_capabilities)
    # wrap command content
    oldcap, args = wireprotov1server.commands['capabilities']

    def newcap(repo, proto):
        return _obshashrange_capabilities(oldcap, repo, proto)
    wireprotov1server.commands['capabilities'] = (newcap, args)

##########################################
###  trigger discovery during exchange ###
##########################################

def _dopushmarkers(pushop):
    return (# we have any markers to push
            pushop.repo.obsstore
            # exchange of obsmarkers is enabled locally
            and obsolete.isenabled(pushop.repo, obsolete.exchangeopt)
            # remote server accept markers
            and 'obsolete' in pushop.remote.listkeys('namespaces'))

def _pushobshashrange(pushop, commonrevs):
    repo = pushop.repo.unfiltered()
    remote = pushop.remote
    missing = findmissingrange(pushop.ui, repo, remote, commonrevs)
    missing += pushop.outgoing.missing
    return missing

# available discovery method, first valid is used
# tuple (canuse, perform discovery))
obsdiscoveries = [
    (_canobshashrange, _pushobshashrange),
]

obsdiscovery_skip_message = """\
(skipping discovery of obsolescence markers, will exchange everything)
(controled by 'experimental.evolution.obsdiscovery' configuration)
"""

def usediscovery(repo):
    return repo.ui.configbool('experimental', 'evolution.obsdiscovery')

@eh.wrapfunction(exchange, '_pushdiscoveryobsmarkers')
def _pushdiscoveryobsmarkers(orig, pushop):
    if _dopushmarkers(pushop):
        repo = pushop.repo
        remote = pushop.remote
        obsexcmsg(repo.ui, "computing relevant nodes\n")
        revs = list(repo.revs('::%ln', pushop.futureheads))
        unfi = repo.unfiltered()

        if not usediscovery(repo):
            # discovery disabled by user
            repo.ui.status(obsdiscovery_skip_message)
            return orig(pushop)

        # look for an obs-discovery protocol we can use
        discovery = None
        for candidate in obsdiscoveries:
            if candidate[0](repo, remote):
                discovery = candidate[1]
                break

        if discovery is None:
            # no discovery available, rely on core to push all relevants
            # obs markers.
            return orig(pushop)

        obsexcmsg(repo.ui, "looking for common markers in %i nodes\n"
                           % len(revs))
        commonrevs = list(unfi.revs('::%ln', pushop.outgoing.commonheads))
        # find the nodes where the relevant obsmarkers mismatches
        nodes = discovery(pushop, commonrevs)

        if nodes:
            obsexcmsg(repo.ui, "computing markers relevant to %i nodes\n"
                               % len(nodes))
            pushop.outobsmarkers = repo.obsstore.relevantmarkers(nodes)
        else:
            obsexcmsg(repo.ui, "markers already in sync\n")
            pushop.outobsmarkers = []

@eh.extsetup
def _installobsmarkersdiscovery(ui):
    olddisco = exchange.pushdiscoverymapping['obsmarker']

    def newdisco(pushop):
        _pushdiscoveryobsmarkers(olddisco, pushop)
    exchange.pushdiscoverymapping['obsmarker'] = newdisco

def buildpullobsmarkersboundaries(pullop, bundle2=True):
    """small function returning the argument for pull markers call
    may to contains 'heads' and 'common'. skip the key for None.

    It is a separed function to play around with strategy for that."""
    repo = pullop.repo
    remote = pullop.remote
    unfi = repo.unfiltered()
    revs = unfi.revs('::(%ln - null)', pullop.common)
    boundaries = {'heads': pullop.pulledsubset}
    if not revs: # nothing common
        boundaries['common'] = [node.nullid]
        return boundaries

    if not usediscovery(repo):
        # discovery disabled by users.
        repo.ui.status(obsdiscovery_skip_message)
        boundaries['common'] = [node.nullid]
        return boundaries

    if bundle2 and _canobshashrange(repo, remote):
        obsexcmsg(repo.ui, "looking for common markers in %i nodes\n"
                  % len(revs))
        boundaries['missing'] = findmissingrange(repo.ui, unfi, pullop.remote,
                                                 revs)
    else:
        boundaries['common'] = [node.nullid]
    return boundaries

# merge later for outer layer wrapping
eh.merge(stablerangecache.eh)
