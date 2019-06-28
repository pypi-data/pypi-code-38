# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute('ALTER TABLE persons ADD COLUMN passwd bytea, ADD COLUMN groups text[];')
    cursor.execute("""
CREATE OR REPLACE FUNCTION update_users_from_legacy ()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
BEGIN
UPDATE users
SET first_name = NEW.firstname,
    last_name = NEW.surname,
    full_name = NEW.fullname
WHERE username = NEW.personid;
RETURN NEW;
END;
$$;""")


def down(cursor):
    cursor.execute('ALTER TABLE persons DROP COLUMN passwd, DROP COLUMN groups;')
    cursor.execute("""
CREATE OR REPLACE FUNCTION update_users_from_legacy ()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
BEGIN
UPDATE users
SET first_name = NEW.firstname,
    last_name = NEW.surname,
    full_name = NEW.fullname
WHERE username = NEW.personid;
RETURN NULL;
END;
$$;""")
