from __future__ import print_function

import os

from build_utils import docker_utils, source_utils, utils
from build_utils.input_hash import InputHash

def create_tar_archive(execution_context, artifact_name, source_dir):
    input_hash = InputHash()

    source_archive = source_utils.create_source_archive(execution_context, source_dir)
    input_hash.update_with_file(source_archive)

    input_hash_digest = input_hash.get_hex_digest()

    artifact_store = execution_context.build_context.get_artifact_store()
    if artifact_store.has_artifact(artifact_name, input_hash_digest):
        print("Artifact {0} with input hash {1} already exists in store, skipping...".format(
            artifact_name, input_hash_digest))
        artifact_location = artifact_store.get_artifact_location(artifact_name, input_hash_digest)
    else:
        print("Storing artifact {0} with input hash {1}".format(artifact_name, input_hash_digest))
        artifact_location = artifact_store.store_artifact_fileobj(
            source_archive,
            artifact_name,
            input_hash_digest
        )

    return {
        'files': {
            artifact_name: artifact_location
        }
    }
