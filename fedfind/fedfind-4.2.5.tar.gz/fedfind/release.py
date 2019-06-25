# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

# Making this explicit is often much easier to read. Stupid warning.
# pylint: disable=no-else-return,too-many-lines

"""Defines the various release classes used as the main entry
points.
"""
from __future__ import unicode_literals
from __future__ import print_function

import abc
import copy
import datetime
import logging
import re
import string

from collections import defaultdict
# this was used for TC/RC handling, we may still need it again
#from decimal import (Decimal, InvalidOperation)
from functools import partial, wraps

from cached_property import cached_property
from productmd.composeinfo import get_date_type_respin
#pylint: disable=import-error
from six.moves.urllib.parse import urlparse

import fedfind.const
import fedfind.exceptions
import fedfind.helpers

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)


# HELPER FUNCTIONS FOR get_release
def _val_in_str(values, strings):
    """True if any value contains any of the strings in the 'strings'
    iterable. Only used by guess_compose.
    """
    for val in values:
        if val and any(str(st).lower() == str(val).lower() for st in strings):
            return True
    return False

def _parse_label(label):
    """Produce a milestone/compose/respin tuple from a compose label."""
    (milestone, comp) = label.split('-')
    (compose, respin) = comp.split('.')
    return (milestone, compose, int(respin))

def _parse_cid(cid):
    # pylint:disable=too-many-return-statements
    """Produce a dist/release/milestone/compose/respin tuple from
    a compose ID. Will always give the values that produce a raw,
    non-mirrored Release instance. Should work for fedfind fake
    CIDs (returning a Release class instance matching the one that
    # produced the fake CID in the first place).
    """
    # Assume a real Pungi 4 compose ID
    ciddic = fedfind.helpers.parse_cid(cid, dic=True)
    (dist, release, date, typ, respin) = (ciddic['short'], ciddic['version'], ciddic['date'],
                                          ciddic['compose_type'], ciddic['respin'])
    release = release.capitalize()

    if ciddic['version_type'] in ('updates', 'updates-testing'):
        if dist not in ("FedoraRespin", "Fedora"):
            raise fedfind.exceptions.UnsupportedComposeError(
                "get_release(): fedfind does not support composes "
                "like {0} as they contain no images".format(cid))

    # Atomic stable nightly composes, 'Fedora-Atomic' shortname
    if dist == 'Fedora-Atomic':
        return (dist, release, '', date, int(respin))

    # Docker stable nightly composes, 'Fedora-Docker' shortname
    if dist == 'Fedora-Docker':
        return (dist, release, '', date, int(respin))

    # Container stable nightly composes, 'Fedora-Container' shortname
    if dist == 'Fedora-Container':
        return (dist, release, '', date, int(respin))

    # Cloud stable nightly composes, 'Fedora-Cloud' shortname
    if dist == 'Fedora-Cloud':
        return (dist, release, '', date, int(respin))

    # IoT stable nightly composes, 'Fedora-IoT' shortname
    if dist == 'Fedora-IoT':
        return (dist, release, '', date, int(respin))

    # Semi-official stable live respin composes
    if dist == 'FedoraRespin':
        return (dist, release, '', date, 0)

    if typ == 'nightly':
        if release == 'Rawhide':
            milestone = ''
        else:
            milestone = 'Branched'
        return (dist, release, milestone, date, int(respin))
    elif typ == 'production':
        if ciddic['version_type'] == 'updates':
            # 'updates' compose
            return (dist, release, 'Updates', date, int(respin))
        elif ciddic['version_type'] == 'updates-testing':
            # 'updates-testing' compose
            return (dist, release, 'Updates-testing', date, int(respin))
        # date 19700101 indicates a fedfind fake CID, most likely
        # for a stable release, so just return the release number
        # so we get a stable release class
        if date == '19700101':
            return (dist, release, '', '', 0)
        return (dist, release, 'Production', date, int(respin))
    else:
        raise ValueError("get_release(): could not parse compose ID {0}!".format(cid))

def _parse_url(url):
    """Handle a URL if specified. If this looks like the URL for
    RespinRelease, return that. Otherwise if we can find a compose
    ID, return appropriate dist/release/milestone/compose/respin
    tuple. Otherwise just return None (we don't handle URLs for
    things like stable releases ATM).
    """
    if url.rstrip('/').endswith('/alt/live-respins'):
        # special case: assume we wanted RespinRelease
        return ('FedoraRespin', '', '', '', 0, None)
    cid = fedfind.helpers.find_cid(url)
    if cid:
        try:
            return _parse_cid(cid) + (cid,)
        except ValueError:
            # let's fall through to a Pungi4Release
            pass
    return None

# VALUE GUESSING
def _guess_compose(dist='', release='', milestone='', compose=''):
    """Works out what to use as 'compose' value. We never want
    to transform it if set, so simply returns it. If not set, we
    guess at the current date if 'release' and 'milestone' are
    not set, or if dist, release or milestone is set to one of the
    'snapshot'-type values; otherwise we leave it blank (this is so
    e.g. (22, '', '') returns Fedora 22).
    """
    snaps = ('rawhide', 'bikeshed', 'branched', 'Fedora-Atomic', 'Fedora-Docker', 'Fedora-Cloud',
             'Fedora-Container', 'Fedora-IoT', 'production', 'updates', 'updates-testing')
    # we also don't want to guess for FedoraRespin even if release
    # and milestone are not set
    if compose or dist.lower() == 'fedorarespin':
        return compose
    if (not release and not milestone) or _val_in_str(snaps, (dist, release, milestone)):
        logger.debug("Guessing date")
        compose = fedfind.helpers.date_check(datetime.date.today(), out='str')
    return compose

def _guess_release(dist='', release='', milestone='', compose=''):
    # pylint:disable=too-many-return-statements
    """Works out what to use as a 'release' value. We handle a
    few different guessing scenarios here, and conversion from
    wikitcms '24 Rawhide (date)' type settings.
    """
    # Regardless of any other value, if milestone is Rawhide, we
    # return Rawhide. This is to correctly 'translate' wikitcms
    # 23 Rawhide 20150324 (for e.g.) to release 'Rawhide'.
    if milestone.lower() == 'rawhide':
        return 'Rawhide'

    # Aside from that, if release is set, sanity check and return
    # it.
    if release:
        check = str(release).lower()
        if check.isdigit() or check in ('rawhide', 'bikeshed'):
            return release
        else:
            raise ValueError("get_release(): Release must be a number or Rawhide or Bikeshed!")

    # If we were specifically asked for a valid milestone, return
    # appropriate release.
    if milestone.lower() in ('branched', 'production'):
        return fedfind.helpers.get_current_release() + 1
    elif milestone.lower() in ('updates', 'updates-testing'):
        return fedfind.helpers.get_current_release()
    elif dist.lower() in ('fedora-atomic', 'fedora-docker', 'fedora-cloud',
                          'fedora-container', 'fedora-iot'):
        # Note: cloud and docker are actually composed for both
        # current and prev, but we gotta guess something...
        return fedfind.helpers.get_current_release()
    elif dist.lower() == 'fedorarespin':
        # no expected release here
        return release

    # Otherwise, if compose is a date, guess Rawhide...
    elif fedfind.helpers.date_check(compose, fail_raise=False):
        return 'Rawhide'

    # ...otherwise, guess next release (to allow e.g. 'Beta TC2'
    # with no release).
    return fedfind.helpers.get_current_release() + 1


# UTILITY FUNCTIONS FOR SELECTING APPROPRIATE CLASSES
def _get_stable(release):
    """Return the appropriate stable release class for a given
    release number.
    """
    # This is disabled for now because Pungi metadata is being
    # stripped when the release is synced (because some of the
    # compose contents are split off into alt, hence the metadata
    # is not accurate as regards the contents of each location)
    # without metadata what we get should be handled just like
    # pre-Pungi 4 composes, even though the bits did come out of
    # Pungi 4
#        if int(release) > 23:
#            return Pungi4Mirror(
#                '/fedora/linux/releases/{0}'.format(str(release)))

    if int(release) < 7:
        return CoreRelease(release)
    if int(release) < 26:
        return ArchiveRelease(release)
    # All the ways we can try to handle the stable vs. archived
    # cutoff are basically hideous. This is the one I'm picking. We
    # used to just return ArchiveRelease if it existed, else return
    # CurrentRelease, but that stopped working because releng started
    # populating the ArchiveRelease location while the release also
    # still existed as a CurrentRelease. So we need to be more picky.
    # If CurrentRelease exists, return it. If CurrentRelease doesn't
    # exist but ArchiveRelease does, return that. If neither seems to
    # exist, go with CurrentRelease.
    rel = CurrentRelease(release)
    if not rel.exists:
        arcrel = ArchiveRelease(release)
        if arcrel.exists:
            rel = arcrel
    return rel

def _guess_nightly_respin(dist, release, milestone, date):
    """We have to handle 'respins' for nightlies if one wasn't
    explicitly passed. We just count down from 5 and stop when one
    exists or we hit 0.
    """
    if dist.lower() == 'fedora-atomic':
        testcls = partial(AtomicNightly, release=release, compose=date)
    elif dist.lower() == 'fedora-docker':
        testcls = partial(DockerNightly, release=release, compose=date)
    elif dist.lower() == 'fedora-cloud':
        testcls = partial(CloudNightly, release=release, compose=date)
    elif dist.lower() == 'fedora-container':
        testcls = partial(ContainerNightly, release=release, compose=date)
    elif dist.lower() == 'fedora-iot':
        testcls = partial(IoTNightly, release=release, compose=date)
    elif dist.lower() == 'fedora-modular':
        if release == 'Rawhide':
            testcls = partial(RawhideModularNightly, compose=date)
        elif release == 'Bikeshed':
            testcls = partial(BikeshedModularNightly, compose=date)
        else:
            testcls = partial(BranchedModularNightly, release=release, compose=date)
    elif milestone.lower() == 'updates':
        testcls = partial(Updates, release=release, compose=date)
    elif milestone.lower() == 'updates-testing':
        testcls = partial(UpdatesTesting, release=release, compose=date)
    elif release == 'Rawhide':
        testcls = partial(RawhideNightly, compose=date)
    else:
        testcls = partial(BranchedNightly, release=release, compose=date)
    respin = 5
    while respin > -1:
        test = testcls(respin=respin)
        if test.status in fedfind.const.PUNGI_SUCCESS:
            return test
        respin -= 1
    return test

