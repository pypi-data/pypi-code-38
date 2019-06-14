import polib

from django_amazon_translate.management.commands.auto_translate_text \
    import _language_from_path
from django_amazon_translate.translator import translate_po_file

pofile = """
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2019-05-23 12:46+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"

#: ham/egg/models.py:1
msgid "String to translate"
msgstr ""

#: ham/egg/models.py:2
msgid "String that is already translated"
msgstr "Chaîne déjà traduite"
"""


def test_translatepofile(mocker):
    x = mocker.patch(
        'django_amazon_translate.translator._amazonTranslate.translate_text',
        return_value={'TranslatedText': 'Nothing'}
    )

    po = polib.pofile(pofile)
    po = translate_po_file(po, "fr")

    x.assert_called_once()


def test_extractlanguage():
    assert(
        _language_from_path(
            'LOCALE_PATH',
            'LOCALE_PATH/en/LC_MESSAGES/django.po'
        ) == 'en'
    )
