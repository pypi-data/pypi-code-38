# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli_common.ml_cli_error import MlCliError
from azureml._cli_common.cli_workspace import get_workspace
from azureml.core.image import Image
from azureml.core.model import Model
from azureml._model_management._constants import MODEL_METADATA_FILE_ID_KEY, IMAGE_METADATA_FILE_ID_KEY,\
    CLI_METADATA_FILE_WORKSPACE_KEY, CLI_METADATA_FILE_RG_KEY
from .iot_image import IotContainerImage
import json


def _parse_kv_list(kv_list, name):
    if not kv_list:
        return None

    kv_dict = dict()
    for kv in kv_list:
        if '=' not in kv:
            raise MlCliError('Error, %s must be entered in the following format: key=value' % name)
        key, value = kv.partition("=")[::2]
        key = key.strip()
        value = value.strip()
        if not key:
            raise MlCliError('Error, %s must be entered in the following format: key=value' % name)
        kv_dict[key] = value

    return kv_dict


def image_create_container(image_name, image_description, execution_script, architecture, dependencies, requirements,
                           docker_file, models, model_metadata_files, tags, properties, workspace_name, resource_group,
                           no_wait_flag, verbose, output_metadata_file):
    workspace = get_workspace(workspace_name, resource_group)

    tags_dict = _parse_kv_list(tags, "tags")
    properties_dict = _parse_kv_list(properties, "properties")

    if model_metadata_files:
        for model_meta_file in model_metadata_files:
            with open(model_meta_file, 'r') as infile:
                model_metadata = json.load(infile)
                if model_metadata[CLI_METADATA_FILE_WORKSPACE_KEY] != workspace.name or \
                        model_metadata[CLI_METADATA_FILE_RG_KEY] != workspace.resource_group:
                    raise MlCliError('Model metadata file "{}" contains information for a model in a workspace that '
                                     'does not match the one provided for Image creation. If the model specified in '
                                     'the file is intended to be used, please either register it in the workspace '
                                     'provided to this command, or specify the corresponding workspace to this '
                                     'command.'.format(model_meta_file))
                models.append(Model(workspace, model_metadata[MODEL_METADATA_FILE_ID_KEY]))

    image_config = IotContainerImage.image_configuration(execution_script, architecture, requirements, docker_file,
                                                         dependencies, tags_dict, properties_dict,
                                                         image_description)
    image = Image.create(workspace, image_name, models, image_config)

    if output_metadata_file:
        image_metadata = {IMAGE_METADATA_FILE_ID_KEY: image.id, CLI_METADATA_FILE_WORKSPACE_KEY: workspace_name,
                          CLI_METADATA_FILE_RG_KEY: resource_group}

        with open(output_metadata_file, 'w') as outfile:
            json.dump(image_metadata, outfile)

        print("Wrote JSON metadata to {}".format(output_metadata_file))

    if no_wait_flag:
        print('Image may take a few minutes to be created.')
        print('To see if your image is ready to use, run:')
        print('  az ml image show -n {}'.format(image.name))
    else:
        image.wait_for_creation(verbose)

        if image.creation_state.lower() != 'succeeded':
            raise MlCliError('Polling for Image creation ended in "{}" state. More information can be found here: {}\n'
                             'Image ID: {}\n'
                             'Workspace Name: {}\n'
                             'Resource Group: {}\n'
                             'Generated Dockerfile can be found here: {}'
                             .format(image.creation_state,
                                     image.image_build_log_uri,
                                     image.id,
                                     workspace_name,
                                     resource_group,
                                     image.generated_dockerfile_uri))

        print('Image ID: {}'.format(image.id))
        print('More details: \'az ml image show -i {}\''.format(image.id))
        print('Usage information: \'az ml image usage -i {}\''.format(image.id))

    return image.serialize(), verbose
