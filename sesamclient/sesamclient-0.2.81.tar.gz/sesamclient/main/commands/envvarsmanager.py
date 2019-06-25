# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import os
import json

from ..utils import print_item, exit_with_error


def get_env_vars_cmd(connection, args):
    env_vars_info = connection.get_env_vars()
    print_item(env_vars_info, args)


def put_env_vars_cmd(connection, args):
    env_vars_path = args.env_vars_file

    if not os.path.exists(env_vars_path):
        exit_with_error("The specified path '%s' doesn't exist!" % (env_vars_path,))
    with open(env_vars_path, "r", encoding="utf-8") as env_vars_content:
        env_vars_info = connection.put_env_vars(json.loads(env_vars_content.read()))
        print_item(env_vars_info, args)


def post_env_vars_cmd(connection, args):
    env_vars_path = args.env_vars_file

    if not os.path.exists(env_vars_path):
        exit_with_error("The specified path '%s' doesn't exist!" % (env_vars_path,))
    with open(env_vars_path, "r", encoding="utf-8") as env_vars_content:
        env_vars_info = connection.post_env_vars(json.loads(env_vars_content.read()))
        print_item(env_vars_info, args)


def delete_env_var_cmd(connection, args):
    env_vars_info = connection.delete_env_var(args.env_var)
    print_item(env_vars_info, args)
