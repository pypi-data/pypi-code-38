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


from collections import OrderedDict

import sympy

from .. import exceptions
from ..core.samples import SampleId, SampleItem, SampleIndex
from .inputoutputrun import AdvancedFlowOutputRun, OutputRun
from .job import InlineJob, JobState
from .noderun import NodeRun
from ..helpers import log

__all__ = ['FlowNodeRun', 'AdvancedFlowNodeRun']


class FlowNodeRun(NodeRun):
    """
    A Flow NodeRun is a special subclass of Nodes in which the amount of samples
    can vary per Output. This allows non-default data flows.
    """
    _OutputType = OutputRun

    @property
    def blocking(self):
        """
        A FlowNodeRun is (for the moment) always considered blocking.

        :return: True
        """
        return True

    @property
    def outputsize(self):
        """
        Size of the outputs in this NodeRun
        """
        # Get sizes of all input groups
        output_size = []
        for input_group in self.input_groups.values():
            if input_group.size is not None:
                output_size.extend(input_group.size)
            else:
                return None

        output_size.append(sympy.symbols('N_{}'.format(self.id)))
        return tuple(output_size)

    @property
    def dimnames(self):
        """
        Names of the dimensions in the NodeRun output. These will be reflected
        in the SampleIdList of this NodeRun.
        """
        if self.nodegroup is not None:
            extra_dim = self.nodegroup
        else:
            extra_dim = self.id

        return super(FlowNodeRun, self).dimnames + (extra_dim,)

    def set_result(self, job, failed_annotation):
        """
        Incorporate result of a job into the FlowNodeRun.

        :param Type job: job of which the result to store
        """
        log.debug('Job output data: {}'.format(job.output_data))

        # Get the main sample index from the Job
        sample_index = job.sample_index

        for output in self.outputs.values():
            if output.id not in job.output_data:
                log.error('Could not find expected data for {} in {}!'.format(output.fullid, job.output_data))

            if failed_annotation:
                data = [(job.sample_id, (job.get_deferred(output.id, 0),))]
            else:
                data = job.output_data[output.id]

            log.debug('output_data = {}'.format(data))

            # Make sure dictionary is sorted, can also be list of items
            # which will be kept ordered
            if isinstance(data, dict):
                data = sorted(data.items())

            if not all(isinstance(x, (list, tuple)) and len(x) == 2 for x in data):
                raise exceptions.FastrValueError('The output data for a FlowNodeRun should be a dictionary or a list of items (length 2 per entry)')

            for sample_nr, (sample_id, sample_data) in enumerate(data):
                orig_sample_id = sample_id

                # Ensure we have a SampleId (cast if need be)
                if not isinstance(sample_id, SampleId):
                    # Make sure sample_id is built from a tuple of str
                    if isinstance(sample_id, str):
                        sample_id = (str(sample_id),)
                    else:
                        sample_id = tuple(str(x) for x in sample_id)

                    sample_id = SampleId(sample_id)

                    log.debug('Change sample_id from {} ({}) to {} ({})'.format(orig_sample_id,
                                                                                      type(orig_sample_id).__name__,
                                                                                      sample_id,
                                                                                      type(sample_id).__name__))

                if len(sample_id) != output.ndims:
                    sample_id = job.sample_id + sample_id
                    log.debug('Updated sample_id to {}'.format(sample_id))
                    if len(sample_id) != output.ndims:
                        raise exceptions.FastrValueError('Sample ID {} has the wrong dimensionality!'.format(sample_id))

                log.debug('Setting data for blocking node: {} sample: {}'.format(output.fullid, sample_id))

                output_values = tuple(job.get_deferred(output.id,
                                                       c,
                                                       orig_sample_id) for c, _ in enumerate(sample_data))

                log.debug('Setting collected for {} sample_id {} sample_index {!r} data: {}'.format(output.fullid,
                                                                                                          sample_id,
                                                                                                          sample_index + (sample_nr),
                                                                                                          output_values))

                # Save with sample_index and sample nr in the extra dimension
                output[sample_id, sample_index + (sample_nr)] = SampleItem(sample_index + (sample_nr),
                                                                           sample_id,
                                                                           OrderedDict({0: tuple(output_values)}),
                                                                           {job},
                                                                           failed_annotation)

                # Register the samples parent job
                self.jobs[sample_id] = job


class AdvancedFlowNodeRun(FlowNodeRun):
    _OutputType = AdvancedFlowOutputRun
    _JobType = InlineJob

    def execute(self):
        """
        Execute the node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        # Make sure a NodeRun is valid
        if not self.valid:
            message = 'NodeRun {} is not valid'.format(self.fullid)
            log.error(message)
            log.error('Messages:\n{}'.format('\n'.join(self.messages)))
            raise exceptions.FastrNodeNotValidError(message)
        input_groups = self.input_groups

        # Prepare the output of the NodeRun
        log.debug('InputGroups: {}'.format(list(input_groups.values())))
        log.debug('Inputs: {}'.format([x for ig in list(input_groups.values()) for x in list(ig.values())]))
        log.debug('Sources: {}'.format([x.source for ig in list(input_groups.values()) for x in list(ig.values())]))

        data = {x.id: list(x.items()) for x in self.inputs.values()}
        target = self.tool.target

        job = self.create_job(SampleId('FLOW'),
                              SampleIndex(0),
                              job_data=data,
                              job_dependencies=None)

        with target:
            result = self.tool.interface.execute(target, data)

        job.flow_data = result.result_data

        output_data = {key: {str(v.id): v.data.sequence_part() for k, v in list(value.items())} for key, value in list(result.result_data.items())}
        job.output_data = output_data

        job.status = JobState.execution_done
        job.write()

        yield [job]

    def set_result(self, job, failed_annotation):
        for output, data in job.flow_data.items():
            log.debug('Advanced flow for output: {}'.format(output))
            for (sample_index, sample_id), value in data.items():
                log.debug('Advanced flow sample {!r} -> {}'.format(sample_index, list(value.data)))

                output_values = tuple(job.get_deferred(output,
                                                       c,
                                                       sample_id) for c, _ in enumerate(value.data))

                log.debug('Setting collected for {} sample_id {!r} sample_index {!r} data: {}'.format(output,
                                                                                                      sample_id,
                                                                                                      sample_index,
                                                                                                      output_values))

                # Save with sample_index and sample nr in the extra dimension
                self.outputs[output][sample_index] = SampleItem(value.index,
                                                                value.id,
                                                                OrderedDict({0: tuple(output_values)}),
                                                                {job},
                                                                failed_annotation)

        self.jobs['FLOW'] = job
