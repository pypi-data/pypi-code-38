# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import base64
import errno
import json
import os
import shutil

from tempfile import NamedTemporaryFile

CREDENTIALS_FILENAME = ".qfsd_cred"
CONTENT_TYPE_BINARY = "application/octet-stream"
CREDENTIALS_VERSION = 1

def encode_nonce(s):
    "Use web-safe base64 encoding without padding for simple nonce string"
    return base64.urlsafe_b64encode(s).strip("=")

class Credentials(object):
    # If you change the credential structure, bump CREDENTIALS_VERSION above!
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    @classmethod
    def from_login_response(cls, obj):
        return cls(bearer_token=obj.get('bearer_token', None))

    METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
    BINARY_METHODS = ("PATCH", "PUT", "POST")
    NO_CONTENT_METHODS = ("GET", "DELETE", "HEAD", "OPTIONS", "POST")

    def auth_header(self):
        return 'Bearer {}'.format(str(self.bearer_token))

def credential_store_filename():
    home = os.getenv("HOME")
    if not home:
        home = os.getenv("HOMEPATH")
    if not home:
        raise EnvironmentError(
            "Could not find HOME or HOMEPATH environment variable")

    path = os.path.join(home, CREDENTIALS_FILENAME)
    if os.path.isdir(path):
        raise EnvironmentError("Credentials store is a directory: %s" % path)
    return path

def remove_credentials_store(path):
    try:
        os.unlink(path)
    except EnvironmentError as e:
        if e.errno != errno.ENOENT:
            raise

def set_credentials(login_response, path):
    login_response["version"] = CREDENTIALS_VERSION
    cred_pre = os.path.basename(path) + '.'
    cred_dir = os.path.dirname(path)
    cred_tmp = NamedTemporaryFile(prefix=cred_pre, dir=cred_dir, delete=False)
    try:
        os.chmod(cred_tmp.name, 0o600)
        cred_tmp.write(json.dumps(login_response) + '\n')
        cred_tmp.flush()
        cred_tmp.close()
        shutil.move(cred_tmp.name, path)
    finally:
        # On windows, cred_tmp must be closed before it can be unlinked
        if not cred_tmp.close_called:
            cred_tmp.close()
        if os.path.exists(cred_tmp.name):
            os.unlink(cred_tmp.name)

def get_credentials(path):
    if not os.path.isfile(path):
        return None
    store = open(path, "r")
    if os.fstat(store.fileno()).st_size == 0:
        return None
    response = json.load(store)
    store.close()

    if response.get("version") != CREDENTIALS_VERSION:
        remove_credentials_store(path)
        return None

    return Credentials.from_login_response(response)
