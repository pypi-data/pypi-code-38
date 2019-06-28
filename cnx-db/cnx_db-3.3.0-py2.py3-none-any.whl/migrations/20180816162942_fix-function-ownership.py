# -*- coding: utf-8 -*-
from dbmigrator import super_user


def up(cursor):
    cursor.execute('SELECT current_user')
    username = cursor.fetchall()[0][0]
    with super_user() as super_cursor:
        super_cursor.execute('''
ALTER FUNCTION ident_hash (uuid, integer, integer) OWNER TO {user};
ALTER FUNCTION is_baked (uuid, text) OWNER TO {user};
ALTER FUNCTION short_ident_hash (uuid, integer, integer) OWNER TO {user};
ALTER FUNCTION shred_collxml (integer, integer, boolean) OWNER TO {user};
ALTER FUNCTION shred_collxml (text, integer) OWNER TO {user};
ALTER FUNCTION strip_html (text) OWNER TO {user};
ALTER FUNCTION subcol_uuids (uuid, text) OWNER TO {user};
ALTER FUNCTION uuid5 (uuid, text) OWNER TO {user};
'''.format(user=username))


def down(cursor):
    # TODO rollback code
    pass
