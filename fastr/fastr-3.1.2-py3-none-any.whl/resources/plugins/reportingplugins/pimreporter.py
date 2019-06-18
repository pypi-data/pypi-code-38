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


from abc import ABCMeta, abstractmethod
from collections import deque
import datetime
import getpass
import itertools
import json
from logging import LogRecord
import os
import time
from typing import Dict
from threading import Lock, Thread

import requests
import fastr

from fastr.helpers.classproperty import classproperty
from fastr.plugins.reportingplugin import ReportingPlugin
from fastr.execution.job import JobState, Job
from fastr.execution.networkrun import NetworkRun


class BasePimAPI(metaclass=ABCMeta):
    """
    Base class for PIM API classes which specifies the methods required to function
    """
    @abstractmethod
    def pim_update_status(self, job: Job):
        """
        Update the status of a job

        :param job: The job which to update
        """

    @abstractmethod
    def pim_register_run(self, network: NetworkRun):
        """
        Send the basic Network layout to PIM and register the run.

        :param network: The network run to register to PIM
        """

    @abstractmethod
    def pim_finish_run(self, network: NetworkRun):
        """
        Set the PIM run to finished and clean up

        :param network: The network run to finish
        """

    @abstractmethod
    def pim_log_line(self, record: LogRecord):
        """
        Send a new line of log record to PIM
        :param record: the log record to send
        """


