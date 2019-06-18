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

import time
import logging
import voluptuous as v

from zuul.reporter import BaseReporter
from zuul.exceptions import MergeFailure
from zuul.driver.pagure.paguresource import PagureSource


class PagureReporter(BaseReporter):
    """Sends off reports to Pagure."""

    name = 'pagure'
    log = logging.getLogger("zuul.PagureReporter")

    def __init__(self, driver, connection, pipeline, config=None):
        super(PagureReporter, self).__init__(driver, connection, config)
        self._commit_status = self.config.get('status', None)
        self._create_comment = self.config.get('comment', True)
        self._merge = self.config.get('merge', False)
        self.context = "{}/{}".format(pipeline.tenant.name, pipeline.name)

    def report(self, item):
        """Report on an event."""

        # If the source is not PagureSource we cannot report anything here.
        if not isinstance(item.change.project.source, PagureSource):
            return

        # For supporting several Pagure connections we also must filter by
        # the canonical hostname.
        if item.change.project.source.connection.canonical_hostname != \
                self.connection.canonical_hostname:
            return

        if self._commit_status is not None:
            if (hasattr(item.change, 'patchset') and
                    item.change.patchset is not None):
                self.setCommitStatus(item)
            elif (hasattr(item.change, 'newrev') and
                    item.change.newrev is not None):
                self.setCommitStatus(item)
        if hasattr(item.change, 'number'):
            if self._create_comment:
                self.addPullComment(item)
        if self._merge:
            self.mergePull(item)
            if not item.change.is_merged:
                msg = self._formatItemReportMergeFailure(item)
                self.addPullComment(item, msg)

    def _formatItemReportJobs(self, item):
        # Return the list of jobs portion of the report
        ret = ''
        jobs_fields = self._getItemReportJobsFields(item)
        for job_fields in jobs_fields:
            ret += '- [%s](%s) : %s%s%s%s\n' % job_fields
        return ret

    def addPullComment(self, item, comment=None):
        message = comment or self._formatItemReport(item)
        project = item.change.project.name
        pr_number = item.change.number
        self.log.debug(
            'Reporting change %s, params %s, message: %s' %
            (item.change, self.config, message))
        self.connection.commentPull(project, pr_number, message)

    def setCommitStatus(self, item):
        project = item.change.project.name
        if hasattr(item.change, 'patchset'):
            sha = item.change.patchset
        elif hasattr(item.change, 'newrev'):
            sha = item.change.newrev
        state = self._commit_status
        change_number = item.change.number

        url_pattern = self.config.get('status-url')
        sched_config = self.connection.sched.config
        if sched_config.has_option('web', 'status_url'):
            url_pattern = sched_config.get('web', 'status_url')
        url = item.formatUrlPattern(url_pattern) \
            if url_pattern else 'https://sftests.com'

        description = '%s status: %s (%s)' % (
            item.pipeline.name, self._commit_status, sha)

        self.log.debug(
            'Reporting change %s, params %s, '
            'context: %s, state: %s, description: %s, url: %s' %
            (item.change, self.config,
             self.context, state, description, url))

        self.connection.setCommitStatus(
            project, change_number, state, url, description, self.context)

    def mergePull(self, item):
        project = item.change.project.name
        pr_number = item.change.number

        for i in [1, 2]:
            try:
                self.connection.mergePull(project, pr_number)
                item.change.is_merged = True
                return
            except MergeFailure:
                self.log.exception(
                    'Merge attempt of change %s  %s/2 failed.' %
                    (item.change, i), exc_info=True)
                if i == 1:
                    time.sleep(2)
        self.log.warning(
            'Merge of change %s failed after 2 attempts, giving up' %
            item.change)

    def getSubmitAllowNeeds(self):
        return []


def getSchema():
    pagure_reporter = v.Schema({
        'status': v.Any('pending', 'success', 'failure'),
        'status-url': str,
        'comment': bool,
        'merge': bool,
    })
    return pagure_reporter
