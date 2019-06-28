# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute("""
    alter table print_style_recipes drop constraint print_style_recipes_pkey ;
    alter table print_style_recipes add constraint print_style_recipes_pkey
        PRIMARY KEY (print_style, tag);
    """)


def down(cursor):
    cursor.execute("""
    alter table print_style_recipes drop constraint print_style_recipes_pkey ;
    alter table print_style_recipes add constraint print_style_recipes_pkey
        PRIMARY KEY (print_style);
    """)
