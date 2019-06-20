import os
import argparse
from ruamel import yaml


def load_yaml(imput_file):
    with open(imput_file, "r") as input_stream:
        data = yaml.round_trip_load(input_stream, preserve_quotes=True)
    return data


def gen_dag_id(cwl_file):
    return os.path.splitext(os.path.basename(cwl_file))[0].replace(".", "_dot_")


def normalize_args(args, skip_list=[]):
    normalized_args = {}
    for key, value in args.__dict__.items():
        if value and key not in skip_list:
            normalized_args[key] = os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace(**normalized_args)


def get_folder(abs_path, permissions=0o0775, exist_ok=True):
    try:
        os.makedirs(abs_path, mode=permissions)
    except os.error as ex:
        if not exist_ok:
            raise
    return abs_path