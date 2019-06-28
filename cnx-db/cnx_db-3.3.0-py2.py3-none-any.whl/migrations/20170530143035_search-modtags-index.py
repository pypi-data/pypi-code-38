# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("SELECT 1 FROM pg_indexes "
                   "WHERE tablename  = 'moduletags' "
                   "AND indexname = 'moduletags_module_ident_idx'")
    if cursor.rowcount == 0:
        # FUTURE postgresql > 9.4 has "IF NOT EXISTS" for this case
        cursor.execute('CREATE INDEX moduletags_module_ident_idx '
                       'on moduletags (module_ident)')


def down(cursor):
    # FUTURE postgresql > 9.4 has "IF EXISTS" for this case
    cursor.execute('DROP INDEX moduletags_module_ident_idx')