def _guess_nightly_branched_atomic(dist, release, date, respin):
    """Handles guessing between Branched and Atomic for _get_nightly
    (which handles non-Rawhide nightly cases), if user didn't specify.
    This is kind of a legacy thing; these days there are other
    possible candidates (Production, Docker, Cloud, Container, IoT),
    but we don't include those. Split out to make pylint happier.
    """
    # Guess: try Branched, if it doesn't exist, try Atomic. We
    # don't include 'production', Docker, Container, Cloud or IoT.
    if respin is not None:
        if dist.lower() == 'fedora-modular':
            branched = BranchedModularNightly(release=release, compose=date, respin=respin)
        else:
            branched = BranchedNightly(release=release, compose=date, respin=respin)
    else:
        branched = _guess_nightly_respin(dist, release, '', date)
    if branched.exists:
        return branched
    else:
        if respin is not None:
            atomic = AtomicNightly(release=release, compose=date, respin=respin)
        else:
            atomic = _guess_nightly_respin('Fedora-Atomic', release, '', date)
        if atomic.exists:
            return atomic
        return branched

def _get_nightly(dist, release, milestone, date, respin=None):
    """Return the appropriate nightly release class for a given
    dist, release, milestone, date, and respin. Handles guessing
    milestone. If respin is not specified, handles guessing that.
    """
    if milestone.lower() == 'production':
        if respin is None:
            raise ValueError("Cannot guess respin for a production candidate compose!")
        if dist.lower() == 'fedora-modular':
            return ModularProduction(release, date, respin)
        return Production(release, date, respin)

    if milestone.lower() in ('updates', 'updates-testing'):
        if respin is None:
            return _guess_nightly_respin(dist, release, milestone, date)
        elif milestone.lower() == 'updates':
            return Updates(release=release, compose=date, respin=respin)
        elif milestone.lower() == 'updates-testing':
            return UpdatesTesting(release=release, compose=date, respin=respin)

    if milestone.lower() == 'branched' or dist.lower() in ('fedora-atomic', 'fedora-docker',
                                                           'fedora-cloud', 'fedora-container',
                                                           'fedora-iot'):
        if respin is None:
            return _guess_nightly_respin(dist, release, milestone, date)
        if dist.lower() == 'fedora-atomic':
            klass = AtomicNightly
        elif dist.lower() == 'fedora-docker':
            klass = DockerNightly
        elif dist.lower() == 'fedora-cloud':
            klass = CloudNightly
        elif dist.lower() == 'fedora-container':
            klass = ContainerNightly
        elif dist.lower() == 'fedora-iot':
            klass = IoTNightly
        else:
            # this is the 'branched' path, right here
            if dist.lower() == 'fedora-modular':
                klass = BranchedModularNightly
            else:
                klass = BranchedNightly
        return klass(release=release, compose=date, respin=respin)

    if milestone:
        logger.warning("Invalid milestone %s for nightly! Ignoring.", milestone)
    return _guess_nightly_branched_atomic(dist, release, date, respin)

def _legacy_milestones(dist, milestone):
    """Before we implemented the 'dist' concept in fedfind - the
    dist being what productmd calls the 'shortname', and what Fedora
    tends to use to identify different compose types, like 'Fedora'
    for the main distro composes, 'Fedora-Atomic' for post-release
    nightly Atomic composes, and so on - we handled some of these
    cases by overloading the meaning of the 'milestone' concept. After
    the 'dist' concept was added, things were clearly inconsistent.
    From 4.0 onwards the intent is that the 'dist' concept is the
    right one, but we want to remain backwards compatible. So this
    function handles the cases where a 'dist' could be specified as a
    milestone, and transforms the values, so the rest of get_release
    and its helpers can just deal with the 'expected' inputs.
    """
    pairs = {
        'atomic': 'Fedora-Atomic',
        'docker': 'Fedora-Docker',
        'cloud': 'Fedora-Cloud',
        'respin': 'FedoraRespin',
    }
    if milestone.lower() in pairs:
        if dist.lower() == 'fedora' or dist == pairs[milestone.lower()]:
            logger.warning('get_release: Passing %s as a milestone is deprecated. Instead, please '
                           'pass %s as dist.', milestone, pairs[milestone.lower()])
            return (pairs[milestone.lower()], '')
        else:
            # this should very rarely happen, but we can't reasonably
            # know what to do if it does
            raise ValueError('get_release: {0} as dist and {1} as milestone are ambiguous! Cannot '
                             'be sure what was meant.'.format(dist, milestone))
    return (dist, milestone)

