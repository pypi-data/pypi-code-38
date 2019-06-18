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
import fastr
from fastr.core.version import Version
from fastr.data import url
from fastr.datatypes import URLType


class Directory(URLType):
    """
    DataType representing a directory.
    """
    description = 'A directory on the disk'
    extension = None

    def _validate(self):
        """
        Validate the value of the DataType.

        :return: flag indicating validity of Boolean
        :rtype: bool
        """
        value = self.value

        if url.isurl(self.value):
            value = url.get_path_from_url(value)

        try:
            return os.path.isdir(value)
        except ValueError:
            return False

    def __eq__(self, other):
        """
        Directories are equal by default as long as the validatity matches.

        :param Directory other: other to compare against
        :return: equality flag
        """
        return self.valid == other.valid

    def action(self, name):
        """
        This method makes sure the Directory exists. A Tool can indicate an
        action that should be called for an Output which will be called before
        execution.

        :param str name: name of the action to execute
        :return: None
        """
        if name is None:
            pass
        elif name == "ensure":
            if url.isurl(self.value):
                dir_name = url.get_path_from_url(self.value)
            else:
                dir_name = self.value

            fastr.log.debug('ensuring {} exists.'.format(dir_name))
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        else:
            fastr.log.warning("unknown action")
