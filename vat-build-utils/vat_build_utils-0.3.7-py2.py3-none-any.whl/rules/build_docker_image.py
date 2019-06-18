from __future__ import print_function

import os
import re

import docker

from build_utils import docker_utils, source_utils, utils
from build_utils.input_hash import InputHash

def build_docker_image(execution_context, image_name, path, include=None, dockerfile=None, parent_images=[]):
    input_hash = InputHash()

    input_hash.update_with_args((
        image_name,
        dockerfile
    ))

    source_archive = source_utils.create_source_archive(execution_context, source_path=path, include=include)
    input_hash.update_with_file(source_archive)

    image_registry = execution_context.build_context.get_image_registry()

    build_args = {}
    for parent_image_name in parent_images:
        _, parent_image_tag = execution_context.output['images'][parent_image_name].rsplit(':', 1)
        parent_image_ref = image_registry.pull_image(parent_image_name, parent_image_tag)
        build_args[_get_image_arg_name(parent_image_name)] = parent_image_ref

    input_hash.update_with_args(build_args)    

    tag = input_hash.get_hex_digest()
    full_tag = image_registry.get_full_image_tag(image_name, tag)

    docker_client = docker.from_env(version='auto')

    if not image_registry.has_image(image_name, tag):
        docker_utils.build_docker_image(
            docker_client.api,
            tag=full_tag,
            fileobj=source_archive,
            custom_context=True,
            dockerfile=dockerfile,
            forcerm=True,
            buildargs=build_args
        )

        image_registry.push_image(image_name, tag)

    else:
        print("Image {0} already exists in registry, skipping...".format(full_tag))

    return {
        "images": {
            image_name: full_tag
        }
    }

def _get_image_arg_name(image_name):
    return 'PI_{0}'.format(re.sub(r'\W+', '_', image_name).upper())
