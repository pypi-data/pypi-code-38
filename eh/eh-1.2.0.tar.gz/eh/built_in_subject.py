# Copyright (c) 2016 Justin L. Hammond
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os 

from eh import base_subject as base

class BuiltInSubjects(base.BaseSubject):
    versions = ['1.0']

    def __init__(self, path=None):
        super(BuiltInSubjects, self).__init__()
        paths = 'contrib/subjects'
        cur_path = os.path.dirname(__file__)
        target_path = os.path.join(cur_path, paths)
        if path is not None:
            target_path = path
        self.populate_subjects(target_path)
