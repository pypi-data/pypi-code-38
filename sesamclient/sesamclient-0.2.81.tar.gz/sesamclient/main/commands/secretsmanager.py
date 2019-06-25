# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import os
import json

from ..utils import print_item, exit_with_error, print_item_list


def get_secrets_cmd(connection, args):
    system_id = args.system_id
    if system_id:
        system = connection.get_system(system_id)
        if system is None:
            exit_with_error("No system with id '%s' was found!" % (args.system_id,))
        secrets_info = system.get_secrets()
    else:
        secrets_info = connection.get_secrets()
    print_item_list(secrets_info, args)


def put_secrets_cmd(connection, args):
    secrets_path = args.secrets_file

    if not os.path.exists(secrets_path):
        exit_with_error("The specified path '%s' doesn't exist!" % (secrets_path,))
    with open(secrets_path, "r", encoding="utf-8") as secrets_content:
        secrets = json.loads(secrets_content.read())

    system_id = args.system_id
    if system_id:
        system = connection.get_system(system_id)
        if system is None:
            exit_with_error("No system with id '%s' was found!" % (args.system_id,))
        secrets_info = system.put_secrets(secrets, args.dont_encrypt)
    else:
        secrets_info = connection.put_secrets(secrets, args.dont_encrypt)
    print_item(secrets_info, args)


def post_secrets_cmd(connection, args):
    secrets_path = args.secrets_file

    if not os.path.exists(secrets_path):
        exit_with_error("The specified path '%s' doesn't exist!" % (secrets_path,))
    with open(secrets_path, "r", encoding="utf-8") as secrets_content:
        secrets = json.loads(secrets_content.read())

    system_id = args.system_id
    if system_id:
        system = connection.get_system(system_id)
        if system is None:
            exit_with_error("No system with id '%s' was found!" % (args.system_id,))
        secrets_info = system.post_secrets(secrets, args.dont_encrypt)
    else:
        secrets_info = connection.post_secrets(secrets, args.dont_encrypt)
    print_item(secrets_info, args)


def delete_secret_cmd(connection, args):
    system_id = args.system_id
    if system_id:
        system = connection.get_system(system_id)
        if system is None:
            exit_with_error("No system with id '%s' was found!" % (args.system_id,))
        secret_info = system.delete_secret(args.secret_key)
    else:
        secret_info = connection.delete_secret(args.secret_key)
    print_item(secret_info, args)
