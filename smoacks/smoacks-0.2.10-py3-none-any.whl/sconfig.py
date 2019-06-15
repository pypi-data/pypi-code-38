# sconfig.py - smoacks configuration file
import os
import yaml
import logging

structure_overrides = ['SMOACKS_ROOT']
parameters_overrides = ['SMOACKS_SOURCE_SPEC', 'SMOACKS_DEST_SPEC',
                        'SMOACKS_SERVER_CONTAINER_PORT', 'SMOACKS_INCLUDE_LOGIN']
env_defaults_overrides = ['SMOACKS_APP_NAME']

LOGGER = logging.getLogger('SMOACKS')

sconfig = None
custom_config = None

with open('conf/smoacks_default.yaml', 'r') as yaml_def_config:
    sconfig = yaml.load(yaml_def_config, Loader=yaml.FullLoader)

if os.path.isfile('conf/smoacks.yaml'):
    with open('conf/smoacks.yaml', 'r') as yaml_config:
        custom_config = yaml.load(yaml_config, Loader=yaml.FullLoader)
        if 'structure' in custom_config:
            sconfig['structure'].update(custom_config['structure'])
        if 'env_defaults' in custom_config:
            sconfig['env_defaults'].update(custom_config['env_defaults'])
        if 'parameters' in custom_config:
            sconfig['parameters'].update(custom_config['parameters'])

sconfig['env_defaults']['smoacks_app_name_c'] = sconfig['env_defaults']['smoacks_app_name'].upper()
sconfig['env_defaults']['smoacks_app_name_k'] = sconfig['env_defaults']['smoacks_app_name'].replace('_', '-')
# Promote spec name from parameters into env defaults so it can more easily
# be used in jinja templates during generation
sconfig['env_defaults']['dest_spec'] = sconfig['parameters']['dest_spec']

for ovr in structure_overrides:
    if ovr in os.environ:
        sconfig['structure'][ovr[8:].lower()] = os.environ[ovr]
for ovr in parameters_overrides:
    if ovr in os.environ:
        sconfig['parameters'][ovr[8:].lower()] = os.environ[ovr]
for ovr in env_defaults_overrides:
    if ovr in os.environ:
        sconfig['env_defaults'][ovr.lower()] = os.environ[ovr]

LOGGER.debug('SMOACKS configuration: {}'.format(str(sconfig)))
