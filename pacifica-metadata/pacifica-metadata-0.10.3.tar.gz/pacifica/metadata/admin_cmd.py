#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Admin Module for Admin Commands."""
from __future__ import print_function
from sys import argv as sys_argv
from datetime import timedelta
from json import loads, dumps
from argparse import ArgumentParser
from peewee import PeeweeException
from .orm.all_objects import ORM_OBJECTS
from .orm.sync import OrmSync, MetadataSystem


def render_obj(args):
    """Render an object based on args."""
    OrmSync.connect_and_check()
    test_obj = args.object()
    test_obj = args.object.get(
        test_obj.where_clause(args.where_clause)
    )
    print(
        dumps(
            test_obj.to_hash(recursion_depth=args.recursion),
            indent=4
        )
    )


def delete_obj(args):
    """Delete an object based on args."""
    OrmSync.connect_and_check()
    test_obj = args.object()
    args.where_clause['force'] = args.force
    args.where_clause['recursive'] = args.recursive
    # pylint: disable=protected-access
    test_obj._delete(**args.where_clause)
    # pylint: enable=protected-access


def create_table(args):
    """Create a specific object."""
    OrmSync.dbconn_blocking()
    if not args.object.table_exists():
        args.object.create_table()


def bool2cmdint(command_bool):
    """Convert a boolean to either 0 for true  or -1 for false."""
    if command_bool:
        return 0
    return -1


def dbchk(args):
    """Check the database for the version running."""
    OrmSync.dbconn_blocking()
    if args.check_equal:
        res = MetadataSystem.is_equal()
        OrmSync.close()
        return bool2cmdint(res)
    res = MetadataSystem.is_safe()
    OrmSync.close()
    return bool2cmdint(res)


def dbsync(_args=None):
    """Create or update the database."""
    OrmSync.dbconn_blocking()
    try:
        MetadataSystem.get_version()
    except PeeweeException:
        OrmSync.dbconn_blocking()
        OrmSync.create_tables()
        OrmSync.close()
        return
    OrmSync.update_tables()
    OrmSync.close()
    return


def create_subcommands(subparsers):
    """Create the subcommands from the subparsers."""
    create_table_parser = subparsers.add_parser(
        'create_table',
        help='create_table help',
        description='create table in the DB'
    )
    delete_obj_parser = subparsers.add_parser(
        'delete_obj',
        help='delete_obj help',
        description='delete an object in the DB'
    )
    render_parser = subparsers.add_parser(
        'render',
        help='render help',
        description='render and object from database w/o API'
    )
    db_parser = subparsers.add_parser(
        'dbsync',
        help='dbsync help',
        description='Update or Create the Database.'
    )
    dbchk_parser = subparsers.add_parser(
        'dbchk',
        help='dbchk help',
        description='Check database against current version.'
    )
    return (
        (render_parser, render_options),
        (create_table_parser, create_table_options),
        (delete_obj_parser, delete_obj_options),
        (db_parser, db_options),
        (dbchk_parser, dbchk_options)
    )


def db_options(db_parser):
    """Add the options for dbsync subcommand."""
    db_parser.set_defaults(func=dbsync)


def dbchk_options(dbchk_parser):
    """Add the options for dbchk."""
    dbchk_parser.add_argument(
        '--equal', default=False,
        dest='check_equal', action='store_true'
    )
    dbchk_parser.set_defaults(func=dbchk)


def objstr_to_timedelta(obj_str):
    """Turn an object string of the format X unit ago into timedelta."""
    value, unit, check = obj_str.split()
    assert check == 'ago'
    return timedelta(**{unit: float(value)})


def objstr_to_ormobj(obj_str):
    """Convert a string to an orm object or raise ValueError."""
    obj_strs = [obj.__name__ for obj in ORM_OBJECTS]
    if str(obj_str) not in obj_strs:
        raise ValueError('{} not a valid Metadata Object.'.format(obj_str))
    return [obj for obj in ORM_OBJECTS if obj.__name__ == str(obj_str)][0]


def objstr_to_whereclause(obj_str):
    """Convert a string to a where clause hash or raise ValueError."""
    json_obj = loads(obj_str)
    if not isinstance(json_obj, dict):
        raise ValueError('{} should be a dict not {}'.format(
            json_obj, type(json_obj)))
    return json_obj


def delete_obj_options(delete_obj_parser):
    """Delete the object command line options."""
    delete_obj_parser.add_argument(
        '--where-clause',
        dest='where_clause',
        type=objstr_to_whereclause,
        help='object where args query.',
        required=True
    )
    delete_obj_parser.add_argument(
        '--object-name',
        dest='object',
        type=objstr_to_ormobj,
        help='object type to query.',
        required=True
    )
    delete_obj_parser.add_argument(
        '--force',
        dest='force',
        default=False, action='store_true',
        help='force delete object.'
    )
    delete_obj_parser.add_argument(
        '--recursive',
        dest='recursive',
        default=False, action='store_true',
        help='recursive delete related objects.'
    )
    delete_obj_parser.set_defaults(func=delete_obj)


def create_table_options(create_table_parser):
    """Add the create object command line options."""
    create_table_parser.add_argument(
        '--object-name',
        dest='object',
        type=objstr_to_ormobj,
        help='object table to create.',
        required=True
    )
    create_table_parser.set_defaults(func=create_table)


def render_options(render_parser):
    """Add the essync command line options."""
    render_parser.add_argument(
        '--object-name',
        dest='object',
        type=objstr_to_ormobj,
        help='object type to query.',
        required=True
    )
    render_parser.add_argument(
        '--where-clause',
        dest='where_clause',
        type=objstr_to_whereclause,
        help='query to use.',
        required=True
    )
    render_parser.add_argument(
        '--recursion',
        default=1,
        dest='recursion',
        type=int,
        help='recursive level to go',
        required=False
    )
    render_parser.set_defaults(func=render_obj)


def main(*argv):
    """Main method for admin command line tool."""
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    for subparser, options_func in create_subcommands(subparsers):
        options_func(subparser)
    if not argv:  # pragma: no cover
        argv = sys_argv[1:]
    args = parser.parse_args(argv)
    return args.func(args)
