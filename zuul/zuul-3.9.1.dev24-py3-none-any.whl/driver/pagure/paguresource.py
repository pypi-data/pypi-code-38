# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re
import urllib
import logging

from zuul.source import BaseSource
from zuul.model import Project

from zuul.driver.pagure.paguremodel import PagureRefFilter


class PagureSource(BaseSource):
    name = 'pagure'
    log = logging.getLogger("zuul.source.PagureSource")

    def __init__(self, driver, connection, config=None):
        hostname = connection.canonical_hostname
        super(PagureSource, self).__init__(driver, connection,
                                           hostname, config)
        self.change_re = re.compile(r"/(.*?)/pull-request/(\d+)")

    def getRefSha(self, project, ref):
        """Return a sha for a given project ref."""
        raise NotImplementedError()

    def waitForRefSha(self, project, ref, old_sha=''):
        """Block until a ref shows up in a given project."""
        raise NotImplementedError()

    def isMerged(self, change, head=None):
        """Determine if change is merged."""
        if not change.number:
            # Not a pull request, considering merged.
            return True
        return change.is_merged

    def canMerge(self, change, allow_needs):
        """Determine if change can merge."""
        if not change.number:
            # Not a pull request, considering merged.
            return True
        return self.connection.canMerge(change, allow_needs)

    def postConfig(self):
        """Called after configuration has been processed."""
        raise NotImplementedError()

    def getChange(self, event, refresh=False):
        return self.connection.getChange(event, refresh)

    def getChangeByURL(self, url):
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            return None
        m = self.change_re.match(parsed.path)
        if not m:
            return None
        project_name = m.group(1)
        try:
            num = int(m.group(2))
        except ValueError:
            return None
        pull = self.connection.getPull(project_name, num)
        if not pull:
            return None
        project = self.getProject(project_name)
        change = self.connection._getChange(
            project, num,
            patchset=pull.get('commit_stop'),
            url=url)
        return change

    def getChangesDependingOn(self, change, projects, tenant):
        return self.connection.getChangesDependingOn(
            change, projects, tenant)

    def getCachedChanges(self):
        return self.connection._change_cache.values()

    def getProject(self, name):
        p = self.connection.getProject(name)
        if not p:
            p = Project(name, self)
            self.connection.addProject(p)
        return p

    def getProjectBranches(self, project, tenant):
        return self.connection.getProjectBranches(project, tenant)

    def getProjectOpenChanges(self, project):
        """Get the open changes for a project."""
        raise NotImplementedError()

    def updateChange(self, change, history=None):
        """Update information for a change."""
        raise NotImplementedError()

    def getGitUrl(self, project):
        """Get the git url for a project."""
        return self.connection.getGitUrl(project)

    def getGitwebUrl(self, project, sha=None):
        """Get the git-web url for a project."""
        raise NotImplementedError()

    # This driver does not implement pipeline requirements.
    def getRequireFilters(self, config):
        f = PagureRefFilter(
            connection_name=self.connection.connection_name,
            score=config.get('score'),
            open=config.get('open'),
            merged=config.get('merged'),
            status=config.get('status'),
        )
        return [f]

    def getRejectFilters(self, config):
        raise NotImplementedError()

    def getRefForChange(self, change):
        raise NotImplementedError()


# Require model
def getRequireSchema():
    require = {
        'score': int,
        'open': bool,
        'merged': bool,
        'status': str,
    }
    return require


def getRejectSchema():
    reject = {}
    return reject