def _url_cid_check(func):
    """Decorator that implements URL and CID checks for get_release.
    This is the least ugly way I could come up with to retrofit this;
    I like it a bit more than changing every return call in
    get_release, or renaming it to _get_release_main and making
    get_release a wrapper.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """The wrapper function for this decorator."""
        rel = func(*args, **kwargs)
        url = kwargs.get('url')
        cid = kwargs.get('cid')
        if url:
            loc = rel.location
            # just compare the path components, so we don't fail on
            # scheme differences or dl.fp.o vs. download.fp.o etc.
            urlpath = urlparse(url).path
            locpath = urlparse(loc).path
            if urlpath.startswith(locpath) or locpath.startswith(urlpath):
                pass
            else:
                raise fedfind.exceptions.UrlMatchError(url, rel)
        elif cid and rel.cid and rel.cid != cid:
            ok = False
            # handle a special case: the old form of fake CID for
            # respin releases
            if isinstance(rel, RespinRelease):
                fixedcid = cid.rsplit('-', 1)
                fixedcid.insert(1, 'updates')
                fixedcid = '-'.join(fixedcid)
                if rel.cid == fixedcid:
                    ok = True
            if not ok:
                raise fedfind.exceptions.CidMatchError(cid, rel)
        return rel
    return wrapper

@_url_cid_check
def get_release(release='', milestone='', compose='', respin=None,
                cid='', label='', url='', promote=False, dist='Fedora'):
    # pylint:disable=too-many-arguments,too-many-branches,too-many-statements
    # pylint:disable=too-many-return-statements
    """Function to return an appropriate Release subclass for the
    version information. Figures out if you want a nightly, compose,
    milestone, or stable release and gives it to you. Catches some
    nonsense choices. Tries to figure out the appropriate subclass
    (current, archive, core...) for stable releases. Can work off
    fedfind/wikitcms-style 'release, milestone, compose, respin, dist',
    or from a compose URL (expected to be the URL available from
    releng fedmsgs - the /compose directory of a Pungi 4 compose),
    or from a Pungi 4 compose ID, or from a Pungi 4 compose label.
    Yeah, that's a lot of choice.

    Priority goes to url, then label, then cid, then r/m/c/r/d. So if
    url is specified, all other values are ignored; if url is not
    specified but label is, label is used and all other values except
    release are ignored; if neither url nor label is specified but
    cid is, cid is used and all other values are ignored; if none of
    url, label, or cid is specified, we do what we can with whatever
    release, milestone, compose and respin values are given. Note
    if you pass label you probably also want to pass release; labels
    identify only milestone and compose. If you don't, it will be
    guessed. By default, if you pass 'cid', we do not try to 'promote'
    the result - that is, if the compose in question is a production
    compose and was actually synced out as a Candidate or released as
    a Milestone or a stable release, we do not discover its label and
    give you one of those instances based on the label, you just get
    a Production, which is the compose's expected location in the non-
    mirrored kojipkgs server where *all* Pungi 4 composes initially
    appear. If you want to 'promote' from the cid in this way, pass
    promote=True.

    Not all values are sanity checked; this may return a non-plausible
    release. Specifically, we do not check the sanity of milestone or
    compose values. An insane milestone value might be silently turned
    into a sane one, depending on other values; an insane compose
    value is likely to result in either an exception or a non-
    plausible release. Of course this function may also return a
    release that does not exist, and this is desired in some cases.

    Note that if all version values are left unset, you will get the
    current date's most recent RawhideNightly if there is one, or
    else you will get a non-existent RawhideNightly for today's date
    with respin 0. Also note that either release or milestone being
    set to Rawhide will always result in a RawhideNightly; this is to
    ensure compatibility with wikitcms, where Rawhide compose events
    are versioned as e.g. 23 Rawhide 20150304. Wikitcms similarly
    tries to handle fedfind release values (by guessing a release
    number for a version like Rawhide '' 20150304 0), so usually,
    fedfind and wikitcms versions are transparently interchangeable.

    For nightlies, pass compose as 'YYYYMMDD'. You'll wind up with
    either a Rawhide, Branched, Atomic, Docker, Cloud, Container, IoT,
    Updates or Updates-testing nightly, depending on release and
    milestone. If you set a valid release number and leave milestone
    unset, you'll get an Atomic only if it exists and BranchedNightly
    for the same values doesn't, otherwise you'll get BranchedNightly.
    You can never get anything else by nightly detection, you must
    specify it via dist, milestone, cid or url. If you set a valid
    release number and a valid nightly milestone or dist, you'll get
    what you asked for. For any other case you'll wind up with
    RawhideNightly (or RawhideModularNightly).

    At present the interesting values for dist are 'Fedora' (the
    default), 'Fedora-Atomic', 'Fedora-Cloud', 'Fedora-Docker',
    'Fedora-Container' and 'Fedora-IoT'. 'Fedora' is the defualt and
    will give you 'mainstream' composes. The other dists give you the
    post-release two-week Atomic, Cloud, Docker, Container and IoT
    nightly composes respectively.

    If you set a nightly type milestone and leave compose unset, we
    will use today's date as the compose. For all cases, if you
    specify respin, you'll get an instance with that respin, whether
    it exists or not. If you don't specify it, fedfind will try to
    find the latest completed compose for the release, milestone and
    date given or guessed and return that; if there aren't any, it
    will return an instance for 'respin 0' for that date.

    For candidates, you must specify a valid milestone and compose. If
    you don't specify release, we'll try and find out what the
    current Branched is, and use that. If you don't specify a
    milestone, we'll raise ValueError.

    For milestone releases (Alpha/Beta), specify the milestone. We
    will guess the release in the same way as for candidates if it is
    not passed. Note that milestone 'RC' / 'Final' will be treated the
    same way as no milestone at all, i.e. returning a stable release.

    For stable releases, specify the release. You may specify
    milestone 'Final' but it is not necessary. There is no release
    guessing for stable releases.
    """
    # For safety in case these are passed as None.
    if not release:
        release = ''
    if not milestone:
        milestone = ''
    if not compose:
        compose = ''

    # ACTUAL LOGIC STARTS HERE
    if url:
        ret = _parse_url(url)
        if ret:
            (dist, release, milestone, compose, respin, cid) = ret
        else:
            # we couldn't parse the URL, so just give a raw Pungi4
            # Release and hope for the best...but let's only do it
            # if the URL is within fedoraproject.org.
            if url.startswith(fedfind.const.KNOWN_PREFIXES):
                return Pungi4Release(url)
            else:
                raise ValueError("Unexpected URL {0}, expected to start with one of {1}".format(
                    url, ' '.join(fedfind.const.KNOWN_PREFIXES)))
    elif cid:
        (dist, release, milestone, compose, respin) = _parse_cid(cid)
        if promote:
            label = fedfind.helpers.label_from_cid(cid)
            if label:
                (milestone, compose, respin) = _parse_label(label)
    elif label:
        (milestone, compose, respin) = _parse_label(label)

    # this handles the pre-4.x cases where we handled some dists as
    # milestones
    (dist, milestone) = _legacy_milestones(dist, milestone)

    compose = _guess_compose(dist, release, milestone, compose)
    release = _guess_release(dist, release, milestone, compose)

    # RespinRelease case
    if str(dist).lower() == 'fedorarespin':
        try:
            return RespinRelease(release=release, compose=compose)
        except fedfind.exceptions.DiscoveryError as err:
            raise ValueError(err)

    # Handle pre-Pungi 4 'Final' milestone; in Pungi 4 world, 'RC' is
    # the milestone for these
    if str(milestone).lower() == 'final':
        milestone = 'RC'

    if respin is None and '.' in compose:
        # as a bit of fudge, we'll see if we got a compose value that
        # looks like it includes a respin, and parse it out if so.
        # This will handle '1.1' and '20160314.n.0'
        elems = compose.split('.')
        (compose, respin) = (elems[0], elems[-1])

    if respin is not None:
        try:
            respin = int(str(respin))
        except ValueError:
            raise ValueError("get_release(): respin must be an integer!")

    # All Rawhide cases.
    if release == 'Rawhide':
        if not fedfind.helpers.date_check(compose, fail_raise=False):
            raise ValueError("get_release(): for Rawhide, compose must be a date!")
        if respin is not None:
            if dist.lower() == 'fedora-modular':
                return RawhideModularNightly(compose, respin)
            else:
                return RawhideNightly(compose, respin)
        else:
            return _guess_nightly_respin(dist, release, milestone, compose)

    # 'Bikeshed' modular nightly case (this is basically Rawhide, but
    # releng decided to change the name for some goddamn reason).
    if release == 'Bikeshed' and dist.lower() == 'fedora-modular':
        if respin is not None:
            return BikeshedModularNightly(compose, respin)
        else:
            return _guess_nightly_respin(dist, release, milestone, compose)

    # All nightly cases. 'Production' also handled here, as 'compose'
    # is a date.
    if fedfind.helpers.date_check(compose, fail_raise=False):
        return _get_nightly(dist, release, milestone, compose, respin)

    # Production candidates ('Alpha 1.1' etc.)
    if milestone and compose:
        if respin is None:
            raise ValueError("get_release(): for candidate composes, respin "
                             "must be specified or included in compose")
        # first, see if we have a Compose - i.e. the compose has been
        # synced to alt/stage
        if dist.lower() == 'fedora-modular':
            rel = ModularCompose(release, milestone, compose, respin)
        else:
            rel = Compose(release, milestone, compose, respin)
        if rel.exists:
            return rel

        # if not, try getting the cid from the label and return a
        # Production - the location for the compose on the unmirrored
        # kojipkgs server
        if not label:
            label = "{0}-{1}.{2}".format(milestone, compose, respin)
        if not cid:
            # We may actually have a compose ID already on one path:
            # if the user called us with a compose ID and promote=True
            # and we got a label, but the compose is not mirrored and
            # so not found as a Compose above. Re-use it in this case.
            cid = fedfind.helpers.cid_from_label(release, label)
        if cid:
            (dist, release, milestone, compose, respin) = _parse_cid(cid)
            return Production(release, compose, respin)
        else:
            raise ValueError("get_release(): could not find release for {0}, "
                             "{1}, {2}".format(release, milestone, compose))

    # At this point we've handled all composes that we can. If compose
    # is still set, this has to be an error.
    if compose:
        raise ValueError("get_release(): cannot guess milestone for non-date compose!")

    # Non-final milestones.
    if milestone and str(milestone).lower() != 'rc':
        return Milestone(release, milestone)

    # Anything that makes it this far must be a stable release.
    return _get_stable(release)


class Release(object):
    """Abstract class for releases, providing shared attributes and
    methods.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, release='', milestone='', compose=''):
        self.release = str(release).capitalize()
        self.milestone = str(milestone).capitalize()
        self.compose = str(compose).upper()
        self.version = self.release
        if self.milestone:
            self.version += ' {0}'.format(self.milestone)
        if self.compose:
            self.version += ' {0}'.format(self.compose)
        try:
            if self.respin:
                self.version += '.{0}'.format(self.respin)
        except AttributeError:
            # some classes have no respin
            pass
        # the 'dist' for most non-Pungi4 releases is 'Fedora', Pungi4
        # classes handle this differently, as does RespinRelease
        self.dist = "Fedora"

    def __repr__(self):
        return "{0}(release='{1}', milestone='{2}', compose='{3}')".format(
            self.__class__, self.release, self.milestone, self.compose)

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self.version)

    @abc.abstractproperty
    def previous_release(self):
        """The previous release of the same series. Like follows like,
        in this case: the 'previous' release for a stable release is
        the previous stable release, not the last RC. Cannot be relied
        upon for all cases, there are some where it's just too icky:
        will raise a ValueError in that case. May also return a
        release that never existed (in the case of the very first
        Branched nightly for a release, for instance), a release that
        existed but no longer does (an old milestone), or a release
        that does not yet exist but may later."""
        pass

    @abc.abstractproperty
    def location(self):
        """Compose's base location, as an HTTPS URL."""
        pass

    @abc.abstractproperty
    def exists(self):
        """Whether the release is considered to 'exist'."""
        pass

    @abc.abstractproperty
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        pass

    @abc.abstractproperty
    def done(self):
        """Whether the compose is complete."""
        pass

    @abc.abstractproperty
    def metadata(self):
        """dict containing some productmd-style metadata for the
        compose. For a compose that actually exists, it's expected to
        contain at least the key 'images', whose value should be a
        dict in the form of the productmd images.json file. May also
        contain 'composeinfo' and 'rpms' items containing dicts in
        those formats (though 'rpms' is very large and should
        probably be retrieved / parsed only on specific request).
        For a compose that doesn't exist, this dict may be empty.
        """
        pass

    @property
    def alt_location(self):
        """The base URL of the bits of the compose that live under
        /alt on the mirrors. This only really exists for MirrorRelease
        and subclasses, but we set it here just to make pylint happy.
        The branch of all_images on which its used will only ever be
        hit for MirrorRelease subclasses, but pylint doesn't know.
        """
        return ""

    @property
    def expected_images(self):
        """These are the most important images that should be expected
        to exist for a release of the given type. Basically if any of
        these images does not exist, we ought to be worried. Pretty
        close to the concept of a 'release blocking' image, but I
        didn't want to commit to this being exactly that. Must be an
        iterable of (subvariant, imagetype, arch) tuples. Here we list
        ones that most releases share; Release classes should start
        from this list and add more. For Fedora.next releases (post
        F20), we expect KDE and Workstation lives and Cloud base and
        atomic disk images. For Fedora 7-20 we expect KDE and Desktop
        lives. For releases after ARM became primary (F20+), we expect
        a minimal disk image and one desktop disk image; for F20-F22
        it was Xfce, for F23+ it's KDE.

        Getting this historically correct is a bit anal, but if
        nothing else this code may serve as some kind of record of
        Fedora key deliverables for the future.
        """
        imgs = list()
        intels = (arch.name for arch in fedfind.const.ARCHES if arch.group == 'intel')
        # i386 stopped being primary in f26, fedfind doesn't currently
        # handle secondary arches
        if self._relnum > 25:
            intels = (intel for intel in intels if intel != 'i386')
        arms = (arch.name for arch in fedfind.const.ARCHES if arch.group == 'arm')
        for arch in intels:
            if self._relnum > 20:
                imgs.append(('kde', 'live', arch))
                imgs.append(('workstation', 'live', arch))
                imgs.append(('server', 'boot', arch))
                imgs.append(('server', 'dvd', arch))
                # per dgilmore, we stopped doing 32-bit Cloud with F24
                if arch == 'x86_64' or self._relnum < 24:
                    imgs.append(('cloud_base', 'raw-xz', arch))
                    imgs.append(('cloud_base', 'qcow2', arch))
            elif self._relnum > 1:
                imgs.append(('everything', 'boot', arch))
                if self._relnum > 2:
                    imgs.append(('everything', 'dvd', arch))
                if self._relnum > 6:
                    imgs.append(('kde', 'live', arch))
                    imgs.append(('desktop', 'live', arch))
                # 7 and 8 had no installer CDs, for...some reason?
                if self._relnum < 15 and self._relnum not in (7, 8):
                    imgs.append(('everything', 'cd', arch))

        if self._relnum > 19:
            for arch in arms:
                imgs.append(('minimal', 'raw-xz', arch))
                if self._relnum > 22:
                    imgs.append(('xfce', 'raw-xz', arch))
                else:
                    imgs.append(('kde', 'raw-xz', arch))

        return imgs

    @property
    def all_images(self):
        """All images from the compose. Flatten the image dicts from
        the compose metadata, stuff the variant into each image dict,
        'correct' the dict (fix issues in upstream metadata values),
        add 'url' and 'direct_url' keys with download URLs for the
        image, return list of all image dicts.
        """
        if not self.metadata.get('images'):
            return []
        images = []
        imgsdict = self.metadata['images']['payload']['images']
        for variant in imgsdict.keys():
            for arch in imgsdict[variant].keys():
                for imgdict in imgsdict[variant][arch]:
                    imgdict['variant'] = variant
                    # apply any necessary 'corrections'
                    imgdict = fedfind.helpers.correct_image(imgdict)
                    # add a URL key (save consumers having to do this
                    # work themselves)
                    if imgdict.get('alt', False):
                        imgdict['url'] = "{0}/{1}".format(self.alt_location, imgdict['path'])
                    else:
                        imgdict['url'] = "{0}/{1}".format(self.location, imgdict['path'])
                    # add a direct_url key, again for consumer ease
                    if imgdict['url'].startswith(fedfind.const.HTTPS):
                        imgdict['direct_url'] = imgdict['url'].replace(
                            fedfind.const.HTTPS, fedfind.const.HTTPS_DL)
                    else:
                        imgdict['direct_url'] = imgdict['url']
                    images.append(imgdict)
        return images

    @cached_property
    def _relnum(self):
        """Having to deal with 'rawhide' when checking self.release is
        really annoying; this is a silly hack to help with that. It's
        a property because self.release can actually involve a round
        trip, for bare Pungi4Release instances, so we don't want to
        set it up in __init__.
        """
        try:
            if self.release.lower() == 'rawhide':
                return 999
            else:
                return int(self.release)
        except AttributeError:
            # this happens in an odd path used in RespinRelease init
            return 999

    def check_expected(self):
        """This checks whether all expected images are included in the
        release. If the release doesn't exist, it will raise an
        exception. If any expected images are missing, it will return
        a set of (subvariant, imagetype, arch) tuples identifying the
        missing images. If nothing is missing, it will return an empty
        set.
        """
        if not self.exists:
            raise ValueError('Release does not exist!')
        logger.debug("expected images: %s", self.expected_images)
        missing = set(self.expected_images)
        for exptup in self.expected_images:
            for imgdict in self.all_images:
                imgtup = (imgdict['subvariant'].lower(), imgdict['type'], imgdict['arch'])
                if imgtup == exptup:
                    missing.discard(exptup)
        return missing

    def get_package_nvras(self, packages):
        """Passed a list of source package names, returns a dict with
        the names as the keys and the NVRAs of those packages found in
        the compose's tree as the values. May raise an exception if
        the compose doesn't exist, or it can't reach the server. For
        any package not found, the value will be the empty string.
        Note this truly returns NVRAs, not NEVRAs; we cannot discover
        the epoch. It returns the arch even though it's *always* going
        to be 'src' so you can feed the result to common NEVRA split
        functions.
        """
        verdict = dict((package, '') for package in packages)
        initials = set([p[0].lower() for p in packages])
        text = ''
        # Grab the directory indexes we need. This is a bit different
        # for older releases; it's awkward to express this via the
        # classes so just conditionalize it here. Before F17, package
        # directories like this one are not split into subdirectories
        # by first character. Before F7, there was no /Everything.
        # Before F5, there was no /source.
        tree = "Everything"
        if "Modular" in self.location:
            # Modular composes don't have an Everything tree ATM
            tree = "Server"
        split = True
        if self._relnum < 17:
            split = False
        if self._relnum > 23:
            url = '{0}/{1}/source/tree/Packages/'.format(self.location, tree)
        elif self._relnum > 6:
            url = '{0}/{1}/source/SRPMS/'.format(self.location, tree)
        elif self._relnum > 4:
            url = '{0}/source/SRPMS/'.format(self.location)
        else:
            url = '{0}/SRPMS/'.format(self.location)
        if split:
            for i in initials:
                suburl = '{0}{1}/'.format(url, i)
                index = fedfind.helpers.urlopen_retries(suburl)
                text += index.read().decode('utf-8')
        else:
            text = fedfind.helpers.urlopen_retries(url).read().decode('utf-8')
        # Now find each package's NVR. This is making a couple of
        # assumptions about how the index HTML source will look and
        # also assuming that the 'version-release' is the bit after
        # packagename- and before .src.rpm, it's not perfect (won't do
        # epochs) but should be good enough.
        for package in packages:
            patt = re.compile('href="(' + package + r'.*?\.src)\.rpm')
            match = patt.search(text)
            if match:
                ver = match.group(1)
                verdict[package] = ver
        return verdict


