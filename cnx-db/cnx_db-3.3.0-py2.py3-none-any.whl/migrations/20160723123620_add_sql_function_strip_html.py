# -*- coding: utf-8 -*-

from dbmigrator import super_user


def up(cursor):
    with super_user() as super_cursor:
        super_cursor.execute("""\
CREATE OR REPLACE FUNCTION strip_html(html_text TEXT)
  RETURNS text
AS $$
  import re
  return re.sub('<[^>]*?>', '', html_text, re.MULTILINE)
$$ LANGUAGE plpythonu IMMUTABLE;
    """)


def down(cursor):
    with super_user() as super_cursor:
        super_cursor.execute("DROP FUNCTION IF EXISTS strip_html(TEXT)")
