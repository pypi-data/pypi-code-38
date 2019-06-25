# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import json
import sys
import textwrap

import yaml
import os.path

from .. import entity_json


def print_message(message, file=None, indent=0):
    if message:
        if not message.endswith("\n"):
            message += "\n"
        if file is None:
            file = sys.stdout
        if indent:
            index_prefix = " " * indent
            message = textwrap.indent(message, index_prefix)
        file.write(message)
        file.flush()


def _exit(status=0, message=None):
    if message:
        print_message(message, sys.stderr)

    sys.exit(status)


def exit_with_error(message):
    if message:
        message = "error: " + message
    _exit(status=1, message=message)


def item_as_json_object(item):
    if isinstance(item, (str, int, float)):
        return item
    return item.as_json_object()


def print_item_list(itemlist, args):

    ids_only = getattr(args, "ids_only", False)
    if args.out == "json":
        if ids_only:
            json_object_list = [item.id for item in itemlist]
        else:
            json_object_list = [item_as_json_object(item) for item in itemlist]
        print_message(entity_json.entities_to_json(json_object_list, indent=4))

    elif args.out == "yaml":
        if ids_only:
            json_object_list = [item.id for item in itemlist]
        else:
            json_object_list = [item_as_json_object(item) for item in itemlist]

        print_message(yaml.dump(json_object_list))

    elif args.out == "plain":
        for item in itemlist:
            if ids_only:
                print_message(str(item.id))
            else:
                print_message(str(item))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def print_item(item, args):
    if isinstance(item, dict) or item is None:
        json_object = item
    else:
        json_object = item.as_json_object()

    if args.out == "json":
        print_message(entity_json.entities_to_json(json_object, indent=4))

    elif args.out == "yaml":
        print_message(yaml.dump(json_object))

    elif args.out == "plain":
        print_message(str(item))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def is_valid_configfile_name(filename):
    filename = os.path.basename(filename)
    return filename.endswith(".conf.json") or is_valid_but_deprecated_configfile_name(filename)


def is_valid_but_deprecated_configfile_name(filename):
    filename = os.path.basename(filename)
    return filename == "nodeconfig.json"
