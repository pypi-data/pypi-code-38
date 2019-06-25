# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import shutil

import sys

from ..utils import print_item, print_item_list, exit_with_error, print_message


def get_datasets_cmd(connection, args):
    # TODO: filtering
    datasets = connection.get_datasets()
    print_item_list(datasets, args)


def get_dataset_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)

    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))

    if args.out == "json":
        print_message(dataset.as_json())
    else:
        print_message(str(dataset))


def delete_dataset_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)
    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))
    dataset.delete()
    print_item(dataset, args)


def get_dataset_entities_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)

    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))

    # We must take care when printing out the entities, since it could be billions of them. We can't make a list and
    # print everything in one go, since that could take too much resources. Instead we get the raw byte-stream
    # from the server and copy it to sys.stdout.buffer. This is orders of magnitude faster than using the
    # print_message() function (or sys.stdout.write()) for each line.
    entities_stream = dataset.get_entities_as_stream(since=args.since, limit=args.limit, start=args.start,
                                                     history=args.history, deleted=args.deleted)
    shutil.copyfileobj(entities_stream, sys.stdout.buffer)
    sys.stdout.flush()


def get_dataset_entity_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)
    entity_id = args.entity_id

    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))

    entity = dataset.get_entity(entity_id)
    print_item(entity, args)
