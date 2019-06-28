# -*- coding: utf-8 -*-

from dbmigrator import super_user


def up(cursor):
    with super_user() as super_cursor:
        super_cursor.execute("""\
CREATE EXTENSION pg_trgm;
CREATE INDEX modules_strip_html_name_trgm_gin ON modules \
    USING gin(strip_html(name) gin_trgm_ops);
""")


def down(cursor):
    with super_user() as super_cursor:
        super_cursor.execute("""\
DROP INDEX IF EXISTS modules_strip_html_name_trgm_gin;
DROP EXTENSION IF EXISTS pg_trgm;
""")
