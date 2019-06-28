# -*- coding: utf-8 -*-


def up(cursor):
    # Do a blanket set to make sure everything has the ``trees.latest``
    # column set. This value should be True for all legacy content.
    cursor.execute("UPDATE trees SET latest = true")


def down(cursor):
    # No need for a rollback migration
    pass
