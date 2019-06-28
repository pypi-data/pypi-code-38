# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

from dbmigrator import super_user


@contextmanager
def open_here(filepath, *args, **kwargs):
    """open a file relative to this files location"""

    here = os.path.abspath(os.path.dirname(__file__))
    fp = open(os.path.join(here, filepath), *args, **kwargs)
    yield fp
    fp.close()


def up(cursor):
    with super_user() as super_cursor:
        with open_here('../archive-sql/schema/shred_collxml.sql', 'rb') as f:
            super_cursor.execute(f.read())


def down(cursor):
    with super_user() as super_cursor:
        with open_here('shred_collxml_20170922150407_pre.sql', 'rb') as f:
            super_cursor.execute(f.read())