class Pungi4Release(Release):
    """A Pungi 4 release. Real metadata! Other unicorn-like things! We
    *can* derive pretty much all information about a Pungi 4 release
    from its metadata, and this class works that way, and must be told
    where the compose is located: the single required argument is an
    HTTP(S) URL to the /compose directory for the compose. There are
    several optional args which will be stored on the instance (thus
    preventing those properties being retrieved from metadata) if set.
    Child classes may work more like old fedfind classes, allowing you
    to locate a compose based on its version information, and will
    pass the optional args. A Pungi4Release instance for a compose
    that does not exist at all is fairly useless and you will rarely
    want such a beast.
    """
    # This is intentional: parent class __init__ does nothing for us.
    # There isn't really a better way to set this up.
    # pylint:disable=super-init-not-called,too-many-arguments,too-many-instance-attributes
    def __init__(self, location, release=None, milestone=None, compose=None,
                 respin=None, typ=None, cid=None, label=None, version=None):
        self._location = location.strip('/')
        # These are defaults for semi-cached properties.
        self._status = None
        self._exists = False
        self._metadata = None
        self._release = release
        self._milestone = milestone
        self._compose = compose
        self._respin = respin
        self._type = typ
        self._cid = cid
        self._label = label
        self._version = version
        self._prefurl = "direct"

    def __repr__(self):
        return "{0}(location='{1}')".format(self.__class__, self.location)

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self.location)

    @property
    def location(self):
        """Compose's location. Implemented as a property to make
        pylint happy (it's about class inheritance and blahblah.)
        """
        return self._location

    @property
    def _checkloc(self):
        """Used for finding metadata, checking existence, stuff like
        that. In most cases is the same as location, but for some
        releases, we want to use HTTPS for location but HTTPS_DL for
        _checkloc (subclasses implement this).
        """
        return self._location

    @property
    def exists(self):
        """Whether the compose exists. We cache 'True' because if we
        exist we're unlikely to *stop* existing."""
        if self._exists:
            return self._exists
        elif fedfind.helpers.url_exists(self._checkloc):
            self._exists = True
            return self._exists
        else:
            return False

    @cached_property
    def https_url_generic(self):
        """Everything tree is 'generic' for Pungi 4."""
        return "{0}/{1}".format(self.location, "Everything")

    @property
    def status(self):
        """The canary file is all we need. We cache finished states as
        they will not change.
        """
        if self._status:
            return self._status
        if self.exists:
            try:
                url = self._checkloc[:-7] + "STATUS"
                resp = fedfind.helpers.urlopen_retries(url)
                resp = resp.read().decode('utf-8').strip('\n')
                if resp in fedfind.const.PUNGI_DONE:
                    self._status = resp
                return resp
            except ValueError:
                logger.warning("Pungi4Release: failed to find status!")
                return ""
        else:
            return ""

    @property
    def done(self):
        """Check status against the Pungi status constants.
        """
        return self.status in fedfind.const.PUNGI_DONE

    @property
    def metadata(self):
        """Read metadata from server. We cache this if we're done as
        it will not change.
        """
        done = self.done
        metadata = {'composeinfo': {}, 'images': {}}
        if done and self._metadata:
            return self._metadata
        elif self.exists:
            try:
                url = "{0}{1}".format(self._checkloc, "/metadata/composeinfo.json")
                metadata['composeinfo'] = fedfind.helpers.download_json(url)
                url = "{0}{1}".format(self._checkloc, "/metadata/images.json")
                metadata['images'] = fedfind.helpers.download_json(url)
                if done:
                    self._metadata = metadata
                return metadata
            except ValueError:
                logger.error("Pungi4Release: failed to download metadata!")
                return metadata
        else:
            return metadata

    @property
    def cid(self):
        """Compose ID. It's a property because it may involve a remote
        trip. There are two places where this may be found (as for
        status), we check both.
        """
        if self._cid:
            return self._cid
        try:
            return self.metadata['composeinfo']['payload']['compose']['id']
        except KeyError:
            try:
                url = self._checkloc[:-7] + "COMPOSE_ID"
                resp = fedfind.helpers.urlopen_retries(url)
                resp = resp.read().decode('utf-8').strip('\n')
                self._cid = resp
                return resp
            except ValueError:
                logger.warning("Pungi4Release: failed to find compose ID!")
                return ""

    @property
    def label(self):
        """Compose 'label'. Exists only for production composes, looks
        like "Alpha-1.1" or similar. Found similarly to CID.
        """
        if self._label:
            return self._label
        try:
            return self.metadata['composeinfo']['payload']['compose']['label']
        except KeyError:
            logger.debug("Pungi4Release: failed to find compose label!")
            return ""

    @property
    def version(self):
        """For generic Pungi 4 release just use the CID stripped a bit.
        """
        if self._version:
            return self._version
        return '-'.join(self.cid.rsplit('-', 2)[1:])

    @property
    def release(self):
        """Release. It's a property because it may involve a remote
        trip. _release is so subclasses for which this is intrinsic
        can define it and this property returns it.
        """
        if self._release:
            return self._release
        return fedfind.helpers.parse_cid(self.cid, dic=True)['version'].lower()

    @property
    def milestone(self):
        """Milestone. It's a property because it may involve a remote
        trip. _milestone is for same reasons as _release, above.
        """
        if self._milestone is not None:
            return self._milestone
        if self.label:
            return self.label.rsplit('-', 1)[0]
        else:
            # sometimes we just don't know
            return ''

    @property
    def compose(self):
        """Compose. It's a property because it may involve a remote
        trip. _milestone is for same reasons as _release, above.
        """
        if self._compose:
            return self._compose
        if self.label:
            return self.label.rsplit('-', 1)[1].split('.')[0]
        else:
            # sometimes we just don't know
            return ''

    @property
    def type(self):
        """Compose "type" (in productmd terms). Can be parsed from
        cid, but we prefer to read it from metadata. _type is for same
        reasons as _release, above.
        """
        if self._type:
            return self._type
        try:
            return self.metadata['composeinfo']['payload']['compose']['type']
        except KeyError:
            try:
                res = get_date_type_respin(self.cid)[1]
                if res:
                    return res
                else:
                    return ''
            except ValueError:
                return ''

    @property
    def respin(self):
        """Compose "respin" (in productmd terms). Can be parsed from
        cid, but we prefer to read it from metadata. _respin is for the
        same reasons as _release and _type, above.
        """
        if self._respin is not None:
            return self._respin
        if self.label:
            return self.label.rsplit('-', 1)[1].split('.')[1]
        try:
            return str(self.metadata['composeinfo']['payload']['compose']['respin'])
        except KeyError:
            try:
                res = get_date_type_respin(self.cid)[2]
                if res:
                    return str(res)
                else:
                    return ''
            except ValueError:
                return ''

    @property
    def dist(self):
        """Compose "dist" - the first component of the compose ID,
        so 'Fedora', 'Fedora-Atomic', 'Fedora-Docker', 'Fedora-Cloud'
        etc. In productmd terms this is in fact the 'short name', but
        Fedora releng decided not to make them very short...
        """
        return fedfind.helpers.parse_cid(self.cid, dic=True)['short']

    @property
    def product(self):
        """Old name for 'dist', I wound up calling this 'dist' in all
        the get_release stuff, and it's a better name.
        """
        logger.warning("The 'product' attribute is deprecated and will be removed in future. "
                       "Please use the 'dist' attribute instead.")
        return fedfind.helpers.parse_cid(self.cid, dic=True)['short']

    @property
    def previous_release(self):
        """For Pungi 4 composes, we use PDC. We ask for all composes
        for the same release and type, find the one we 'are', and
        return the previous one. We can only do this for completed
        composes, because PDC only stores those. May raise ValueError
        on unknown problems and IndexError if this is the first
        compose of its type for the release.
        """
        if self.status not in fedfind.const.PUNGI_SUCCESS:
            raise ValueError("Cannot find previous compose for "
                             "incomplete or failed Pungi 4 compose!")
        params = {'version': self.release, 'name': self.dist}
        # you can query 'releases' in PDC and releases have a property
        # which is a list of composes ordered by creation date. handy!
        pdcrel = fedfind.helpers.pdc_query('releases', params)[0]
        complist = pdcrel['compose_set']
        # filter to composes of the correct type
        complist = [comp for comp in complist if get_date_type_respin(comp)[1] == self.type]
        try:
            idx = complist.index(self.cid)
        except IndexError:
            raise ValueError("Could not find previous compose for {0}".format(self))
        if idx == 0:
            raise IndexError("{0} is the first compose of its type for this release!".format(self))
        return get_release(cid=complist[idx-1])

    def get_package_nevras_pdc(self, packages):
        """Passed a list of package names, returns a dict with the
        names as the keys and the NEVRAs of those packages found in
        the compose's tree as the values, by querying PDC; this might
        raise ValueError if contacting PDC fails. The value for any
        package not found will be the empty string. Note that unlike
        get_package_nvras, this gives NEVRAs, not NVRAs: we can get
        the epoch from PDC. This allows more accurate comparisons, but
        you cannot safely compare output of get_package_nevras_pdc
        with output of get_package_nvras. There is no equivalent for
        composes that are not in PDC. Also, this will only work once
        the RPMs for a compose have been imported to PDC; the main
        compose metadata is imported before the package metadata, so
        there is a window where the compose is present in PDC but the
        package metadata is not, and if you use this method in that
        time, it will return empty values for all packages (and log a
        warning). You can listen for the fedmsg topic `pdc.rpms` to
        to know when the RPMs for a compose have reached PDC.
        """
        verdict = dict((package, '') for package in packages)
        params = [('compose', self.cid), ('arch', 'src')]
        for package in packages:
            params.append(('name', '^{0}$'.format(package)))
        res = fedfind.helpers.pdc_query('rpms', params)
        if not res:
            logger.warning("get_package_nevras_pdc: No results found in PDC for compose %s! "
                           "Compose RPMs may not yet have been imported.", self.cid)
        for pkg in res:
            verdict[pkg['name']] = pkg['srpm_nevra']
        return verdict

