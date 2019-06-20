# -*- coding: utf-8 -*-
import codecs
import os

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import ProgrammingError
from django.utils import translation

from congo.conf import settings
from congo.utils.db import namedtuple_fetchall
from congo.utils.types import list2sqllist


PARLER_2_PO_DEFAULT_LANG_FROM = settings.CONGO_PARLER_2_PO_DEFAULT_LANG_FROM
PARLER_2_PO_DEFAULT_LANG_TO = settings.CONGO_PARLER_2_PO_DEFAULT_LANG_TO
PARLER_2_PO_MODELS = settings.CONGO_PARLER_2_PO_MODELS
PARLER_2_PO_CONFIG = settings.CONGO_PARLER_2_PO_CONFIG

class Command(BaseCommand):
    help = 'Create *.po file'
    
    def add_arguments(self, parser):
        parser.add_argument('filename', type = type(""))
        parser.add_argument(
            '--lang_from',
            dest = 'lang_from',
            default = PARLER_2_PO_DEFAULT_LANG_FROM,
            help = 'Defaultowy jezyk z',
        )
        
        parser.add_argument(
            '--lang_to',
            dest = 'lang_to',
            default = PARLER_2_PO_DEFAULT_LANG_TO,
            help = 'Defaultowy jezyk do'
        )

        parser.add_argument(
            '--models',
            dest = 'models',
            default = " ".join(PARLER_2_PO_MODELS),
            help = 'Modele'
        )
        
    def handle(self, *args, **options):
        file_path = os.path.join(settings.FILE_EXPORT_PATH, options['filename'])
        file = codecs.open(file_path, 'w+', 'utf-8')
        cursor = connections['default'].cursor()
        lang_from = options.get('lang_from')
        lang_to = options.get('lang_to')
        models = options.get('models').split(' ')

        def get_originals(model_class, obj_id_list = None):
            try:
                sql_dict = {
                    'db_name': model_class._meta.db_table,
                    'lang_code': lang_from,
                }

                sql = """
                    SELECT *
                    FROM %(db_name)s_translation
                    WHERE language_code LIKE '%(lang_code)s'
                """
                
                if obj_id_list is not None:
                    sql += """
                        AND master_id IN %(master_id_list)s
                    """
                    sql_dict['master_id_list'] = list2sqllist(obj_id_list)


                cursor.execute(sql % sql_dict)
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
        
        file.write('msgid ""\n')
        file.write('msgstr ""\n')
        file.write('"Project-Id-Version: "\n')
        file.write('"Report-Msgid-Bugs-To: "\n')
        file.write('"POT-Creation-Date: 2018-12-05 00:04+0100"\n')
        file.write('"PO-Revision-Date: 2018-12-21 13:26+0100"\n')
        file.write('"Last-Translator: "\n')
        file.write('"Language-Team: "\n')
        file.write('"Language: %s"\n' % PARLER_2_PO_DEFAULT_LANG_TO)
        file.write('"MIME-Version: 1.0"\n')
        file.write('"Content-Type: text/plain; charset=UTF-8"\n')
        file.write('"Content-Transfer-Encoding: 8bit"\n')               
        file.write('"X-Generator: Django"\n\n')
        
        for model in models:
            print "Processing model", model
            config = {}
            if model in PARLER_2_PO_CONFIG:
                config = PARLER_2_PO_CONFIG[model]

            model_class = apps.get_model(model)

            ignore_field_list = ['master_id', 'id', 'language_code']
            if 'ignore_fields' in config:
                ignore_field_list.extend(config.get('ignore_fields'))
                print "  Ignoring fields:", " ".join(config.get('ignore_fields'))

            obj_id_list = None
            if 'use_manager' in config:
                obj_id_list = getattr(model_class, config.get('use_manager')).all().values_list('id', flat = True)
                print "  Using manager", config.get('use_manager')

            originals = get_originals(model_class, obj_id_list)
            if originals:
                for original in originals:
                    trans = get_translations(model_class, original.master_id)
                    for field, value in original._asdict().iteritems():
                        if field not in ignore_field_list and value:
                            file.write(u'msgctxt "%s:%s (id: %s)"\n' % (model, field, original.master_id))
                            file.write(u'msgid "%s"\n' % value.replace("\r\n", ""))
                            if len(trans) == 1:
                                file.write(u'msgstr "%s"\n\n' % getattr(trans[0], field))
                            else:
                                file.write(u'msgstr ""\n\n')
                            
        file.write(u"# END")
        
        
        
        
        
