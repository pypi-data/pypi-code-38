# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
File Monitor Utilities
"""

from __future__ import unicode_literals

import os
import logging


log = logging.getLogger(__name__)


def queue_existing(profile, path):
    """
    Adds files found in a watched folder to a processing queue.  This is called
    when the monitor first starts, to handle the case of files which exist
    prior to startup.

    If files are found, they are first sorted by modification timestamp, using
    a lexical sort on the filename as a tie-breaker, and then added to the
    queue in that order.

    :param profile: Monitor configuration profile for which the folder is to be
       watched.  The profile is expected to already have a queue attached; any
       existing files will be added to this queue.

    :param path: Folder path which is to be checked for files.
    """
    paths = [os.path.join(path, p) for p in os.listdir(path)]
    paths = sorted(paths, key=lambda p: (os.path.getmtime(p), p))
    for path in paths:

        # Only process normal files.
        if not os.path.isfile(path):
            continue

        # If using locks, don't process "in transit" files.
        if profile.watch_locks and path.endswith(u'.lock'):
            continue

        log.debug(u"queuing existing file: {0}".format(path))
        profile.queue.put(path)
