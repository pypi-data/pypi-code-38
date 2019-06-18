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

import gzip
import json
# Try to import the faster cPickle if available and fall back when needed
try:
    import pickle as pickle
except ImportError:
    import pickle
import os
import shutil
import time

from . import log
from .filesynchelper import FileSyncHelper, filesynchelper_enabled
from ..resources import tools


def load_gpickle(path, retry_scheme=None):
    if filesynchelper_enabled():
        file_sync_helper = FileSyncHelper()
        if file_sync_helper.has_file_promise(path):
            # If we use filesynchelper we don't care about the
            # pickle on the filesystem. Use the filesynchelper
            # cache instead.
            data = file_sync_helper.load(path)
            try:
                result = pickle.loads(data)
                return result
            except AttributeError as exception:
                # This is probably due to an Enum that is created on the fly
                # when a Tool is loaded
                log.warning('Cannot find attribute during unpickling,'
                             ' this is probably an extension type that'
                             'was created with an older fastr version, '
                             'attempting to populate resources and try '
                             'again. Original exception: {}'.format(exception))
                tools.populate()
                return pickle.loads(data)

    if retry_scheme is None:
        retry_scheme = (1, 3, 5)

    log.debug('Attempting to load {} with retry scheme {}'.format(path, retry_scheme))

    # Start with a non-delayed attempt
    retry_scheme = (0,) + tuple(retry_scheme)

    # Get the jobfile if given a job
    for attempt, delay in enumerate(retry_scheme, start=1):
        try:
            # Wait before trying to load the file
            log.debug('Attempt {} after {} seconds of delay'.format(attempt, delay))
            time.sleep(delay)

            try:
                with gzip.open(path, 'rb') as fh_in:
                    data = pickle.load(fh_in)
            except AttributeError as exception:
                # This is probably due to an Enum that is created on the fly
                # when a Tool is loaded
                log.warning('Cannot find attribute during unpickling,'
                            ' this is probably an extension type that'
                            'was created with an older fastr version, '
                            'attempting to populate resources and try '
                            'again. Original exception: {}'.format(exception))
                tools.populate()
                with gzip.open(path, 'rb') as fh_in:
                    data = pickle.load(fh_in)

            return data
        except Exception as exception:
            # Last retry failed
            if attempt == len(retry_scheme):
                raise exception


def save_gpickle(path, data):
    with gzip.open(path, 'wb') as fh_out:
        pickle.dump(data, fh_out)

        # Make sure the data gets flushed
        fh_out.flush()
        os.fsync(fh_out.fileno())

    if filesynchelper_enabled():
        file_sync_helper = FileSyncHelper()
        # if we use filesynchelper store the pickle
        # in there as well
        file_sync_helper.store(path, pickle.dumps(data))


def save_json(path, data, indent=2):
    with open(path, 'w') as fh_out:
        json.dump(data, fh_out, indent=indent)

        # Make sure the data gets flushed
        fh_out.flush()
        os.fsync(fh_out.fileno())

    if filesynchelper_enabled():
        FileSyncHelper().store(path, json.dumps(data))


def load_json(path):
    if filesynchelper_enabled():
        file_sync_helper = FileSyncHelper()
        if file_sync_helper.has_file_promise(path):
            return json.loads(file_sync_helper.load(path))

    with open(path, 'r') as in_fh:
        return json.load(in_fh)


def link_or_copy(source: str, destination: str):
    try:
        os.symlink(source, destination)
    except OSError:
        shutil.copy2(source, destination)

