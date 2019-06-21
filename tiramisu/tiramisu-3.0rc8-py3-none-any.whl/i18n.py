# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The original `Config` design model is unproudly borrowed from
# the rough gus of pypy: pypy: http://codespeak.net/svn/pypy/dist/pypy/config/
# the whole pypy projet is under MIT licence
"internationalisation utilities"
from gettext import translation, NullTranslations
from platform import system
from pkg_resources import resource_filename
from .log import log


DEFAULT = 'en'


def get_translation() -> str:
    """Sets the user locale as langage
    The default is set to english
    """
    # Application name (without .i18n)
    app_name = __name__[:-5]
    translations_path = resource_filename(app_name, 'locale')

    if 'Windows' in system():
        import ctypes
        from locale import windows_locale
        default_locale = windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
    else:
        from locale import getdefaultlocale
        default_locale = getdefaultlocale()
    if default_locale and isinstance(default_locale, tuple):
        if default_locale[0] is not None:
            user_locale = default_locale[0][:2]
        else:
            user_locale = DEFAULT
    elif default_locale:
        user_locale = default_locale[:2]
    else:
        user_locale = DEFAULT
    try:
        trans = translation(domain=app_name,
                            localedir=translations_path,
                            languages=[user_locale],
                            codeset='UTF-8')
    except FileNotFoundError:
        log.debug('cannot found translation file for langage {} in localedir {}'.format(user_locale,
                                                                                        translations_path))
        trans = NullTranslations()
    return trans.gettext


_ = get_translation()
