"""
Methods the Data Store import process
"""
import json

from propargs import property_file

def set_props_from_ds(prop_args):
    if prop_args.ds_file:
        ds_dict = _open_file_as_json(prop_args.ds_file)
        property_file.set_props_from_dict(prop_args, ds_dict)


def _open_file_as_json(ds_file):
    with open(ds_file, 'r') as f:
        ds_dict = json.load(f)
    return ds_dict