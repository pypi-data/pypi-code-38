# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""
-- Create a function that always returns the first non-NULL item
CREATE OR REPLACE FUNCTION first_agg ( anyelement, anyelement )
RETURNS anyelement LANGUAGE SQL IMMUTABLE STRICT AS $$
        SELECT $1;
$$;

-- And then wrap an aggregate around it
CREATE AGGREGATE FIRST (
        sfunc    = first_agg,
        basetype = anyelement,
        stype    = anyelement
);

-- Create a function that always returns the last non-NULL item
CREATE OR REPLACE FUNCTION last_agg ( anyelement, anyelement )
RETURNS anyelement LANGUAGE SQL IMMUTABLE STRICT AS $$
        SELECT $2;
$$;

-- And then wrap an aggregate around it
CREATE AGGREGATE LAST (
        sfunc    = last_agg,
        basetype = anyelement,
        stype    = anyelement
)""")


def down(cursor):
    cursor.execute("""
    DROP FUNCTION first_agg(anyelement, anyelement)  CASCADE;
    DROP FUNCTION last_agg(anyelement, anyelement)  CASCADE""")
