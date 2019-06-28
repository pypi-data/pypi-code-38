# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute('''
CREATE OR REPLACE FUNCTION
 short_ident_hash(uuid uuid, major integer, minor integer)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
AS $$ select public.short_id(uuid) || '@' || concat_ws('.', major, minor) $$
''')


def down(cursor):
    cursor.execute('''
CREATE OR REPLACE FUNCTION
short_ident_hash(uuid uuid, major integer, minor integer)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
AS $$ select short_id(uuid) || '@' || concat_ws('.', major, minor) $$
''')
