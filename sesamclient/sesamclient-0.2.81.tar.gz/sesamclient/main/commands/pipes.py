# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import pprint

from ..utils import print_item, print_item_list, exit_with_error
from ...exceptions import PipeAlreadyExists


def get_pipes_cmd(connection, args):
    # TODO: filtering
    pipes = connection.get_pipes()
    print_item_list(pipes, args)


def get_pipe_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    print_item(pipe, args)


def get_pipe_schema_def_cmd(connection, args):
    sample_size = args.sample_size
    keys_only = args.keys_only

    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    schema_def = connection.get_pipe_schema_def(args.pipe_id, sample_size, keys_only)
    print_item_list(schema_def, args)


def add_pipes_cmd(connection, args):
    try:
        pipes = connection.add_pipes(args.pipe_configurations, force=args.force)
        print_item_list(pipes, args)
    except PipeAlreadyExists as e:
        exit_with_error("One or more of the pipes already exist: %s" % (e,))


def modify_pipe_cmd(connection, args):
    pipe_config = args.pipe_configuration
    pipe_id = pipe_config.get("_id")
    if not pipe_id:
        exit_with_error("The pipe-configuration doesn't contain a '_id' attribute! pipe_config: \n%s" % (
            pprint.pformat(pipe_config),))

    pipe = connection.get_pipe(pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (pipe_id,))

    pipe.modify(pipe_config, force=args.force)
    print_item(pipe, args)


def delete_pipe_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    pipe.delete()
    print_item(pipe, args)
