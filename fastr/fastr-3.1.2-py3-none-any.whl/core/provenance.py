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

import os
import urllib.parse

import prov
from prov.model import ProvDocument

import fastr
from fastr import exceptions
from fastr.data import url
from fastr.datatypes import Deferred
from fastr.helpers import iohelpers


class Provenance(object):
    """
    The Provenance object keeps track of everything that happens to a data object.
    """

    def __init__(self, host=None):
        if host is not None:
            self.host = host.rstrip('/')
        else:
            self.host = fastr.config.web_url()
        self.namespaces = {}
        self.document = ProvDocument()

        # Define default namespaces
        self.fastr = self._add_namespace('fastr')
        self.tool = self._add_namespace('tool')
        self.node = self._add_namespace('node')
        self.job = self._add_namespace('job')
        self.data = self._add_namespace('data')
        self.worker = self._add_namespace('worker')
        self.network = self._add_namespace('network')
        self.fastr_info = self._add_namespace('fastrinfo')

        # Add fastr agent
        self.fastr_agent = self.agent(self.fastr[fastr.version.version])

    def _add_namespace(self, name, parent=None, url=None):
        if parent is None:
            host = self.host
        else:
            if parent in list(self.namespaces.keys()):
                host = self.namespaces[parent].uri
            else:
                return None

        if url is None:
            self.namespaces[name] = self.document.add_namespace(name, "{}/{}/".format(host, name))
        else:
            self.namespaces[name] = self.document.add_namespace(name, "{}/{}".format(host, url))
        return self.namespaces[name]

    def agent(self, identifier, other_attributes=None):
        return self.document.agent(identifier, other_attributes)

    def activity(self, identifier, start_time=None, end_time=None, other_attributes=None):
        return self.document.activity(identifier, start_time, end_time, other_attributes)

    def entity(self, identifier, other_attributes=None):
        return self.document.entity(identifier, other_attributes)

    def init_provenance(self, job):
        """
        Create initial provenance document
        """
        self.job_activity = self.activity(self.job[job.id])
        self.tool_agent = self.agent(
            self.tool["{}/{}".format(job.tool_name, job.tool_version)],
            {
                'fastrinfo:tool_dump': job.tool.dumps()
            }
        )
        self.node_agent = self.agent(self.node[job.node_id])
        self.network_agent = self.agent(self.network["{}/{}".format(job.network_id, job.network_version)])

        self.document.actedOnBehalfOf(self.network_agent, self.fastr_agent)
        self.document.actedOnBehalfOf(self.node_agent, self.tool_agent)
        self.document.actedOnBehalfOf(self.node_agent, self.network_agent)
        self.document.wasAssociatedWith(self.job_activity, self.node_agent)

    def collect_provenance(self, job, advanced_flow=False):
        """
        Collect the provenance for this job
        """
        tool = job.tool
        for input_argument_key, input_argument_value in job.input_arguments.items():
            input_description = tool.inputs[input_argument_key]

            if input_description.hidden:
                # Skip hidden inputs (they are used for the system to feed
                # additional data to sources/sinks etc) not interesting
                # for provenance
                continue

            if not advanced_flow:
                self.collect_input_argument_provenance(input_argument_value)
            else:
                for sample in input_argument_value:
                    self.collect_input_argument_provenance(sample)

        self.document._records = list(set(self.document._records))

    def collect_input_argument_provenance(self, input_argument):
        for cardinality, value in enumerate(input_argument.data.iterelements()):
            parent_provenance, parent_job = self.get_parent_provenance(value)
            value_url = self.data_uri(value, parent_job)

            if isinstance(parent_provenance, ProvDocument):
                self.document.update(parent_provenance)
                data_entity = self.entity(self.data[value_url], {
                    'fastrinfo:value': value.value
                })
                self.document.wasGeneratedBy(data_entity, self.activity(self.job[parent_job.id]))
            else:
                data_entity = self.entity(self.data[value_url])
            self.document.used(self.job_activity, data_entity)

    @staticmethod
    def data_uri(value, job):
        if isinstance(value.raw_value, str) and value.raw_value.startswith('val://'):
            val_uri = urllib.parse.urlparse(value.raw_value)
            val_query = urllib.parse.parse_qs(val_uri.query)
            sample_id = val_query['sampleid'][0] if 'sampleid' in val_query else job.sample_id

            return 'fastr://data/job/{job_id}/output/{outputid}/sample/{sample}/cardinality/{cardinality}'.format(
                job_id=job.id,
                outputid=val_query['outputname'][0],
                sample=sample_id,
                cardinality=val_query['nr'][0]
            )
        else:
            if url.isurl(value.raw_value):
                return value.raw_value
            else:
                return 'fastr://data/constant/{}'.format(value.raw_value)

    @staticmethod
    def get_parent_provenance(value):
        """
        Find the provenance of the parent job

        :param str value: url for the value for which to find the job
        :return: the provenance of the job that created the value
        :raises FastrKeyError: if the deferred is not available (yet)
        :raises FastrValueError: if the value is not a valid deferred url
        """
        if not isinstance(value, Deferred):
            return None, None

        parsed_url = urllib.parse.urlparse(value.raw_value)

        if parsed_url.scheme != 'val':
            raise exceptions.FastrValueError('Cannot lookup value {}, wrong url scheme'.format(value.raw_value))

        # First load job to find location of the prov file
        datafile = os.path.join(fastr.config.mounts[parsed_url.netloc],
                                os.path.normpath(parsed_url.path[1:]))

        # Open Job file
        job_data = iohelpers.load_gpickle(datafile)

        # Get provenance file
        provenance_data = prov.read(job_data.provfile, 'json')

        return provenance_data, job_data

    def serialize(self, filename, format):
        with open(filename, 'w') as fh_out:
            self.document.serialize(destination=fh_out, format=format)

            # Make sure the data gets flushed
            fh_out.flush()
            os.fsync(fh_out.fileno())
