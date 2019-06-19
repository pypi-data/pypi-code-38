import importlib
import sys
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
from logging_decorator import logging
import path_helpers as Ph
from config import Config

PRINT_ACTIONS = Config().get()["settings"]["debugging"]["print_actions"]

@logging
def __get_actions_list():
    actions_list = []
    all_action_files = []
    actions_paths = Ph.get_paths_for_plugin("actions")
    for actions_path in actions_paths:
        action_files = [f for f in listdir(actions_path) if isfile(join(actions_path, f))]
        if action_files and actions_path not in sys.path:
            sys.path.insert(0, actions_path)
            all_action_files.extend(action_files)
    for action_file in all_action_files:
        if Path(action_file).suffix.lower() == ".py" and action_file.lower() != "__init__.py":
            actions_list.append(Path(action_file).stem.lower())
    return actions_list

ACTIONS_LIST = __get_actions_list()

@logging
def run_action(action_name, args_dict):
    if PRINT_ACTIONS:
        print("Action: " + action_name + " args: " + str(args_dict))
    if action_name.lower() in ACTIONS_LIST:
        return __call_action_class(action_name, args_dict)
    else:
        raise TypeError("error: action: " + action_name + " is not a valid action")

@logging
def __call_action_class(action_name, args_dict):
    importlib.import_module(action_name)
    action = getattr(sys.modules[action_name], action_name)
    return action().run(**args_dict)
