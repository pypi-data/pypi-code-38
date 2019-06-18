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
from collections import OrderedDict

import sympy

from .flownoderun import FlowNodeRun
from .inputoutputrun import SourceOutputRun
from .job import SourceJob, JobState
from .. import exceptions
from ..core import vfs_plugin as vfs
from ..core.samples import SampleId, SampleItem, SampleIndex
from ..data import url
from ..datatypes import DataType, types
from ..helpers import log

__all__ = ['SourceNodeRun', 'ConstantNodeRun']


class SourceNodeRun(FlowNodeRun):
    """
    Class providing a connection to data resources. This can be any kind of
    file, stream, database, etc from which data can be received.
    """

    __dataschemafile__ = 'SourceNodeRun.schema.json'
    _OutputType = SourceOutputRun
    _JobType = SourceJob

    def __init__(self, node, parent):
        """ Instantiation of the SourceNodeRun.

        :param fastr.planning.node.Node node: The Node that this Run is based on.
        :param NetworkRun parent: The NetworkRun that this NodeRun belongs to
        :return: newly created sink node run
        """
        super(SourceNodeRun, self).__init__(node, parent)

        # Set the DataType
        self._input_data = None
        self._outputsize = None
        self.outputsize = 'N_{}'.format(self.id)

    def __eq__(self, other):
        """Compare two Node instances with each other. This function ignores
        the parent and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: NodeRun
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, SourceNodeRun):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['_parent']
        del dict_self['_status']
        del dict_self['_input_groups']
        del dict_self['_input_data']
        del dict_self['_outputsize']
        del dict_self['input_group_combiner']

        dict_other = dict(vars(other))
        del dict_other['_parent']
        del dict_other['_status']
        del dict_other['_input_groups']
        del dict_other['_input_data']
        del dict_other['_outputsize']
        del dict_other['input_group_combiner']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the SourceNodeRun

        :return: the state of the object
        :rtype dict:
        """
        state = super(SourceNodeRun, self).__getstate__()

        return state

    def __setstate__(self, state):
        """
        Set the state of the SourceNodeRun by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SourceNodeRun, self).__setstate__(state)

        self._input_data = None
        self._outputsize = None
        self.outputsize = 'N_{}'.format(self.id)

    @property
    def datatype(self):
        """
        The datatype of the data this source supplies.
        """
        return self.outputs['output'].datatype

    @property
    def sourcegroup(self):
        log.warning('[DEPRECATED] The sourcegroup property of the'
                    ' SourceNodeRun is deprecated and replaced by the'
                    ' nodegroup property of the NodeRun. Please use that'
                    ' property instead, it will have the same'
                    ' functionality')
        return self.nodegroup

    @property
    def dimnames(self):
        """
        Names of the dimensions in the SourceNodeRun output. These will be reflected
        in the SampleIdLists.
        """
        if self.nodegroup is not None:
            return self.nodegroup,
        else:
            return self.id,

    @property
    def output(self):
        """
        Shorthand for ``self.outputs['output']``
        """
        return self.outputs['output']

    @property
    def outputsize(self):
        """
        The size of output of this SourceNodeRun
        """
        return self._outputsize

    @outputsize.setter
    def outputsize(self, value):
        # it seems pylint does not realize this is part of a property
        # pylint: disable=arguments-differ
        if isinstance(value, str):
            self._outputsize = (sympy.symbols(value),)
        elif isinstance(value, int):
            self._outputsize = (value,)
        else:
            try:
                self._outputsize = [x if isinstance(x, int) else sympy.symbols(x.replace(' ', '_')) for x in value]
            except TypeError:
                raise exceptions.FastrTypeError('Not a valid input type')

    @property
    def valid(self):
        """
        This does nothing. It only overloads the valid method of NodeRun().
        The original is intended to check if the inputs are connected to
        some output. Since this class does not implement inputs, it is skipped.
        """
        return True

    def set_data(self, data, ids=None):
        """
        Set the data of this source node.

        :param data: the data to use
        :type data: dict, OrderedDict or list of urls
        :param ids: if data is a list, a list of accompanying ids
        """
        self._input_data = OrderedDict()

        # Check if data has key or generate keys
        log.debug('Storing {} (ids {}) in {}'.format(data, ids, self.fullid))
        if isinstance(data, OrderedDict):
            ids = [SampleId(x) for x in data.keys()]
            data = list(data.values())
        elif isinstance(data, dict):
            # Have data sorted on ids
            ids, data = list(zip(*sorted(data.items())))
            ids = [SampleId(x) for x in ids]
        elif isinstance(data, list):
            if ids is None:
                ids = [SampleId('id_{}'.format(k)) for k in range(len(data))]
            elif not isinstance(ids, list):
                raise exceptions.FastrTypeError('Invalid type! The ids argument should be a list that matches the data samples!')
        elif isinstance(data, tuple):
            # A single sample with cardinality
            ids = [SampleId('id_0')]
            data = [data]
        else:
            if isinstance(data, set):
                log.warning('Source data for {} is given as a set,'.format(self.fullid) +
                                  ' this is most probably a mistake and a list or dict should'
                                  ' be used instead')
            ids = [SampleId('id_0')]
            data = [data]

        log.debug('Set data in {} with {} (Type {})'.format(self.id, data, self.datatype))

        for key, value in zip(ids, data):
            if isinstance(value, tuple):
                self._input_data[key] = tuple(x if self.datatype.isinstance(x) else str(x) for x in value)
            else:
                self._input_data[key] = (value if self.datatype.isinstance(value) else str(value)),
            log.debug('Result {}: {} (Type {})'.format(key, self._input_data[key], type(self._input_data[key]).__name__))

        self.outputsize = len(self._input_data),

    def execute(self):
        """
        Execute the source node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        if not self.valid or self._input_data is None:
            msg = 'Cannot executed a SourceNodeRun that is not valid! Messages:\n{}'.format('\n'.join(self.messages))
            log.error(msg)
            raise exceptions.FastrValueError(msg)

        joblist = []

        for index, (sample_id, value) in enumerate(self._input_data.items()):
            sample_index = SampleIndex(index)

            if all(not url.isurl(x) for x in value):
                # A simple string should not be send to IOPlugin for procesing
                log.debug('No job needed for sample {} at {}'.format(sample_id, self.fullid))
                self.jobs[sample_id] = None
                output_value = []

                for subvalue in value:
                    # it appears pylint does not realize that self.datatype is a class
                    # pylint: disable=not-callable
                    if self.datatype.isinstance(subvalue):
                        output_value.append(subvalue)
                    else:
                        output_value.append(self.datatype(subvalue))

                self.outputs['output'][sample_id, sample_index + (0,)] = SampleItem(sample_index + (0,),
                                                                                    sample_id,
                                                                                    {0: tuple(output_value)},
                                                                                    set())

                # Broadcast fake job update?
                job = self.create_job(sample_id,
                                      sample_index,
                                      job_data={'input': value},
                                      job_dependencies=None)
                job.status = JobState.finished
            else:
                # We found an URL, should be
                log.debug('Spawning job for sample {} at {}'.format(sample_id, self.fullid))
                joblist.append(self.create_job(sample_id, sample_index, {'input': value}, []))

        self.drained = True
        yield joblist

    def create_job(self, sample_id, sample_index, job_data, job_dependencies, **kwargs):
        job = super(SourceNodeRun, self).create_job(sample_id, sample_index,
                                                    job_data, job_dependencies,
                                                    **kwargs)
        job._datatype = self.datatype.id
        return job

    def _wrap_arguments(self, job_data, sample_id, sample_index):
        """
        Wrap arguments into a list of tuples that the execution script can parse

        :param dict job_data: dictionary containing all input data for the job
        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the wrapped arguments in a tuple with the form ``(inputs, outputs)``

        .. note::
            For a SourceNodeRun this function adds a few default (hidden) arguments
        """
        log.debug('Wrapping SourceNodeRun with {}'.format(job_data))
        arguments = super(SourceNodeRun, self)._wrap_arguments(job_data, sample_id, sample_index)
        arguments[0]['input'] = job_data['input']
        arguments[0]['datatype'] = types['String'](self.datatype.id),
        arguments[0]['sample_id'] = types['String'](str(sample_id)),

        outputurl = url.join(self.parent.tmpurl, self.id, str(sample_id), 'result')
        outputpath = vfs.url_to_path(outputurl)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)
        arguments[0]['targetdir'] = types['Directory'](outputurl),

        return arguments

    def _update(self, key, forward=True, backward=False):
        """
        Update the NodeRun information and validity of the NodeRun and propagate
         the update downstream. Updates inputs, input_groups, outputsize and outputs.

        A NodeRun is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.planning.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized
        """
        # Make sure the Inputs and input groups are up to date
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        for input_ in self.inputs.values():
            input_.update(key)

        # Update own status
        valid = True
        messages = []

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('Input {} is not valid: {}'.format(id_, message))

        for input_group in self.input_groups.values():
            if input_group.empty:
                valid = False
                messages.append('InputGroup {} is empty'.format(input_group.id))

        for id_, output in self.outputs.items():
            if output.resulting_datatype is not None and not issubclass(output.resulting_datatype, DataType):
                valid = False
                messages.append(
                    'Output {} cannot determine the Output DataType (got {}), '
                    'please specify a valid DataType or add casts to the Links'.format(
                        id_, output.resulting_datatype))

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, backward)


