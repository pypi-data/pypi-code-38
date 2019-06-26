# Copyright 2019 Red Hat
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
import yaml
import time
import socket

from testtools.matchers import MatchesRegex

import zuul.rpcclient

from tests.base import ZuulTestCase, simple_layout
from tests.base import ZuulWebFixture


class TestPagureDriver(ZuulTestCase):
    config_file = 'zuul-pagure-driver.conf'

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_pull_request_opened(self):

        initial_comment = "This is the\nPR initial_comment."
        A = self.fake_pagure.openFakePullRequest(
            'org/project', 'master', 'A', initial_comment=initial_comment)
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)

        job = self.getJobFromHistory('project-test2')
        zuulvars = job.parameters['zuul']
        self.assertEqual(str(A.number), zuulvars['change'])
        self.assertEqual(str(A.commit_stop), zuulvars['patchset'])
        self.assertEqual('master', zuulvars['branch'])
        self.assertEquals('https://pagure/org/project/pull-request/1',
                          zuulvars['items'][0]['change_url'])
        self.assertEqual(zuulvars["message"], initial_comment)
        self.assertEqual(2, len(self.history))
        self.assertEqual(2, len(A.comments))
        self.assertEqual(
            A.comments[0]['comment'], "Starting check jobs.")
        self.assertThat(
            A.comments[1]['comment'],
            MatchesRegex(r'.*\[project-test1 \]\(.*\).*', re.DOTALL))
        self.assertThat(
            A.comments[1]['comment'],
            MatchesRegex(r'.*\[project-test2 \]\(.*\).*', re.DOTALL))
        self.assertEqual(2, len(A.flags))
        self.assertEqual('success', A.flags[0]['status'])
        self.assertEqual('pending', A.flags[1]['status'])

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_pull_request_updated(self):

        A = self.fake_pagure.openFakePullRequest('org/project', 'master', 'A')
        pr_tip1 = A.commit_stop
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))
        self.assertHistory(
            [
                {'name': 'project-test1', 'changes': '1,%s' % pr_tip1},
                {'name': 'project-test2', 'changes': '1,%s' % pr_tip1},
            ], ordered=False
        )

        self.fake_pagure.emitEvent(A.getPullRequestUpdatedEvent())
        pr_tip2 = A.commit_stop
        self.waitUntilSettled()
        self.assertEqual(4, len(self.history))
        self.assertHistory(
            [
                {'name': 'project-test1', 'changes': '1,%s' % pr_tip1},
                {'name': 'project-test2', 'changes': '1,%s' % pr_tip1},
                {'name': 'project-test1', 'changes': '1,%s' % pr_tip2},
                {'name': 'project-test2', 'changes': '1,%s' % pr_tip2}
            ], ordered=False
        )

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_pull_request_updated_builds_aborted(self):

        A = self.fake_pagure.openFakePullRequest('org/project', 'master', 'A')
        pr_tip1 = A.commit_stop

        self.executor_server.hold_jobs_in_build = True

        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.fake_pagure.emitEvent(A.getPullRequestUpdatedEvent())
        pr_tip2 = A.commit_stop
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertHistory(
            [
                {'name': 'project-test1', 'result': 'ABORTED',
                 'changes': '1,%s' % pr_tip1},
                {'name': 'project-test2', 'result': 'ABORTED',
                 'changes': '1,%s' % pr_tip1},
                {'name': 'project-test1', 'changes': '1,%s' % pr_tip2},
                {'name': 'project-test2', 'changes': '1,%s' % pr_tip2}
            ], ordered=False
        )

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_pull_request_commented(self):

        A = self.fake_pagure.openFakePullRequest('org/project', 'master', 'A')
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent('I like that change'))
        self.waitUntilSettled()
        self.assertEqual(2, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent('recheck'))
        self.waitUntilSettled()
        self.assertEqual(4, len(self.history))

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_pull_request_with_dyn_reconf(self):

        zuul_yaml = [
            {'job': {
                'name': 'project-test3',
                'run': 'job.yaml'
            }},
            {'project': {
                'check': {
                    'jobs': [
                        'project-test3'
                    ]
                }
            }}
        ]
        playbook = "- hosts: all\n  tasks: []"

        A = self.fake_pagure.openFakePullRequest(
            'org/project', 'master', 'A')
        A.addCommit(
            {'.zuul.yaml': yaml.dump(zuul_yaml),
             'job.yaml': playbook}
        )
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test3').result)

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_ref_updated(self):

        event = self.fake_pagure.getGitReceiveEvent('org/project')
        expected_newrev = event[1]['msg']['stop_commit']
        self.fake_pagure.emitEvent(event)
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))
        self.assertEqual(
            'SUCCESS',
            self.getJobFromHistory('project-post-job').result)

        job = self.getJobFromHistory('project-post-job')
        zuulvars = job.parameters['zuul']
        self.assertEqual('refs/heads/master', zuulvars['ref'])
        self.assertEqual('post', zuulvars['pipeline'])
        self.assertEqual('project-post-job', zuulvars['job'])
        self.assertEqual('master', zuulvars['branch'])
        self.assertEqual(
            'https://pagure/org/project/commit/%s' % zuulvars['newrev'],
            zuulvars['change_url'])
        self.assertEqual(expected_newrev, zuulvars['newrev'])

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_ref_updated_and_tenant_reconfigure(self):

        self.waitUntilSettled()
        old = self.sched.tenant_last_reconfigured.get('tenant-one', 0)
        time.sleep(1)

        zuul_yaml = [
            {'job': {
                'name': 'project-post-job2',
                'run': 'job.yaml'
            }},
            {'project': {
                'post': {
                    'jobs': [
                        'project-post-job2'
                    ]
                }
            }}
        ]
        playbook = "- hosts: all\n  tasks: []"
        self.create_commit(
            'org/project',
            {'.zuul.yaml': yaml.dump(zuul_yaml),
             'job.yaml': playbook},
            message='Add InRepo configuration'
        )
        event = self.fake_pagure.getGitReceiveEvent('org/project')
        self.fake_pagure.emitEvent(event)
        self.waitUntilSettled()

        new = self.sched.tenant_last_reconfigured.get('tenant-one', 0)
        # New timestamp should be greater than the old timestamp
        self.assertLess(old, new)

        self.assertHistory(
            [{'name': 'project-post-job'},
             {'name': 'project-post-job2'},
            ], ordered=False
        )

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_client_dequeue_change_pagure(self):

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_pagure.openFakePullRequest('org/project', 'master', 'A')

        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        client.dequeue(
            tenant='tenant-one',
            pipeline='check',
            project='org/project',
            change='%s,%s' % (A.number, A.commit_stop),
            ref=None)

        self.waitUntilSettled()

        tenant = self.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']
        self.assertEqual(check_pipeline.getAllItems(), [])
        self.assertEqual(self.countJobResults(self.history, 'ABORTED'), 2)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_client_enqueue_change_pagure(self):

        A = self.fake_pagure.openFakePullRequest('org/project', 'master', 'A')

        client = zuul.rpcclient.RPCClient('127.0.0.1',
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        r = client.enqueue(tenant='tenant-one',
                           pipeline='check',
                           project='org/project',
                           trigger='pagure',
                           change='%s,%s' % (A.number, A.commit_stop))
        self.waitUntilSettled()

        self.assertEqual(self.getJobFromHistory('project-test1').result,
                         'SUCCESS')
        self.assertEqual(self.getJobFromHistory('project-test2').result,
                         'SUCCESS')
        self.assertEqual(r, True)

    @simple_layout('layouts/requirements-pagure.yaml', driver='pagure')
    def test_pr_score_require_1_vote(self):

        A = self.fake_pagure.openFakePullRequest(
            'org/project1', 'master', 'A')
        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent("I like that change"))
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

        self.assertEqual(
            'SUCCESS',
            self.getJobFromHistory('project-test').result)

    @simple_layout('layouts/requirements-pagure.yaml', driver='pagure')
    def test_pr_score_require_2_votes(self):

        A = self.fake_pagure.openFakePullRequest(
            'org/project2', 'master', 'A')
        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent("I like that change"))
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsdown:"))
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

    @simple_layout('layouts/requirements-pagure.yaml', driver='pagure')
    def test_status_trigger(self):

        A = self.fake_pagure.openFakePullRequest(
            'org/project3', 'master', 'A')

        self.fake_pagure.emitEvent(
            A.getPullRequestStatusSetEvent("failure"))
        self.waitUntilSettled()
        self.assertEqual(0, len(self.history))

        self.fake_pagure.emitEvent(
            A.getPullRequestStatusSetEvent("success"))
        self.waitUntilSettled()
        self.assertEqual(1, len(self.history))

    @simple_layout('layouts/merging-pagure.yaml', driver='pagure')
    def test_merge_action_in_independent(self):

        A = self.fake_pagure.openFakePullRequest(
            'org/project1', 'master', 'A')
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()

        self.assertEqual(1, len(self.history))
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test').result)
        self.assertEqual('Merged', A.status)

    @simple_layout('layouts/merging-pagure.yaml', driver='pagure')
    def test_merge_action_in_dependent(self):

        A = self.fake_pagure.openFakePullRequest(
            'org/project2', 'master', 'A')
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        # connection.canMerge is not validated
        self.assertEqual(0, len(self.history))

        # Set the mergeable PR flag to a expected value
        A.cached_merge_status = 'MERGE'
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        # connection.canMerge is not validated
        self.assertEqual(0, len(self.history))

        # Set the score threshold as reached
        A.threshold_reached = True
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        # connection.canMerge is not validated
        self.assertEqual(0, len(self.history))

        # Set CI flag as passed CI
        A.addFlag('success', 'https://url', 'Build passed')
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent())
        self.waitUntilSettled()
        # connection.canMerge is validated
        self.assertEqual(1, len(self.history))

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test').result)
        self.assertEqual('Merged', A.status)

    @simple_layout('layouts/crd-pagure.yaml', driver='pagure')
    def test_crd_independent(self):

        # Create a change in project1 that a project2 change will depend on
        A = self.fake_pagure.openFakePullRequest('org/project1', 'master', 'A')

        # Create a commit in B that sets the dependency on A
        msg = "Depends-On: %s" % A.url
        B = self.fake_pagure.openFakePullRequest(
            'org/project2', 'master', 'B', initial_comment=msg)

        # Make an event to re-use
        event = B.getPullRequestCommentedEvent('A comment')
        self.fake_pagure.emitEvent(event)
        self.waitUntilSettled()

        # The changes for the job from project2 should include the project1
        # PR content
        changes = self.getJobFromHistory(
            'project2-test', 'org/project2').changes

        self.assertEqual(changes, "%s,%s %s,%s" % (A.number,
                                                   A.commit_stop,
                                                   B.number,
                                                   B.commit_stop))

        # There should be no more changes in the queue
        tenant = self.sched.abide.tenants.get('tenant-one')
        self.assertEqual(len(tenant.layout.pipelines['check'].queues), 0)

    @simple_layout('layouts/crd-pagure.yaml', driver='pagure')
    def test_crd_dependent(self):

        # Create a change in project3 that a project4 change will depend on
        A = self.fake_pagure.openFakePullRequest('org/project3', 'master', 'A')

        # Create a commit in B that sets the dependency on A
        msg = "Depends-On: %s" % A.url
        B = self.fake_pagure.openFakePullRequest(
            'org/project4', 'master', 'B', initial_comment=msg)

        # Make an event to re-use
        event = B.getPullRequestCommentedEvent('A comment')

        self.fake_pagure.emitEvent(event)
        self.waitUntilSettled()

        # Neither A and B can't merge (no flag, no score threshold)
        self.assertEqual(0, len(self.history))

        B.threshold_reached = True
        B.addFlag('success', 'https://url', 'Build passed')
        self.fake_pagure.emitEvent(event)
        self.waitUntilSettled()

        # B can't merge as A got no flag, no score threshold
        self.assertEqual(0, len(self.history))

        A.threshold_reached = True
        A.addFlag('success', 'https://url', 'Build passed')
        self.fake_pagure.emitEvent(event)
        self.waitUntilSettled()

        # The changes for the job from project4 should include the project3
        # PR content
        changes = self.getJobFromHistory(
            'project4-test', 'org/project4').changes

        self.assertEqual(changes, "%s,%s %s,%s" % (A.number,
                                                   A.commit_stop,
                                                   B.number,
                                                   B.commit_stop))

        self.assertTrue(A.is_merged)
        self.assertTrue(B.is_merged)

    @simple_layout('layouts/crd-pagure.yaml', driver='pagure')
    def test_crd_needed_changes(self):

        # Given change A and B, where B depends on A, when A
        # completes B should be enqueued (using a shared queue)

        # Create a change in project3 that a project4 change will depend on
        A = self.fake_pagure.openFakePullRequest('org/project3', 'master', 'A')
        A.threshold_reached = True
        A.addFlag('success', 'https://url', 'Build passed')

        # Set B to depend on A
        msg = "Depends-On: %s" % A.url
        B = self.fake_pagure.openFakePullRequest(
            'org/project4', 'master', 'B', initial_comment=msg)
        # Make the driver aware of change B by sending an event
        # At that moment B can't merge
        self.fake_pagure.emitEvent(B.getPullRequestCommentedEvent('A comment'))
        # Now set B mergeable
        B.threshold_reached = True
        B.addFlag('success', 'https://url', 'Build passed')

        # Enqueue A, which will make the scheduler detect that B is
        # depending on so B will be enqueue as well.
        self.fake_pagure.emitEvent(A.getPullRequestCommentedEvent('A comment'))
        self.waitUntilSettled()

        # The changes for the job from project4 should include the project3
        # PR content
        changes = self.getJobFromHistory(
            'project4-test', 'org/project4').changes

        self.assertEqual(changes, "%s,%s %s,%s" % (A.number,
                                                   A.commit_stop,
                                                   B.number,
                                                   B.commit_stop))

        self.assertTrue(A.is_merged)
        self.assertTrue(B.is_merged)


