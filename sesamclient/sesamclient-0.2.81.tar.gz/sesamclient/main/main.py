# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import argparse
import inspect
import json
import logging
import os.path
from html.parser import HTMLParser

import requests.exceptions
import sys

import time

from .commands.login import logout_cmd, login_cmd
from ..exceptions import PumpDoesNotSupportTheOperation, BadRequestException
from .commands.license import get_license_cmd, put_license_cmd
from .commands.config import config_cmd, get_configparser, get_configfilename
from .commands.datasets import delete_dataset_cmd, get_dataset_cmd, get_dataset_entities_cmd, \
    get_dataset_entity_cmd, get_datasets_cmd
from .commands.export import export_cmd
from .commands.import_cmd import import_cmd
from .commands.logs import get_log_content_cmd, get_logs_cmd
from .commands.secretsmanager import get_secrets_cmd, delete_secret_cmd, put_secrets_cmd, post_secrets_cmd
from .commands.envvarsmanager import get_env_vars_cmd, delete_env_var_cmd, put_env_vars_cmd, post_env_vars_cmd
from .commands.pipes import get_pipe_cmd, get_pipes_cmd, add_pipes_cmd, delete_pipe_cmd, \
    modify_pipe_cmd, get_pipe_schema_def_cmd
from .commands.pumps import disable_pump_cmd, enable_pump_cmd, get_pump_cmd, run_pump_operation_cmd, start_pump_cmd, \
    stop_pump_cmd, unset_last_seen_cmd, update_last_seen_cmd, wait_for_pump_to_finish_running_cmd
from .commands.systems import get_system_cmd, get_systems_cmd, add_systems_cmd, delete_system_cmd, modify_system_cmd
from .utils import exit_with_error
from .. import Connection
from .. import utils
from . import utils as main_utils
logger = logging.getLogger(__name__)


def get_parser_used_by_sphinx_argparse_extension():
    """This is the method that is used when autogeneration documentation with the sphinx argparse extension.
    It has a quirk (or bug?) that causes it to print an "Undocumented" message  for subparsers that don't have
    a "help"-parameter, even for subparsers that has a "description"-parameter. The "description"-parameter is the one
    that is actually displayed on the command line, so that is the one we want to use. But to get the sphinx-stuff to
    work we must specify the "help"-param instead of the "description"-param when we generate the parser the
    sphinx-stuff sees.
    """
    return get_parser(use_help_instead_of_description_for_subparsers=True)