## PUNGI 4 NIGHTLY CLASSES ##


class OldPreviousReleaseMixin(object):
    """This is a mix-in that provides the old, hacky previous_release
    implementation for use while compose import to PDC is broken:
    https://pagure.io/fedora-infrastructure/issue/7935
    """

    @property
    def previous_release(self):
        """We're overriding the parent class here because PDC doesn't
        work right yet. This is hideous, but I dunno how else you can
        do it. We start on the same date. If respin is > 0, we just
        subtract 1, instantiate a compose for the new respin, and see
        if it exists and is complete. We keep doing this till respin
        hits 0, then we subtract a day from the date, reset respin to
        5 (arbitrarily chosen; I haven't seen respin > 4 yet) and try
        that. We rinse and repeat till we've tried 30 times, then give
        up.
        """
        date = self.compose
        respin = int(self.respin)
        # we've gotta give up at some point.
        tries = 30
        # this is to avoid spamming the 'failed to find compose ID!'
        # or 'failed to download metadata!' warning over and over...
        loglevel = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)
        while tries:
            tries -= 1
            if respin == 0:
                date = fedfind.helpers.date_check(date, out='obj')
                date = date - datetime.timedelta(1)
                date = fedfind.helpers.date_check(date, out='str')
                respin = 5
            else:
                respin -= 1
            # productmd ComposeInfo class has a create_compose_id,
            # but it seems like more work to jump through the hoops
            # to instantiate that than it is to reproduce it...
            testcid = "Fedora-{0}-{1}.n.{2}".format(self.release, date, respin)
            # we use get_release_cid not self.__class__ because the
            # params are different for the children classes
            test = get_release(cid=testcid)
            if test.status in fedfind.const.PUNGI_SUCCESS:
                logger.setLevel(loglevel)
                return test
        logger.setLevel(loglevel)
        raise ValueError("Could not find previous compose for "
                         "{0}".format(self))


