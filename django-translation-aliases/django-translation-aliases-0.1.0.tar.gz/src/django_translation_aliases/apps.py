import re

import django.utils.translation.template
from django.apps import AppConfig
from django.templatetags.i18n import do_translate
from django.templatetags.i18n import register

from django_translation_aliases.templatetags import do_block_translate

inline_re = re.compile(
    # Match the trans 'some text' part
    r"""^\s*trans(?:late)?\s+((?:"[^"]*?")|(?:'[^']*?'))"""
    # Match and ignore optional filters
    r"""(?:\s*\|\s*[^\s:]+(?::(?:[^\s'":]+|(?:"[^"]*?")|(?:'[^']*?')))?)*"""
    # Match the optional context part
    r"""(\s+.*context\s+((?:"[^"]*?")|(?:'[^']*?')))?\s*"""
)
block_re = re.compile(
    r"""^\s*blocktrans(?:late)?(\s+.*context\s+((?:"[^"]*?")|(?:'[^']*?')))?(?:\s+|$)"""
)
endblock_re = re.compile(r"""^\s*endblocktrans(?:late)?$""")


class DjangoTranslationAliasesAppConfig(AppConfig):
    name = "django_translation_aliases"

    def ready(self):
        django.utils.translation.template.inline_re = inline_re
        django.utils.translation.template.block_re = block_re
        django.utils.translation.template.endblock_re = endblock_re

        register.tag("blocktranslate", do_block_translate)
        register.tag("translate", do_translate)
