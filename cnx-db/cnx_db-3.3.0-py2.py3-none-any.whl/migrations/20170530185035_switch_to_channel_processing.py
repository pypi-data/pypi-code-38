# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("DROP TABLE post_publications")
    cursor.execute("""\
CREATE TABLE document_baking_result_associations (
  -- This associates the modules.module_ident with the celery result id.
  "module_ident" INTEGER NOT NULL,
  -- We loosely associate the result_id, because it could be in the database
  -- or in some other storage service depending on the configuration.
  "result_id" UUID NOT NULL,
  "created" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("module_ident", "result_id"),
  FOREIGN KEY ("module_ident") REFERENCES modules ("module_ident")
);
""")


def down(cursor):
    cursor.execute("DROP TABLE document_baking_result_associations")
    cursor.execute("""\
CREATE TABLE post_publications (
  "module_ident" INTEGER NOT NULL,
  "state" post_publication_states NOT NULL,
  "state_message" TEXT,
  "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("module_ident") REFERENCES modules ("module_ident")
);
""")
