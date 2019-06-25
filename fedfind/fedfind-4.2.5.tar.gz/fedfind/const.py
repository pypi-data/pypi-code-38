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

"""Various shared constants."""

from __future__ import unicode_literals
from __future__ import print_function

import collections
import re

# For all of these, we identify each we want to consider unique; that
# is the 'name'. 'values' is an iterable of values which should map to
# that name; for instance, we don't want to treat i486, i586 and i686
# as separate arches, but every time we see any of those we want to
# treat it as i386. 'weight' is an integer to be used for sort
# weighting if desired.
#
# For ArchTuple, each entry in ARCHES is a primary arch. group is used
# to group related arches together. current is whether it's currently
# a primary arch.
#
# For LoadTuple, each entry in FLAVORS or LOADOUTS is something we
# consider a unique flavor or loadout. subs is an iterable of sub-
# flavors.

ArchTuple = collections.namedtuple('ArchTuple',
                                   'name values group current')
LoadTuple = collections.namedtuple('LoadTuple', 'name values')


HTTPS = 'https://download.fedoraproject.org/pub'
HTTPS_DL = 'https://dl.fedoraproject.org/pub'
NIGHTLY_BASE = 'https://kojipkgs.fedoraproject.org/compose'
KNOWN_PREFIXES = (HTTPS, 'http://download.fedoraproject.org/pub',
                  HTTPS_DL, 'http://dl.fedoraproject.org/pub',
                  NIGHTLY_BASE, 'http://kojipkgs.fedoraproject.org/compose',
                  # secondary arch compose locations, see RHBZ #1435953
                  'http://ppc.koji.fedoraproject.org/compose',
                  'https://ppc.koji.fedoraproject.org/compose',
                  'http://s390.koji.fedoraproject.org/compose',
                  'https://s390.koji.fedoraproject.org/compose',
                  'http://arm.koji.fedoraproject.org/compose',
                  'https://arm.koji.fedoraproject.org/compose',)
PDC_API = 'https://pdc.fedoraproject.org/rest_api/v1'

# we could import these from pungi but jeez, the dependencies are
# growing as it is. Pungi compose states.
PUNGI_SUCCESS = ("FINISHED", "FINISHED_INCOMPLETE")
PUNGI_FAILURE = ("DOOMED",)
PUNGI_DONE = PUNGI_SUCCESS + PUNGI_FAILURE

# SUBVARIANTS
# used for synthesizing 'subvariant' value for pre-Pungi 4 composes
# This has to be ordered so we get the right result for e.g. 'kde'
# vs. 'jam_kde'
SUBVARIANTS = (
    LoadTuple('Desktop', ('desktop',)),
    LoadTuple('Multi', ('multi',)),
    LoadTuple('KDE', ('kde',)),
    LoadTuple('Xfce', ('xfce',)),
    LoadTuple('SoaS', ('soas',)),
    LoadTuple('Mate', ('mate_compiz', 'mate-compiz', 'mate')),
    LoadTuple('Cinnamon', ('cinnamon', 'cinn')),
    LoadTuple('LXDE', ('lxde',)),
    LoadTuple('Design_suite', ('design_suite', 'design-suite')),
    LoadTuple('Electronic_lab', ('electronic_lab', 'electronic-lab')),
    LoadTuple('Games', ('games',)),
    LoadTuple('Robotics', ('robotics',)),
    LoadTuple('Security', ('security',)),
    LoadTuple('Jam_KDE', ('jam_kde',)),
    LoadTuple('Scientific_KDE', ('scientific_kde', 'scientific-kde')),
    LoadTuple('Astronomy_KDE', ('astronomy_kde',)),
    LoadTuple('Minimal', ('minimal',)),
    LoadTuple('Source', ('source', 'srpms')),
    LoadTuple('Cloud', ('cloud',)),
    LoadTuple('Cloud_Base', ('cloud-base', 'cloud_base')),
    # the '-' here is to prevent Postrelease nightly Cloud images
    # getting 'Atomic' as their subvariant, as they always have
    # /atomic/ in their path names
    LoadTuple('Atomic', ('atomic-',)),
    # 'Atomic' was renamed 'AtomicHost' from F28 onwards
    LoadTuple('AtomicHost', ('atomichost',)),
    # 'Workstation Ostree' was renamed 'AtomicWorkstation' from F28
    # onwards, and also for post-release F26/F27 nightlies...
    LoadTuple('AtomicWorkstation', ('atomicworkstation',)),
    # ...and was then renamed to 'Silverblue' from F29 onwards...
    LoadTuple('Silverblue', ('silverblue',)),
    LoadTuple('Container_Base', ('container-base', 'container_base')),
    LoadTuple('Container_Minimal_Base', ('container-minimal-base', 'container_minimal_base')),
    LoadTuple('Docker_Base', ('docker-base', 'docker_base')),
    LoadTuple('Workstation', ('workstation', 'work')),
    # This was renamed 'AtomicWorkstation' around F28, see above
    LoadTuple('Workstation Ostree', ('workstationostree',)),
    LoadTuple('Server', ('server',)),
    LoadTuple('Everything', ('everything',)),
    LoadTuple('Python_Classroom', ('python-classroom',)),
    LoadTuple('LXQt', ('lxqt',)),
    LoadTuple('IoT', ('-iot-',)),
)

# ARCHES
ARCHES = (
    ArchTuple('x86_64', ('x86_64',), 'intel', True),
    ArchTuple('i386', ('i386', 'i486', 'i586', 'i686'), 'intel', False),
    ArchTuple('armhfp', ('armhfp',), 'arm', True),
    ArchTuple('ppc', ('ppc',), 'ppc', False),
    ArchTuple('ppc64', ('ppc64',), 'ppc', False)
)

# regex used to identify live-respins images. Used in a few different
# places, so we keep it here. Uses named groups for convenience

RESPINRE = re.compile(r'F(?P<release>\d+)-(?P<subv>[^-]+)-(?P<arch>[^-]+)-(?P<date>\d{8,8})(-Live)?\.iso',
                      re.I)

# vim: set textwidth=100 ts=8 et sw=4:
