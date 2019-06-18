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

import urllib.parse
import fastr
from fastr.data import url
from fastr.datatypes import URLType


class AnalyzeImageFile(URLType):
    description = 'Analyze Image file formate'
    extension = 'hdr'

    @classmethod
    def content(cls, invalue, outvalue=None):
        fastr.log.debug('Determining content of AnalyzeImageFile from invalue "{}" and outvalue "{}"'.format(invalue, outvalue))

        # The suffix translation table
        def substitute_extension(path):
            fastr.log.debug('Substituting: {}'.format(path))
            suffixes = {'.hdr.gz': '.img.gz', '.hdr': '.img'}

            for hdr_suffix, img_suffix in suffixes.items():
                if path.endswith(hdr_suffix):
                    return path[:-len(hdr_suffix)] + img_suffix
            raise ValueError('Extension is not valid for AnalyzeImageFile {}'.format(path))

        if url.isurl(invalue):
            parts = urllib.parse.urlparse(invalue)

            fastr.log.debug('input URL parts found: {}'.format(parts))
            path = substitute_extension(parts.path)

            in_img = urllib.parse.urlunparse((parts.scheme, parts.netloc, path, parts.params, parts.query, parts.fragment))
        else:
            in_img = substitute_extension(invalue)
            fastr.log.debug('input path found: {} -> {}'.format(invalue, in_img))

        if outvalue is not None:
            if url.isurl(outvalue):
                parts = urllib.parse.urlparse(outvalue)

                fastr.log.debug('output URL parts found: {}'.format(parts))
                path = substitute_extension(parts.path)

                out_img = urllib.parse.urlunparse((parts.scheme, parts.netloc, path, parts.params, parts.query, parts.fragment))
            else:
                out_img = substitute_extension(outvalue)
                fastr.log.debug('output path found: {} -> {}'.format(outvalue, out_img))

            contents = [(invalue, outvalue), (in_img, out_img)]
        else:
            contents = [invalue, in_img]

        return contents
