# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import os
import json

import fastr
from fastr.helpers.classproperty import classproperty
from fastr.abc.baseplugin import PluginState
from fastr.plugins.reportingplugin import ReportingPlugin
from fastr.execution.job import JobState, Job
from fastr.exceptions import FastrOptionalModuleNotAvailableError


try:
    from elasticsearch import Elasticsearch
    elasticsearch_loaded = True
except ImportError:
    elasticsearch_loaded = False


class ElasticsearchReporter(ReportingPlugin):
    if not elasticsearch_loaded:
        _status = (PluginState.failed, 'Could not load elasticsearch module required for cluster communication')

    def __init__(self):
        super().__init__()

    @classmethod
    def test(cls):
        if not elasticsearch_loaded:
            raise FastrOptionalModuleNotAvailableError('Could not import the required elasticsearch for this plugin')

    def activate(self):
        """
        Activate the reporting plugin
        """
        super().activate()

        # Parse URI
        if fastr.config.elasticsearch_host == '':
            fastr.log.info("No valid elasticsearchsearch host given, elasticsearch Reporting will be disabled!")
            self.elasticsearch_uri = None
            return
        fastr.log.info("")
    
        self.elasticsearch_uri = fastr.config.elasticsearch_host
        self.elasticsearch_index = fastr.config.elasticsearch_index

        # Create Elastic search index 
        fastr.log.info("ES Logging to {} at index {}".format(self.elasticsearch_uri, self.elasticsearch_index))
        es = Elasticsearch([self.elasticsearch_uri])
        es.indices.create(index=self.elasticsearch_index, ignore=400)

    @classproperty
    def configuration_fields(cls):
        return {
            "elasticsearch_host": (str, "", "The elasticsearch host to report to"),
            "elasticsearch_index": (str, "fastr", "The elasticsearch index to store data in"),
            "elasticsearch_debug": (bool, False, "Setup elasticsearch debug mode to send stdout stderr on job succes"),
        }

    def elasticsearch_update_status(self, job):
        es = Elasticsearch([self.elasticsearch_uri])
        es.indices.create(index=self.elasticsearch_index, ignore=400)
        node = job.node
        job_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "network_id" : node.parent.long_id,
            "network_version" : str(node.parent.network_version),
            "network_tmpurl" : node.parent.tmpurl,
            "run_id" : node.parent.id,
            "node" : str(node),
            "node_id" : node.id,
            "node_global_id" : node.global_id,
            "tool_name" : node.tool.ns_id,
            "tool_version" : str(node.tool.command['version']),
            "sample_index" : list(job.sample_index),
            "sample_id": list(job.sample_id),
            "errors": str(job.errors),
            "status": str(job.status),
        }
        if os.path.exists(job.extrainfofile):
            with open(job.extrainfofile) as extra_info_file:
                extra_info = json.load(extra_info_file)
                process = extra_info.get('process')
                job_data['process'] = process
        
        es.index(index=self.elasticsearch_index, doc_type='fastr-job', body=job_data)

    def job_updated(self, job: Job):
        if self.elasticsearch_uri:
            self.elasticsearch_update_status(job)

    # def run_started(self, run: NetworkRun):
    #     if self.elasticsearch_uri:
    #         self.api.elasticsearch_register_run(run)

    # def run_finished(self, run: NetworkRun):
    #     if self.elasticsearch_uri:
    #         self.api.elasticsearch_finish_run(run)

    # def log_record_emitted(self, record: LogRecord):
    #     if self.elasticsearch_uri:
    #         self.api.elasticsearch_log_line(record)
