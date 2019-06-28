# -*- coding: utf-8 -*-
"""Migrates the post_publication trigger function to use send a payload
with the notification.

"""


def up(cursor):
    cursor.execute("""\
CREATE OR REPLACE FUNCTION post_publication() RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('post_publication', '{"module_ident": '||NEW.module_ident||', "ident_hash": "'||ident_hash(NEW.uuid, NEW.major_version, NEW.minor_version)||'", "timestamp": "'||CURRENT_TIMESTAMP||'"}');
  RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';""")


def down(cursor):
    cursor.execute("""\
CREATE OR REPLACE FUNCTION post_publication() RETURNS trigger AS $$
BEGIN
  NOTIFY post_publication;
  RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';""")
