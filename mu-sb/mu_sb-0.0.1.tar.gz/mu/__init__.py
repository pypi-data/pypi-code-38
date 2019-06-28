import gettext
import os

from PyQt5.QtCore import QLocale


# Configure locale and language
# Define where the translation assets are to be found.
localedir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'locale'))
language_code = QLocale.system().name()
# DEBUG/TRANSLATE: override the language code here (e.g. to Chinese).
# language_code = 'zh'
gettext.translation('mu', localedir=localedir,
                    languages=[language_code], fallback=True).install()

# IMPORTANT
# ---------
# Keep these metadata assignments simple and single-line. They are parsed
# somewhat naively by setup.py and the Windows installer generation script.

__title__ = 'mu_sb'
__description__ = 'Mu supporting Studuino:bit'

__version__ = '0.0.1'

__license__ = 'GPL3'
__url__ = ''

__author__ = 'Artec Co., Ltd.'
__email__ = 'support@artec-kk.co.jp'
