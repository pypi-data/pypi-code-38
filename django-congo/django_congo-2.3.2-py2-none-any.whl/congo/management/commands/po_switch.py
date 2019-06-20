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
from unidecode import unidecode
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
        parser.add_argument('filename_from', type = type(""))
        
    def handle(self, *args, **options):
        filename_from = options.get('filename_from')
        filename_to = filename_from.split('.')[0] + '_switch.po'
        
        filename_from_path = os.path.join(settings.FILE_IMPORT_PATH, filename_from)
        filename_to_path = os.path.join(settings.FILE_EXPORT_PATH, filename_to)
        assert os.path.exists(filename_from_path)
        
        with open(filename_from_path, 'r') as file_from, codecs.open(filename_to_path, 'w+', 'utf-8') as file_to:
            content = force_bytes(file_from.read()).decode('utf-8')
            
            header = ""
            msgid = ""
            msgstr = ""
            msgid_started = False
            msgstr_started = False
            for line in content.split('\n'):
                
                if line.startswith('#'):
                    header = header.rstrip()
                    msgid = msgid.rstrip()
                    msgstr = msgstr.rstrip()
                    
                    if msgid.endswith('"'):
                        msgid = msgid[:-1]
                    if msgstr.endswith('"'):
                        msgstr = msgstr[:-1]
                    
                    if header:
                        file_to.write(u"%s\n" % (header))
                        file_to.write(u'msgid "%s"\n' % msgstr)
                        file_to.write(u'msgstr "%s"\n\n' % (msgid))
            
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
                
            file_to.write(u"# END")    
                
                
                
                
                
