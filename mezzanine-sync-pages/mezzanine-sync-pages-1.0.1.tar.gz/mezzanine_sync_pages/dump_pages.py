# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from os import makedirs
from os.path import basename, dirname, join

from mezzanine.pages.models import Page

from mezzanine_sync_pages.base import SyncPagesBase


class DumpPagesController(SyncPagesBase):

    # ----------------------------------------------------------------------
    def __init__(self, destination_path, stdout=None, verbosity=None):
        self._destination_path = destination_path
        self._stdout = stdout
        self._verbosity = verbosity
        self._pages = None
        self._page = None
        self._page_count = 0

    # ----------------------------------------------------------------------
    def dump(self):
        self._fetch_pages()
        self._dump_pages()

    # ----------------------------------------------------------------------
    def _fetch_pages(self):
        self._pages = Page.objects.all()
        self._log('Retrieved {} pages from database'.format(len(self._pages)))

    # ----------------------------------------------------------------------
    def _dump_pages(self):
        for self._page in self._pages:
            self._dump_page()

        self._log('Written {} pages to filesystem'.format(self._page_count))

    # ----------------------------------------------------------------------
    def _dump_page(self):
        slug = self._page.slug
        content = self._get_page_content()
        if content is None:
            self._log('Skipping page: "{}" because it has no content\n'.format(self._page.title))
            return  # skip empty / non-pages

        extension = self._get_content_file_extension()
        page_relative_filename = '{}.{}'.format(basename(slug), extension)
        page_relative_path = dirname(slug)
        page_path = join(self._destination_path, page_relative_path)
        page_filename = join(page_path, page_relative_filename)

        self._log('Dumping page: "{}" to "{}"\n'.format(self._page.title, page_filename))
        # create target directory, it might already exist
        self._create_directory_if_necessary(page_path)
        # CRLF to LF
        content = self._convert_crlf_to_lf(content)
        # ensure empty new line at end of file
        content = self._ensure_trailing_new_line(content)
        # write the page content to file
        with open(page_filename, 'w') as output_file:
            output_file.write(content)
            self._page_count += 1

    # ----------------------------------------------------------------------
    def _create_directory_if_necessary(self, path):
        makedirs(path, mode=0o755, exist_ok=True)

    # ----------------------------------------------------------------------
    def _ensure_trailing_new_line(self, content):
        if content and content[-1] != '\n':
            content = '{}\n'.format(content)

        return content
