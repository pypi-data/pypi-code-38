from __future__ import print_function

import io
import logging
import os
import posixpath
import subprocess
import sys
import tarfile
from xml.etree import ElementTree

import docker

from build_utils import docker_utils, source_utils, utils
from build_utils.input_hash import InputHash

logger = logging.getLogger(__name__)

def build_generic_artifact(execution_context, artifact_name, source_dir, image,
        build_command='/bin/bash build.sh', artifact_path='artifact', artifact_extension=None,
        working_dir='/app/work'):
    input_hash = InputHash()

    input_hash.update_with_args((
        image,
        build_command,
        artifact_path,
        artifact_extension
    ))

    source_archive = source_utils.create_source_archive(execution_context, source_dir)
    input_hash.update_with_file(source_archive)

    if isinstance(image, dict):
        image_registry = execution_context.build_context.get_image_registry()
        ref_image_name = image['ref']
        _, parent_image_tag = execution_context.output['images'][ref_image_name].rsplit(':', 1)
        image = image_registry.pull_image(ref_image_name, parent_image_tag)
        input_hash.update_with_args((image,))

    artifact_store = execution_context.build_context.get_artifact_store()

    input_hash_digest = input_hash.get_hex_digest()
    if artifact_extension is not None:
        input_hash_digest = "{}.{}".format(input_hash_digest, artifact_extension)

    if artifact_store.has_artifact(artifact_name, input_hash_digest):
        print("Artifact {0} with input hash {1} already exists in store, skipping...".format(artifact_name, input_hash_digest))
        return {
            'files': {
                artifact_name: artifact_store.get_artifact_location(artifact_name, input_hash_digest)
            }
        }

    docker_client = docker.from_env(version='auto')

    container_create_args = dict(
        image=image,
        command="/bin/bash -c '{0}'".format(build_command),
        working_dir=working_dir
    )
    try:
        container = docker_client.containers.create(**container_create_args)
    except docker.errors.ImageNotFound:
        docker_client.images.pull(image)
        container = docker_client.containers.create(**container_create_args)

    try:
        container.put_archive(working_dir, source_archive)

        subprocess.check_call(['docker', 'start', '-a', container.id])

        tar_stream = container.get_archive(
            posixpath.join(working_dir, artifact_path))[0]
        tar_file_data = utils.read_file_stream(tar_stream)
        
        with tarfile.TarFile(fileobj=tar_file_data) as tar_file:
            artifact_file = tar_file.extractfile(os.path.basename(artifact_path))

            return {
                'files': {
                    artifact_name: artifact_store.store_artifact_fileobj(
                        artifact_file,
                        artifact_name,
                        input_hash_digest
                    )
                }
            }

    except:
        container.remove(v=True)
        raise

    container.remove(v=True)

# def _create_dir_archive(dir_path):
#     archive_buffer = io.BytesIO()
#     with tarfile.open(fileobj=archive_buffer, mode='w') as tar_file:
#         tar_info = tarfile.TarInfo(dir_path)
#         tar_info.type = tarfile.DIRTYPE
#         tar_file.addfile(tar_info)
#     archive_buffer.seek(0)
#     return archive_buffer
