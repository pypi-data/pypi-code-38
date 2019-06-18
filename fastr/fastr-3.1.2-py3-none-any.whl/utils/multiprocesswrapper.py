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

import imp
import os
import fastr


def function_wrapper(filepath, fnc_name, *args, **kwargs):
    fastr.log.debug('Starting function wrapper: {} {}'.format(filepath, fnc_name))
    # Prepend filename so importing will be possible
    filebase, extension = os.path.splitext(os.path.basename(filepath))
    fastr.log.debug('Loading module with {} {}'.format(filebase, filepath))

    if extension == '.py':
        temp_module = imp.load_source(filebase, filepath)
    elif extension == '.pyc':
        temp_module = imp.load_compiled(filebase, filepath)
    else:
        message = 'File does not have correct extension, must be .py or .pyc (is {})!'.format(extension)
        fastr.log.critical(message)
        raise ValueError(message)

    if hasattr(temp_module, fnc_name):
        fnc = getattr(temp_module, fnc_name)
    else:
        fastr.log.critical('Cannot get pickled function!')
        raise ValueError('Function not found in file!')

    fastr.log.debug('Calling function')
    return fnc(*args, **kwargs)