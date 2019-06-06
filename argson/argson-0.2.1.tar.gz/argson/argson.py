import argparse
import json
import logging
import os
from typing import List, Tuple

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

DEFAULT_ARGUMENTS_FILE = "config/arguments.json"
DEFAULT_DEFAULTS_FILE = "config/defaults.json"
DEFAULT_SELF_FILE = "config/self.json"


def parse_file_and_arguments(config_file: str = DEFAULT_ARGUMENTS_FILE,
                             self_file: str = DEFAULT_SELF_FILE,
                             defaults_file: str = DEFAULT_DEFAULTS_FILE,
                             working_dir: str = os.getcwd(),
                             no_builtins: bool = False,
                             verbose: bool = False) -> object:
    argument_parser, remaining_args = parse_config_file(config_file,
                                                        self_file,
                                                        defaults_file,
                                                        working_dir,
                                                        no_builtins,
                                                        verbose)

    arguments = argument_parser.parse_args(remaining_args)
    return arguments


def parse_config_file(config_file: str = DEFAULT_ARGUMENTS_FILE,
                      self_file: str = DEFAULT_SELF_FILE,
                      defaults_file: str = DEFAULT_DEFAULTS_FILE,
                      working_dir: str = os.getcwd(),
                      no_builtins: bool = False,
                      verbose: bool = False) -> Tuple[argparse.ArgumentParser, List[str]]:
    builtin_parser, builtin_flags, remaining_args = parse_builtins(no_builtins,
                                                                   self_file,
                                                                   defaults_file)

    if no_builtins is False:
        defaults_file = builtin_flags.defaults_file
        self_file = builtin_flags.self_file
        verbose = builtin_flags.verbose

    defaults, self_info = [load_configuration_json(working_dir, file_name, verbose)
                           for file_name in [defaults_file, self_file]]
    argument_parser = get_argument_parser(
        builtin_parser, self_info, defaults, working_dir, config_file)
    return argument_parser, remaining_args


def parse_builtins(no_builtins, default_self_file, default_defaults_file) -> Tuple[
    argparse.ArgumentParser, object, List[str]]:
    config_file_parser = argparse.ArgumentParser(add_help=False)
    if no_builtins is False:
        config_file_parser.add_argument(
            "--defaults-file",
            type=str,
            help="sets file from which defaults are read",
            default=default_defaults_file)
        config_file_parser.add_argument(
            "--verbose",
            action="store_true",
            help="sets verbose mode")
        config_file_parser.add_argument(
            "--self-file",
            type=str,
            help="sets file containing self information. Exposes all configurations supported by argparse.ArgumentParser constructor",
            default=default_self_file)

    builtin_flags, remaining_args = config_file_parser.parse_known_args()
    return config_file_parser, builtin_flags, remaining_args


def get_argument_parser(builtin_parser, self_info, defaults, load_path, config_file) -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(parents=[builtin_parser],
                                              **self_info)
    argument_parser.set_defaults(**defaults)

    arguments_dict = load_configuration_json(
        load_path, config_file, strict=True)

    supported_types = {
        "float": float,
        "int": int,
        "str": str
    }

    for argument_config in arguments_dict:
        arg_flags = argument_config.pop("flags", None)

        if "type" in argument_config:
            if argument_config["type"] in supported_types:
                argument_config["type"] = supported_types.get(argument_config["type"])
            else:
                argument_config["type"] = globals()[argument_config["type"]]

        argument_parser.add_argument(
            *arg_flags, **argument_config)

    return argument_parser


def load_configuration_json(path, json_file, verbose: bool = False, strict: bool = False) -> dict:
    path_to_file = f"{path}/{json_file}"
    try:
        with open(path_to_file) as configuration_file:
            return json.load(configuration_file)
    except (FileNotFoundError, IsADirectoryError) as e:
        if strict:
            raise e
        if verbose:
            message = ''
            if isinstance(e, FileNotFoundError):
                message = f"cannot load file '{path_to_file}'"
            else:
                message = f"cannot load the directory '{path}' as file"
            print(f"[WARNING] {message}")
        return {}
