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
"""knot_keystore.archive.local module."""

import logging
import os
import shutil
import stat

from knot_keystore.archive.base import ArchiveBase, with_encrypted_archive

log = logging.getLogger(__name__)


class ArchiveLocal(ArchiveBase):
    """Archive knot kasp-db to local filesystem."""

    @with_encrypted_archive
    def exec(self, ciphertext_path=None, key=None):
        """Execute archival proceedure."""
        log.debug(f"Trying to save encrypted archive to {self.path}")
        try:
            archive_path = shutil.copy(src=ciphertext_path, dst=self.path)
        except Exception as e:
            log.error(f"Failed to copy encrypted archive from \
                        {ciphertext_path}: {e}")
            raise e
        log.info(f"Encrypted archive written to {archive_path}")
        key_path = os.path.join(self.path, "kasp-db.key")
        log.debug("Trying to write encryption key to file")
        try:
            with open(key_path, "wb") as key_file:
                key_file.write(key)
            os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception as e:
            log.error(f"Failed to write encryption key to file: {e}")
            raise e
        log.info(f"Encryption key written to {key_path}")
        return
