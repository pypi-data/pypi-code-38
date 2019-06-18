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

from abc import ABCMeta

from .. import exceptions
from ..abc.serializable import Serializable
from ..abc.updateable import Updateable


class BaseNodeRun(Updateable, Serializable, metaclass=ABCMeta):
    NODE_RUN_TYPES = {}
    NODE_RUN_MAP = {}

    def __init_subclass__(cls, **kwargs):
        """
        Register nodes in class for easly location
        """
        name = cls.__name__
        cls.NODE_RUN_TYPES[name] = cls
        if name.endswith('Run'):
            key = name[:-3]
        else:
            raise exceptions.FastrValueError('Cannot determine matching Node class for this BaseNodeRun subclass.')

        cls.NODE_RUN_MAP[key] = cls