def get_parser(use_help_instead_of_description_for_subparsers=False):
    parser_description = """
description:
    This is a command line tool for connecting to a Sesam installation and performing
    various operations.

    The root address of the Sesam installation rest api can be specified with the --"server_base_url"
    argument, or by by using the 'config' command to store the address persistently.

    To get detailed help for a command, add '-h' after the command, like this:
      %%(prog)s config -h

    (version: %s)
    """ % (utils.get_version(),)

    parser = argparse.ArgumentParser(description=parser_description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--loglevel",
        help="The loglevel to use. The default is 'WARNING'",
        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='WARNING')

    # We use a separate subparser for each command. Each subparser gets assigned a function that gets called
    # when the user specifies the command in the command line arguments. This main() function does all the common
    # setup, while the subparser-functions does all the command-specific stuff.
    subparsers = parser.add_subparsers(dest="command")

    # noinspection PyShadowingBuiltins
    def add_subparser(*args,
                      add_default_arguments=True,
                      add_default_arguments_for_list_commands=False,
                      add_default_output_format_argument=True,
                      help=None, description=None,
                      **kwargs):
        subparser_kwargs = dict(**kwargs)
        subparser_kwargs["help"] = help
        subparser_kwargs["description"] = description
        if use_help_instead_of_description_for_subparsers and (help is None):
            subparser_kwargs["help"] = description
            subparser_kwargs["description"] = None
        subparser = subparsers.add_parser(*args, **subparser_kwargs)

        if add_default_arguments:

            subparser.add_argument(
                "--server_base_url",
                metavar="<server base url>",
                help="""The server base url to use. If specified, this overrides any default value that has been set with the
                        'config' command. Example usage: --server_base_url http://localhost:10001/api""")

            subparser.add_argument(
                "--jwt",
                metavar="<jwt filename>",
                help="""Specify a file containg a JWT authorization token to use when talking to the server. If
                        specified, this overrides any JWT-token that has been stored as a result of a 'sesam login'
                        command. Example usage: --jwt ~/my_jwt_tokens/prodserver1.jwt""")

            subparser.add_argument(
                "--server_username",
                metavar="<username>",
                help="""The username to use when authenticating to the server. If specified, this overrides any default value
                        that has been set with the
                        'config' command. Example usage: --server_username olanorman""")

            subparser.add_argument(
                "--server_password",
                metavar="<password>",
                help="""The password to use when authenticating to the server. If specified, this overrides any default value
                        that has been set with the
                        'config' command. Example usage: --server_password verysecret""")

            subparser.add_argument(
                "--server_timeout",
                metavar="<timeout in seconds>",
                help="""The server timeout to use. If specified, this overrides any default value that has been set with the
                        'config' command. Example usage: --server_timeout 60""")

        if add_default_arguments and add_default_output_format_argument:
            subparser.add_argument(
                "--out",
                choices=['json', 'yaml', 'plain'],
                default='json',
                help="""The output format to use. The default format is 'json'.""")

        if add_default_arguments_for_list_commands:
            subparser.add_argument(
                "--ids-only",
                default=False,
                action='store_true',
                help="""If this is specified, only the id's of the items will be displayed.""")

        return subparser

    def add_force_config_argument(subparser):
        subparser.add_argument(
            "--force",
            default=False,
            action="store_true",
            help="Forces the server to accept configuration errors and do a best-effort attempt to apply the new "
                 "configuration. This is rarely a good idea.")

    # The "config"-command is used to set or get persistently stored configuration options (server root url, etc).
    configcmd_parser = add_subparser(
        "config",
        description="Gets or sets a config option.",
        add_default_arguments=False  # The config sub-command is special, and doesn't use the default args.
    )
    configcmd_parser.add_argument(
        "optionname", help="The config option to get or set",
        choices=["server.base_url",
                 "server.username",
                 "server.password",
                 "server.timeout",
                 ])
    configcmd_parser.add_argument(
        "optionvalue",
        help="If specified, the config option will be set to this value. "
             "If no value is specified, the current value will be displayed.",
        nargs=argparse.REMAINDER,
        default=None)
    configcmd_parser.set_defaults(subparser_func=config_cmd)

    get_pipes_parser = add_subparser(
        "get-pipes",
        description="Display a list of pipes",
        add_default_arguments_for_list_commands=True)
    get_pipes_parser.set_defaults(subparser_func=get_pipes_cmd)

    get_pipe_parser = add_subparser(
        "get-pipe",
        description="Display detailed information about the specified pipe")
    get_pipe_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    get_pipe_parser.set_defaults(subparser_func=get_pipe_cmd)

    get_pipe_schema_def_parser = add_subparser(
        "get-pipe-schema-definition",
        description="Generate a schema defintion for the pipe")
    get_pipe_schema_def_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    get_pipe_schema_def_parser.add_argument(
        "sample_size",
        help="The number of entities to sample for the schema.", default=1000)
    get_pipe_schema_def_parser.add_argument(
        "--keys_only",
        default=False,
        action="store_true",
        help="If set only returns the keys of the schema as an array.")

    get_pipe_schema_def_parser.set_defaults(subparser_func=get_pipe_schema_def_cmd)

    add_pipes_parser = add_subparser(
        "add-pipes",
        description="Add one or more new pipes",
        add_default_arguments_for_list_commands=True
    )
    add_pipes_parser.add_argument(
        "pipe_configurations",
        type=json.loads,
        help="A list of the configurations of the new pipes. Each pipe configuration should be a json-encoded dict on "
             "the same format as used when  defining a pipe in the sesam-node configuration file. "
             """Example: '[{"_id": "my_new_pipe", "type": "pipe", "short_config": "sql://Northwind/Customers"}]'
             """)
    add_force_config_argument(add_pipes_parser)
    add_pipes_parser.set_defaults(subparser_func=add_pipes_cmd)

    modify_pipe_parser = add_subparser(
        "modify-pipe",
        description="Modify a pipe by uploading a new configuration for the pipe")
    modify_pipe_parser.add_argument(
        "pipe_configuration",
        type=json.loads,
        help="The new configuration of the pipe. This should be a json object on the same format as used when "
             "defining a pipe in the sesam-node configuration file. The pipe to modify is specified by the '_id' "
             "attribute of the configuration. "
             """Example: '{"_id": "my_existing_pipe", "type": "pipe", "short_config": "sql://Northwind/Customers"}'"
             """)
    add_force_config_argument(modify_pipe_parser)
    modify_pipe_parser.set_defaults(subparser_func=modify_pipe_cmd)

    delete_pipe_parser = add_subparser(
        "delete-pipe",
        description="Deletes the specified pipe from the sesam-node")
    delete_pipe_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    delete_pipe_parser.set_defaults(subparser_func=delete_pipe_cmd)

    get_logs_parser = add_subparser(
        "get-logs",
        description="Display a list of logs",
        add_default_arguments_for_list_commands=True)
    get_logs_parser.set_defaults(subparser_func=get_logs_cmd)

    get_log_parser = add_subparser(
        "get-log",
        description="Display the content of the specified log")
    get_log_parser.add_argument(
        "log_id",
        help="The id of the log.")
    get_log_parser.set_defaults(subparser_func=get_log_content_cmd)

    get_systems_parser = add_subparser(
        "get-systems",
        description="Display a list of systems",
        add_default_arguments_for_list_commands=True)
    get_systems_parser.set_defaults(subparser_func=get_systems_cmd)

    get_system_parser = add_subparser(
        "get-system",
        description="Display detailed information about the specified system")
    get_system_parser.add_argument(
        "system_id",
        help="The id of the system.")
    get_system_parser.set_defaults(subparser_func=get_system_cmd)

    add_systems_parser = add_subparser(
        "add-systems",
        description="Add one or more new systems",
        add_default_arguments_for_list_commands=True
    )
    add_systems_parser.add_argument(
        "system_configurations",
        type=json.loads,
        help="A list of the configurations of the new systems. Each system configuration should be a json-encoded "
             "dict on the same format as used when  defining a system in the sesam-node configuration file. "
             """Example: '[{"_id": "my_new_system", "type": "system", "short_config": "sql://Northwind/Customers"}]'
             """)
    add_force_config_argument(add_systems_parser)
    add_systems_parser.set_defaults(subparser_func=add_systems_cmd)

    modify_system_parser = add_subparser(
        "modify-system",
        description="Modify a system by uploading a new configuration for the system")
    modify_system_parser.add_argument(
        "system_configuration",
        type=json.loads,
        help="The new configuration of the system. This should be a json object on the same format as used when "
             "defining a system in the sesam-node configuration file. The system to modify is specified by the '_id' "
             "attribute of the configuration. "
             """Example: '{"_id": "my_existing_system", "type": "system", "short_config": "sql://Northwind/Customers"}'"
             """)
    add_force_config_argument(modify_system_parser)
    modify_system_parser.set_defaults(subparser_func=modify_system_cmd)

    delete_system_parser = add_subparser(
        "delete-system",
        description="Deletes the specified system from the sesam-node")
    delete_system_parser.add_argument(
        "system_id",
        help="The id of the system.")
    delete_system_parser.set_defaults(subparser_func=delete_system_cmd)

    get_datasets_parser = add_subparser(
        "get-datasets",
        description="Display a list of datasets",
        add_default_arguments_for_list_commands=True)
    get_datasets_parser.set_defaults(subparser_func=get_datasets_cmd)

    get_dataset_parser = add_subparser(
        "get-dataset",
        description="Display detailed information about the specified dataset")
    get_dataset_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    get_dataset_parser.set_defaults(subparser_func=get_dataset_cmd)

    delete_dataset_parser = add_subparser(
        "delete-dataset",
        description="Deletes the specified dataset from the sesam-node")
    delete_dataset_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    delete_dataset_parser.set_defaults(subparser_func=delete_dataset_cmd)

    get_dataset_entities_parser = add_subparser(
        "get-dataset-entities",
        description="Returns the entities of the specified dataset")
    get_dataset_entities_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    get_dataset_entities_parser.add_argument(
        "--since",
        help="""The "since" parameter is the opaque value that can be used to efficiently skip already \
seen entities.""", default=None)
    get_dataset_entities_parser.add_argument(
        "--limit",
        help="""The "limit" parameter specifies the maximum number of entities to return. \
If this is not specified, all available entities are returned.""",
        default=None)
    get_dataset_entities_parser.add_argument(
        "--start",
        help="""The "start" parameter is a positive integer that specified how many entities to skip from the \
start of where the "since"-parameters starts. This is far less efficient than using the "since"-parameter, but it \
can be manually set in a gui to explore the dataset. NOTE: Clients should use the "since"-parameter whenever \
possible.""",
        default=0)
    get_dataset_entities_parser.add_argument(
        "--history",
        default=True,
        help="""If this is true (the default) all entities, including replaced ones, will be returned. \
    If this is false, only the latest version of the entities will be returned""")
    get_dataset_entities_parser.add_argument(
        "--deleted",
        default=True,
        help="""If this is True (the default) deleted entities will also be returned. \
                If this is False, only the non-deleted entities will be returned.""")
    get_dataset_entities_parser.set_defaults(subparser_func=get_dataset_entities_cmd)

    get_dataset_entity_parser = add_subparser(
        "get-dataset-entity",
        description="Returns the specified entity of the specified dataset")
    get_dataset_entity_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    get_dataset_entity_parser.add_argument(
        "entity_id",
        help="The id of the entity.")
    get_dataset_entity_parser.set_defaults(subparser_func=get_dataset_entity_cmd)

    get_pump_parser = add_subparser(
        "get-pump",
        description="Display detailed information about the pump in the specified pipe")
    get_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    get_pump_parser.set_defaults(subparser_func=get_pump_cmd)

    stop_pump_parser = add_subparser(
        "stop-pump",
        description="Stop the pump in the specified pipe")
    stop_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    stop_pump_parser.set_defaults(subparser_func=stop_pump_cmd)

    start_pump_parser = add_subparser(
        "start-pump",
        description="Run the pump in the speficied pipe")
    start_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    start_pump_parser.add_argument(
        "--allow-already-running-pump",
        default=False,
        action='store_true',
        help="This option will make the command ignore an already running pump. Normally, that is treated as an error.")
    start_pump_parser.add_argument(
        "--dont-wait-for-pump-to-start",
        default=False,
        action='store_true',
        help="This option will prevent the command from waiting for the pump to start before returning. This is useful "
             "for batch-operations where you want to schedule lots of pumps to run, but don't wait for the server to "
             "actually start them all.")
    start_pump_parser.add_argument(
        "--wait-timeout",
        dest="wait_timeout",
        default=0,
        type=int,
        help="If this is not zero (the default), the command will wait for the pump to finish running. "
             "If the pump hasn't stopped within the specified number of seconds, an error is raised.")
    start_pump_parser.set_defaults(subparser_func=start_pump_cmd)

    disable_pump_parser = add_subparser(
        "disable-pump",
        description="Disable the pump in the specified pipe")
    disable_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    disable_pump_parser.set_defaults(subparser_func=disable_pump_cmd)

    enable_pump_parser = add_subparser(
        "enable-pump",
        description="Enable the pump in the specified pipe")
    enable_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    enable_pump_parser.set_defaults(subparser_func=enable_pump_cmd)

    wait_for_pump_to_finish_running_parser = add_subparser(
        "wait-for-pump-to-finish-running",
        description="Wait for the pump in the specified pipe to finish running")
    wait_for_pump_to_finish_running_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    wait_for_pump_to_finish_running_parser.add_argument(
        "timeout",
        default=60,
        type=int,
        help="The maximum number of seconds to wait.")
    wait_for_pump_to_finish_running_parser.set_defaults(subparser_func=wait_for_pump_to_finish_running_cmd)

    unset_last_seen_parser = add_subparser(
        "unset-last-seen",
        description="Unset 'last seen' token on the specified pipe")
    unset_last_seen_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    unset_last_seen_parser.set_defaults(subparser_func=unset_last_seen_cmd)

    update_last_seen_parser = add_subparser(
        "update-last-seen",
        description="Update the 'last seen' token on the specified pipe")
    update_last_seen_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    update_last_seen_parser.add_argument(
        "last_seen",
        help="The new last change token. For sdshare-clients, this should be on the form: '2015-07-20T10:00:15Z'")
    update_last_seen_parser.set_defaults(subparser_func=update_last_seen_cmd)

    run_pump_operation_parser = add_subparser(
        "run-pump-operation",
        description="""This is a special generic command that runs the specified operation on the specified pipe.
The usecase is pipes that support operations that aren't part of the 'official'sesam-api, and operations that hasn't
yet gotten their own dedicated command in the command-line client.""")
    run_pump_operation_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    run_pump_operation_parser.add_argument(
        "operation",
        help="The operation to run.")
    run_pump_operation_parser.add_argument(
        "-d",
        action="append",
        metavar="<parametername>=<parametervalue>",
        dest="operation_parameters",
        help='A <parametername>=<parametervalue> pair. This option can be specified zero or more times. '
             'Example: -d last-seen="2015-07-20T10:00:15Z".')
    run_pump_operation_parser.set_defaults(subparser_func=run_pump_operation_cmd)

    export_parser = add_subparser(
        "export",
        description='Exports the complete configuration to a file called "sesam.conf.json" in the given "exportdir" '
                    'directory. If no directory is given then it will be written to the current directory.')
    export_parser.add_argument(
        "exportdir",
        default=".",
        nargs="?",
        help="The directory to put the configuration file(s) in. Defaults to the current directory.")
    export_parser.add_argument(
        "--export-filename",
        default=None,
        help="The filename to use when storing the configuration. Defaults to 'sesam.conf.json'. This option is mutually exclusive with the '--expand' option.")
    export_parser.add_argument(
        "--expand",
        default=False,
        action="store_true",
        help="Instead of writing the configuration to a JSON file, write it to multiple files.  This option is mutually exclusive with the '--export_filename' option.")
    export_parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="""Force a "yes" response to all interactive questions.""")
    export_parser.add_argument(
        "--dry-run",
        default=False,
        action="store_true",
        help="""Show which files would be overwritten, deleted or created if the export had run.""")
    export_parser.set_defaults(subparser_func=export_cmd)

    import_parser = add_subparser(
        "import",
        description='Imports the complete configuration from one or more files and or directories containing '
                    '"*.conf.json" files.')
    import_parser.add_argument(
        "config_file_or_folder",
        metavar="config-file-or-folder",
        nargs="+",
        help='One or more configfiles and/or directories containing one or more *.conf.json files.')
    import_parser.add_argument(
        "--dry-run",
        default=False,
        action="store_true",
        help="Show which files would be used if the import had been run, and which errors (if any) would have "
             "resulted.")
    add_force_config_argument(import_parser)
    import_parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help='If specified then the full details of any errors will be displayed. '
             '(By default only a short summary of the errors is shown)')
    import_parser.set_defaults(subparser_func=import_cmd)

    # License stuff

    get_license_parser = add_subparser(
        "get-license",
        description="Returns the current license info for the node")
    get_license_parser.set_defaults(subparser_func=get_license_cmd)

    put_license_parser = add_subparser(
        "put-license",
        description="Replaces the license for the node with the specified license key")
    put_license_parser.add_argument(
        "license_file",
        metavar="path-to-license-key",
        help='The file containing the license key.')
    put_license_parser.set_defaults(subparser_func=put_license_cmd)

    # Secrets manager

    # Get all secrets
    get_secrets_parser = add_subparser(
        "get-secrets",
        description="Returns the current secret for the node")
    get_secrets_parser.add_argument(
        "system_id",
        metavar="system-id",
        nargs="?",
        default=None,
        help='The id of the System to get the secrets from. If this parameter is omitted, the global secrets will '
             'returned.')
    get_secrets_parser.set_defaults(subparser_func=get_secrets_cmd)

    # Puts secrets file
    put_secrets_parser = add_subparser(
        "put-secrets",
        description="Updates the node secret manager with the contents of a key:secret JSON file")
    put_secrets_parser.add_argument(
        "system_id",
        metavar="system-id",
        nargs="?",
        default=None,
        help='The id of the System the secret(s) should apply to. If this parameter is omitted, the secret(s) will '
             'apply to all Systems.')
    put_secrets_parser.add_argument(
        "secrets_file",
        metavar="path-to-secrets-file",
        help='The file containing the secrets in JSON format.')
    put_secrets_parser.add_argument(
        "--dont_encrypt",
        default=False,
        action='store_true',
        help="Don't encrypt the secrets (for testing purposes).")
    put_secrets_parser.set_defaults(subparser_func=put_secrets_cmd)


    # Posts secrets file
    post_secrets_parser = add_subparser(
        "post-secrets",
        description="Updates the node secret manager with the contents of a key:secret JSON file")
    post_secrets_parser.add_argument(
        "system_id",
        metavar="system-id",
        nargs="?",
        default=None,
        help='The id of the System the secret(s) should apply to. If this parameter is omitted, the secret(s) will '
             'apply to all Systems.')
    post_secrets_parser.add_argument(
        "secrets_file",
        metavar="path-to-secrets-file",
        help='The file containing the secrets in JSON format.')
    post_secrets_parser.add_argument(
        "--dont_encrypt",
        default=False,
        action='store_true',
        help="Don't encrypt the secrets (for testing purposes).")
    post_secrets_parser.set_defaults(subparser_func=post_secrets_cmd)


    # Delete a secret
    delete_secret_parser = add_subparser(
        "delete-secret",
        description="Deletes the given secret from the node")
    delete_secret_parser.add_argument(
        "system_id",
        metavar="system-id",
        nargs="?",
        default=None,
        help='The id of the System the secret should deleted from. If this parameter is omitted, the secret will '
             'be deleted from the global secrets.')
    delete_secret_parser.add_argument(
        "secret_key",
        metavar="secret-key",
        help='The secret key to delete.')
    delete_secret_parser.set_defaults(subparser_func=delete_secret_cmd)

    # Env vars manager

    # Get all env vars
    get_env_vars_parser = add_subparser(
        "get-env-vars",
        description="Returns the current environment variables for the node")
    get_env_vars_parser.set_defaults(subparser_func=get_env_vars_cmd)

    # Put env vars file
    put_env_vars_parser = add_subparser(
        "put-env-vars",
        description="Replaces the contents of the node environment variable manager with the contents of a "
                    "environment-var:value JSON file")
    put_env_vars_parser.add_argument(
        "env_vars_file",
        metavar="path-to-env-vars-file",
        help='The file containing the environment variables in JSON format.')
    put_env_vars_parser.set_defaults(subparser_func=put_env_vars_cmd)

    # Post env vars file
    post_env_vars_parser = add_subparser(
        "post-env-vars",
        description="Updates the node environment variable manager with the contents of a "
                    "environment-var:value JSON file")
    post_env_vars_parser.add_argument(
        "env_vars_file",
        metavar="path-to-env-vars-file",
        help='The file containing the environment variables in JSON format.')
    post_env_vars_parser.set_defaults(subparser_func=post_env_vars_cmd)

    # Delete a env var
    delete_env_var_parser = add_subparser(
        "delete-env-var",
        description="Deletes the given environment variable from the node")
    delete_env_var_parser.add_argument(
        "env_var",
        metavar="env-var",
        help='The environment variable to delete.')
    delete_env_var_parser.set_defaults(subparser_func=delete_env_var_cmd)

    # log in to a sesam installation
    login_parser = add_subparser(
        "login",
        description="Log in to a sesam installation",
        add_default_output_format_argument=False)
    login_parser.set_defaults(subparser_func=login_cmd)

    # log out from a sesam installation
    logout_parser = add_subparser(
        "logout",
        description="Log out from a sesam installation",
        add_default_output_format_argument=False)
    logout_parser.set_defaults(subparser_func=logout_cmd)

    return parser


