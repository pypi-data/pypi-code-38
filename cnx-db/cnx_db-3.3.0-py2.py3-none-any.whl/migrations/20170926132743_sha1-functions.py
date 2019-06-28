# -*- coding: utf-8 -*-

from dbmigrator import super_user
from psycopg2 import sql


def up(cursor):
    pg_user = cursor.connection.get_dsn_parameters()['user']
    with super_user() as super_cursor:
        super_cursor.execute("""\
            CREATE OR REPLACE FUNCTION sha1(file text)
             RETURNS text
             LANGUAGE plpythonu
             IMMUTABLE STRICT
            AS $function$
            import hashlib
            return hashlib.new('sha1', file).hexdigest()
            $function$;
            """)

        super_cursor.execute(sql.SQL('alter function sha1(text) owner to {}'
                                     ).format(sql.Identifier(pg_user)))

        super_cursor.execute("""\
            CREATE OR REPLACE FUNCTION sha1(f bytea)
             RETURNS text
             LANGUAGE plpythonu
            AS $function$
            import hashlib
            return hashlib.new('sha1',f).hexdigest()
            $function$
            """)

        super_cursor.execute(sql.SQL('alter function sha1(bytea) owner to {}'
                                     ).format(sql.Identifier(pg_user)))


def down(cursor):
    with super_user() as super_cursor:
        super_cursor.execute("DROP FUNCTION sha1(text)")
        super_cursor.execute("DROP FUNCTION sha1(bytea)")
