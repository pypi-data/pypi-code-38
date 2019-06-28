# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute("""\
    ALTER TABLE print_style_recipes
       ADD COLUMN title text,
       ADD COLUMN commit_id text
       """)
    cursor.execute("""\
    ALTER TABLE default_print_style_recipes
       ADD COLUMN title text,
       ADD COLUMN commit_id text
       """)
    cursor.execute("""\
CREATE OR REPLACE FUNCTION update_default_recipes() RETURNS trigger AS $$
BEGIN
  IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') AND
          NEW.revised >= ((SELECT revised FROM print_style_recipes
              WHERE print_style = NEW.print_style ORDER BY revised DESC LIMIT 1)
              UNION ALL VALUES (NEW.revised) LIMIT 1) -- avoid compare to NULL
  THEN
      DELETE FROM default_print_style_recipes WHERE print_style = NEW.print_style;
      INSERT into default_print_style_recipes (
        print_style, title, tag, commit_id, fileid, recipe_type, revised)
    VALUES (
        NEW.print_style, NEW.title, NEW.tag, NEW.commit_id, NEW.fileid, NEW.recipe_type, NEW.revised);
  END IF;

  IF TG_OP = 'UPDATE' THEN
    PERFORM 1 from modules where recipe = OLD.fileid;
    IF FOUND and NEW.fileid != OLD.fileid THEN
        RAISE WARNING 'Cannot change recipe file: recipe in use';
        RETURN NULL;
    END IF;
    UPDATE default_print_style_recipes SET
      tag=NEW.tag,
      title=NEW.title,
      fileid=NEW.fileid,
      recipe_type=NEW.recipe_type
      WHERE print_style=NEW.print_style and revised=NEW.revised;
  END IF;

RETURN NEW;
END;

$$ LANGUAGE 'plpgsql';
""")
    cursor.execute("""\
CREATE OR REPLACE FUNCTION delete_from_default_recipes() RETURNS trigger AS $$
BEGIN
  PERFORM 1 FROM modules where recipe = OLD.fileid;
  IF FOUND THEN
    RAISE WARNING 'Cannot delete: recipe in use';
    RETURN NULL;
  ELSE
    DELETE FROM  default_print_style_recipes
      WHERE print_style=OLD.print_style and tag=OLD.tag;
    IF FOUND THEN
      INSERT into default_print_style_recipes (
          print_style, title, tag, commit_id, fileid, recipe_type, revised)
      SELECT
          print_style, title, tag, commit_id, fileid, recipe_type, revised
      from print_style_recipes where print_style=OLD.print_style
                                   and tag != OLD.tag
      order by revised desc LIMIT 1;
    END IF;
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE 'plpgsql';
""")
    cursor.execute("""\
DROP TRIGGER IF EXISTS delete_from_default_recipes
ON print_style_recipes;
CREATE TRIGGER delete_from_default_recipes
  BEFORE DELETE ON print_style_recipes FOR EACH ROW
  EXECUTE PROCEDURE delete_from_default_recipes();
""")


def down(cursor):
    cursor.execute("""\
    ALTER TABLE print_style_recipes
       DROP COLUMN title,
       DROP COLUMN commit_id
       """)
    cursor.execute("""\
    ALTER TABLE default_print_style_recipes
       DROP COLUMN title,
       DROP COLUMN commit_id
       """)
    cursor.execute("""\
CREATE OR REPLACE FUNCTION public.update_default_recipes()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') AND
          NEW.revised >= ((SELECT revised FROM print_style_recipes
              WHERE print_style = NEW.print_style ORDER BY revised DESC LIMIT 1)
              UNION ALL VALUES (NEW.revised) LIMIT 1)
  THEN
      DELETE FROM default_print_style_recipes WHERE print_style = NEW.print_style;
      INSERT into default_print_style_recipes (
        print_style, tag, fileid, recipe_type, revised)
    VALUES (
        NEW.print_style, NEW.tag, NEW.fileid, NEW.recipe_type, NEW.revised);
  END IF;

  IF TG_OP = 'UPDATE' THEN
      UPDATE default_print_style_recipes SET
        fileid=NEW.fileid,
        recipe_type=NEW.recipe_type,
        revised=NEW.revised
        WHERE print_style=NEW.print_style AND tag=NEW.tag;
  END IF;

RETURN NEW;
END;

$function$
""")
    cursor.execute("""\
CREATE OR REPLACE FUNCTION public.delete_from_default_recipes()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  DELETE FROM  default_print_style_recipes
    WHERE print_style=OLD.print_style and tag=OLD.tag;
  IF FOUND THEN
    INSERT into default_print_style_recipes (
        print_style, tag, fileid, recipe_type, revised)
    SELECT DISTINCT ON (print_style)
        print_style, tag, fileid, recipe_type, max(revised)
    from print_style_recipes where print_style=OLD.print_style
    order by revised desc;
  END IF;
  RETURN OLD;
END;
$function$
""")
    cursor.execute("""\
DROP TRIGGER IF EXISTS delete_from_default_recipes
ON print_style_recipes;
CREATE TRIGGER delete_from_default_recipes
  AFTER DELETE ON print_style_recipes FOR EACH ROW
  EXECUTE PROCEDURE delete_from_default_recipes();
""")
