# -*- coding: utf-8 -*-
# :Project:   PatchDB -- I18n stuff
# :Created:   gio 17 nov 2016 16:43:13 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

PACKAGE = 'metapensiero.sphinx.patchdb'
"The name of distribution."

DOMAIN = PACKAGE.replace('.', '-')
"The translation domain."


def _gettext(x):
    return x


def _ngettext(s, p, n):
    return s if n == 1 else p


def gettext(msg):
    return _gettext(msg)


def ngettext(smsg, pmsg, n):
    return _ngettext(smsg, pmsg, n)


def setup(app=None):
    "Setup the translation context."

    from pkg_resources import resource_filename
    locale_dir = resource_filename(PACKAGE, 'locale')
    if app is not None:
        from sphinx.locale import init as init_locale

        # The config is not yet loaded at this time

        def handler(sa):
            global _gettext, _ngettext

            translator, has_translation = init_locale([locale_dir],
                                                      sa.config.language,
                                                      DOMAIN)
            if has_translation:
                _gettext = translator.gettext
                _ngettext = translator.ngettext

        app.connect('builder-inited', handler)
    else:
        from gettext import translation

        translator = translation(DOMAIN, locale_dir, fallback=True)

        global _gettext, _ngettext
        _gettext = translator.gettext
        _ngettext = translator.ngettext
