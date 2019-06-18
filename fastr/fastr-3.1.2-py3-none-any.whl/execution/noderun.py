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

"""
A module to maintain a run of a network node.
"""

import weakref
from collections import OrderedDict

from .basenoderun import BaseNodeRun
from .inputoutputrun import BaseInputRun, InputRun, OutputRun
from .job import Job
from .. import exceptions, resources
from ..core.samples import SampleId, SampleIndex, SampleItem
from ..core.resourcelimit import ResourceLimit
from ..core.tool import Tool
from ..datatypes import DataType
from ..helpers import log
from ..planning.inputgroupcombiner import DefaultInputGroupCombiner, MergingInputGroupCombiner
from ..planning.node import InputGroup

__all__ = ['NodeRun']


class NodeRun(BaseNodeRun):
    """
    The class encapsulating a node in the network. The node is responsible
    for setting and checking inputs and outputs based on the description
    provided by a tool instance.
    """
    __dataschemafile__ = 'NodeRun.schema.json'

    _InputType = InputRun
    _OutputType = OutputRun
    _JobType = Job

    def __init__(self, node, parent):
        """
        Instantiate a node.

        :param node: The node to base the noderun on
        :type node: :py:class:`Tool <fastr.planning.node.NodeRun>`
        :param parent: the parent network of the node
        :type parent: :py:class:`Network <fastr.planning.network.Network>`
        :return: the newly created NodeRun
        """
        super(NodeRun, self).__init__()

        self._tool = node.tool
        self._parent = weakref.ref(parent)
        self._id = node.id
        self.nodegroup = node.nodegroup
        self.drained = False

        inputlist = []
        outputlist = []

        # Create Input/Output objects
        for input_ in node.inputs.values():
            # It can happen that this has been done by a subclass, check first
            inputobj = self._InputType(self, input_)
            inputlist.append((inputobj.id, inputobj))

        for output in node.outputs.values():
            # It can happen that this has been done by a subclass, check first
            outputobj = self._OutputType(self, output)
            outputlist.append((outputobj.id, outputobj))

        self.inputs = OrderedDict(inputlist)
        self.outputs = OrderedDict(outputlist)

        self._input_groups = OrderedDict()

        # Set the job requirements
        self._resources = node.resources

        # Set the flow control
        self.input_group_combiner = None
        self.merge_dimensions = node.merge_dimensions

        # Set the input groups
        self.update_input_groups()
        self.input_group_combiner.update()

        self.jobs = {}

        # Update Inputs and self (which calls Outputs)
        self.update()

    def __repr__(self):
        """
        Get a string representation for the NodeRun

        :return: the string representation
        :rtype: str
        """
        return str(self)

    def __str__(self):
        """
        Get a string version for the NodeRun

        :return: the string version
        :rtype: str
        """
        return "<{}: {}>".format(type(self).__name__, self.id)

    def __eq__(self, other):
        """Compare two Node instances with each other. This function ignores
        the parent and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: NodeRun
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, NodeRun):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['_parent']
        del dict_self['_status']
        del dict_self['_input_groups']
        del dict_self['jobs']
        del dict_self['input_group_combiner']

        dict_other = dict(vars(other))
        del dict_other['_parent']
        del dict_other['_status']
        del dict_other['_input_groups']
        del dict_other['jobs']
        del dict_other['input_group_combiner']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the NodeRun

        :return: the state of the object
        :rtype dict:
        """
        state = super(NodeRun, self).__getstate__()

        # Make id prettier in the result
        state['id'] = self.id

        # Add the class of the NodeRun in question
        state['class'] = type(self).__name__

        # Get all input and output
        state['inputs'] = [x.__getstate__() for x in self.inputs.values()]
        state['outputs'] = [x.__getstate__() for x in self.outputs.values()]

        if self._tool is not None:
            state['tool'] = [self._tool.ns_id, str(self._tool.command['version'])]
        else:
            state['tool'] = None

        # Add resource requirements
        state['_resources'] = self._resources.__getstate__()
        state['merge_dimensions'] = self._merge_dimensions

        return state

    def __setstate__(self, state):
        """
        Set the state of the NodeRun by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        # Make sure the NodeRun classes are aligned (and warn if not so)
        if 'class' in state and state['class'] != type(self).__name__:
            log.warning('Attempting to set the state of a {} to {}'.format(
                state['class'],
                type(self).__name__
            ))

        self.jobs = None

        if not hasattr(self, '_input_groups'):
            self._input_groups = OrderedDict()

        if 'id' in state:
            self._id = state['id']

        if 'parent' in state:
            parent = state['parent']
            del state['parent']
        else:
            parent = None

        if state['tool'] is not None:
            self._tool = resources.tools[tuple(state['tool'])]
        else:
            self._tool = None

        # Create Input/Output objects
        inputlist = []
        for input_ in state['inputs']:
            if 'node' in input_:
                # Check if the expected NodeRun id matches our current id
                if input_['node'] != state['id']:
                    raise exceptions.FastrParentMismatchError('This Input has different parent node!')
                del input_['node']

            # It can happen that this has been done by a subclass, check first
            if not isinstance(input_, BaseInputRun):
                description = self.tool.inputs[input_['id']]
                inputobj = self._InputType(self, description)
                inputobj._node = self
                inputobj.__setstate__(input_)
            else:
                inputobj = input_
            inputlist.append((inputobj.id, inputobj))

        outputlist = []
        for output in state['outputs']:
            if '_node' in output:
                # Check if the expected NodeRun id matches our current id
                if output['_node'] != state['_id']:
                    raise exceptions.FastrParentMismatchError('This Input has different parent node!')
                del output['_node']

            # It can happen that this has been done by a subclass, check first
            if not isinstance(output, OutputRun):
                description = self.tool.outputs[output['id']]
                outputobj = self._OutputType(self, description)
                outputobj.__setstate__(output)
            else:
                outputobj = output
            outputlist.append((outputobj.id, outputobj))

        self.inputs = OrderedDict(inputlist)
        self.outputs = OrderedDict(outputlist)

        super(NodeRun, self).__setstate__(state)

        self._parent = None
        if parent is not None:
            self.parent = parent
        else:
            message = 'parent argument is None, need a parent Network to function!'
            raise exceptions.FastrValueError(message)

        self._resources = ResourceLimit()
        self._resources.__setstate__(state['resources'])
        self.merge_dimensions = state['merge_dimensions']

        self.update()

    @property
    def merge_dimensions(self):
        return self._merge_dimensions

    @merge_dimensions.setter
    def merge_dimensions(self, value):
        if isinstance(value, str):
            options = ['all', 'none']
            if value not in options:
                raise exceptions.FastrValueError('Invalid option {} given (valid options: {})'.format(value, options))
            self._merge_dimensions = value
            if value == 'none':
                self.input_group_combiner = DefaultInputGroupCombiner(self)
            elif value == 'all':
                self.input_group_combiner = MergingInputGroupCombiner(self, value)
        else:
            self._merge_dimensions = value
            self.input_group_combiner = MergingInputGroupCombiner(self, tuple(value))

    def update_input_groups(self):
        """
        Update all input groups in this node
        """
        input_groups = OrderedDict()

        for input_ in self.inputs.values():
            if input_.input_group not in input_groups:
                input_groups[input_.input_group] = InputGroup(self, input_.input_group)
            input_groups[input_.input_group][input_.id] = input_

        self._input_groups = input_groups

    @classmethod
    def createobj(cls, state, network=None):
        if 'parent' not in state:
            if network is not None:
                log.debug('Setting network to: {}'.format(network))
                state['parent'] = network
            else:
                log.debug('No network given for de-serialization')
        else:
            log.debug('Parent is already defined as: {}'.format(network))

        state = dict(state)

        return super(NodeRun, cls).createobj(state, network)

    @property
    def blocking(self):
        """
        Indicate that the results of this NodeRun cannot be determined without first executing the NodeRun, causing a
        blockage in the creation of jobs. A blocking Nodes causes the Chunk borders.
        """
        for output in self.outputs.values():
            if output.blocking:
                log.debug('Blocking because Output {} has cardinality {}'.format(output.fullid,
                                                                                       output.cardinality()))
                return True
        return False

    @property
    def dimnames(self):
        """
        Names of the dimensions in the NodeRun output. These will be reflected
        in the SampleIdList of this NodeRun.
        """
        if hasattr(self, '_dimnames') and self._dimnames is not None:
            return self._dimnames
        else:
            return self.input_group_combiner.dimnames

    @dimnames.setter
    def dimnames(self, value):
        if isinstance(value, str):
            value = value,

        if not isinstance(value, tuple) or not all(isinstance(x, str) for x in value):
            raise exceptions.FastrTypeError('Dimnames has to be a tuple of str!')

        log.warning('You are overriding the dimnames of a NodeRun, beware this is possible but not encouraged and can lead to strange results!')
        self._dimnames = value

    @dimnames.deleter
    def dimnames(self):
        del self._dimnames

    @property
    def fullid(self):
        """
        The full defining ID for the NodeRun inside the network
        """
        return '{}/nodelist/{}'.format(self.parent.fullid, self.id)

    @property
    def global_id(self):
        """
        The global defining ID for the Node from the main network (goes out
        of macro nodes to root network)
        """
        return '{}/nodelist/{}'.format(self.parent.global_id, self.id)

    @property
    def input_groups(self):
        """
        A list of input groups for this NodeRun. An input group is InputGroup
         object filled according to the NodeRun

        """
        return self._input_groups

    @property
    def outputsize(self):
        """
        Size of the outputs in this NodeRun
        """
        # Get sizes of all input groups
        return self.input_group_combiner.size

    @property
    def id(self):
        """
        The id of the NodeRun
        """
        return self._id

    @property
    def listeners(self):
        """
        All the listeners requesting output of this node, this means the
        listeners of all Outputs and SubOutputs
        """
        listeners = []
        for output in self.outputs.values():
            for listener in output.listeners:
                if listener not in listeners:
                    listeners.append(listener)
        return listeners

    @property
    def name(self):
        """
        Name of the Tool the NodeRun was based on. In case a Toolless NodeRun was
        used the class name is given.
        """
        if hasattr(self, '_tool') and isinstance(self._tool, Tool):
            return self._tool.id
        else:
            return self.__class__.__name__

    @property
    def parent(self):
        """
        The parent network of this node.
        """
        return self._parent()

    @parent.setter
    def parent(self, value):
        """
        The parent network of this node. (setter)
        """
        if self._parent() is value:
            return  # Setting to same value doesn't do anything

        if self._parent() is not None:
            raise exceptions.FastrAttributeError('Cannot reset attribute once set')

        self._parent = weakref.ref(value)
        self._parent().add_node(self)

    @property
    def resources(self):
        """
        Number of cores required for the execution of this NodeRun
        """
        return self._resources

    @property
    def status(self):
        return self._status

    @property
    def tool(self):
        return self._tool

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

        log.info('Generating jobs for node "{}" with dimensions: {}'.format(
            self.id,
            ', '.join('[{}: {}]'.format(name, size) for name, size in zip(self.dimnames, self.outputsize))
        ))

        # Iterate over all combinations of input_groups to create sets of data
        job_list = []

        log.debug('InputGroups: {}'.format(list(input_groups.values())))
        log.debug('Inputs: {}'.format([x for ig in input_groups.values() for x in ig.values()]))
        log.debug('Sources: {}'.format([x.source for ig in input_groups.values() for x in ig.values()]))

        for sample_index, sample_id, job_data, job_depends, failed_annotations in self.input_group_combiner:
            log.debug('----- START -----')
            log.debug('INDEX: {}'.format(sample_index))
            log.debug('SAMPLE_ID: {} {}'.format(repr(sample_id), sample_id))
            log.debug('JOBDATA: {}'.format(job_data))
            log.debug('JOBDEPS: {}'.format(job_depends))
            log.debug('FAILS: {}'.format(failed_annotations))
            log.debug('------ END ------')

            job_list.append(self.create_job(sample_id, sample_index, job_data, job_depends))

        log.debug('joblist: {}'.format(job_list))
        log.debug('===== END execute_node =====')
        self.drained = True
        yield job_list

    def set_result(self, job, failed_annotation):
        """
        Incorporate result of a job into the NodeRun.

        :param Type job: job of which the result to store
        :param failed_annotation: A set of annotations, None if no errors else containing a tuple describing the errors
        """
        sample_id, sample_index = job.sample_id, job.sample_index
        # Replace following code by node.set_data(job.output_data) ? or something like it?
        for output in self.outputs.values():
            if output.id not in job.output_data and len(output.listeners) > 0 and len(failed_annotation) == 0:
                error_message = 'Could not find required data for {} in {}!'.format(output.fullid, job.output_data)
                log.error(error_message)

        for output in self.outputs.values():
            # No Errors and No samples in output
            if not failed_annotation and self.blocking:
                log.debug('>>>> >>>> No Errors and No samples in output in sample[{};{}]'.format(sample_id, sample_index))

                if output.id not in job.output_data:
                    # There is not data, skip this output, if this was a problem,
                    # a failure should have been detected anyways, but probably it
                    # was a non-required output
                    continue

                output_data = job.output_data[output.id]

                log.debug('Setting data for blocking node: {} sample: {} with annotation: {}'.format(output.fullid,
                                                                                                           sample_id,
                                                                                                           failed_annotation))

                output_values = tuple(job.get_deferred(output.id, c) for c in range(len(output_data)))

                log.debug('Setting collected for {} sample_id {} data: {}'.format(output.fullid,
                                                                                        sample_id,
                                                                                        output_values))
                output[sample_id, sample_index] = SampleItem(sample_index,
                                                             sample_id,
                                                             OrderedDict({0: tuple(output_values)}),
                                                             {job},
                                                             failed_annotation)
            # Errors and no samples
            elif failed_annotation and self.blocking:
                output_values = (job.get_deferred(output.id, 0),)

                log.debug('Setting data for blocking node: {} sample: {} with annotation: {}'.format(output.fullid,
                                                                                                           sample_id,
                                                                                                           failed_annotation))

                log.debug('>>>> >>>> Errors and No samples in output in sample[{};{}]'.format(sample_id, sample_index))
                output[sample_id, sample_index] = SampleItem(sample_index,
                                                             sample_id,
                                                             OrderedDict({0: tuple(output_values)}),
                                                             {job},
                                                             failed_annotation)

                log.debug('$$ new annotation: {}'.format(output[sample_index].failed_annotations))
                # Errors and samples
            elif failed_annotation and not self.blocking:
                log.debug('>>>> >>>> Errors and samples in output in sample[{};{}]'.format(sample_id, sample_index))
                output[sample_index].failed_annotations.update(failed_annotation)
            else:
                log.debug(">>>> >>>> No errors and samples in output in sample[{};{}]".format(sample_id, sample_index))

            self.jobs[sample_id] = job

    def create_job(self, sample_id: SampleId, sample_index: SampleIndex, job_data,
                   job_dependencies, **kwargs):
        """
        Create a job based on the sample id, job data and job dependencies.

        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param sample_index: the index of the corresponding sample
        :type sample_index: :py:class:`SampleIndex <fastr.core.sampleidlist.SampleIndex>`
        :param dict job_data: dictionary containing all input data for the job
        :param job_dependencies: other jobs that need to finish before this job can run
        :return: the created job
        :rtype: :py:class:`Job <fastr.execution.job.Job>`
        """
        log.info('Creating job for node {} sample id {!r}, index {!r}'.format(self.global_id, sample_id, sample_index))
        log.debug('Creating job for sample {} with data {}'.format(sample_id, job_data))

        # Get the arguments
        input_arguments, output_arguments = self._wrap_arguments(job_data, sample_id, sample_index)

        preferred_types = {output.id: output.preferred_types for output in self.outputs.values()}

        job = self._JobType(node=self,
                            sample_id=sample_id,
                            sample_index=sample_index,
                            input_arguments=input_arguments,
                            output_arguments=output_arguments,
                            hold_jobs=job_dependencies,
                            preferred_types=preferred_types,
                            **kwargs)
        self.jobs[sample_id] = job

        # Check which outputs are required or connected and set them
        if not self.blocking:
            for output in self.outputs.values():
                # Not that this always has to happen, as we need the samples
                # to possibly annotate errors later, even if the output will
                # not be used later because of a lack of listeners
                log.debug('Preparing output {}'.format(output.id))
                log.debug('Cardinality request: spec: {}, job_data: {}, and index: {}'.format(output.cardinality_spec,
                                                                                              job_data,
                                                                                              sample_index))
                cardinality = output.cardinality(sample_index, job_data)
                log.debug('Cardinality for {} is {}'.format(output.id, cardinality))
                if not isinstance(cardinality, int):
                    message = 'For execution cardinality should be an int, for output ' \
                              '{} we found {} (type {})'.format(output.id,
                                                                cardinality,
                                                                type(cardinality).__name__)
                    log.critical(message)
                    raise exceptions.FastrTypeError(message)

                value = tuple(job.get_deferred(output.id, cardinality_nr) for cardinality_nr in range(cardinality))

                output[sample_id] = SampleItem(sample_index,
                                               sample_id,
                                               {0: value},
                                               {job})
        else:
            log.debug('Cannot determine blocking node output a priori! Needs to be collected afterwards!')

        return job

    def _wrap_arguments(self, job_data, sample_id, sample_index):
        """
        Wrap arguments into a list of tuples that the execution script can parse

        :param dict job_data: dictionary containing all input data for the job
        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the wrapped arguments in a tuple with the form ``(inputs, outputs)``
        """
        arguments = ({}, {})  # format is (input_args, output_args)
        for key, input_ in self.inputs.items():
            # Skip inputs that have no data
            if job_data[key] is None:
                if input_.default is not None:
                    # Insert the default data if present
                    job_data[key] = [input_.datatype(input_.default)]
                elif input_.required:
                    log.debug('Job data: {}'.format(job_data))
                    raise exceptions.FastrValueError('NodeRun "{}" is missing data for required Input "{}"'.format(self.id, input_.id))
                else:
                    continue

            arguments[0][key] = job_data[key]

        for key, output in self.outputs.items():
            if not output.automatic:
                cardinality = output.cardinality(key=sample_index, job_data=job_data)
            else:
                cardinality = None

            if output.required or len(output.listeners) > 0:
                requested = True
            else:
                requested = False

            log.debug('Cardinality to be used: {}'.format(cardinality))

            arguments[1][key] = {
                'id': key,
                'cardinality': cardinality if cardinality is not None else str(output.cardinality_spec),
                'datatype': output.resulting_datatype.id,
                'requested': requested
            }

        return arguments

    def get_sourced_nodes(self):
        """
        A list of all Nodes connected as sources to this NodeRun

        :return: list of all nodes that are connected to an input of this node
        """
        sourced_nodes = []
        for input_ in self.inputs.values():
            for sourced_node in input_.get_sourced_nodes():
                if sourced_node not in sourced_nodes:
                    sourced_nodes.append(sourced_node)
        return sourced_nodes

    def find_source_index(self, target_index, target, source):
        # If there are multiple input groups, select only part of index from
        # the inputgroup which source belongs to
        if len(self.input_groups) > 1:
            input_groups = self.input_groups
            mask = [True if ig.id == source.input_group else False for ig in input_groups.values() for _ in ig.size]
            target_index = tuple(k for k, m in zip(target_index, mask) if m)

        # Delegate to InputGroup to check mixing within InputGroup
        return self.input_groups[source.input_group].find_source_index(target_size=target.size,
                                                                       target_dimnames=target.dimnames,
                                                                       source_size=source.size,
                                                                       source_dimnames=source.dimnames,
                                                                       target_index=target_index)

    def _update(self, key, forward=True, backward=False):
        """
        Update the NodeRun information and validity of the NodeRun and propagate
         the update downstream. Updates inputs, input groups, outputsize and outputs.

        A NodeRun is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.planning.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized
        """
        # Make sure the Inputs and input groups are up to date
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        if backward:
            for sourced_node in self.get_sourced_nodes():
                sourced_node.update(key, False, backward)

        for input_ in list(self.inputs.values()):
            input_.update(key, forward, backward)

        self.update_input_groups()
        self.input_group_combiner.update()

        # Update own status
        valid = True
        messages = []

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('[{}] Input {} is not valid: {}'.format(self.id, input_.id, message))

        for input_group in self.input_groups.values():
            if input_group.empty:
                valid = False
                messages.append('[{}] InputGroup {} is empty'.format(self.id, input_group.id))

        for id_, output in self.outputs.items():
            if output.resulting_datatype is not None and not issubclass(output.resulting_datatype, DataType):
                valid = False
                messages.append('[{}] Output {} cannot determine the Output DataType (got {}), please specify a '
                                'valid DataType or add casts to the Links'.format(self.id,
                                                                                  id_,
                                                                                  output.resulting_datatype))

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update all outputs
        for output in self.outputs.values():
            output.update(key, forward, backward)

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, False)
