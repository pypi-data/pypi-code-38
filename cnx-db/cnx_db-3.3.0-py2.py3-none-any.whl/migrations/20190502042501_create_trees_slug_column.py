# -*- coding: utf-8 -*-
"""\
Adds the 'slug' text column to the 'trees' table
"""
from dbmigrator import super_user


def up(cursor):
    # Add the new column to the trees table
    with super_user() as super_cursor:
        super_cursor.execute("ALTER TABLE trees ADD COLUMN slug text")


def down(cursor):
    # Drop the new column to the trees table
    with super_user() as super_cursor:
        super_cursor.execute("ALTER TABLE trees DROP COLUMN slug")