class PimAPIv2(object):
    """
    Class to publish to PIM
    """
    PIM_STATUS_MAPPING = {
        JobState.nonexistent: 5,
        JobState.created: 0,
        JobState.queued: 0,
        JobState.hold: 0,
        JobState.running: 1,
        JobState.execution_done: 1,
        JobState.execution_failed: 1,
        JobState.processing_callback: 1,
        JobState.finished: 2,
        JobState.failed: 3,
        JobState.cancelled: 4,
    }

    NODE_CLASSES = {
        'NodeRun': 'node',
        'SourceNodeRun': 'source',
        'ConstantNodeRun': 'constant',
        'SinkNodeRun': 'sink'
    }

    STATUS_TYPES = [
        {
            "color": "#aaccff",
            "description": "Jobs that are waiting for input",
            "title": "idle"
        },
        {
            "color": "#daa520",
            "description": "Jobs that are running",
            "title": "running"
        },
        {
            "color": "#23b22f",
            "description": "Jobs that finished successfully",
            "title": "success"
        },
        {
            "color": "#dd3311",
            "description": "Jobs that have failed",
            "title": "failed"
        },
        {
            "color": "#334477",
            "description": "Jobs which were cancelled",
            "title": "cancelled"
        },
        {
            "color": "#ccaa99",
            "description": "Jobs with an undefined state",
            "title": "undefined"
        }
    ]

    def __init__(self, uri=None):
        self.pim_uri = uri
        self.registered = False
        self.run_id = None
        self.jobs_uri = None

        # Data for sending will be cached and flushed
        self.running = True
        self.submit_thread = Thread(target=self.job_update_loop, name='PimSubmitter', daemon=True)
        self.update_interval = fastr.config.pim_update_interval
        self.batch_size = fastr.config.pim_batch_size
        self.finished_timeout = fastr.config.pim_finished_timeout

        self.queued_job_updates = deque()
        self.submitted_job_updates = []
        self.updates_lock = Lock()

        # Some data
        self.counter = itertools.count()
        self.scopes = {None: 'root'}
        self.nodes = {}
        self.job_states = {}

    def create_job_data(self, job: Job) -> Dict:
        """
        Create a job data json part that is ready to send to PIM

        :param job: the job to convert
        :return:
        """
        try:
            node = self.nodes[job.node_global_id]
        except KeyError:
            fastr.log.info('NODES: {}'.format(self.nodes))
            raise

        # Create PIM job data
        pim_job_data = {
            "path": '{}/{}'.format(node, job.id),
            "title": "",
            "customData": {
                "sample_id": list(job.sample_id),
                "sample_index": list(job.sample_index),
                "errors": job.errors,
            },
            "status": self.PIM_STATUS_MAPPING[job.status],
            "description": "",
        }

        # Send the data to PIM
        fastr.log.debug('Updating PIM job status {} => {} ({})'.format(job.id,
                                                                       job.status,
                                                                       self.PIM_STATUS_MAPPING[job.status]))

        if (job.status == JobState.failed or fastr.config.pim_debug) and os.path.exists(job.extrainfofile):

            with open(job.extrainfofile) as extra_info_file:
                extra_info = json.load(extra_info_file)

                process = extra_info.get('process')

                if process:
                    # Process information
                    pim_job_data['customData']['__stdout__'] = process.get('stdout')
                    pim_job_data['customData']['__stderr__'] = process.get('stderr')
                    pim_job_data['customData']['command'] = process.get('command')
                    pim_job_data['customData']['returncode'] = process.get('returncode')
                    pim_job_data['customData']['time_elapsed'] = process.get('time_elapsed')

                # Host information
                pim_job_data['customData']['hostinfo'] = extra_info.get('hostinfo')

                # Input output hashes for validation of files
                pim_job_data['customData']['input_hash'] = extra_info.get('input_hash')
                pim_job_data['customData']['output_hash'] = extra_info.get('output_hash')

                # Tool information
                pim_job_data['customData']['tool_name'] = extra_info.get('tool_name')
                pim_job_data['customData']['tool_version'] = extra_info.get('tool_version')

        return pim_job_data

    def pim_update_status(self, job):
        if self.pim_uri is None:
            return

        if not self.registered:
            fastr.log.debug('Did not register a RUN with PIM yet! Cannot'
                            ' send status updates!')
            return

        if job.status not in [
            JobState.created,
            JobState.running,
            JobState.finished,
            JobState.cancelled,
            JobState.failed,
        ]:
            return

        if job.id in self.job_states and self.job_states[job.id] == self.PIM_STATUS_MAPPING[job.status]:
            # Not a valid update
            fastr.log.debug('Ignoring non-PIM update')
            return
        else:
            self.job_states[job.id] = self.PIM_STATUS_MAPPING[job.status]

        with self.updates_lock:
            self.queued_job_updates.append(self.create_job_data(job))

    def job_update_loop(self):
        """
        Loop that periodically updates job data
        """
        while self.running or len(self.submitted_job_updates) != 0 or len(self.queued_job_updates) != 0:
            # Not time of start of this loop iteration
            last_update = time.time()

            # Select job data to submit
            with self.updates_lock:
                # Find number of jobs we can add
                number_of_jobs = min(self.batch_size - len(self.submitted_job_updates),
                                     len(self.queued_job_updates))

                # Append extra jobs to fill the batch size
                for _ in range(number_of_jobs):
                    self.submitted_job_updates.append(
                        self.queued_job_updates.popleft()
                    )

            # If there are jobs update to submit, do so
            if len(self.submitted_job_updates) > 0:
                try:
                    response = requests.put(self.jobs_uri, json=self.submitted_job_updates, timeout=5)
                except requests.ConnectionError as exception:
                    fastr.log.warning('Could no publish status to PIM, encountered exception: {}'.format(exception))
                except requests.Timeout:
                    fastr.log.warning('Connection to PIM timed out during job update submission')
                else:
                    if response.status_code >= 300:
                        fastr.log.warning('Response of jobs update: [{r.status_code}] {r.text}'.format(r=response))
                    else:
                        # Success
                        self.submitted_job_updates = []

            # Sleep to get a roughly update_interval second loop time
            time_to_sleep = last_update + self.update_interval - time.time()
            time_to_sleep = time_to_sleep if time_to_sleep > 0 else 0
            time.sleep(time_to_sleep)

    def pim_serialize_node(self, node, scope, links):
        # Fish out macros and use specialized function
        if type(node).__name__ == 'MacroNodeRun':
            return self.pim_serialize_macro(node, scope, links)

        node_data = {
            "name": node.id,
            "title": node.id,
            "children": [],
            "customData": {},
            "inPorts": [
                {
                    "name": output.id,
                    "title": output.id,
                    "customData": {
                        "input_group": output.input_group,
                        "datatype": output.datatype.id,
                        "dimension_names": [x.name for x in output.dimensions],
                    },
                } for output in node.inputs.values()
            ],
            "outPorts": [
                {
                    "name": output.id,
                    "title": output.id,
                    "customData": {
                        "datatype": output.resulting_datatype.id,
                        "dimension_names": [x.name for x in output.dimensions],
                    },
                } for output in node.outputs.values()
            ],
            "type": type(node).__name__,
        }

        if type(node).__name__ == 'SourceNodeRun':
            node_data['inPorts'].append(
                {
                    "name": 'input',
                    "title": 'input',
                    "customData": {
                        "datatype": node.output.datatype.id,
                        "dimension_names": [node.id],
                    },
                }
            )

        if type(node).__name__ == 'SinkNodeRun':
            node_data['outPorts'].append(
                {
                    "name": 'output',
                    "title": 'output',
                    "customData": {
                        "datatype": node.input.datatype.id,
                        "dimension_names": node.dimnames,
                    },
                }
            )

        # Register node id mapping
        self.nodes[node.global_id] = '{}/{}'.format(scope, node.id)

        return node_data

    def pim_serialize_macro(self, node, scope, links):
        new_scope = '{}/{}'.format(scope, node.id)
        self.nodes[node.global_id] = new_scope

        # Set node data
        node_data = {
            "name": node.id,
            "title": node.id,
            "children": [],
            "customData": {},
            "inPorts": [],
            "outPorts": [],
            "type": type(node).__name__,
        }

        # Serialize underlying network
        self.pim_serialize_network(node.network_run, new_scope, node_data, links)

        return node_data

    def pim_serialize_network(self, network, scope, parent, links):
        visited_nodes = set()

        for step_name, step_nodes in network.stepids.items():
            step_data = {
                "name": step_name,
                "title": step_name,
                "children": [],
                "customData": {},
                "inPorts": [],
                "outPorts": [],
                "type": "NetworkStep",
            }

            parent['children'].append(step_data)

            # Serialize nodes to parents child list
            for node in step_nodes:
                step_data['children'].append(self.pim_serialize_node(node, '{}/{}'.format(scope, step_name), links))
                visited_nodes.add(node.id)

        # Serialize nodes to parents child list
        for node in network.nodelist.values():
            if node.id not in visited_nodes:
                parent['children'].append(self.pim_serialize_node(node, scope, links))

        # Serialize links to global link list
        for link in network.linklist.values():
            links.append(self.pim_serialize_link(link))

    def pim_serialize_link(self, link):
        if type(link.source.node).__name__ == 'MacroNodeRun':
            from_port = "{}/{}/output".format(self.nodes[link.source.node.global_id],
                                              link.source.id)
        else:
            from_port = "{}/{}".format(self.nodes[link.source.node.global_id],
                                       link.source.id)

        if type(link.target.node).__name__ == 'MacroNodeRun':
            to_port = "{}/{}/input".format(self.nodes[link.target.node.global_id],
                                           link.target.id)
        else:
            to_port = "{}/{}".format(self.nodes[link.target.node.global_id],
                                     link.target.id)

        link_data = {
            "customData": {
                "expand": link.expand,
                "collapse": link.collapse
            },
            "description": "",
            "fromPort": from_port,
            "name": link.id,
            "title": link.id,
            "toPort": to_port,
            "dataType": link.source.resulting_datatype.id
        }

        return link_data

    def pim_register_run(self, network):
        if self.pim_uri is None:
            fastr.log.warning('No valid PIM uri known. Cannot register to PIM!')
            return

        self.run_id = network.id
        pim_run_data = {
            "title": self.run_id,
            "name": self.run_id,
            "assignedTo": [],
            "user": fastr.config.pim_username,
            "root": {
                "name": "root",
                "title": network.network_id,
                "description": "",
                "children": [],
                "customData": {},
                "inPorts": [],
                "outPorts": [],
                "type": "NetworkRun",
            },
            "links": [],
            "description": "Run of {} started at {}".format(network.id,
                                                            network.timestamp),
            "customData": {
                "workflow_engine": "fastr",
                "tmpdir": network.tmpdir,
            },
            "statusTypes": self.STATUS_TYPES,
        }

        self.pim_serialize_network(network=network,
                                   scope="root",
                                   parent=pim_run_data["root"],
                                   links=pim_run_data["links"])

        uri = '{pim}/api/runs/'.format(pim=fastr.config.pim_host)
        fastr.log.info('Registering {} with PIM at {}'.format(self.run_id, uri))

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, json.dumps(pim_run_data, indent=2)))

        # Cache the jobs uri
        self.jobs_uri = '{pim}/api/runs/{run_id}/jobs'.format(pim=fastr.config.pim_host,
                                                              run_id=self.run_id)

        # Send out the response and record if we registered correctly
        try:
            response = requests.post(uri, json=pim_run_data)
            if response.status_code in [200, 201]:
                self.registered = True
                self.submit_thread.start()
                fastr.log.info('Run registered in PIM at {}/runs/{}'.format(fastr.config.pim_host,
                                                                            self.run_id))
            else:
                fastr.log.warning('Could not register run at PIM, got a {} response'.format(response.status_code))
                fastr.log.warning('Response: {}'.format(response.text))
        except requests.ConnectionError as exception:
            fastr.log.error('Could no register network to PIM, encountered'
                            ' exception: {}'.format(exception))

        # Create dummy job
        root_job_data = {
            "path": 'root/master',
            "title": "",
            "customData": {
            },
            "status": self.PIM_STATUS_MAPPING[JobState.running],
            "description": "",
        }

        self.queued_job_updates.append(root_job_data)

    def pim_finish_run(self, run):
        # Finish dummy job
        root_job_data = {
            "path": 'root/master',
            "title": "",
            "customData": {
            },
            "status": self.PIM_STATUS_MAPPING[JobState.finished if run.result else JobState.failed],
            "description": "",
        }
        self.queued_job_updates.append(root_job_data)

        self.running = False

        run_finished = datetime.datetime.now()

        while len(self.queued_job_updates) != 0 or len(self.submitted_job_updates) != 0:
            timer = datetime.datetime.now() - run_finished
            if timer.seconds > self.finished_timeout:
                fastr.log.warning('Not all PIM updates sent, timeout reached!')
                break
            time.sleep(self.update_interval)
            fastr.log.info('Waiting for all jobs to be published to PIM...')

    def pim_log_line(self, record: LogRecord):
        timestamp = datetime.datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')

        root_job_data = {
            "path": 'root/master',
            "customData": {
                '__log__': {
                    timestamp: {
                        'process_name': record.processName,
                        'thread_name': record.threadName,
                        'level_name': record.levelname,
                        'module': record.module,
                        'function': record.funcName,
                        'lineno': record.lineno,
                        'message': record.msg
                    }
                }
            }
        }
        self.queued_job_updates.append(root_job_data)


