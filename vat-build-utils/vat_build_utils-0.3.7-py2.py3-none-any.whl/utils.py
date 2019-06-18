import hashlib
import io
from itertools import chain, groupby
import json
import os
import posixpath
import sys
import uuid

import boto3

def get_file_dir_path(file_path):
    return os.path.dirname(os.path.abspath(file_path))

def read_text_file(file_path):
    with open(file_path, 'r') as text_file:
        file_data = text_file.read()

    return file_data

def write_text_file(file_path, data):
    with open(file_path, 'w') as text_file:
        text_file.write(data)

def store_artifact(store_config, data):
    store_type = store_config['type']

    content_hash = hashlib.sha256(data.read()).hexdigest()

    if store_type == 'local':
        dir_path = store_config['dir_path']

        file_path = os.path.join(dir_path, content_hash)
        with open(file_path) as artifact_file:
            artifact_file.write(data)

        return {
            'type': store_type,
            'path': file_path
        }

    elif store_type == 's3':
        s3 = boto3.resource('s3')

        bucket_name = store_config['bucket']
        prefix = store_config['prefix']

        artifact_object = s3.Object(bucket_name, posixpath.join(prefix, content_hash))
        data.seek(0)
        artifact_object.upload_fileobj(data)

        return {
            'type': store_type,
            'bucket': bucket_name,
            'key': artifact_object.key
        }

def compute_file_hash(fileobj):
    CHUNK_SIZE = 4096
    file_hash = hashlib.sha256()
    for chunk in iter(lambda: fileobj.read(CHUNK_SIZE), b""):
        file_hash.update(chunk)

    return file_hash.hexdigest()

def get_ssm_parameter_value(parameter_name):
    client = boto3.client('ssm')

    response = client.get_parameters(
        Names=[parameter_name],
        WithDecryption=True
    )

    parameters = response['Parameters']
    invalid_parameters = response['InvalidParameters']
    if len(parameters) != 1:
        raise RuntimeError(
            "Expected exactly one parameter. Invalid parameters: {0}".format(invalid_parameters))

    return parameters[0]['Value']

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

import collections

# Source: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def recursive_merge_dicts(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            recursive_merge_dicts(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]

def dump_config_to_hcl(cfg):
    """
    Dump a simple config object to a HCL string
    """
    def dump_to_hcl(val, indent_level):
        """
        Recursively dump a value to a HCL string
        """
        sub_indent_level = indent_level + 4
        if isinstance(val, dict):
            output = "{\n"
            for key, value in val.items():
                output = output + sub_indent_level * ' ' + '"{0}" = {1}\n'.format(key, dump_to_hcl(value, sub_indent_level))

            return output + indent_level * ' ' + "}"

        elif isinstance(val, list):
            output = "[\n"
            for item in val:
                output = output + sub_indent_level * ' ' + '{0},\n'.format(dump_to_hcl(item, sub_indent_level))
            return output + indent_level * ' ' + "]"

        elif isinstance(val, str) or isinstance(val, unicode):
            return json.dumps(val)

        else:
            raise RuntimeError("Values of type {0} not supported".format(type(val)))

    if not isinstance(cfg, dict):
        raise ValueError("Config object must be a dict")

    output = ""
    for key, value in cfg.items():
        output = output + '"{0}" = {1}\n'.format(key, dump_to_hcl(value, 0))

    return output

def read_file_stream(file_stream):
    data = io.BytesIO()
    for chunk in file_stream:
        data.write(chunk)
    data.seek(0)
    return data