class TestPagureToGerritCRD(ZuulTestCase):
    config_file = 'zuul-crd-pagure.conf'
    tenant_config_file = 'config/cross-source-pagure/gerrit.yaml'

    def test_crd_gate(self):
        "Test cross-repo dependencies"
        A = self.fake_pagure.openFakePullRequest('pagure/project2', 'master',
                                                 'A')
        B = self.fake_gerrit.addFakeChange('gerrit/project1', 'master', 'B')

        # A Depends-On: B
        A.editInitialComment('Depends-On: %s\n' % (B.data['url']))

        A.addFlag('success', 'https://url', 'Build passed')
        A.threshold_reached = True

        B.addApproval('Code-Review', 2)

        # Make A enter the pipeline
        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()

        # Expect not merged as B not approved yet
        self.assertFalse(A.is_merged)
        self.assertEqual(B.data['status'], 'NEW')

        for connection in self.connections.connections.values():
            connection.maintainCache([])

        B.addApproval('Approved', 1)
        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()

        self.assertTrue(A.is_merged)
        self.assertEqual(B.data['status'], 'MERGED')
        self.assertEqual(len(A.comments), 4)
        self.assertEqual(B.reported, 2)

        changes = self.getJobFromHistory(
            'project-merge', 'pagure/project2').changes
        self.assertEqual(changes, '1,1 1,%s' % A.commit_stop)

    def test_crd_check(self):
        "Test cross-repo dependencies in independent pipelines"
        A = self.fake_pagure.openFakePullRequest('pagure/project2', 'master',
                                                 'A')
        B = self.fake_gerrit.addFakeChange(
            'gerrit/project1', 'master', 'B')

        # A Depends-On: B
        A.editInitialComment('Depends-On: %s\n' % (B.data['url'],))

        self.executor_server.hold_jobs_in_build = True

        self.fake_pagure.emitEvent(A.getPullRequestUpdatedEvent())
        self.waitUntilSettled()

        self.assertTrue(self.builds[0].hasChanges(A, B))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertFalse(A.is_merged)
        self.assertEqual(B.data['status'], 'NEW')
        self.assertEqual(len(A.comments), 2)
        self.assertEqual(B.reported, 0)

        changes = self.getJobFromHistory(
            'project-merge', 'pagure/project2').changes
        self.assertEqual(changes, '1,1 1,%s' % A.commit_stop)


class TestGerritToPagureCRD(ZuulTestCase):
    config_file = 'zuul-crd-pagure.conf'
    tenant_config_file = 'config/cross-source-pagure/gerrit.yaml'

    def test_crd_gate(self):
        "Test cross-repo dependencies"
        A = self.fake_gerrit.addFakeChange('gerrit/project1', 'master', 'A')
        B = self.fake_pagure.openFakePullRequest('pagure/project2', 'master',
                                                 'B')

        A.addApproval('Code-Review', 2)

        AM2 = self.fake_gerrit.addFakeChange('gerrit/project1', 'master',
                                             'AM2')
        AM1 = self.fake_gerrit.addFakeChange('gerrit/project1', 'master',
                                             'AM1')
        AM2.setMerged()
        AM1.setMerged()

        # A -> AM1 -> AM2
        # A Depends-On: B
        # M2 is here to make sure it is never queried.  If it is, it
        # means zuul is walking down the entire history of merged
        # changes.

        A.setDependsOn(AM1, 1)
        AM1.setDependsOn(AM2, 1)

        A.data['commitMessage'] = '%s\n\nDepends-On: %s\n' % (
            A.subject, B.url)

        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertFalse(B.is_merged)

        for connection in self.connections.connections.values():
            connection.maintainCache([])

        B.addFlag('success', 'https://url', 'Build passed')
        B.threshold_reached = True
        self.fake_pagure.emitEvent(
            B.getPullRequestCommentedEvent(":thumbsup:"))
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))

        self.waitUntilSettled()

        self.assertEqual(AM2.queried, 0)
        self.assertEqual(A.data['status'], 'MERGED')
        self.assertTrue(B.is_merged)
        self.assertEqual(A.reported, 2)
        self.assertEqual(len(B.comments), 3)

        changes = self.getJobFromHistory(
            'project-merge', 'gerrit/project1').changes
        self.assertEqual(changes, '1,%s 1,1' % B.commit_stop)

    def test_crd_check(self):
        "Test cross-repo dependencies in independent pipelines"
        A = self.fake_gerrit.addFakeChange('gerrit/project1', 'master', 'A')
        B = self.fake_pagure.openFakePullRequest(
            'pagure/project2', 'master', 'B')

        # A Depends-On: B
        A.data['commitMessage'] = '%s\n\nDepends-On: %s\n' % (
            A.subject, B.url)

        self.executor_server.hold_jobs_in_build = True

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertTrue(self.builds[0].hasChanges(A, B))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.data['status'], 'NEW')
        self.assertFalse(B.is_merged)
        self.assertEqual(A.reported, 1)
        self.assertEqual(len(B.comments), 0)

        changes = self.getJobFromHistory(
            'project-merge', 'gerrit/project1').changes
        self.assertEqual(changes, '1,%s 1,1' % B.commit_stop)


class TestPagureToGithubCRD(ZuulTestCase):
    config_file = 'zuul-crd-pagure.conf'
    tenant_config_file = 'config/cross-source-pagure/github.yaml'

    def test_crd_gate(self):
        "Test cross-repo dependencies"
        A = self.fake_pagure.openFakePullRequest('pagure/project2', 'master',
                                                 'A')
        B = self.fake_github.openFakePullRequest('github/project1', 'master',
                                                 'B')
        # A Depends-On: B
        A.editInitialComment('Depends-On: %s\n' % (B.url))

        A.addFlag('success', 'https://url', 'Build passed')
        A.threshold_reached = True

        # Make A enter the pipeline
        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()

        # Expect not merged as B not approved yet
        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)

        for connection in self.connections.connections.values():
            connection.maintainCache([])

        B.addLabel('approved')
        self.fake_pagure.emitEvent(
            A.getPullRequestCommentedEvent(":thumbsup:"))
        self.waitUntilSettled()

        self.assertTrue(A.is_merged)
        self.assertTrue(B.is_merged)
        self.assertEqual(len(A.comments), 4)
        self.assertEqual(len(B.comments), 2)

        changes = self.getJobFromHistory(
            'project-merge', 'pagure/project2').changes
        self.assertEqual(changes, '1,%s 1,%s' % (B.head_sha, A.commit_stop))

    def test_crd_check(self):
        "Test cross-repo dependencies in independent pipelines"
        A = self.fake_pagure.openFakePullRequest('pagure/project2', 'master',
                                                 'A')
        B = self.fake_github.openFakePullRequest('github/project1', 'master',
                                                 'A')

        # A Depends-On: B
        A.editInitialComment('Depends-On: %s\n' % B.url)

        self.executor_server.hold_jobs_in_build = True

        self.fake_pagure.emitEvent(A.getPullRequestUpdatedEvent())
        self.waitUntilSettled()

        self.assertTrue(self.builds[0].hasChanges(A, B))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)
        self.assertEqual(len(A.comments), 2)
        self.assertEqual(len(A.comments), 2)

        changes = self.getJobFromHistory(
            'project-merge', 'pagure/project2').changes
        self.assertEqual(changes, '1,%s 1,%s' % (B.head_sha, A.commit_stop))


class TestGithubToPagureCRD(ZuulTestCase):
    config_file = 'zuul-crd-pagure.conf'
    tenant_config_file = 'config/cross-source-pagure/github.yaml'

    def test_crd_gate(self):
        "Test cross-repo dependencies"
        A = self.fake_github.openFakePullRequest('github/project1', 'master',
                                                 'A')
        B = self.fake_pagure.openFakePullRequest('pagure/project2', 'master',
                                                 'B')

        # A Depends-On: B
        A.editBody('Depends-On: %s\n' % B.url)

        event = A.addLabel('approved')
        self.fake_github.emitEvent(event)
        self.waitUntilSettled()

        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)

        for connection in self.connections.connections.values():
            connection.maintainCache([])

        B.addFlag('success', 'https://url', 'Build passed')
        B.threshold_reached = True
        self.fake_pagure.emitEvent(
            B.getPullRequestCommentedEvent(":thumbsup:"))

        self.fake_github.emitEvent(event)

        self.waitUntilSettled()

        self.assertTrue(A.is_merged)
        self.assertTrue(B.is_merged)
        self.assertEqual(len(A.comments), 2)
        self.assertEqual(len(B.comments), 3)

        changes = self.getJobFromHistory(
            'project-merge', 'github/project1').changes
        self.assertEqual(changes, '1,%s 1,%s' % (B.commit_stop, A.head_sha))

    def test_crd_check(self):
        "Test cross-repo dependencies in independent pipelines"
        A = self.fake_github.openFakePullRequest(
            'github/project1', 'master', 'A')
        B = self.fake_pagure.openFakePullRequest(
            'pagure/project2', 'master', 'B')

        # A Depends-On: B
        A.editBody('Depends-On: %s\n' % B.url)

        self.executor_server.hold_jobs_in_build = True

        self.fake_github.emitEvent(A.getPullRequestEditedEvent())
        self.waitUntilSettled()

        self.assertTrue(self.builds[0].hasChanges(A, B))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)
        self.assertEqual(len(A.comments), 1)
        self.assertEqual(len(B.comments), 0)

        changes = self.getJobFromHistory(
            'project-merge', 'github/project1').changes
        self.assertEqual(changes, '1,%s 1,%s' % (B.commit_stop, A.head_sha))


class TestPagureWebhook(ZuulTestCase):
    config_file = 'zuul-pagure-driver.conf'

    def setUp(self):
        super(TestPagureWebhook, self).setUp()

        # Start the web server
        self.web = self.useFixture(
            ZuulWebFixture(self.gearman_server.port,
                           self.config, self.test_root))

        host = '127.0.0.1'
        # Wait until web server is started
        while True:
            port = self.web.port
            try:
                with socket.create_connection((host, port)):
                    break
            except ConnectionRefusedError:
                pass

        self.fake_pagure.setZuulWebPort(port)

    def tearDown(self):
        super(TestPagureWebhook, self).tearDown()

    @simple_layout('layouts/basic-pagure.yaml', driver='pagure')
    def test_webhook(self):

        A = self.fake_pagure.openFakePullRequest(
            'org/project', 'master', 'A')
        self.fake_pagure.emitEvent(A.getPullRequestOpenedEvent(),
                                   use_zuulweb=True,
                                   project='org/project')
        self.waitUntilSettled()

        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test1').result)
        self.assertEqual('SUCCESS',
                         self.getJobFromHistory('project-test2').result)
