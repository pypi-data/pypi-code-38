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


from .job import SinkJob
from .noderun import NodeRun
from .. import exceptions
from ..core.samples import SampleItem, SampleValue
from ..datatypes import types
from ..helpers import log

__all__ = ['SinkNodeRun']


class SinkNodeRun(NodeRun):
    """
    Class which handles where the output goes. This can be any kind of file, e.g.
    image files, textfiles, config files, etc.
    """

    __dataschemafile__ = 'SinkNodeRun.schema.json'
    _JobType = SinkJob

    def __init__(self, node, parent):
        """ Instantiation of the SinkNodeRun.

        :param fastr.planning.node.Node node: The Node that this Run is based on.
        :param NetworkRun parent: The NetworkRun that this NodeRun belongs to
        :return: newly created sink node run
        """
        NodeRun.__init__(self, node, parent)

        # Set the DataType
        self.datatype = node.datatype
        self.url = node.url

    def __getstate__(self):
        state = super(SinkNodeRun, self).__getstate__()
        state['url'] = self.url
        return state

    def __setstate__(self, state):
        super(SinkNodeRun, self).__setstate__(state)
        self.url = state['url']

    @property
    def datatype(self):
        """
        The datatype of the data this sink can store.
        """
        return self.inputs['input'].datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of the data this sink can store (setter).
        """
        self.inputs['input'].datatype = value

    @property
    def input(self):
        """
        The default input of the sink NodeRun
        """
        return self.inputs['input']

    @input.setter
    def input(self, value):
        """
        The default input of the sink NodeRun (setter)
        """
        self.inputs['input'] = value

    def execute(self):
        """
        Execute the sink node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        joblist = []

        for sample_index, sampleid, data, jobs, fails in self.inputs['input'].items():
            for cardinality_nr, value in enumerate(data.sequence_part()):
                log.debug('Spawning job for {}'.format(self.inputs['input'].fullid))
                joblist.append(self.create_job(sampleid,
                                               sample_index,
                                               {
                                                   'input': SampleItem(
                                                       sample_index,
                                                       sampleid,
                                                       SampleValue({0: (value,)})
                                                   ),
                                                   'cardinality': cardinality_nr
                                               }, jobs))

        self.drained = True
        yield joblist

    def set_data(self, data):
        """
        Set the targets of this sink node.

        :param data: the targets rules for where to write the data
        :type data: dict or list of urls

        The target rules can include a few fields that can be filled out:

        =========== ==================================================================
        field       description
        =========== ==================================================================
        sample_id   the sample id of the sample written in string form
        cardinality the cardinality of the sample written
        ext         the extension of the datatype of the written data, including the .
        extension   the extension of the datatype of the written data, excluding the .
        network     the id of the network the sink is part of
        node        the id of the node of the sink
        timestamp   the iso formatted datetime the network execution started
        uuid        the uuid of the network run (generated using uuid.uuid1)
        =========== ==================================================================

        An example of a valid target could be:

        .. code-block:: python

          >>> target = 'vfs://output_mnt/some/path/image_{sample_id}_{cardinality}{ext}'

        .. note::
            The ``{ext}`` and ``{extension}`` are very similar but are both offered.
            In many cases having a ``name.{extension}`` will feel like the correct way
            to do it. However, if you have DataTypes with and without extension that
            can both exported by the same sink, this would cause either ``name.ext`` or
            ``name.`` to be generated. In this particular case ``name{ext}`` can help
            as it will create either ``name.ext`` or ``name``.

        .. note::
            If a datatype has multiple extensions (e.g. .tiff and .tif) the first
            extension defined in the extension tuple of the datatype will be used.
        """
        if isinstance(data, str):
            try:
                data.format(sample_id='dummy',
                            cardinality=0,
                            ext='.ext',
                            extension='ext',
                            network='network',
                            node='node',
                            timestamp='timestamp',
                            uuid='uuid')
            except KeyError as error:
                raise exceptions.FastrValueError(
                    ('Using unknown substitution "{}" in SinkData "{}", valid'
                     ' substitution fields are: sample_id, cardinality,'
                     ' ext').format(error.message, data)
                )
            self.url = data
        else:
            raise exceptions.FastrTypeError(
                'Invalid datatype for SinkNode data, expected str but got {}!'.format(type(data).__name__)
            )

    def set_result(self, job, failed_annotation):
        """
        Incorporate result of a sink job into the Network.

        :param Type job: job of which the result to store
        :param set failed_annotation: A set of annotations, None if no errors else containing
                                      a tuple describing the errors
        """
        super(SinkNodeRun, self).set_result(job, failed_annotation)

        if self.id not in self.parent.sink_results:
            self.parent.sink_results[self.id] = {}

        self.parent.sink_results[self.id][job.sample_id] = (job, failed_annotation)

    def create_job(self, sample_id, sample_index, job_data, job_dependencies, **kwargs):
        """
        Create a job for a sink based on the sample id, job data and job dependencies.

        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param dict job_data: dictionary containing all input data for the job
        :param job_dependencies: other jobs that need to finish before this job can run
        :return: the created job
        :rtype: :py:class:`Job <fastr.execution.job.Job>`
        """

        substitutions = {'sample_id': sample_id,
                         'cardinality': job_data['cardinality'],
                         'timestamp': self.parent.timestamp.isoformat(),
                         'uuid': self.parent.uuid,
                         'network': self.parent.id,
                         'node': self.id}

        job = super(SinkNodeRun, self).create_job(sample_id, sample_index, job_data, job_dependencies,
                                                  substitutions=substitutions, **kwargs)

        self.jobs[sample_id] = job
        return job

    def _wrap_arguments(self, job_data, sample_id, sample_index):
        """
        Wrap arguments into a list of tuples that the execution script can parse

        :param dict job_data: dictionary containing all input data for the job
        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the wrapped arguments in a tuple with the form ``(inputs, outputs)``

        .. note::
            For a SinkNodeRun this function adds a few default (hidden) arguments
        """
        arguments = super(SinkNodeRun, self)._wrap_arguments(job_data, sample_id, sample_index)
        arguments[0]['output'] = types['String'](self.url),
        arguments[0]['datatype'] = types['String'](self.datatype.id),

        log.debug('Wrapped Sink arguments to {}'.format(arguments))

        return arguments
