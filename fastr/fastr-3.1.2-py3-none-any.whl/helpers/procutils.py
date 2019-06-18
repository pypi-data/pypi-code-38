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


def which(name):
    """
    Find executable by name on the PATH, returns the executable that will be
     found in case it is used for a Popen call
     """
    mode = os.X_OK
    exts = os.environ.get('PATHEXT', '').split(os.pathsep)

    for path in os.environ.get('PATH', '').split(os.pathsep):
        path = os.path.join(path, name)

        if os.access(path, mode):
            return path

        for ext in exts:
            pathext = path + ext

            if os.access(pathext, mode):
                return path

    return None
