# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from collections import OrderedDict
from difflib import unified_diff
from os.path import splitext
from pathlib import Path

from mezzanine.pages.models import Page

from mezzanine_sync_pages.base import SyncPagesBase


class SyncPagesController(SyncPagesBase):

    # ----------------------------------------------------------------------
    def __init__(self, destination_path, stdout=None, stderr=None, verbosity=None):
        self._destination_path = destination_path
        self._stdout = stdout
        self._stderr = stderr
        self._verbosity = verbosity
        self._pages = None
        self._page = None
        self._page_content = None
        self._page_slug = None

    # ----------------------------------------------------------------------
    def sync(self):
        self._fetch_pages_from_filesystem()
        self._sync_pages()

    # ----------------------------------------------------------------------
    def _fetch_pages_from_filesystem(self):
        self._pages = OrderedDict()

        path = Path(self._destination_path)
        extension = self._get_content_file_extension()
        for entry in path.glob('**/*.{}'.format(extension)):
            relative_path = entry.relative_to(self._destination_path)
            slug = splitext(relative_path.as_posix())[0]  # strip the file extension
            content = entry.read_text(encoding='utf-8')
            # remember for later
            self._pages[slug] = content

        self._log('Read {} pages from filesystem\n'.format(len(self._pages)))

    # ----------------------------------------------------------------------
    def _sync_pages(self):
        for self._page_slug, self._page_content in self._pages.items():
            self._fetch_page()
            self._sync_page()

    # ----------------------------------------------------------------------
    def _fetch_page(self):
        try:
            self._page = Page.objects.get(slug=self._page_slug)
        except Page.DoesNotExist:
            self._stderr.write('Page not found for slug "{}"\n'.format(self._page_slug))
            raise

    # ----------------------------------------------------------------------
    def _sync_page(self):
        current_page_content = self._get_page_content()
        current_page_content = self._convert_crlf_to_lf(current_page_content)  # CRLF to LF

        new_page_content = self._pages[self._page_slug]

        # early out if page content didn't change
        if current_page_content == new_page_content:
            self._log(
                'Skip updating page "{}" because the content did not change\n'.format(
                    self._page_slug))
            return

        # print diff if in verbose mode
        self._log_unified_diff(current_page_content, new_page_content)

        # update page content in database
        self._set_page_content(new_page_content)
        self._log('Update page "{}" in database\n'.format(self._page_slug))

    # ----------------------------------------------------------------------
    def _log_unified_diff(self, current_page_content, new_page_content):
        if self._stdout is not None and self._verbosity is not None and self._verbosity >= 2:
            current_page_content_lines = current_page_content.splitlines(keepends=True)
            new_page_content_lines = new_page_content.splitlines(keepends=True)
            result = unified_diff(current_page_content_lines, new_page_content_lines)
            self._log('-------------\n')
            self._log('Diff for page "{}":\n'.format(self._page_slug))
            self._stdout.writelines(result)
            self._log('-------------\n')
