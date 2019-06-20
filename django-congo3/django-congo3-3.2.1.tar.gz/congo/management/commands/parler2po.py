# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import translation
from django.apps import apps
from congo.utils.db import namedtuple_fetchall
from django.db import connections
from django.db.utils import ProgrammingError
import codecs
import os
from django.conf import settings

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

        parser.add_argument(
            '--apps',
            dest = 'apps',
            default = " ".join(PARLER_2_PO_APPS),
            help = 'Aplikacje'
        )

        parser.add_argument(
            '--ignore-apps',
            dest = 'ignore_apps',
            default = " ".join(PARLER_2_PO_IGNORE_APPS),
            help = 'Aplikacje do zignorowania'
        )

        parser.add_argument(
            '--models',
            dest = 'models',
            default = " ".join(PARLER_2_PO_MODELS),
            help = 'Modele'
        )

        parser.add_argument(
            '--ignore-models',
            dest = 'ignore_models',
            default = " ".join(PARLER_2_PO_IGNORE_MODELS),
            help = 'Modele do zignorowania'
        )

    def handle(self, *args, **options):
        file_path = os.path.join(settings.FILE_EXPORT_PATH, options['filename'])
        file = codecs.open(file_path, 'w+', 'utf-8')
        cursor = connections['default'].cursor()
        lang_from = options.get('lang_from')
        lang_to = options.get('lang_to')
        models = [x for x in options.get('models').split(' ') if x not in options.get('ignore_models').split(' ')]

        def get_originals(model_class):
            try:
                cursor.execute(
                   """
                   SELECT *
                   FROM %s_translation
                   WHERE language_code LIKE '%s'
                   """ % (model_class._meta.db_table, lang_from)
                )
                return namedtuple_fetchall(cursor)
            except ProgrammingError:
                return False

        def get_translations(model_class, master_id, lang_code = lang_to):
            try:
                cursor.execute(
                   """
                   SELECT *
                   FROM %s_translation
                   WHERE master_id = %s %s
                   """ % (model_class._meta.db_table, master_id, (" AND language_code = '%s'" % lang_code) if lang_code else "")
                )
                return namedtuple_fetchall(cursor)
            except ProgrammingError:
                return False

        for model in models:
            model_class = apps.get_model(model)
            for original in get_originals(model_class):
                trans = get_translations(model_class, original.master_id)
                for field, value in original._asdict().items():
                    if field not in ('master_id', 'id', 'language_code') and value:
                        file.write("# %s:%s (id: %s)\n" % (model, field, original.master_id))
                        file.write('msgid "%s"\n' % value)
                        if len(trans) == 1:
                            file.write('msgstr "%s"\n\n' % getattr(trans[0], field))
                        else:
                            file.write('msgstr ""\n\n')

        file.write("# END")