class RawhideNightly(OldPreviousReleaseMixin, Pungi4Release):
    """Rawhide "nightly" (bit of a misnomer, now) composes."""
    def __init__(self, compose, respin=0, cid=None):
        compose = str(compose)
        respin = str(respin)
        path = "rawhide/Fedora-Rawhide-{0}.n.{1}/compose".format(compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(RawhideNightly, self).__init__(url, release="Rawhide", milestone='', compose=compose,
                                             respin=respin, typ="nightly", cid=cid)

    @property
    def expected_images(self):
        imgs = super(RawhideNightly, self).expected_images
        if int(self.compose) < 20190214:
            # We expected to get Atomic disk images for nightlies prior
            # to 2019-02-14, but we DON'T get them for candidate
            # composes, so they must go here in the nightly classes
            imgs.append(('atomichost', 'raw-xz', 'x86_64'))
            imgs.append(('atomichost', 'qcow2', 'x86_64'))
        return tuple(imgs)


class RawhideModularNightly(Pungi4Release):
    """Rawhide modular "nightly" (bit of a misnomer, now) composes.
    Note these were replaced by BikeshedModularNightly between
    20171003 and 20171013, there are none of these composes after
    that date; once the earlier composes are removed this class will
    likely be turned into a redirect to BikeshedModularNightly.
    """
    def __init__(self, compose, respin=0, cid=None):
        compose = str(compose)
        respin = str(respin)
        path = "Fedora-Modular-Rawhide-{0}.n.{1}/compose".format(compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(RawhideModularNightly, self).__init__(
            url, release="Rawhide", milestone='', compose=compose,
            respin=respin, typ="nightly", cid=cid)

    @property
    def expected_images(self):
        return (
            ('docker_base', 'docker', 'x86_64'),
            ('server', 'dvd', 'arm'),
            ('server', 'dvd', 'x86_64'),
            ('server', 'qcow2', 'x86_64'),
            ('server', 'raw-xz', 'x86_64'),
        )

    @cached_property
    def https_url_generic(self):
        """Server tree is 'generic' for modular composes at present,
        there is no Everything tree.
        """
        return "{0}/{1}".format(self.location, "Server")


class BikeshedModularNightly(Pungi4Release):
    """Bikeshed modular "nightly" (bit of a misnomer, now) composes.
    This is basically Rawhide for modular, I don't know why releng
    decided to change the name other than to screw with me...
    """
    def __init__(self, compose, respin=0, cid=None):
        compose = str(compose)
        respin = str(respin)
        path = "Fedora-Modular-Bikeshed-{0}.n.{1}/compose".format(compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(BikeshedModularNightly, self).__init__(
            url, release="Bikeshed", milestone='', compose=compose,
            respin=respin, typ="nightly", cid=cid)

    @property
    def expected_images(self):
        return (
            ('docker_base', 'docker', 'x86_64'),
            ('server', 'dvd', 'arm'),
            ('server', 'dvd', 'x86_64'),
            ('server', 'qcow2', 'x86_64'),
            ('server', 'raw-xz', 'x86_64'),
        )

    @cached_property
    def https_url_generic(self):
        """Server tree is 'generic' for modular composes at present,
        there is no Everything tree.
        """
        return "{0}/{1}".format(self.location, "Server")


class BranchedNightly(OldPreviousReleaseMixin, Pungi4Release):
    """Branched "nightly" (bit of a misnomer, now) composes."""
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "branched/Fedora-{0}-{1}.n.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(BranchedNightly, self).__init__(
            url, release=release, milestone="Branched", compose=compose,
            respin=respin, typ="nightly", cid=cid)
        self._release = release
        self._milestone = "Branched"

    @property
    def expected_images(self):
        imgs = super(BranchedNightly, self).expected_images
        if int(self.compose) < 20190214:
            # We expected to get Atomic disk images for nightlies prior
            # to Fedora 30, but we DON'T get them for candidate
            # composes, so they must go here in the nightly classes
            imgs.append(('atomichost', 'raw-xz', 'x86_64'))
            imgs.append(('atomichost', 'qcow2', 'x86_64'))
        return tuple(imgs)


class BranchedModularNightly(Pungi4Release):
    """Branched modular "nightly" (bit of a misnomer, now) composes."""
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "Fedora-Modular-{0}-{1}.n.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(BranchedModularNightly, self).__init__(
            url, release=release, milestone="Branched", compose=compose,
            respin=respin, typ="nightly", cid=cid)
        self._release = release
        self._milestone = "Branched"

    @property
    def expected_images(self):
        return (
            ('docker_base', 'docker', 'x86_64'),
            ('server', 'dvd', 'arm'),
            ('server', 'dvd', 'x86_64'),
            ('server', 'qcow2', 'x86_64'),
            ('server', 'raw-xz', 'x86_64'),
        )


class AtomicNightly(Pungi4Release):
    """Two-week Atomic nightly composes. Note, these are usually
    'production' composes in productmd terms, even though they're
    built nightly.
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "twoweek/Fedora-Atomic-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(AtomicNightly, self).__init__(
            url, release=release, milestone="Nightly", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Atomic images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the important Atomic images. Historical note:
        these composes included Cloud images for some time, but this
        stopped around early 2017. We don't bother 'expecting' Cloud
        images for composes from before the change, it just doesn't
        seem important enough to be worth bothering with.
        """
        if self._relnum > 27:
            subv = 'atomichost'
        else:
            subv = 'atomic'
        return (
            (subv, 'qcow2', 'x86_64'),
            (subv, 'raw-xz', 'x86_64'),
            (subv, 'vagrant-libvirt', 'x86_64'),
            (subv, 'vagrant-virtualbox', 'x86_64'),
            (subv, 'dvd-ostree', 'x86_64')
        )


class CloudNightly(Pungi4Release):
    """Cloud nightly composes for the current stable release (like
    the Atomic nightly composes, except they only build Cloud images).
    As with AtomicNightly, these are 'production' type composes, even
    though they happen nightly.
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "cloud/Fedora-Cloud-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(CloudNightly, self).__init__(
            url, release=release, milestone="Nightly", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Cloud images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the intended images.
        """
        return (
            ('cloud_base', 'qcow2', 'x86_64'),
            ('cloud_base', 'raw-xz', 'x86_64'),
            ('cloud_base', 'vagrant-libvirt', 'x86_64'),
            ('cloud_base', 'vagrant-virtualbox', 'x86_64'),
        )


class DockerNightly(Pungi4Release):
    """Docker nightly composes for the current stable release (like
    the Atomic nightly composes, except they only build the Docker
    base image). As with AtomicNightly, these are 'production' type
    composes, even though they happen nightly.
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "container/Fedora-Docker-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(DockerNightly, self).__init__(
            url, release=release, milestone="Nightly", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Docker images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the intended images.
        """
        return (
            ('docker_base', 'docker', 'x86_64'),
            ('docker_base', 'docker', 'armhfp'),
        )


class ContainerNightly(Pungi4Release):
    """Container nightly composes for the current stable release.
    This is basically DockerNightly renamed to be more generic - the
    DockerNightly composes will go away when F27 goes EOL, I think.
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "container/Fedora-Container-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(ContainerNightly, self).__init__(
            url, release=release, milestone="Nightly", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Docker images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the intended images.
        """
        return (
            ('container_base', 'docker', 'x86_64'),
            ('container_base', 'docker', 'armhfp'),
            ('container_minimal_base', 'docker', 'x86_64'),
            ('container_minimal_base', 'docker', 'armhfp'),
        )


class IoTNightly(Pungi4Release):
    """IoT nightly composes for stable releases (like the Atomic
    nightly composes, but with IoT images).
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "iot/Fedora-IoT-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(IoTNightly, self).__init__(
            url, release=release, milestone="Nightly", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Docker images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the intended images.
        """
        return (
            ('iot', 'dvd', 'x86_64'),
            ('iot', 'dvd-ostree', 'x86_64'),
            ('iot', 'raw-xz', 'x86_64'),
            ('iot', 'dvd', 'aarch64'),
            ('iot', 'dvd-ostree', 'aarch64'),
            ('iot', 'raw-xz', 'aarch64'),
        )


class Updates(Pungi4Release):
    """'updates' compose. These are mainly intended to produce the
    'updates' repository for a release, but they also produce Atomic
    images, and this is intended to replace the AtomicNightly composes
    at some point.  Like other post-release nightlies, these are of
    type 'production'.
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "updates/Fedora-{0}-updates-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(Updates, self).__init__(
            url, release=release, milestone="Updates", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Atomic images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the intended images.
        """
        if self.release.isdigit and int(self.release) > 29:
            # right now, these do not include any images, as we
            # stopped doing atomichost from 30, but coreos is not
            # happening yet
            return tuple()
        return (
            ('atomichost', 'qcow2', 'x86_64'),
            ('atomichost', 'raw-xz', 'x86_64'),
        )


class UpdatesTesting(Pungi4Release):
    """'updates-testing' compose. These are mainly intended to produce
    the 'updates-testing' repository for a release, but they also
    produce Atomic images. Like other post-release nightlies, these are
    of type 'production'.
    """
    def __init__(self, release, compose, respin=0, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "updates/Fedora-{0}-updates-testing-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(UpdatesTesting, self).__init__(
            url, release=release, milestone="Updates-testing", compose=compose,
            respin=respin, typ="production", cid=cid)
        self._release = release

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies include only Atomic images, so we do not
        take the 'universal' definition from the Release class, we
        just 'expect' the intended images.
        """
        if self.release.isdigit and int(self.release) > 29:
            # right now, these do not include any images, as we
            # stopped doing atomichost from 30, but coreos is not
            # happening yet
            return tuple()
        return (
            ('atomichost', 'qcow2', 'x86_64'),
            ('atomichost', 'raw-xz', 'x86_64'),
        )

## PUNGI 4 CANDIDATE COMPOSES ##


class Production(Pungi4Release):
    """A Pungi 4 'production' compose, on kojipkgs, identified by date
    and respin (not label). 'compose' is the date. e.g. 24, 20160314,
    1 for
    https://kojipkgs.fedoraproject.org/compose/24/Fedora-24-20160314.1
    The *same* compose may have been synced to the mirror system and
    be instantiable as a Compose (see below).
    NOTE: Production instances have their *real* milestone, compose
    and respin as self.milestone, self.compose, and self.respin, not
    'Production', the date, and the respin relative to date. This is
    is pretty much arbitrary.
    """
    def __init__(self, release, compose, respin, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "{0}/Fedora-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(Production, self).__init__(url, release=release, cid=cid)
        # We do not set compose or milestone as we want those to be
        # parsed from the label - see class docstring.

    @property
    def version(self):
        """Use release milestone compose.respin, but don't set
        _version in init as that would cause remote trips, do it here
        as a property.
        """
        return "{0} {1} {2}.{3}".format(self.release, self.milestone, self.compose, self.respin)


class ModularProduction(Pungi4Release):
    """A modular Pungi 4 'production' compose, on kojipkgs, identified
    by date and respin (not label). 'compose' is the date. e.g. 27,
    20171107, 1 for
    https://kojipkgs.fedoraproject.org/compose/27/Fedora-Modular-27-20171107.1
    The *same* compose may have been synced to the mirror system and
    be instantiable as a ModularCompose (see below).
    """
    def __init__(self, release, compose, respin, cid=None):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "{0}/Fedora-Modular-{0}-{1}.{2}/compose".format(release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(ModularProduction, self).__init__(url, release=release, cid=cid)
        # We do not set compose or milestone as we want those to be
        # parsed from the label - see class docstring.

    @property
    def version(self):
        """Use release milestone compose.respin, but don't set
        _version in init as that would cause remote trips, do it here
        as a property.
        """
        return "{0} Modular {1} {2}.{3}".format(
            self.release, self.milestone, self.compose, self.respin)


class Compose(Pungi4Release):
    """A candidate compose that has been synced to the staging tree
    on the mirrors. The exact same compose may be available from
    kojipkgs as a Production (above). As for old-fedfind, we do not
    use the mirror system for this class because syncing is not super
    reliable (as I write this, a day after F24 Alpha 1.5 happened,
    mirrors.kernel.org has still not synced it fully). That's why this
    isn't a Pungi4Mirror subclass.
    """
    # pylint:disable=too-many-arguments
    def __init__(self, release, milestone, compose, respin, cid=None):
        release = str(release)
        milestone = str(milestone)
        compose = str(compose)
        respin = str(respin)
        label = "{0}-{1}.{2}".format(milestone, compose, respin)
        version = "{0} {1} {2}.{3}".format(release, milestone, compose, respin)
        url = '{0}/alt/stage/{1}_{2}'.format(fedfind.const.HTTPS_DL, release, label)
        super(Compose, self).__init__(
            url, release=release, milestone=milestone, compose=compose,
            respin=respin, label=label, typ="production", version=version, cid=cid)

    @property
    def status(self):
        """Assume mirrored composes are always FINISHED."""
        return "FINISHED"


class ModularCompose(Pungi4Release):
    """A modular candidate compose that has been synced to the staging
    tree on the mirrors. The exact same compose may be available from
    kojipkgs as a ModularProduction.
    """
    # pylint:disable=too-many-arguments
    def __init__(self, release, milestone, compose, respin, cid=None):
        release = str(release)
        milestone = str(milestone)
        compose = str(compose)
        respin = str(respin)
        label = "{0}-{1}.{2}".format(milestone, compose, respin)
        version = "{0} Modular {1} {2}.{3}".format(release, milestone, compose, respin)
        url = '{0}/alt/stage/{1}_Modular_{2}'.format(fedfind.const.HTTPS_DL, release, label)
        super(ModularCompose, self).__init__(
            url, release=release, milestone=milestone, compose=compose,
            respin=respin, label=label, typ="production", version=version, cid=cid)

    @property
    def status(self):
        """Assume mirrored composes are always FINISHED."""
        return "FINISHED"

## PUNGI 4 MIRROR CLASSES ##


class Pungi4Mirror(Pungi4Release):
    """A Pungi 4-type release which is in the mirror system. We want
    to use dl.fp.o for grabbing metadata and stuff (as the mirrors
    are not sufficiently reliable) but print URLs with download.fp.o.
    Note, even though milestone releases since Fedora 24 have been
    built with Pungi 4, we are not yet using this class, as when
    milestone releases are synced to the public mirrors they are split
    between two separate locations and the productmd metadata for the
    compose is not included in either location, since it would not
    accurately reflect what was actually present in either location.
    """
    def __init__(self, path, **kwargs):
        self._basepath = path.rstrip('/')
        super(Pungi4Mirror, self).__init__("{0}{1}".format(fedfind.const.HTTPS, path), **kwargs)

    def __repr__(self):
        return "{0}(path='{1}')".format(self.__class__, self._basepath)

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self._basepath)

    @property
    def _checkloc(self):
        """We use const.HTTPS in the public 'location' for this class,
        but for check purposes we want to use HTTPS_DL, more reliable.
        """
        return self.location.replace(fedfind.const.HTTPS, fedfind.const.HTTPS_DL)

    @property
    def status(self):
        """Assume mirrored composes are always FINISHED."""
        return "FINISHED"

## NON-PUNGI 4 CLASSES ##


class MirrorRelease(Release):
    """A parent class for releases synced into the public mirror
    system. This includes both stable releases built with pre-Pungi
    4 tooling, and milestone and stable releases built with Pungi 4
    but split into 'main' and 'alt' trees and with their metadata
    stripped when synced to the public mirrors.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, release, milestone='', compose=''):
        super(MirrorRelease, self).__init__(release, milestone, compose)
        self._prefurl = "mirror"
        # Defaults for semi-cached properties.
        self._exists = False
        self._all_paths = []
        self._metadata = None
        # This is a faked-up compose ID which may be used as our 'cid'
        # property if we can't find a real one. We store it on the
        # instance so methods can check if we have a real or fake one
        # by doing 'self.cid == self._fakecid".
        self._fakecid = "Fedora-{0}-19700101.0".format(self.release)

    @abc.abstractproperty
    def _basepath(self):
        """Top level path for the main section of this release,
        relative to /pub on the master mirror).
        """
        pass

    @abc.abstractproperty
    def _altbasepath(self):
        """Top level path for the alt section of this release,
        relative to /pub on the master mirror).
        """
        pass

    @property
    def all_paths(self):
        """All image paths for this release, by parsing the relevant
        file lists (we figure these out from the base paths). If the
        release does not exist will return an empty list. Usually
        returns a list of tuples, (location, path), where location is
        'alt' or 'main' to indicate whether the image is in the 'alt'
        or 'main' location and 'path' is the path relative to
        _basepath or _altbasepath. NOTE: from Fedora 9 onwards,
        boot.iso files are omitted, as they are always hardlinks to a
        netinst.iso file and including both in the results serves no
        purpose.
        """
        # pylint:disable=too-many-branches
        if self._all_paths:
            return self._all_paths

        ret = []

        # figure out the relevant file lists
        filelists = []
        for flist in ('fedora', 'archive', 'alt'):
            if self._basepath.startswith(flist):
                filelists = [flist]
        if self._altbasepath and 'alt' not in filelists:
            filelists.append('alt')
        for flist in filelists:
            # this isn't "protected" from fedfind internal use, it's
            # "protected" from use by fedfind consumers.
            # pylint:disable=protected-access
            with fedfind.helpers._get_filelist(flist) as listfh:
                if flist == 'alt' and self._altbasepath:
                    checkpath = self._altbasepath
                else:
                    checkpath = self._basepath

                for path in listfh:
                    # in the file list, paths start with './'. But our
                    # base paths start with the folder name. So sub
                    # ./ with the folder name for comparison
                    path = path.split('/')
                    # along the way, let's check for boot.iso and
                    # throw it out if we're > 8
                    if self._relnum > 8:
                        fname = path[-1].strip()
                        if fname == 'boot.iso':
                            continue
                    path[0] = flist
                    path = '/'.join(path)

                    # Next three lines check if path starts with
                    # checkpath and give us the remnant if so
                    path = path.split(checkpath, 1)
                    if len(path) == 2 and path[0] == '':
                        path = path[1].strip()
                        path = path.lstrip('/')
                        # Stuff remnant in list
                        if flist == 'alt' and self._altbasepath:
                            ret.append(('alt', path))
                        else:
                            ret.append(('main', path))

        if ret:
            # if we got anything, we probably exist and can cache.
            self._all_paths = ret
        return ret

    @property
    def exists(self):
        """Release 'exists' if its https_url_generic is there (we use
        HTTPS_DL instead of HTTPS for reliability, though). If the
        class has no https_url_generic, e.g. RespinRelease, we check
        its base URL. Just checking the base location is wrong for
        releases which have been archived: the 'CurrentRelease' base
        location exists, but contains only a README file pointing to
        the archives. True is cached as it will not change."""
        if self._exists:
            return self._exists
        url = self.https_url_generic.replace(fedfind.const.HTTPS, fedfind.const.HTTPS_DL)
        if not url:
            url = '{0}/{1}'.format(fedfind.const.HTTPS_DL, self._basepath)
        logger.debug("exists: checking URL %s", url)
        if fedfind.helpers.url_exists(url):
            self._exists = True
            return self._exists
        else:
            return False

    @property
    def done(self):
        """For non-nightlies, we just assume we're done if the compose
        exists.
        """
        return self.exists

    @property
    def location(self):
        """Full URL to the top level of the release's main section.
        Used for constructing image paths, etc.
        """
        if self._prefurl == "direct":
            return "{0}/{1}".format(fedfind.const.HTTPS_DL, self._basepath)
        else:
            return "{0}/{1}".format(fedfind.const.HTTPS, self._basepath)

    @property
    def alt_location(self):
        """Full URL to the top level of the release's alt section.
        Used for constructing image paths, etc.
        """
        if self._prefurl == "direct":
            return "{0}/{1}".format(fedfind.const.HTTPS_DL, self._altbasepath)
        else:
            return "{0}/{1}".format(fedfind.const.HTTPS, self._altbasepath)

    @property
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        if self._relnum < 7:
            return self.location
        elif self._relnum < 21:
            return '{0}/Fedora'.format(self.location)
        elif self._relnum <= 23:
            return '{0}/Server'.format(self.location)
        else:
            return '{0}/Everything'.format(self.location)

    @property
    def metadata(self):
        """Pungi 4 / productmd-style metadata for the compose. If we
        can, we identify the compose, retrieve its original metadata
        from PDC, and tweak it a bit (to correct the paths of renamed
        images, and add the 'alt' property).  by analyzing the
        compose's properties. The result can be used in exactly the
        same way as you can access the *real* metadata for a Pungi 4
        compose, so you can treat non-Pungi 4 composes just the same.
        It's a long way from perfect, so far, but it's better than a
        slap around the face with a wet fish. This also helps us with
        internal stuff, like the way all_images is produced from this
        'metadata'. Note that as mirrored releases are split across
        'main' and 'alt' locations, we add an extra property to the
        image dict to indicate which location the image is in.
        """
        # this is just a complicated operation. we can randomly split it
        # into sub-functions, but that doesn't really make it *better*.
        # pylint:disable=too-many-locals,too-many-branches,too-many-statements
        if self._metadata:
            return self._metadata

        imagesdict = defaultdict(lambda: defaultdict(list))
        origmd = None
        if self.cid != self._fakecid:
            # We can try to get the real metadata from PDC and just
            # tweak it a bit.
            try:
                origmd = fedfind.helpers.pdc_query('compose-images/{0}'.format(self.cid))
                # we should also be able to retrieve the original
                # composeinfo dict, but I can't find that at all...
            except ValueError:
                origmd = None

        paths = self.all_paths
        if not paths:
            return {'composeinfo': {}, 'images': {}}

        # composeinfo variants dict, gets populated as we parse the
        # images
        variants = {}
        # look, this is just complicated, okay? jeez.
        # pylint:disable=too-many-nested-blocks
        for (loc, path) in paths:
            matches = 0
            matched = None
            # We only try to find *unique* filenames in the existing
            # data (otherwise we wind up just updating one dict for
            # every boot.iso file, for e.g.) If this condition fails
            # we'll fall through to synthesizing the dict.
            if origmd and len([item for item in self.all_paths
                               if item[1].split('/')[-1] == path.split('/')[-1]]) == 1:
                fname = path.split('/')[-1]
                for variant in origmd['payload']['images']:
                    # troll through the existing dict and see if any
                    # filenames match
                    for arch in origmd['payload']['images'][variant]:
                        for img in origmd['payload']['images'][variant][arch]:
                            matchname = img['path'].split('/')[-1]
                            if fname == matchname:
                                matches += 1
                                matched = (variant, arch, img)

            if matches == 1:
                # if we found *exactly one* image with the same file
                # name, we can just use that dict
                (variant, arch, imgdict) = matched
                imgdict['path'] = path
            else:
                # otherwise, we synthesize one
                imgdict = fedfind.helpers.create_image_dict(path)
                # if we didn't update an existing image in-place, we
                # must figure out where to add the new image dict.
                # Special rule for RespinRelease:
                if self.milestone.lower() == 'respin':
                    variant = "Spins"
                # this is kinda dumb, but as it happens, if the first
                # letter in the path is upper-case, we know that first
                # path element is the variant.
                elif path[0] in string.ascii_uppercase:
                    variant = path.split('/')[0]
                else:
                    variant = "Fedora"
                arch = imgdict['arch']

            # in either case, we indicate whether this is a 'main' or
            # 'alt' image
            imgdict['alt'] = bool(loc == 'alt')

            # populate the variants dict
            if variant not in variants:
                variants[variant] = {
                    'arches': [arch],
                    'id': variant,
                    'name': variant,
                    # I can't be bothered constructing this unless
                    # we find something that needs it
                    'paths': {},
                    'type': "variant",
                    'uid': variant,
                }
            else:
                if arch not in variants[variant]['arches']:
                    variants[variant]['arches'].append(arch)

            imagesdict[variant][arch].append(imgdict)

        if origmd:
            origmd['payload']['images'] = imagesdict
            self._metadata = {'images': origmd}

        else:
            fullimgdict = {
                'header': {
                    "version": "99",
                    "type": "productmd.images",
                },
                'payload': {
                    "compose": {
                        "id": self.cid,
                        "type": 'production',
                    },
                    "images": dict(imagesdict),
                },
            }
            self._metadata = {'images': fullimgdict}

        # add the composeinfo dict
        # this will get us data from the fakecid for cases where we
        # can't find the real cid, but that's all we can really do
        (dist, release, date, typ, respin) = fedfind.helpers.parse_cid(self.cid, dist=True)
        reltype = "ga"
        # let's call the live respins "updates" so we have *some* way
        # to identify them
        if isinstance(self, RespinRelease):
            reltype = "updates"
        cidict = {
            'header': {
                "version": "99",
                "type": "productmd.composeinfo",
            },
            'payload': {
                "compose": {
                    "date": date,
                    "id": self.cid,
                    "respin": respin,
                    "type": typ,
                },
                "release": {
                    "internal": False,
                    "name": dist,
                    "short": dist,
                    "type": reltype,
                    "version": release,
                },
                "variants": variants,
            },
        }

        if origmd:
            # re-use the 'compose' dict at least
            cidict['payload']['compose'] = copy.deepcopy(origmd['payload']['compose'])

        self._metadata['composeinfo'] = cidict

        return self._metadata

    @cached_property
    def label(self):
        """Try to figure out the compose label, if we can (i.e. if the
        compose was done with Pungi 4 but had its metadata stripped).
        We do this by parsing the image file names, looking for an
        expected pattern.
        """
        if self._relnum < 24:
            # These composes cannot be said to have a label.
            return ""

        if self.milestone:
            relname = '_'.join((self.release, self.milestone))
        else:
            relname = self.release
        exp = re.compile(r'-{0}-(\d+\.\d+)\.'.format(relname))
        for (_, path) in self.all_paths:
            fname = path.split('/')[-1]
            match = exp.search(fname)
            if match:
                if self.milestone:
                    milestone = self.milestone
                else:
                    # for GA releases, milestone is 'RC'
                    milestone = 'RC'
                return '-'.join((milestone, match.group(1)))

        # if we get here, we failed to find the label
        logger.debug("Failed to discover label!")
        return ""

    @cached_property
    def cid(self):
        """If we can, try to figure out the true compose ID by first
        getting the label (see above) and then getting the CID from
        it. If we can't, just return something fake.
        """
        if self._relnum < 24:
            # No chance.
            return self._fakecid

        if self.label:
            cid = fedfind.helpers.cid_from_label(self.release, self.label)
            if cid:
                return cid

        # Either we didn't get a label, or PDC didn't give us a CID.
        return self._fakecid

