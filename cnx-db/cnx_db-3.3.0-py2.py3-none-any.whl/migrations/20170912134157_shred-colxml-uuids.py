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
        super_cursor.execute('drop function shred_collxml(text)')
        super_cursor.execute('drop function shred_collxml(int)')
        super_cursor.execute('drop function shred_collxml(int,int)')


def down(cursor):
    with super_user() as super_cursor:
        with open_here('shred_collxml_20170912134157_pre.sql', 'rb') as f:
            super_cursor.execute(f.read())
        super_cursor.execute('drop function shred_collxml(text, integer)')
        super_cursor.execute('drop function shred_collxml(integer, integer, bool)')