class PimReporter(ReportingPlugin):
    SUPPORTED_APIS = {
        2: PimAPIv2,
    }

    def __init__(self):
        self.pim_uri = None
        super().__init__()
        self.api = None

    def activate(self):
        """
        Activate the reporting plugin
        """
        super().activate()

        # Parse URI
        if fastr.config.pim_host == '':
            fastr.log.info("No valid PIM host given, PIM publishing will be disabled!")
            self.pim_uri = None
            self.api = None
            return

        self.pim_uri = fastr.config.pim_host

        try:
            response = requests.get('{pim}/api/info'.format(pim=self.pim_uri))
            if response.status_code >= 300:
                version = 1
            else:
                version = response.json().get('version', 1)
        except requests.ConnectionError as exception:
            fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))
            return

        try:
            api_class = self.SUPPORTED_APIS[version]
            fastr.log.info('Using PIM API version {}'.format(version))
        except KeyError:
            fastr.log.error('PIM API version {} not supported!'.format(version))
            return

        self.api = api_class(self.pim_uri)

    @classproperty
    def configuration_fields(cls):
        return {
            "pim_host": (str, "", "The PIM host to report to"),
            "pim_username": (str, getpass.getuser(), "Username to send to PIM",
                             "Username of the currently logged in user"),
            "pim_update_interval": (float, 2.5, "The interval in which to send jobs to PIM"),
            "pim_batch_size": (int, 100, "Maximum number of jobs that can be send to PIM in a single interval"),
            "pim_debug": (bool, False, "Setup PIM debug mode to send stdout stderr on job success"),
            "pim_finished_timeout": (int, 10, "Maximum number of seconds after the network finished in which PIM "
                                              "tries to synchronize all remaining jobs")
        }

    def job_updated(self, job: Job):
        if self.pim_uri and self.api:
            self.api.pim_update_status(job)

    def run_started(self, run: NetworkRun):
        if self.pim_uri and self.api:
            self.api.pim_register_run(run)

    def run_finished(self, run: NetworkRun):
        if self.pim_uri and self.api:
            self.api.pim_finish_run(run)

    def log_record_emitted(self, record: LogRecord):
        if self.pim_uri and self.api and self.api.running:
            self.api.pim_log_line(record)

