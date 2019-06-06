# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension

import os
import codecs
import unicodecsv


class IncludePreprocessor(Preprocessor):

    def __init__(self, root_directory='', current_directory='', asset_directory='', extension_map=None, **kwargs):
        self.asset_directory = asset_directory
        self.current_directory = current_directory
        self.root_directory = root_directory
        self.extension_map = extension_map or {}
        super(IncludePreprocessor, self).__init__(**kwargs)

    def find_file_path(self, file_name):
        """
        Find path to the file within self.root_directory

        Start at `self.current_directory/self.asset_directory/file_name` looking for `file_name`.  Recursively
        strip one directory level off of `self.current_directory` to see if `self.asset_directory/file_name`
        exists there up until the path matched `self.root_directory`
        """
        current_dir = self.current_directory
        asset_directory = os.path.join(current_dir, self.asset_directory)
        file_path = os.path.join(asset_directory, file_name)

        root_directory = os.path.join(self.root_directory, self.asset_directory)

        while not os.path.isfile(file_path):
            if asset_directory == root_directory:
                return None

            head, tail = os.path.split(os.path.split(asset_directory)[0])
            asset_directory = os.path.join(head, self.asset_directory)
            file_path = os.path.join(asset_directory, file_name)
        return file_path

    def handle_code(self, file_path, file_extension):
        """
        Parse source code lines
        """
        md_lines = []
        code_type = self.extension_map.get(file_extension, file_extension)
        included_file = codecs.open(file_path, 'r')
        # TODO: We are forcing the backticks in here.  Should this extension
        # ensure that the fenced_code extension is loaded and raise an exception
        # if it is not?
        md_lines.append('``` %s' % code_type)
        md_lines[-1].strip()
        for included_line in included_file:
            md_lines.append(included_line.rstrip())
        md_lines.append('```')
        included_file.close()
        return md_lines

    def build_csv_table(self, file_path):
        table_html = ['<table>']
        with open(file_path, 'rb') as csvfile:
            reader = unicodecsv.reader(csvfile)
            for index, row in enumerate(reader):
                table_html.append('<tr>')
                for column in row:
                    table_html.append('<th>' if index == 0 else '<td>')
                    table_html.append(column)
                    table_html.append('</th>' if index == 0 else '</td>')
                table_html.append('</tr>')
        table_html.append('</table>')
        return table_html

    def handle_csv(self, file_path):
        """
        Parse csv file and return as an html table
        """
        return self.markdown.htmlStash.store(''.join(self.build_csv_table(file_path)), safe=True)

    def run(self, lines):
        md_lines = []
        for line in lines:
            if line.startswith('+++'):
                file_name = line[3:].strip()
                file_path = self.find_file_path(file_name)
                if not file_path:
                    break
                file_extension = os.path.splitext(file_name)[1]
                if file_extension == '.csv':
                    md_lines.append(self.handle_csv(file_path))
                else:
                    md_lines.extend(self.handle_code(file_path, file_extension))
            else:
                md_lines.append(line)
        return md_lines


class IncludeExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'asset_directory': ['', ('Name of the dirirectory for the assets to include via this extension within'
                                     ' current_directory and root_directory')],
            'current_directory': ['', 'Root directory to stop searching for assets'],
            'root_directory': ['', 'Root directory to stop searching for assets'],
            'extension_map': [{}, ('Optional dictionary mapping one file extension to another'
                                   ' to override the default assigned by markdown.extensions.fenced_code')]
        }
        super(IncludeExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add IncludePreprocessor to the Markdown instance. """
        md.registerExtension(self)

        asset_directory = self.getConfig('asset_directory')
        root_directory = self.getConfig('root_directory')
        current_directory = self.getConfig('current_directory')
        extension_map = self.getConfig('extension_map')

        md.preprocessors.add(
            'include',
            IncludePreprocessor(root_directory=root_directory,
                                current_directory=current_directory,
                                asset_directory=asset_directory,
                                extension_map=extension_map,
                                markdown_instance=md),
            ">normalize_whitespace")


def makeExtension(*args, **kwargs):
    return IncludeExtension(*args, **kwargs)
