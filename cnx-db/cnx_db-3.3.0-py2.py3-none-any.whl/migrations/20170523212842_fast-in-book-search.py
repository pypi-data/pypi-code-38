# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute('CREATE INDEX collated_fti_lexemes_context_item_idx '
                   'on collated_fti_lexemes (context, item)')


def down(cursor):
    cursor.execute('DROP INDEX collated_fti_lexemes_context_item_idx')
