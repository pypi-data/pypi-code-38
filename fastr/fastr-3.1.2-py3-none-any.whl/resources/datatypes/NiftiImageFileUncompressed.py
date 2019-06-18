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
from fastr.datatypes import URLType


class NiftiImageFileUncompressed(URLType):
    description = 'Nifti Image File format'
    extension = 'nii'

    def _validate(self):
        parsed_value = self.parsed_value

        if self.extension and not parsed_value.endswith(self.extension):
            return False

        if not os.path.isfile(parsed_value):
            return False

        # Check magic bytes for Nifti-1 and Nifti-2 headers
        # type depends on header size and the both have magic bits for
        # identification
        with open(parsed_value, 'rb') as fin:
            header_size_bytes = fin.read(4)

            if len(header_size_bytes) != 4:
                return False

            header_size = int.from_bytes(header_size_bytes, 'little')
            if header_size not in [348, 540]:
                header_size = int.from_bytes(header_size_bytes, 'big')

            if header_size == 348:
                fin.seek(344)
                magic = fin.read(4)
                return magic == b'n+1\x00'
            elif header_size == 540:
                magic = fin.read(8)
                return magic == b'\x6E\x2B\x32\x00\x0D\x0A\x1A\x0A'
            else:
                return False
