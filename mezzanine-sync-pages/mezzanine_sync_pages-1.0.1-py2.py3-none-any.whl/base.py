# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from mezzanine.conf import settings


# pylint: disable=no-member


class SyncPagesBase:

    # ----------------------------------------------------------------------
    def _get_content_file_extension(self):
        if 'mezzanine_pagedown' in settings.INSTALLED_APPS:
            return 'md'  # naive attempt to detect mezzanine_pagedown app

        return 'html'

    # ----------------------------------------------------------------------
    def _get_page_content(self):
        """
        Each Page object has an attribute holding the specific content type object,
        e.g. page.richtextpage and those specific objects all have a "content" attribute
        """
        content_type_object = getattr(self._page, self._page.content_model)
        try:
            return content_type_object.content
        except AttributeError:
            return None  # e.g. Link pages have no content

    # ----------------------------------------------------------------------
    def _set_page_content(self, page_content):
        content_type_object = getattr(self._page, self._page.content_model)
        try:
            content_type_object.content = page_content
        except AttributeError:
            return  # e.g. Link pages have no content
        else:
            content_type_object.save()

    # ----------------------------------------------------------------------
    def _log(self, msg, *args, **kwargs):
        if self._stdout is not None and self._verbosity is not None and self._verbosity >= 2:
            self._stdout.write(msg.format(*args, **kwargs))

    # ----------------------------------------------------------------------
    def _convert_crlf_to_lf(self, content):
        """
        When pages are saved via the web frontend, CRLF is used as line ending characters.
        However, we prefer LF and so to have consistent line ending characters, we convert them
        to LF.
        """
        return content.replace('\r\n', '\n')
