import base64
import hashlib
import io
import json
import os
import posixpath
import shutil
import sys
import tarfile
import tempfile
import zipfile

import boto3
import docker

from build_utils import utils, docker_utils

DEFAULT_ZIPFILE_MODIFICATION_TIME = (2017, 1, 1, 0, 0, 0)

class BuildContext(object):
    def __init__(self, config):
        self.config = config

    def get_image_registry(self):
        registry_type = self.config['image_registry']['type']
        image_registry_config = self.config['image_registry'].get('config')

        if registry_type == 'ecr':
            from build_utils.ecr_registry import EcrRegistry
            return EcrRegistry(image_registry_config)
        elif registry_type == 'local':
            from build_utils.local_registry import LocalRegistry
            return LocalRegistry()
        else:
            raise RuntimeError("Invalid repository type: {0}".format(registry_type))

    def get_artifact_store(self):
        store_type = self.config['artifact_store']['type']
        artifact_store_config = self.config['artifact_store'].get('config')

        if store_type == 's3':
            from build_utils.s3_artifact_store import S3ArtifactStore
            return S3ArtifactStore(artifact_store_config)
        elif store_type == 'local':
            from build_utils.local_artifact_store import LocalArtifactStore
            return LocalArtifactStore(artifact_store_config)
        else:
            raise RuntimeError("Invalid artifact store type: {0}".format(store_type))

    def get_rule_config_value(self, key):
        return self.config['rule_config'][key]

def create_work_dir(parent_dir=None):
    return tempfile.mkdtemp(dir=parent_dir)

def copy_file_tree(src, dest):
    shutil.copytree(src, dest)

def copy_file_tree_prefix(src_root, dest_root, prefix_path):
    src = os.path.join(src_root, prefix_path)
    dest = os.path.join(dest_root, prefix_path)

    copy_file_tree(src, dest)

def copy_dockerignore(src_root, dest_root):
    shutil.copy(os.path.join(src_root, '.dockerignore'), os.path.join(dest_root, '.dockerignore'))

def read_tar_stream(tar_stream):
    tar_file_data = io.BytesIO()
    for chunk in tar_stream:
        tar_file_data.write(chunk)
    tar_file_data.seek(0)
    return tar_file_data
