import os
from pathlib import Path

import polib
from django.conf import settings
from django.core.management import BaseCommand

from django_amazon_translate.translator import translate_po_file


def _language_from_path(locale_path, path):
    p = str(path).replace(str(locale_path) + os.path.sep, "")
    return p[:p.find(os.path.sep)]


class Command(BaseCommand):
    help = 'Use Amazon Translate to translate all the .po files in' \
           ' LOCALE_PATHS, any translated strings are not touched'

    def handle(self, *args, **options):
        # Loop through all locale paths defined in the project
        for f in settings.LOCALE_PATHS:
            # Find all the .po files we can
            root_dir = Path(f)
            file_list = [f for f in root_dir.glob('**/*.po')]

            for entry in file_list:
                language = _language_from_path(f, entry)

                po = polib.pofile(entry)
                po = translate_po_file(po, language)
                po.save(entry)
