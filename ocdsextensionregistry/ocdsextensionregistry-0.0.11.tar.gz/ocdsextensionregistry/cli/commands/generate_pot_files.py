import logging
import subprocess
from contextlib import closing
from glob import glob
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import requests
from babel.messages.catalog import Catalog
from babel.messages.extract import extract, pathmatch
from babel.messages.pofile import write_po
from docutils.parsers.rst import directives
from ocds_babel.extract import extract_codelist, extract_schema, extract_extension_metadata
from ocds_babel.directives import NullDirective
from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify
from sphinx.application import Sphinx
from sphinx.util.osutil import cd

from .base import BaseCommand
from ocdsextensionregistry import EXTENSIONS_DATA, EXTENSION_VERSIONS_DATA

logger = logging.getLogger('ocdsextensionregistry')


class Command(BaseCommand):
    name = 'generate-pot-files'
    help = 'generates POT files (message catalogs) for versions of extensions'

    def add_arguments(self):
        self.add_argument('output_directory',
                          help='the directory in which to write the output')
        self.add_argument('versions', nargs='*',
                          help="the versions of extensions to process (e.g. 'bids' or 'lots==master')")
        self.add_argument('-v', '--verbose', action='store_true',
                          help='print verbose output')
        self.add_argument('--extensions-url', default=EXTENSIONS_DATA,
                          help="the URL of the registry's extensions.csv")
        self.add_argument('--extension-versions-url', default=EXTENSION_VERSIONS_DATA,
                          help="the URL of the registry's extension_versions.csv")
        self.add_argument('--versions-dir',
                          help="a directory containing versions of extensions")

    def handle(self):
        output_directory = Path(self.args.output_directory)

        if self.args.versions_dir:
            versions_directory = Path(self.args.versions_dir)

        # We simulate pybabel and sphinx-build commands. Variable names are chosen to match upstream code.

        # For sphinx-build, the code path is:
        #
        # * bin/sphinx-build calls main() in sphinx, which calls build_main(), which calls main() in sphinx.cmdline
        # * main() calls Sphinx(…).build(…) in sphinx.application

        kwargs = {
            # sphinx-build -E …
            'freshenv': True,
            'confoverrides': {
                'source_suffix': ['.rst', '.md'],
                'source_parsers': {
                    '.md': CommonMarkParser,
                },
                'suppress_warnings': ['image.nonlocal_uri'],
            },
        }
        if not self.args.verbose:
            # sphinx-build -q …
            kwargs.update(status=None)

        # Silence warnings about unregistered directives.
        for name in ('csv-table-no-translate', 'extensiontable'):
            directives.register_directive(name, NullDirective)

        # For pybabel, the code path is:
        #
        # * bin/pybabel calls main() in babel.messages.frontend
        # * main() calls CommandLineInterface().run(sys.argv)
        # * CommandLineInterface() calls extract_messages(), which:
        #   1. Reads the input path and method map from command-line options
        #   2. Instantiates a catalog
        #   3. Calls extract_from_dir() in babel.messages.extract to extract messages
        #   4. extract_from_dir() calls check_and_call_extract_file() to find the method in the method map
        #   5. check_and_call_extract_file() calls extract_from_file() to open a file for extraction
        #   6. extract_from_file() calls extract() to extract messages
        #   7. Adds the messages to the catalog
        #   8. Writes a POT file

        options = {
            'headers': 'Title,Description,Extension',
            'ignore': 'currency.csv',
        }

        # 1. Reads the input path and method map from command-line options
        arguments = [
            # pybabel extract -F babel_ocds_codelist.cfg . -o $(POT_DIR)/$(DOMAIN_PREFIX)codelists.pot
            ('codelists.pot', [
                ('codelists/*.csv', extract_codelist, options),
            ]),
            # pybabel extract -F babel_ocds_schema.cfg . -o $(POT_DIR)/$(DOMAIN_PREFIX)schema.pot
            ('schema.pot', [
                ('*-schema.json', extract_schema, None),
                ('extension.json', extract_extension_metadata, None),
            ]),
        ]

        for version in self.versions():
            if self.args.versions_dir:
                version.directory = versions_directory / version.id / version.version

            if self.args.versions_dir:
                if not version.directory.is_dir():
                    logger.warning('Not processing {}=={} (not in {})'.format(
                        version.id, version.version, versions_directory))
                    continue
            else:
                if not version.download_url:
                    logger.warning('Not processing {}=={} (no Download URL)'.format(
                        version.id, version.version))
                    continue

            outdir = output_directory / version.id / version.version

            outdir.mkdir(parents=True, exist_ok=True)

            # See the `files` method of `ExtensionVersion` for similar code.
            with closing(version.zipfile()) as zipfile:
                names = zipfile.namelist()
                start = len(names[0])

                for output_file, method_map in arguments:
                    # 2. Instantiates a catalog
                    catalog = Catalog()

                    # 3. Calls extract_from_dir() in babel.messages.extract to extract messages
                    for name in names[1:]:
                        filename = name[start:]

                        # 4. extract_from_dir() calls check_and_call_extract_file()
                        for pattern, method, options in method_map:
                            if not pathmatch(pattern, filename):
                                continue

                            # 5. check_and_call_extract_file() calls extract_from_file()
                            with zipfile.open(name) as fileobj:
                                # 6. extract_from_file() calls extract() to extract messages
                                for lineno, message, comments, context in extract(method, fileobj, options=options):
                                    # 7. Adds the messages to the catalog
                                    catalog.add(message, None, [(filename, lineno)],
                                                auto_comments=comments, context=context)

                            break

                    # 8. Writes a POT file
                    if catalog:
                        with open(outdir / output_file, 'wb') as outfile:
                            write_po(outfile, catalog)

                with TemporaryDirectory() as srcdir:
                    for info in zipfile.infolist()[1:]:
                        filename = info.filename[start:]
                        if filename == 'README.md':
                            info.filename = filename
                            zipfile.extract(info, srcdir)

                    with cd(srcdir):
                        # Eliminates a warning, without changing the output.
                        with open('contents.rst', 'w') as f:
                            f.write('.. toctree::\n   :hidden:\n\n   README')

                        # sphinx-build -b gettext $(DOCS_DIR) $(POT_DIR)
                        app = Sphinx('.', None, '.', '.', 'gettext', **kwargs)

                        # Avoid "recommonmark_config not setted, proceed default setting".
                        app.add_config_value('recommonmark_config', {}, True)
                        # To extract messages from `.. list-table`.
                        app.add_transform(AutoStructify)

                        # sphinx-build -a …
                        app.build(True)

                        # https://stackoverflow.com/questions/15408348
                        content = subprocess.run(['msgcat', *glob('*.pot')], check=True, stdout=subprocess.PIPE).stdout

                with open(outdir / 'docs.pot', 'wb') as f:
                    f.write(content)
