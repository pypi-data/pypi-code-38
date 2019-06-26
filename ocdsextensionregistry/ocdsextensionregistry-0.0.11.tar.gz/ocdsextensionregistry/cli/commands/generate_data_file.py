import gettext
import json
import logging
import os
import sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse

import requests
from ocds_babel import TRANSLATABLE_EXTENSION_METADATA_KEYWORDS
from ocds_babel.translate import (translate_codelist_data, translate_schema_data, translate_extension_metadata_data,
                                  translate_markdown_data)

from .base import BaseCommand
from ocdsextensionregistry import EXTENSIONS_DATA, EXTENSION_VERSIONS_DATA
from ocdsextensionregistry.exceptions import CommandError

logger = logging.getLogger('ocdsextensionregistry')


def _translator(version, domain, localedir, language):
    domain = '{}/{}/{}'.format(version.id, version.version, domain)
    return gettext.translation(domain, localedir, languages=[language], fallback=language == 'en')


class Command(BaseCommand):
    name = 'generate-data-file'
    help = 'generates a data file in JSON format with all the information about versions of extensions'

    def add_arguments(self):
        self.add_argument('versions', nargs='*',
                          help="the versions of extensions to process (e.g. 'bids' or 'lots==master')")
        self.add_argument('-d', '--locale-dir',
                          help='a directory containing MO files'),
        self.add_argument('-l', '--languages',
                          help='a comma-separated list of translations to include (default all)'),
        self.add_argument('--extensions-url', help="the URL of the registry's extensions.csv",
                          default=EXTENSIONS_DATA)
        self.add_argument('--extension-versions-url', help="the URL of the registry's extension_versions.csv",
                          default=EXTENSION_VERSIONS_DATA)
        self.add_argument('--versions-dir',
                          help="a directory containing versions of extensions")

    def handle(self):
        if self.args.languages and not self.args.locale_dir:
            self.subparser.error('--locale-dir is required if --languages is set.')

        if self.args.versions_dir:
            versions_directory = Path(self.args.versions_dir)

        data = OrderedDict()
        languages = {'en'}
        localedir = self.args.locale_dir
        headers = ['Title', 'Description', 'Extension']

        if localedir:
            available_translations = [n for n in os.listdir(localedir) if os.path.isdir(os.path.join(localedir, n))]
            if self.args.languages:
                for language in self.args.languages.split(','):
                    if language in available_translations:
                        languages.add(language)
                    else:
                        self.subparser.error('translations to {} are not available'.format(language))
            else:
                languages.update(available_translations)

        for version in self.versions():
            if self.args.versions_dir:
                version.directory = versions_directory / version.id / version.version

            # Add the extension's data.
            if version.id not in data:
                data[version.id] = OrderedDict([
                    ('id', version.id),
                    ('category', version.category),
                    ('core', version.core),
                    ('name', OrderedDict()),
                    ('description', OrderedDict()),
                    ('latest_version', None),
                    ('versions', OrderedDict()),
                ])

            # Add the version's metadata.
            version_data = OrderedDict([
                ('id', version.id),
                ('date', version.date),
                ('version', version.version),
                ('base_url', version.base_url),
                ('download_url', version.download_url),
                ('publisher', OrderedDict([
                    ('name', version.repository_user),
                    ('url', version.repository_user_page),
                ])),
                ('metadata', version.metadata),
                ('schemas', OrderedDict()),
                ('codelists', OrderedDict()),
                ('readme', OrderedDict()),
            ])

            parsed = urlparse(version_data['publisher']['url'])
            if parsed.netloc == 'github.com' and 'GITHUB_ACCESS_TOKEN' in os.environ:
                api_url = 'https://api.github.com/users/{}?access_token={}'.format(
                    version_data['publisher']['name'], os.getenv('GITHUB_ACCESS_TOKEN'))
                version_data['publisher']['name'] = requests.get(api_url).json()['name']

            for language in sorted(languages):
                # Update the version's metadata and add the version's schema.
                translator = _translator(version, 'schema', localedir, language)

                translation = translate_extension_metadata_data(version.metadata, translator, lang=language)
                for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
                    version_data['metadata'][key][language] = translation[key][language]

                for name in ('record-package-schema.json', 'release-package-schema.json', 'release-schema.json'):
                    if name not in version_data['schemas']:
                        version_data['schemas'][name] = OrderedDict()

                    if name in version.schemas:
                        translation = translate_schema_data(version.schemas[name], translator)
                        version_data['schemas'][name][language] = translation

                # Add the version's codelists.
                if version.codelists:
                    translator = _translator(version, 'codelists', localedir, language)
                    for name in sorted(version.codelists):
                        if name not in version_data['codelists']:
                            version_data['codelists'][name] = OrderedDict()

                        codelist = version.codelists[name]
                        version_data['codelists'][name][language] = OrderedDict()

                        translation = [translator.gettext(fieldname) for fieldname in codelist.fieldnames]
                        version_data['codelists'][name][language]['fieldnames'] = translation

                        translation = translate_codelist_data(codelist, translator, headers)
                        version_data['codelists'][name][language]['rows'] = translation

                # Add the version's readme and documentation.
                translator = _translator(version, 'docs', localedir, language)

                translation = translate_markdown_data('README.md', version.remote('README.md'), translator)
                version_data['readme'][language] = translation

            data[version.id]['versions'][version.version] = version_data

        for _id in data:
            # Determine the latest version.
            versions = data[_id]['versions']
            if len(versions) == 1:
                latest_version = list(versions)[0]
            elif 'master' in versions:
                latest_version = 'master'
            else:
                dated = list(filter(lambda kv: kv[1]['date'], versions.items()))
                if dated:
                    latest_version = max(dated, key=lambda kv: kv[1]['date'])[0]
                else:
                    raise CommandError("Couldn't determine latest version of {}".format(_id))

            # Apply the latest version.
            data[_id]['latest_version'] = latest_version
            for field in ('name', 'description'):
                data[_id][field] = data[_id]['versions'][latest_version]['metadata'][field]

        json.dump(data, sys.stdout, ensure_ascii=False, indent=2, separators=(',', ': '))
