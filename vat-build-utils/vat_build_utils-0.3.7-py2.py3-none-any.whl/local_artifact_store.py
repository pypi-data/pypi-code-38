import errno
import shutil
import os

import boto3
from botocore.exceptions import ClientError

class LocalArtifactStore(object):
    def __init__(self, config):
        self.path = config['path']

    def has_artifact(self, name, input_hash):
        artifact_path = self._get_artifact_path(name, input_hash)
        return os.path.isfile(artifact_path)

    def get_artifact_location(self, artifact_name, input_hash):
        # Not so easy to check if an S3 object at a key exists
        return {
            'type': 'local',
            'path': self._get_artifact_path(artifact_name, input_hash)
        }

    def store_artifact_file(self, file_path, artifact_name, input_hash):
        artifact_path = self._get_artifact_path(artifact_name, input_hash)

        shutil.copyfile(file_path, artifact_path)

        return {
            'type': 'local',
            'path': artifact_path
        }

    def store_artifact_fileobj(self, fileobj, artifact_name, input_hash):
        artifact_path = self._get_artifact_path(artifact_name, input_hash)
        artifact_dir_path = os.path.dirname(artifact_path)

        if not os.path.exists(artifact_dir_path):
            try:
                os.makedirs(artifact_dir_path)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(artifact_path, 'wb') as artifact_fileobj:
            shutil.copyfileobj(fileobj, artifact_fileobj)

        return {
            'type': 'local',
            'path': artifact_path
        }

    def _get_artifact_path(self, artifact_name, input_hash):
        return os.path.join(self.path, artifact_name, input_hash)
