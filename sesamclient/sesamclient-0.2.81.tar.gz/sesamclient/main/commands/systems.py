# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import pprint

from ..utils import print_item, print_item_list, exit_with_error
from ...exceptions import SystemAlreadyExists


def get_systems_cmd(connection, args):
    # TODO: filtering
    systems = connection.get_systems()
    print_item_list(systems, args)


def get_system_cmd(connection, args):
    system = connection.get_system(args.system_id)
    if system is None:
        exit_with_error("No system with id '%s' was found!" % (args.system_id,))
    print_item(system, args)


def add_systems_cmd(connection, args):
    try:
        systems = connection.add_systems(args.system_configurations, force=args.force)
        print_item_list(systems, args)
    except SystemAlreadyExists as e:
        exit_with_error("One or more of the systems already exist: %s" % (e,))


def modify_system_cmd(connection, args):
    system_config = args.system_configuration
    system_id = system_config.get("_id")
    if not system_id:
        exit_with_error("The system-configuration doesn't contain a '_id' attribute! system_config: \n%s" % (
            pprint.pformat(system_config),))

    system = connection.get_system(system_id)
    if system is None:
        exit_with_error("No system with id '%s' was found!" % (system_id,))

    system.modify(system_config, force=args.force)
    print_item(system, args)


def delete_system_cmd(connection, args):
    system = connection.get_system(args.system_id)
    if system is None:
        exit_with_error("No system with id '%s' was found!" % (args.system_id,))
    system.delete()
    print_item(system, args)