class Milestone(MirrorRelease):
    """A milestone release - Alpha or Beta. These are in fact built
    with Pungi 4, but the metadata for them is not shipped, so for now
    we just handle them as non-Pungi 4 composes (this code is exactly
    as it was in fedfind 1.6.2 in fact). Ideally we should be able to
    reconstruct a lot of the metadata from PDC instead of resorting to
    old-fashioned mirror scraping and synthesis, but I don't have the
    time to write all that right now. This at least will let people
    find the ISOs.
    """
    def __init__(self, release, milestone):
        super(Milestone, self).__init__(release=release, milestone=milestone)

    @cached_property
    def previous_release(self):
        """We're only going to bother handling the current convention
        (Alpha, Beta, RC/Final), otherwise we'd need a big list of the
        rules older releases followed and it's really not worth it.
        The result may well be a lie for an old release. For Alpha we
        return the previous stable release, not the previous Beta."""
        if self.milestone == 'Beta':
            # we stopped doing Alphas with F26
            if int(self.release) < 26:
                return self.__class__(self.release, 'Alpha')
            else:
                return get_release(str(int(self.release) - 1))
        elif self.milestone == 'Alpha':
            return get_release(str(int(self.release) - 1))

    @property
    def _basepath(self):
        return 'fedora/linux/releases/test/{0}_{1}'.format(self.release, self.milestone)

    @property
    def _altbasepath(self):
        return 'alt/releases/test/{0}_{1}'.format(self.release, self.milestone)

