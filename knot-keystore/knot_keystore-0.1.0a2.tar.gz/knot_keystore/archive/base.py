# Copyright (c) 2019 Workonline Communications (Pty) Ltd. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""knot_keystore.archive.base module."""

import functools
import hashlib
import logging
import os
import shutil
import tempfile

from cryptography.fernet import Fernet

from knot_keystore.knot import Knot

log = logging.getLogger(__name__)


def with_encrypted_archive(func):
    """Wrap the decorated function with archival and encryption."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        log.debug("Generating symetric encryption key")
        key = Fernet.generate_key()
        cipher = Fernet(key)
        log.debug("Creating temp directory")
        with tempfile.TemporaryDirectory() as tmp_path:
            log.debug(f"Working in {tmp_path}")
            cleartext_path, hash = self.get_cleartext_archive(tmp_path)
            ciphertext_path = f"{cleartext_path}.enc"
            log.debug("Trying to open cleartext archive for reading")
            try:
                with open(cleartext_path, "rb") as cleartext_file:
                    cleartext = cleartext_file.read()
            except Exception as e:
                log.error(f"Failed to read cleartext archive: {e}")
                raise e
            log.debug("Trying to encrypt archive")
            try:
                ciphertext = cipher.encrypt(cleartext)
            except Exception as e:
                log.error(f"Failed to encrypt archive: {e}")
                raise e
            log.debug("Trying to open ciphertext archive for writing")
            try:
                with open(ciphertext_path, "wb") as ciphertext_file:
                    ciphertext_file.write(ciphertext)
            except Exception as e:
                log.error(f"Failed to write cyphertext archive: {e}")
                raise e
            log.debug("Trying to call wrapped method")
            try:
                return func(self, *args, **kwargs,
                            ciphertext_path=ciphertext_path,
                            key=key)
            except Exception as e:
                log.error(f"Error during call to wrapped method: {e}")
                raise e
    return wrapper


class ArchiveBase(object):
    """Base class for archive plugins."""

    def __init__(self, knotc_socket=None, config=None, *args, **kwargs):
        """Initialise a new instance."""
        log.debug(f"Initialising archive plugin instance {self}")
        self._knotc_socket = knotc_socket
        if config is not None:
            for k, v in config.items():
                setattr(self, k, v)

    @property
    def knotc_socket(self):
        """Get knotc_socket property."""
        return self._knotc_socket

    def exec(self, ciphertext_path=None, key=None):  # pragma: no cover
        """Execute archival proceedure, overide in child classes."""
        raise NotImplementedError

    def get_cleartext_archive(self, tmp_path):
        """Create an archive of the knot kasp-db."""
        log.debug("Preparing to create temporary kasp-db archive")
        base_name = os.path.join(tmp_path, "kasp-db")
        with Knot(socket=self.knotc_socket) as knot:
            storage_path, kaspdb_dir = knot.kaspdb_path
            with knot.freeze():
                log.debug("Trying to create temporary kasp-db archive")
                try:
                    path = shutil.make_archive(base_name=base_name,
                                               format="xztar",
                                               root_dir=storage_path,
                                               base_dir=kaspdb_dir)
                except Exception as e:
                    log.error(f"Failed to create temp kasp-db archive: {e}")
                    raise e
                log.debug(f"Created temporary archive: {path}")
                log.debug("Calculating sha256 hash over archive contents")
                try:
                    hash = hashlib.sha256()
                    with open(path, "rb") as f:
                        for blk in iter(functools.partial(f.read, 4096), b""):
                            hash.update(blk)
                except Exception as e:
                    log.error(f"Failed to calculate hash over {path}: {e}")
                    raise e
        return path, hash.hexdigest()
