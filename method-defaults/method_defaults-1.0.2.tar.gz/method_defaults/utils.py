import tempfile
import json
import yaml

import configobj


def jsonfile_to_dict(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def yamlfile_to_dict(filepath):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    return data


def convert_jsonfile_to_ini(filepath):
    data = jsonfile_to_dict(filepath)
    config = configobj.ConfigObj()
    config.update(data)
    fdata = config.write()
    buf = write_tempfile(fdata)
    return buf


def convert_yamlfile_to_ini(filepath):
    data = yamlfile_to_dict(filepath)
    config = configobj.ConfigObj()
    config.update(data)
    fdata = config.write()
    buf = write_tempfile(fdata)
    return buf


def write_tempfile(data):
    fp = tempfile.TemporaryFile(mode='w+')
    if isinstance(data, list):
        data = "\n".join(data)
    fp.write(data)
    fp.seek(0)
    return fp