## STABLE RELEASE CLASSES ##


class CurrentRelease(MirrorRelease):
    """A release that public mirrors are expected to carry (not an
    archived one).
    """
    def __init__(self, release):
        super(CurrentRelease, self).__init__(release=release)

    @cached_property
    def previous_release(self):
        """Always just the stable release numbered 1 lower, unless
        that's 0. Same for all stable releases, but sharing it
        between them is a bit of a pain. get_release() handles the
        0 case for us (and raises ValueError)."""
        return get_release(str(int(self.release) - 1))

    @property
    def _basepath(self):
        return 'fedora/linux/releases/{0}'.format(self.release)

    @property
    def _altbasepath(self):
        return 'alt/releases/{0}'.format(self.release)


class ArchiveRelease(MirrorRelease):
    """An archived Fedora (post-Fedora Core) release."""
    def __init__(self, release):
        super(ArchiveRelease, self).__init__(release=release)

    @cached_property
    def previous_release(self):
        """Always just the stable release numbered 1 lower, unless
        that's 0. Same for all stable releases, but sharing it
        between them is a bit of a pain. get_release() handles the
        0 case for us (and raises ValueError)."""
        return get_release(str(int(self.release) - 1))

    @property
    def _basepath(self):
        return 'archive/fedora/linux/releases/{0}'.format(self.release)

    @property
    def _altbasepath(self):
        if self._relnum > 14:
            return 'alt/releases/{0}'.format(self.release)
        else:
            # there were no 'alt' bits prior to F15
            return None


class CoreRelease(MirrorRelease):
    """A Fedora Core release."""
    def __init__(self, release):
        super(CoreRelease, self).__init__(release=release)

    @cached_property
    def previous_release(self):
        """Always just the stable release numbered 1 lower, unless
        that's 0. Same for all stable releases, but sharing it
        between them is a bit of a pain. get_release() handles the
        0 case for us (and raises ValueError)."""
        return get_release(str(int(self.release) - 1))

    @property
    def _basepath(self):
        return 'archive/fedora/linux/core/{0}'.format(self.release)

    @property
    def _altbasepath(self):
        # No Core release had an 'alt' section
        return None

## END STABLE RELEASE CLASSES ##


class RespinRelease(MirrorRelease):
    """The current semi-official post-release live respin release.
    These are done by a volunteer team and live in /live-respins/ in
    the alt tree. They look nothing like any other compose at all as
    they are done by hand and include only live images in a single
    directory. There is only ever one respin release available; older
    ones are not stored anywhere and the directory is not named for
    the date. If release or compose are passed, they are used as
    *checks*: if the current contents don't match the specified
    release and compose, we will raise a DiscoveryError, so you can be
    sure you got the 'right' respin compose. self.release will be the
    actual release number, and self.compose the actual date. We use
    the milestone 'Respin' to denote this release type.
    """
    def __init__(self, release='', compose=''):
        milestone = 'Respin'
        # we need the image paths to get release and compose, we have
        # to populate this temporarily for all_paths to work
        self._all_paths = []
        gotrelease = ''
        for img in (path.split('/')[-1] for (loc, path) in self.all_paths):
            match = fedfind.const.RESPINRE.search(img)
            if match and fedfind.helpers.date_check(match.group('date'), fail_raise=False):
                gotrelease = match.group('release')
                gotcompose = match.group('date')
                break
        if not gotrelease:
            raise fedfind.exceptions.DiscoveryError(
                "Could not determine release and compose for current respin release!")
        if release and release != gotrelease:
            raise fedfind.exceptions.DiscoveryError(
                "RespinRelease: discovered release {0} does not match "
                "requested release {1}!".format(gotrelease, release))
        if compose and compose != gotcompose:
            raise fedfind.exceptions.DiscoveryError(
                "RespinRelease: discovered compose {0} does not match "
                "requested compose {1}!".format(gotcompose, compose))
        super(RespinRelease, self).__init__(gotrelease, milestone, gotcompose)
        # if we got this far, we already know we exist
        self._exists = True
        # custom fake CID for these releases
        self._fakecid = "FedoraRespin-{0}-updates-{1}.0".format(self.release, self.compose)

    def __repr__(self):
        return "{0}()".format(self.__class__)

    @property
    def _basepath(self):
        return 'alt/live-respins'

    @property
    def _altbasepath(self):
        # our main basepath is in alt, so...
        return None

    @property
    def expected_images(self):
        """This is completely different from any normal compose so we
        don't inherit any base, we just do it from scratch.
        """
        return (
            ('workstation', 'live', 'x86_64'),
            ('kde', 'live', 'x86_64'),
            ('xfce', 'live', 'x86_64'),
            ('lxde', 'live', 'x86_64'),
            ('mate', 'live', 'x86_64'),
            ('cinnamon', 'live', 'x86_64'),
            ('soas', 'live', 'x86_64'),
        )

    @property
    def label(self):
        """These composes don't have a label."""
        return ""

    @property
    def cid(self):
        """These composes don't have a real compose ID ever, always
        return the fake.
        """
        return self._fakecid

    @property
    def https_url_generic(self):
        """These composes don't have a generic location. Arguably we
        could return the https_url_generic of the matching stable
        release, but I kinda don't like that.
        """
        return None

    @property
    def previous_release(self):
        """These composes don't have a previous release."""
        return None

    def get_package_nvras(self, packages):
        """We can't find NEVRAs for these composes as we have no info
        on what packages they contain.
        """
        return {}

# vim: set textwidth=100 ts=8 et sw=4:
