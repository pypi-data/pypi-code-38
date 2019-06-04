"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
import unittest

from mocket.mockhttp import Entry
from mocket import mocketize

from cortex_client.jobsclient import JobsClient


class TestJobsClient(unittest.TestCase):

    def setUp(self):
        self.jc = JobsClient('http://localhost:8000', 3, 'token')

    def register_entry(self, verb, uri, body):
        url = self.jc._serviceconnector._construct_url(uri)
        Entry.single_register(verb,
                              url,
                              status = 200,
                              body = json.dumps(body))
    ## Jobs ##

    @mocketize
    def test_get_jobs(self):
        # setup
        uri = self.jc.URIs['jobs']
        returns = {"status": "SUCCESS", "jobs": []}
        self.register_entry(Entry.GET, uri, returns)

        r = self.jc.get_jobs()
        self.assertEqual(r, returns)

    @mocketize
    def test_post_job(self):
        uri = self.jc.URIs['jobs']
        returns = {"status": "OK"}
        self.register_entry(Entry.POST, uri, returns)

        r = self.jc.post_job("job-name")
        self.assertEqual(r, returns)

    @mocketize
    def test_get_job(self):
        # setup
        uri = self.jc._serviceconnector.urljoin([self.jc.URIs['jobs'], 'no-job'])
        returns = {"job": {}}
        self.register_entry(Entry.GET, uri, returns)

        r = self.jc.get_job('no-job')
        self.assertEqual(r, returns)

    ## Tasks ##

    @mocketize
    def test_get_tasks(self):
        uri = self.jc.URIs['tasks'].format('no-job')
        returns = {'status': 'OK', 
                  'message': 'Found tasks for Job: no-job', 
                  'tasks': []}
        self.register_entry(Entry.GET, uri, returns)

        r = self.jc.get_tasks('no-job')
        self.assertEqual(r, returns)
        
    @mocketize
    def test_post_task(self):
        uri = self.jc.URIs['tasks'].format('no-job')
        returns = {'status': 'OK'} 
        self.register_entry(Entry.POST, uri, returns)

        r = self.jc.post_task('no-job', {"some": "task"})
        self.assertEqual(r, returns)

    @mocketize
    def test_get_task(self):
        uri = self.jc._serviceconnector.urljoin([self.jc.URIs['tasks'].format('no-job'), 'task-id'])
        returns = {'status': 'OK'} 
        self.register_entry(Entry.GET, uri, returns)

        r = self.jc.get_task('no-job', 'task-id')
        self.assertEqual(r, returns)

    @mocketize
    def test_cancel_task(self):
        uri = self.jc._serviceconnector.urljoin([self.jc.URIs['tasks'].format('no-job'), 
                                                 'task-id', 
                                                 'cancel'])
        returns = {'status': 'OK'} 
        self.register_entry(Entry.POST, uri, returns)

        r = self.jc.cancel_task('no-job', 'task-id')
        self.assertEqual(r, returns)

    @mocketize
    def test_get_task_logs(self):
        uri = self.jc._serviceconnector.urljoin([self.jc.URIs['tasks'].format('no-job'), 
                                                 'task-id', 
                                                 'logs'])
        returns = {'status': 'OK'} 
        self.register_entry(Entry.POST, uri, returns)

        r = self.jc.get_task_logs('no-job', 'task-id')
        self.assertEqual(r, returns)

    @mocketize
    def test_get_registries(self):
        uri = self.jc.URIs['registries']
        returns = {'registries': []} 
        self.register_entry(Entry.GET, uri, returns)

        r = self.jc.get_registries()
        self.assertEqual(r, returns)

