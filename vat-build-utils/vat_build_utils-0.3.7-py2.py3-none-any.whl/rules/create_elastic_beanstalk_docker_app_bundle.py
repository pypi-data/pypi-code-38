from __future__ import print_function

import hashlib
import io
import json
import os
import zipfile

from build_utils import docker_utils, utils
from build_utils.input_hash import InputHash

def create_elastic_beanstalk_docker_app_bundle(
        execution_context, artifact_name, image_name, container_port):
    input_hash = InputHash()

    # Get image tag from the output of previously run rules
    image_tag = execution_context.output['images'][image_name]

    dockerrun_config = {
        "AWSEBDockerrunVersion": "1",
        "Image": {
            "Name": image_tag,
            "Update": "false"
        },
        "Ports": [
            {
                "ContainerPort": str(container_port)
            }
        ],
        "Logging": "/var/log/nginx"
    }
    input_hash.update_with_args(dockerrun_config)

    input_hash_digest = input_hash.get_hex_digest()

    artifact_store = execution_context.build_context.get_artifact_store()
    if artifact_store.has_artifact(artifact_name, input_hash_digest):
        print("Artifact {0} with input hash {1} already exists in store, skipping...".format(artifact_name, input_hash_digest))
        artifact_location = artifact_store.get_artifact_location(artifact_name, input_hash_digest)
    else:
        print("Storing artifact {0} with input hash {1}".format(artifact_name, input_hash_digest))

        artifact_fileobj = io.BytesIO()
        with zipfile.ZipFile(artifact_fileobj, 'w') as zip_file:
            zip_file.writestr(zipfile.ZipInfo('Dockerrun.aws.json'), json.dumps(dockerrun_config))
        artifact_fileobj.seek(0)
        artifact_location = artifact_store.store_artifact_fileobj(
            artifact_fileobj,
            artifact_name,
            input_hash_digest
        )

    return {
        'files': {
            artifact_name: artifact_location
        }
    }
