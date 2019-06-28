# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""\
CREATE OR REPLACE FUNCTION plainto_or_tsquery (TEXT) RETURNS tsquery AS $$
  SELECT to_tsquery( regexp_replace( $1, E'[\\\\s\\'|:&()!]+','|','g') );
$$ LANGUAGE SQL STRICT IMMUTABLE;
""")


def down(cursor):
    cursor.execute("DROP FUNCTION plainto_or_tsquery (TEXT)")
