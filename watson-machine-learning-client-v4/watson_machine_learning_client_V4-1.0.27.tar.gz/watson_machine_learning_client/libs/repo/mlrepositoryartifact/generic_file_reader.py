################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import os
import shutil
import logging

from watson_machine_learning_client.libs.repo.mlrepository.artifact_reader import ArtifactReader
from watson_machine_learning_client.libs.repo.util.compression_util import CompressionUtil
from watson_machine_learning_client.libs.repo.util.unique_id_gen import uid_generate
from watson_machine_learning_client.libs.repo.util.library_imports import LibraryChecker
from watson_machine_learning_client.libs.repo.base_constants import *

logger = logging.getLogger('GenericFileReader')


class GenericFileReader(ArtifactReader):
    def __init__(self, compressed_archive_path):
        self.archive_path = compressed_archive_path

    def read(self):
        return self._open_stream()

    # This is a no. op. for GenericTarGZReader as we do not want to delete the
    # archive file.
    def close(self):
        pass

    def _open_stream(self):
        return open(self.archive_path, 'rb')

