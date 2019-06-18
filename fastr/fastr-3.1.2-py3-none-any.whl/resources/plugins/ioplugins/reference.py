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
This module contains the Null plugin for fastr
"""

import json
import os

import fastr
from fastr import types, resources
from fastr.core.ioplugin import IOPlugin
from fastr.data import url
from fastr.datatypes import TypeGroup, URLType


class Reference(IOPlugin):
    """
    The Reference plugin is create to handle ``ref://`` type or URLs. These
    URLs are to make the sink just write a simple reference file to the data.
    The reference file contains the DataType and the value so the result can
    be reconstructed. It for files just leaves the data on disk by reference.
    This plugin is not useful for production, but is used for testing purposes.
    """
    scheme = 'ref'

    def __init__(self):
        # initialize the instance and register the scheme
        super(Reference, self).__init__()

    def push_sink_data(self, value, outurl, datatype=None):
        """
        Write out the sink data from the inpath to the outurl.

        :param str value: the path of the data to be pushed
        :param str outurl: the url to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        fastr.log.info('Push sink called with: {}, {}'.format(value, outurl))
        self.setup()

        if datatype is None or issubclass(datatype, TypeGroup):
            previous_datatype = datatype.id if datatype is not None else None
            datatype = types.guess_type(value, options=datatype)
            fastr.log.info('Determined specific datatype as {} (based on {})'.format(datatype.id, previous_datatype))

        out_path = resources.ioplugins['vfs'].url_to_path(outurl, scheme='ref')
        out_dir = os.path.dirname(out_path)

        # Make sure the out directory exists or is created
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        if issubclass(datatype, URLType):
            # Set a target vfs in the output directory
            filename = url.basename(value)
            target_path = os.path.join(out_dir, filename)
            value_url = resources.ioplugins['vfs'].path_to_url(target_path)

            # Make sure data gets copied over correctly
            resources.ioplugins['vfs'].push_sink_data(value, value_url, datatype)

            # Set value to value_url now that the data has been pushed
            value = value_url

        result = {
            'value': value,
            'datatype': datatype.id
        }

        with open(out_path, 'w') as fh_out:
            json.dump(result, fh_out)
