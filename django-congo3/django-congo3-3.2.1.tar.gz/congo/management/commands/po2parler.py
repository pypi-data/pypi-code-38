# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import translation
from django.apps import apps
from congo.utils.db import namedtuple_fetchall
from django.db import connections
from django.db.utils import ProgrammingError
import codecs
from collections import defaultdict
from django.conf import settings
import os

from django.utils.encoding import force_bytes
from congo.utils.types import list2sqllist

PARLER_2_PO_DEFAULT_LANG = settings.CONGO_PARLER_2_PO_DEFAULT_LANG
PARLER_2_PO_APPS = settings.CONGO_PARLER_2_PO_APPS
PARLER_2_PO_IGNORE_APPS = settings.CONGO_PARLER_2_PO_IGNORE_APPS
PARLER_2_PO_IGNORE_APPS = settings.CONGO_PARLER_2_PO_IGNORE_APPS
PARLER_2_PO_MODELS = settings.CONGO_PARLER_2_PO_MODELS
PARLER_2_PO_IGNORE_MODELS = settings.CONGO_PARLER_2_PO_IGNORE_MODELS
PARLER_2_PO_IGNORE_MODELS = settings.CONGO_PARLER_2_PO_IGNORE_MODELS

class Command(BaseCommand):
    help = 'Create *.po file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type = type(""))
        parser.add_argument(
            '--lang_from',
            dest = 'lang_from',
            default = PARLER_2_PO_DEFAULT_LANG,
            help = 'Defaultowy jezyk z',
        )

        parser.add_argument(
            '--lang_to',
            dest = 'lang_to',
            default = PARLER_2_PO_DEFAULT_LANG,
            help = 'Defaultowy jezyk do'
        )

    def handle(self, *args, **options):
        filename = options.get('filename')
        cursor = connections['default'].cursor()
        changes = defaultdict(list)

        file_path = os.path.join(settings.FILE_IMPORT_PATH, filename)
        assert os.path.exists(file_path)

        with open(file_path, 'r') as po_file:
            content = force_bytes(po_file.read()).decode('utf-8')

            header = ""
            msgid = ""
            msgstr = ""
            msgid_started = False
            msgstr_started = False
            for line in content.split('\n'):

                if line.startswith('#'):
                    header = header.rstrip().replace('"', '""').replace("'", "''")
                    msgid = msgid.rstrip().replace('"', '""').replace("'", "''")
                    msgstr = msgstr.rstrip().replace('"', '""').replace("'", "''")
                    if header:
                        master_id = int(header.replace('(', '').replace(')', '').replace('# ', '').split('id: ')[1])
                        model_name = header.replace('(', '').replace(')', '').replace('# ', '').split('id: ')[0].split(':')[0]
                        changes[(master_id, model_name)].append((header, msgid, msgstr))
                    header = line
                    msgid = ""
                    msgstr = ""
                    msgid_started = False
                    msgstr_started = False

                elif "msgid" in line:
                    msgid_started = True
                    msgstr_started = False

                elif "msgstr" in line:
                    msgid_started = False
                    msgstr_started = True

                if msgid_started:
                    try:
                        line = line.split('msgid ')[1]
                        if line.startswith('"'):
                            line = line[1:]
                        if line.endswith('"'):
                            line = line[:-1]

                        msgid += line
                    except IndexError:
                        if msgid:
                            msgid += line
                            msgid += '\n'
                        else:
                            msgid += line

                elif msgstr_started:
                    try:
                        line = line.split('msgstr ')[1]
                        if line.startswith('"'):
                            line = line[1:]

                        if line.endswith('"'):
                            line = line[:-1]

                        msgstr += line
                    except IndexError:
                        if msgstr:
                            msgstr += line
                            msgstr += '\n'
                        else:
                            msgstr += line

        def update(model_class, master_id, field_list, value_list):
            assert len(field_list) == len(value_list)

            cursor.execute(
               """
               SELECT *
               FROM %s_translation
               WHERE master_id = %s
               AND language_code = '%s'
               """ % (model_class._meta.db_table, master_id, options['lang_to'])
            )

            result = namedtuple_fetchall(cursor)

            if result and msgstr:
                str_list = []
                for x in range(0, len(field_list)):
                    str_list.append('%s = "%s"' % (field_list[x], value_list[x]))
                sql_str = " , ".join(str_list)

                cursor.execute(
                    """
                    UPDATE %s_translation
                    SET %s
                    WHERE master_id = %s
                    AND language_code = '%s'
                    """ % (model_class._meta.db_table, sql_str, master_id, options['lang_to'])
                )
            elif not result and msgstr:
                field_list.extend(['language_code', 'master_id'])
                value_list.extend([options['lang_to'], master_id])

                cursor.execute(
                    """
                    INSERT INTO %s_translation %s
                    VALUES %s
                    """ % (model_class._meta.db_table, list2sqllist(field_list, string_wrap = False), list2sqllist(value_list))
                )

        for key, value in list(changes.items()):
            master_id = key[0]
            model = key[1]
            model_class = apps.get_model(model)

            field_list = []
            value_list = []

            for c in value:
                header = c[0]
                msgid = c[1]
                msgstr = c[2]

                header_data = header.replace('(', '').replace(')', '').replace('# ', '').split('id: ')
                field = header_data[0].split(':')[1]
                field_list.append(field.rstrip())
                value_list.append(msgstr if msgstr else msgid)

            update(model_class, master_id, field_list, value_list)








