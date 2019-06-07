# Copyright 2019 Pierre-Yves David <pierre-yves.david@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

def hastopicext(repo):
    """True if the repo use the topic extension"""
    return getattr(repo, 'hastopicext', False)
