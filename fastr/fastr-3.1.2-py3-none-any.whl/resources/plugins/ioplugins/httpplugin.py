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

from fastr import exceptions
from fastr.core.ioplugin import IOPlugin

import requests


CHUNK_SIZE = 524288

class HTTPPlugin(IOPlugin):
    """
    .. warning::
        This Plugin is still under development and has not been tested at all.
        example url: https://server.io/path/to/resource
    """
    scheme = ('https', 'http')

    def __init__(self):
        super(HTTPPlugin, self).__init__()

    def fetch_url(self, inurl, outpath):
        """
        Download file from server.

        :param inurl: url to the file.
        :param outpath: path to store file
        """
        response = requests.get(inurl, allow_redirects=True, stream=True, timeout=60)

        # For download (GET) response should be 200
        if response.status_code != 200:
            raise exceptions.FastrDataTypeValueError(
                "Problem downloading the file, HTTP status code {}".format(response.status_code)
            )

        # Write download stream to file
        with open(outpath, 'wb') as output_file:
            for chunk in response.iter_content(CHUNK_SIZE):
                output_file.write(chunk)

        return outpath
