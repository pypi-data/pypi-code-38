# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run

bookids = ['fd53eae1-fa23-47c7-bb1b-972349835c3c',
           '9b08c294-057f-4201-9f48-5d6ad992740d',
           '85abf193-2bd2-4908-8563-90b8a7ac8df6',
           '30189442-6998-4686-ac05-ed152b91b9de',
           'bc498e1f-efe9-43a0-8dea-d3569ad09a82',
           '5bcc0e59-7345-421d-8507-a1e4608685e8',
           '14fb4ad7-39a1-4eee-ab6e-3ef2482e3e22',
           '2e737be8-ea65-48c3-aa0a-9f35b4c6a966',
           '185cbf87-c72e-48f5-b51e-f14f21b5eabd',
           '8d50a0af-948b-4204-a71d-4826cba765b8',
           '6c322e32-9fb0-4c4d-a1d7-20c95c5c7af2',
           '914ac66e-e1ec-486d-8a9c-97b0f7a99774',
           '8b89d172-2927-466f-8661-01abc7ccdba4',
           '1d39a348-071f-4537-85b6-c98912458c3c',
           'a31cd793-2162-4e9e-acb5-6e6bbd76a5fa',
           '031da8d3-b525-429c-80cf-6c8ed997733a',
           '8d04a686-d5e8-4798-a27d-c608e4d0e187',
           'b3c1e1d2-839c-42b0-a314-e119a8aafbdd',
           '0889907c-f0ef-496a-bcb8-2a5bb121717f',
           '02776133-d49d-49cb-bfaa-67c7f61b25a1',
           '4e09771f-a8aa-40ce-9063-aa58cc24e77f',
           'afe4332a-c97f-4fc4-be27-4e4d384a32d8',
           '02040312-72c8-441e-a685-20e9333f3e1d',
           'e42bd376-624b-4c0f-972f-e0c57998e765',
           'caa57dab-41c7-455e-bd6f-f443cda5519c',
           '69619d2b-68f0-44b0-b074-a9b2bf90b2c6',
           '4061c832-098e-4b3c-a1d9-7eb593a2cb31',
           '33076054-ec1d-4417-8824-ce354efe42d0',
           'ea2f225e-6063-41ca-bcd8-36482e15ef65',
           'ca344e2d-6731-43cd-b851-a7b3aa0b37aa',
           '4abf04bf-93a0-45c3-9cbc-2cefd46e68cc',
           'a7ba2fb8-8925-4987-b182-5f4429d48daa',
           'd50f6e32-0fda-46ef-a362-9bd36ca7c97d',
           '7a0f9770-1c44-4acd-9920-1cd9a99f2a1e',
           'af275420-6050-4707-995c-57b9cc13c358']


def up(cursor):
    cursor.execute("""
CREATE OR REPLACE FUNCTION public.book_pages(uuid uuid, version text, as_collated boolean DEFAULT true)
 RETURNS SETOF modules
 LANGUAGE sql
AS $function$
WITH RECURSIVE t(node, title, path,value, depth, corder, is_collated) AS (
    SELECT nodeid, title, ARRAY[nodeid], documentid, 1, ARRAY[childorder],
           is_collated
    FROM trees tr, modules m
    WHERE m.uuid = $1 AND
          module_version( m.major_version, m.minor_version) = $2 AND
      tr.documentid = m.module_ident AND
      tr.is_collated = $3 AND
      tr.parent_id is NULL
UNION ALL
    SELECT c1.nodeid, c1.title, t.path || ARRAY[c1.nodeid], c1.documentid, t.depth+1, t.corder || ARRAY[c1.childorder], c1.is_collated /* Recursion */
    FROM trees c1 JOIN t ON (c1.parent_id = t.node)
    WHERE not nodeid = any (t.path) AND t.is_collated = c1.is_collated
)
SELECT
m.*
FROM t left join  modules m on t.value = m.module_ident WHERE m.portal_type in ('Module','CompositeModule')

$function$;

CREATE OR REPLACE FUNCTION public.set_canonical(bookid uuid, canonical uuid)
 RETURNS void
 LANGUAGE sql
AS $function$
UPDATE modules set canonical = $2 where uuid in
    (SELECT bp.uuid from latest_modules lm join
        lateral book_pages(uuid, module_version(major_version, minor_version), False) bp on True
     WHERE lm.uuid = $1
    UNION
     SELECT bp.uuid from latest_modules lm join
        lateral book_pages(uuid, module_version(major_version, minor_version), True) bp on True
     WHERE lm.uuid = $1
)

$function$;
    """)

    for bookid in bookids:
        cursor.execute("SELECT set_canonical(%(bookid)s, %(bookid)s)", {'bookid': bookid})


def down(cursor):
    cursor.execute("""
    WITH pages AS (SELECT bp.uuid, default_canonical_book(bp.uuid) AS default
    FROM latest_modules lm JOIN LATERAL
    book_pages(lm.uuid, module_version(lm.major_version, lm.minor_version), False) bp on True
    WHERE lm.uuid = ANY (%(bookids)s::uuid[]))

    UPDATE modules SET canonical = pages.default FROM pages
    WHERE modules.uuid = pages.uuid;
    """, {'bookids': bookids})

    cursor.execute("""
    DROP FUNCTION book_pages(uuid, text, boolean);
    DROP FUNCTION set_canonical(uuid, uuid);
    """)