class BodyDataExtractingHTMLParser(HTMLParser):
    def error(self, message):
        self.parser_error_messages.append(message)

    def __init__(self):
        super().__init__()
        self.parser_error_messages = []
        self.is_inside_body_tag = False
        self.body_data = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.is_inside_body_tag = True

    def handle_endtag(self, tag):
        if tag == "body":
            self.is_inside_body_tag = False

    def handle_data(self, data):
        if self.is_inside_body_tag:
            data = data.strip()
            if data:
                if not data.endswith("."):
                    data += "."
                self.body_data.append(data)


def main():
    parser = get_parser()
    args = parser.parse_args()

    loglevel = {
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG}[args.loglevel]

    logging.basicConfig(level=loglevel,
                        format="%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s")

    logger.info("main() running")
    configfilename = get_configfilename()
    logger.info("Using config file '%s'" % (configfilename,))

    myconfigparser = get_configparser()
    sesamapi_base_url = myconfigparser.get("server",
                                           "base_url",
                                           fallback=getattr(args, "server_base_url", ""))

    logger.info("sesamapi_base_url: '%s'" % (sesamapi_base_url,))

    if hasattr(args, "subparser_func"):
        # A command was specified

        # check if the subparser_func wants a Connection parameter.
        argspec = inspect.getfullargspec(args.subparser_func)
        if argspec.args[0] == "connection":
            # Ok, this function wants a connection argument
            sesamapi_base_url = getattr(args, "server_base_url")
            if not sesamapi_base_url:
                sesamapi_base_url = myconfigparser.get("server", "base_url", fallback="")
            if not sesamapi_base_url:
                main_utils.print_message(
                    "No server base_url specified! Either use the 'sesam config server.base_url "
                    "<baseurl>' command to specify a default base_url, "
                    "or specify the base_url with the '--server_base_url' parameter. "
                    "Falling back to default value ('http://localhost:9042/api')",
                    file=sys.stderr)
                sesamapi_base_url = "http://localhost:9042/api"

            username = getattr(args, "server_username", myconfigparser.get("server", "username", fallback=""))
            password = getattr(args, "server_password", myconfigparser.get("server", "password", fallback=""))

            jwt_auth_token = None
            jwt_filename = args.jwt
            if jwt_filename:
                if not os.path.exists(jwt_filename):
                    exit_with_error("The file '%s' specified with the '--jwt' argument doesn't exist!" % (
                        jwt_filename,))

                try:
                    with open(jwt_filename, "r") as jwt_file:
                        jwt_auth_token = jwt_file.read().strip()

                except IOError as e:
                    exit_with_error("Failed to open the file '%s' specified with the '--jwt' argument: %s" % (
                        jwt_filename, e))

            if jwt_auth_token is None:
                # No jwt-file specified as an commandline argument, so check if we have one stored in the
                # configfile (as a result of an earlier 'sesam login' command).
                jwt_auth_token = myconfigparser.get("server", "jwt", fallback=None)
                got_jwt_from_commandline_argument = False
            else:
                got_jwt_from_commandline_argument = True

            if args.command in ("login", "logout"):
                # This command is special and does not use a jwt token.
                jwt_auth_token = None

            timeout = int(myconfigparser.get("server", "timeout", fallback="") or 30)
            connection = Connection(sesamapi_base_url=sesamapi_base_url,
                                    username=username,
                                    password=password,
                                    timeout=timeout,
                                    jwt_auth_token=jwt_auth_token
                                    )
            try:
                args.subparser_func(connection, args)

            except PumpDoesNotSupportTheOperation as e:
                # This happens if the user user has tried to perform some operation ("start", "stop", "enable",
                # "disable", "update-last-seen", etc) on a pump, but the pump doesn't support that operation.
                # Rather than have each command-function handle this exception on its own, we catch it here,
                # so that we only need to handle it in one common place.
                supported_operations = ["'%s'" % (operation, ) for operation in e.pump.supported_operations]
                if len(supported_operations) == 0:
                    supported_operations_msg = "It doesn't support any operations."
                elif len(supported_operations) == 1:
                    supported_operations_msg = "It only supports this operation: '%s'." % (supported_operations[0],)
                else:
                    two_last_operations_string = " and ".join(supported_operations[-2:])
                    all_operations_string = ", ".join(supported_operations[:-2] + [two_last_operations_string])
                    supported_operations_msg = "It only supports these operations: %s." % (all_operations_string,)

                exit_with_error(
                    "The pump doesn't support the '%s' operation. %s" % (
                        e.operation,
                        supported_operations_msg
                    ))

            except requests.exceptions.ConnectionError as e:
                exit_with_error(
                    "Failed to connect to the sesam installation at '%s'! The following error occurred: %s" % (
                        sesamapi_base_url, e))

            except BadRequestException as e:
                if e.response.status_code in (401, 403):
                    # The user is not authenticated or isn't allowed to perform some operation.

                    # The response from the server looks something like this:
                    #
                    #  <html>
                    #   <head>
                    #    <title>401 Unauthorized</title>
                    #   </head>
                    #   <body>
                    #    <h1>401 Unauthorized</h1>
                    #    This server could not verify that you are authorized to access the document you requested.  Either you supplied the wrong credentials (e.g., bad password), or your browser does not understand how to supply the credentials required.<br/><br/>
                    #  The user does not have the &#x27;Read configuration&#x27; permission.
                    #   </body>
                    #  </html>
                    #
                    # or like this:
                    #
                    #   <html>
                    #   <head>
                    #    <title>403 Forbidden</title>
                    #   </head>
                    #   <body>
                    #    <h1>403 Forbidden</h1>
                    #    Access was denied to this resource.<br/><br/>
                    #  The user does not have the &#x27;Read configuration&#x27; permission.
                    #   </body>
                    #  </html>
                    #
                    #
                    # or like this:
                    #
                    # {
                    #   status: 401,
                    #   type: "about:blank",
                    #   title: "Unauthorized",
                    #   detail: "The user does not have the 'Read configuration' permission."
                    # }
                    # We want to extract the text from the body-tag and display just that to the user.

                    from html.parser import HTMLParser
                    parser = BodyDataExtractingHTMLParser()
                    response_text = e.response.text
                    parser.feed(response_text)
                    error_message = " ".join(parser.body_data)
                    if parser.parser_error_messages or not error_message:
                        # This is not html, lets try parsing it as json
                        try:
                            response_json = e.response.json()
                            error_message = "Got a '%s %s' response: %s" % (response_json["status"], response_json["title"], response_json["detail"])
                        except:
                            # Failed to parse the reply message as either html or json. hmm. Lets just use the raw response text.
                            error_message = response_text
                    exit_with_error(error_message)

                # This is some other error
                raise

        else:
            # This function does not want a connection argument
            args.subparser_func(args)

    else:
        # no command was specified
        parser.print_usage()

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Sesam client only supports Python 3.x")
        sys.exit(1)

    main()
