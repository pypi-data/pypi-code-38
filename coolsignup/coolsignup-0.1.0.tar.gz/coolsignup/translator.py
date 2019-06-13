import gettext
import naval.core
import os.path
import sys


def get_locale_directory():
    for path in sys.path:
        candidate = os.path.join(path, 'coolsignup', 'locale')
        if os.path.isdir(candidate):
            return candidate
    raise IOError("Couldn't find locale directory.")

class Translator(object):
    def __init__(self, locale_dir):
        self._locale_dir = locale_dir

    def translation_func(self, to_lang):
        try:
            naval_translation = gettext.translation(
                "naval", naval.core.settings.locale_dir, [to_lang]
            )
        except (IOError, OSError):
            naval_translation = None
        try:
            coolsignup_translation = gettext.translation(
                "coolsignup", self._locale_dir, [to_lang]
            )
        except (IOError, OSError):
            coolsignup_translation = None
        if coolsignup_translation:
            if naval_translation:
                coolsignup_translation.add_fallback(naval_translation)
            translation = coolsignup_translation
        elif naval_translation:
            translation = naval_translation
        else:
            return (lambda x:x)

        try:
            return translation.ugettext # python 2
        except AttributeError:
            return translation.gettext # python 3
