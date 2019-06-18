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
A module that describes the interface of a Tool. It specifies how a set of
 input values will be translated to commands to be executed. This creates
 a generic interface to different ways of executing underlying software.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple
from typing import Dict, List, Optional, Tuple

from .samples import SampleId, SampleIndex
from .target import TargetResult
from ..abc.baseplugin import Plugin
from ..abc.serializable import Serializable
from .. import exceptions


# Simple containers for minial fields for the input and output specification
InputSpecBase = namedtuple('InputSpec', ['id',
                                         'cardinality',
                                         'datatype',
                                         'required',
                                         'description',
                                         'default',
                                         'hidden'])
OutputSpecBase = namedtuple('OutputSpec', ['id',
                                           'cardinality',
                                           'datatype',
                                           'automatic',
                                           'required',
                                           'description',
                                           'hidden'])


class InputSpec(InputSpecBase):
    """
    Class containing the information about an Input Specification, this is
    essentially a data class (but
    """
    def __new__(cls, id_, cardinality, datatype, required=False, description='', default=None, hidden=False):
        return super(InputSpec, cls).__new__(cls,
                                             id_,
                                             cardinality=cardinality,
                                             datatype=datatype,
                                             required=required,
                                             description=description,
                                             default=default,
                                             hidden=hidden)

    def asdict(self):
        return dict(self._asdict())


class OutputSpec(OutputSpecBase):
    """
    Class containing the information about an Output Specification, this is
    essentially a data class (but
    """
    def __new__(cls, id_, cardinality, datatype, automatic=True, required=False, description='', hidden=False):
        return super(OutputSpec, cls).__new__(cls,
                                              id_,
                                              cardinality=cardinality,
                                              datatype=datatype,
                                              automatic=automatic,
                                              required=required,
                                              description=description,
                                              hidden=hidden)

    def asdict(self):
        return dict(self._asdict())


class Interface(Plugin, Serializable, metaclass=ABCMeta):

    """
    Abstract base class of all Interfaces. Defines the minimal requirements for
    all Interface implementations.
    """

    @abstractmethod
    def execute(self, target, payload):
        """
        Execute the interface given the a target and payload. The payload
        should have the form::

            {
              'input': {
                'input_id_a': (value, value),
                'input_id_b': (value, value)
              },
              'output': {
                'output_id_a': (value, value),
                'output_id_b': (value, value)
              }
            }

        :param target: the target to call
        :param payload: the payload to use
        :returns: the result of the execution
        :rtype: (tuple of) InterfaceResult
        """

    @abstractproperty
    def expanding(self):
        """
        Indicates whether or not this Interface will result in multiple samples
        per run. If the flow is unaffected, this will be zero, if it is nonzero
        it means that number of dimension will be added to the sample array.
        """

    @abstractproperty
    def inputs(self):
        """
        OrderedDict of Inputs connected to the Interface. The format should be
        {input_id: InputSpec}.
        """

    @abstractproperty
    def outputs(self):
        """
        OrderedDict of Output connected to the Interface. The format should be
        {output_id: OutputSpec}.
        """

    @abstractmethod
    def __getstate__(self):
        """
        Retrieve the state of the Interface

        :return: the state of the object
        :rtype dict:
        """

    @abstractmethod
    def __setstate__(self, state):
        """
        Set the state of the Interface
        """

    @classmethod
    def test(cls):
        """
        Test the plugin, interfaces do not need to be tested on import
        """
        pass


class InterfaceResult(object):
    """
    The class in which Interfaces should wrap their results to be picked up by fastr
    """
    def __init__(self,
                 result_data: Dict,
                 target_result: TargetResult,
                 payload: Dict[str, Tuple],
                 sample_index: Optional[SampleIndex]=None,
                 sample_id: Optional[SampleId]=None,
                 errors: Optional[List]=None):
        if ((sample_index is None and sample_id is not None) or
           (sample_index is not None and sample_id is None)):
            raise exceptions.FastrValueError('An InterfaceResult needs both'
                                             ' sample_index and sample_id to'
                                             ' be set or neither of them set.')

        self.sample_index = sample_index
        self.sample_id = sample_id
        self.result_data = result_data
        self.target_result = target_result
        self.payload = payload
        self.errors = errors or []
