import json
import os
import yaml

from easydict import EasyDict

from assemblyline.common.dict_utils import recursive_update


def get_classification(yml_config=None):
    from assemblyline.common.classification import Classification, InvalidDefinition

    if yml_config is None:
        yml_config = "/etc/assemblyline/classification.yml"

    classification_definition = {}
    default_file = os.path.join(os.path.dirname(__file__), "classification.yml")
    if os.path.exists(default_file):
        with open(default_file) as default_fh:
            default_yml_data = yaml.safe_load(default_fh.read())
            if default_yml_data:
                classification_definition.update(default_yml_data)

    # Load modifiers from the yaml config
    if os.path.exists(yml_config):
        with open(yml_config) as yml_fh:
            yml_data = yaml.safe_load(yml_fh.read())
            if yml_data:
                classification_definition = recursive_update(classification_definition, yml_data)

    if not classification_definition:
        raise InvalidDefinition('Could not find any classification definition to load.')

    return Classification(classification_definition)


def get_constants(json_constants=None):
    from assemblyline.common import constants

    if json_constants is None:
        json_constants = "/etc/assemblyline/constants.json"

    constants = {"FILE_SUMMARY": constants.FILE_SUMMARY,
                 "RECOGNIZED_TAGS": constants.RECOGNIZED_TAGS,
                 "RULE_PATH": constants.RULE_PATH,
                 "STANDARD_TAG_CONTEXTS": constants.STANDARD_TAG_CONTEXTS,
                 "STANDARD_TAG_TYPES": constants.STANDARD_TAG_TYPES
                 }
    #default_file = os.path.join(os.path.dirname(__file__), "constants.yml")
    '''if os.path.exists(default_file):
        with open(default_file) as default_fh:
            default_yml_data = yaml.safe_load(default_fh.read())
            if default_yml_data:
                constants.update(default_yml_data)'''

    # Load modifiers from the yaml constants
    if os.path.exists(json_constants):
        with open(json_constants) as yml_fh:
            yml_data = yaml.safe_load(yml_fh.read())
            if yml_data:
                constants = recursive_update(constants, yml_data)

    # Decode nested list into list of tuples for StringTable
    temp = {}
    stringtables = ["FILE_SUMMARY", "STANDARD_TAG_CONTEXTS", "STANDARD_TAG_TYPES"]
    for x in constants:
        if x in stringtables:
            temp_list = []
            for y in constants[x]:
                temp_list.append((str(y[0]), int(y[1])))
            temp[x] = temp_list

    temp['RECOGNIZED_TAGS'] = constants['RECOGNIZED_TAGS']
    constants = {'RECOGNIZED_TAGS': constants['RECOGNIZED_TAGS'],
                 'RULE_PATH': constants['RULE_PATH'],
                 'STANDARD_TAG_TYPES': temp['STANDARD_TAG_TYPES'],
                 'FILE_SUMMARY': temp['FILE_SUMMARY'],
                 'STANDARD_TAG_CONTEXTS': temp['STANDARD_TAG_CONTEXTS']
                 }

    return EasyDict(constants)
