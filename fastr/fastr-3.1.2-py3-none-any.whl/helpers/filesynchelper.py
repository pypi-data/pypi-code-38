# Copyright 2011-2017 Biomedical Imaging Group Rotterdam, Departments of
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
Some helper functions that aid with NFS file sync issues.
"""
from . import config, log
import time
import hashlib
import os.path
from glob import glob


def filesynchelper_enabled():
    return len(config.filesynchelper_url) > 0


if filesynchelper_enabled():
    from redis import Redis


class FileSyncHelper():
    _namespace = 'filesynchelper'
    _redis = Redis.from_url(config.filesynchelper_url) if filesynchelper_enabled() else None

    def __init__(self):
        pass

    def job_finished(self, jobfile):
        key = self._generate_key_for_string('joblock' + str(jobfile))
        self._redis.setex(key, '', 300)

    def wait_for_job(self, jobfile):
        key = self._generate_key_for_string('joblock' + str(jobfile))
        # wait for job or timeout
        timeoutafter = time.time() + 300
        exists = self._redis.exists(key)
        while not exists or time.time() > timeoutafter:
            time.sleep(5)  # wake-up every 5 seconds
            exists = self._redis.exists(key)
        self._redis.delete(key)

    def wait_for_pickle(self, url, timeout=300):
        log.debug('waiting for pickle {}'.format(url))
        # wait for file or timeout
        timeoutafter = time.time() + timeout
        exists = self.has_file_promise(url)
        while not exists or time.time() > timeoutafter:
            time.sleep(5)  # wake-up every 5 seconds
            exists = self.has_file_promise(url)

        return exists

    def store(self, url, data):
        key = self._generate_key_for_string(str(url))
        log.debug('storing {} -> {}'.format(url, key))
        self._redis.delete(key)
        return self._redis.setex(
            key,
            data,
            300
        )

    def load(self, url):
        key = self._generate_key_for_string(str(url))
        log.debug('loading {} from {}'.format(url, key))
        return self._redis.get(key)

    def _generate_key_for_string(self, input_string):
        return self._namespace + self._generate_hash_from_string(input_string)

    def _generate_hash_from_string(self, input_string):
        return hashlib.sha256(input_string).hexdigest()

    def make_file_promise(self, url):
        # ttl of 86400 seconds is 1 day
        # we don't really care about the value if suburls == None, thus an empty string is stored
        key = self._generate_key_for_string(url)
        log.debug('making file promise {} -> {}'.format(url, key))
        if os.path.isdir(url):
            dir = url
        elif url.startswith('vfs://') and os.path.isdir(fastr.vfs.url_to_path(url)):
            dir = fastr.vfs.url_to_path(url)
        else:
            dir = None

        if dir is not None:
            val = ','.join([self._generate_hash_from_string(str(suburl)) for suburl in self._glob_dir(dir)])
        else:
            val = ''

        self._redis.setex(
            key,
            val,
            300
        )

    def has_file_promise(self, url):
        # check if key exists, if it does we have a file promise
        result = self._redis.exists(self._generate_key_for_string(str(url)))
        log.debug('has_file_promise {} {} {}'.format(url, result, self._generate_key_for_string(str(url))))
        return result

    def wait_for_vfs_url(self, vfs_url, timeout=300):
        log.debug('wait_for_vfs_url {}'.format(vfs_url))
        suburls = self._get_suburl_hashes(vfs_url)
        return self._wait_for_file_and_suburls(fastr.vfs.url_to_path(vfs_url), suburls, timeout)

    def wait_for_file(self, path, timeout=300):
        log.debug('wait_for_file {}'.format(path))
        suburls = self._get_suburl_hashes(path)
        return self._wait_for_file_and_suburls(path, suburls, timeout)

    def _get_suburl_hashes(self, path):
        if self.has_file_promise(path):
            suburls = self._redis.get(self._generate_key_for_string(str(path)))
            if len(suburls) > 0:
                return suburls.split(',')
        return None

    def _glob_dir(self, dir):
        if not dir.endswith('/'):
            dir = dir + '/'
        return [y[len(dir):] for x in os.walk(dir) for y in glob(os.path.join(x[0], '*'))]

    def _wait_for_file_and_suburls(self, path, suburls, timeout):
        log.debug('waiting for {}'.format(path))
        # wait for file or timeout
        timeoutafter = time.time() + timeout
        fileexists = os.path.isfile(path)
        while not fileexists or time.time() > timeoutafter:
            time.sleep(5)  # wake-up every 5 seconds
            fileexists = (os.path.isdir(path) if suburls is not None else os.path.isfile(path))

        if suburls is not None:
            fileexists = False
            lookup = {}
            while len(suburls) > 0 or time.time() > timeoutafter:
                files = self._glob_dir(path)
                for file in files:
                    if file not in lookup:
                        lookup[file] = self._generate_hash_from_string(str(file))
                    if lookup[file] in suburls:
                        suburls.remove(lookup[file])
                time.sleep(5) # wake-up every 5 seconds

            if len(suburls) == 0:
                fileexists = True

        return fileexists
