# -*- coding: utf-8 -*-
"""cnx-db subcommands"""
from __future__ import print_function
import sys

from ..scripting import prepare
from .discovery import register_subcommand


@register_subcommand('init')
def init_cmd(args_namespace):
    """initialize the database"""
    try:
        env = prepare()
    except RuntimeError as exc:
        if 'DB_URL' in exc.args[0]:
            print(exc.args[0], file=sys.stderr)
            return 4
        else:  # pragma: no cover
            raise
    from ..init import init_db, DBSchemaInitialized
    try:
        init_db(env['engines']['super'], False)
    except DBSchemaInitialized:
        print("Database is already initialized", file=sys.stderr)
        return 3
    return 0


@register_subcommand('venv')
def venv_cmd(args_namespace):
    """(re)initialize the venv within the database"""
    try:
        env = prepare()
    except RuntimeError as exc:
        if 'DB_URL' in exc.args[0]:
            print(exc.args[0], file=sys.stderr)
            return 4
        else:  # pragma: no cover
            raise
    from ..init import init_venv
    init_venv(env['engines']['super'])
    return 0
