#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sat.core.log import getLogger

log = getLogger(__name__)

try:

    import gettext

    _ = gettext.translation("sat", "i18n", fallback=True).ugettext
    _translators = {None: gettext.NullTranslations()}

    def languageSwitch(lang=None):
        if not lang in _translators:
            _translators[lang] = gettext.translation(
                "sat", languages=[lang], fallback=True
            )
        _translators[lang].install(unicode=True)


except ImportError:

    log.warning("gettext support disabled")
    _ = lambda msg: msg  # Libervia doesn't support gettext

    def languageSwitch(lang=None):
        pass


D_ = lambda msg: msg  # used for deferred translations