class ConstantNodeRun(SourceNodeRun):
    """
    Class encapsulating one output for which a value can be set. For example
    used to set a scalar value to the input of a node.
    """

    __dataschemafile__ = 'ConstantNodeRun.schema.json'

    def __init__(self, node, parent):
        """
        Instantiation of the ConstantNodeRun.

        :param datatype: The datatype of the output.
        :param data: the prefilled data to use.
        :param id_: The url pattern.

        This class should never be instantiated directly (unless you know what
        you are doing). Instead create a constant using the network class like
        shown in the usage example below.

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.Network()
          >>> source = network.create_source(datatype=types['ITKImageFile'], id_='sourceN')

        or alternatively create a constant node by assigning data to an item in an InputDict:

        .. code-block:: python

          >>> node_a.inputs['in'] = ['some', 'data']

        which automatically creates and links a ConstantNodeRun to the specified Input
        """
        super(ConstantNodeRun, self).__init__(node, parent)
        self.set_data(node.data)
        self._data = node.data

    def __getstate__(self):
        """
        Retrieve the state of the ConstantNodeRun

        :return: the state of the object
        :rtype dict:
        """
        state = super(ConstantNodeRun, self).__getstate__()

        state['data'] = list(self._data.items())

        return state

    def __setstate__(self, state):
        """
        Set the state of the ConstantNodeRun by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(ConstantNodeRun, self).__setstate__(state)

        self._data = OrderedDict((SampleId(str(x) for x in key), tuple(str(x) for x in value)) for key, value in state['data'])
        self.set_data()  # Make sure that the output size etc gets set

    def set_data(self, data=None, ids=None):
        """
        Set the data of this constant node in the correct way. This is mainly
        for compatibility with the parent class SourceNodeRun

        :param data: the data to use
        :type data: dict or list of urls
        :param ids: if data is a list, a list of accompanying ids
        """
        # We have to arguments to match the superclas
        # pylint: disable=unused-argument
        if data is None and self.data is not None:
            self._input_data = self.data
        else:
            super(ConstantNodeRun, self).set_data(data, ids)

    @property
    def data(self):
        """
        The data stored in this constant node
        """
        return self._data

    def execute(self):
        """
        Execute the constant node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        # Make sure the data is set
        self.set_data()

        # Run as a normal SourceNode
        for joblist in super(ConstantNodeRun, self).execute():
            yield joblist
