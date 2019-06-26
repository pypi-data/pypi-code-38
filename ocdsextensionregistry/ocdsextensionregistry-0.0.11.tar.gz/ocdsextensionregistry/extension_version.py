import csv
import os
import re
from collections import OrderedDict
from contextlib import closing
from io import BytesIO, StringIO
from urllib.parse import urlparse
from zipfile import ZipFile

import requests

from .codelist import Codelist
from .exceptions import NotAvailableInBulk
from .util import json_loads

SCHEMAS = ('record-package-schema.json', 'release-package-schema.json', 'release-schema.json')


class ExtensionVersion:
    def __init__(self, data):
        """
        Accepts a row from extension_versions.csv and assigns values to properties.
        """
        self.id = data['Id']
        self.date = data['Date']
        self.version = data['Version']
        self.base_url = data['Base URL']
        self.download_url = data['Download URL']
        self.directory = None
        self._files = None
        self._metadata = None
        self._schemas = None
        self._codelists = None

    def update(self, other):
        """
        Merges in the properties of another Extension or ExtensionVersion object.
        """
        for k, v in other.as_dict().items():
            setattr(self, k, v)

    def as_dict(self):
        """
        Returns the object's public properties as a dictionary.
        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    def available_in_bulk(self):
        """
        Returns whether the files are available in bulk (i.e. whether it has a download URL or a local directory).
        """
        return self.directory or self.download_url

    def remote(self, basename):
        """
        Returns the contents of the file within the extension.

        If the extension has a download URL or a local directory, caches all the files' contents. Otherwise, downloads
        and caches the requested file's contents. Raises an HTTPError if a download fails. Raises a KeyError if the
        requested file isn't in the ZIP archive.
        """
        if basename not in self.files:
            if not self.available_in_bulk():
                response = requests.get(self.base_url + basename)
                response.raise_for_status()
                self._files[basename] = response.text

        return self.files[basename]

    @property
    def files(self):
        """
        Returns the unparsed contents of all files. Decodes the contents of CSV, JSON and Markdown files.

        If the extension has a download URL or a local directory, caches all the files' contents. Otherwise, returns an
        empty dict. Raises an HTTPError if the download fails.
        """
        if self._files is None:
            self._files = {}

            if self.available_in_bulk():
                with closing(self.zipfile()) as zipfile:
                    names = zipfile.namelist()
                    start = len(names[0])

                    for name in names[1:]:
                        filename = name[start:]
                        if filename[-1] != '/' and filename != '.travis.yml':
                            content = zipfile.read(name)
                            if os.path.splitext(name)[1] in ('.csv', '.json', '.md'):
                                content = content.decode('utf-8')
                            self._files[filename] = content

        return self._files

    def zipfile(self):
        """
        If the extension has a local directory, returns a ZIP archive of the files it contains. If the extension has a
        download URL, downloads and returns the ZIP archive.
        """
        if self.directory:
            io = BytesIO()
            with ZipFile(io, 'w') as zipfile:
                zipfile.write(self.directory)
                for root, dirs, files in os.walk(self.directory):
                    for file in sorted(files):
                        zipfile.write(os.path.join(root, file))
        elif self.download_url:
            response = requests.get(self.download_url, allow_redirects=True)
            response.raise_for_status()
            io = BytesIO(response.content)
        else:
            raise NotAvailableInBulk('ExtensionVersion.zipfile() requires either a directory or a download_url.')

        return ZipFile(io)

    @property
    def metadata(self):
        """
        Retrieves and returns the parsed contents of the extension's extension.json file.

        Adds language maps if not present.
        """
        if self._metadata is None:
            self._metadata = json_loads(self.remote('extension.json'))

            for field in ('name', 'description', 'documentationUrl'):
                # Add required fields.
                if field not in self._metadata:
                    self._metadata[field] = {}
                # Add language maps.
                if not isinstance(self._metadata[field], dict):
                    self._metadata[field] = OrderedDict({'en': self._metadata[field]})

            # Fix the compatibility.
            if 'compatibility' not in self._metadata or isinstance(self._metadata['compatibility'], str):
                self._metadata['compatibility'] = ['1.1']

            # Remove non-URL dependencies.
            # noqa: See https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/v1.1.1/extension.json
            # noqa: See https://raw.githubusercontent.com/open-contracting-extensions/ocds_finance_extension/v1.1/extension.json
            if 'dependencies' in self._metadata:
                self._metadata['dependencies'] = [d for d in self._metadata['dependencies'] if urlparse(d).scheme]

        return self._metadata

    @property
    def schemas(self):
        """
        Retrieves and returns the parsed contents of the extension's schemas files.
        """
        if self._schemas is None:
            self._schemas = {}

            if 'schemas' in self.metadata:
                names = self.metadata['schemas']
            elif self.available_in_bulk():
                names = [name for name in self.files if name in SCHEMAS]
            else:
                names = SCHEMAS

            for name in names:
                try:
                    self._schemas[name] = json_loads(self.remote(name))
                except requests.exceptions.HTTPError:
                    if 'schemas' in self.metadata:
                        raise

        return self._schemas

    @property
    def codelists(self):
        """
        Retrieves and returns the parsed contents of the extension's codelists files.

        If the extension has no download URL, and if no codelists are listed in extension.json, returns an empty dict.
        """
        if self._codelists is None:
            self._codelists = {}

            if 'codelists' in self.metadata:
                names = self.metadata['codelists']
            elif self.available_in_bulk():
                names = [name[10:] for name in self.files if name.startswith('codelists/')]
            else:
                names = []

            for name in names:
                try:
                    self._codelists[name] = Codelist(name)
                    # Use universal newlines mode, to avoid parsing errors.
                    io = StringIO(self.remote('codelists/' + name), newline='')
                    self._codelists[name].extend(csv.DictReader(io))
                except requests.exceptions.HTTPError:
                    if 'codelists' in self.metadata:
                        raise

        return self._codelists

    @property
    def repository_full_name(self):
        """
        Returns the full name of the extension's repository, which should be a unique identifier on the hosting
        service, e.g. open-contracting-extensions/ocds_bid_extension

        Experimental
        """
        return self._repository_property('full_name')

    @property
    def repository_name(self):
        """
        Returns the short name of the extension's repository, i.e. omitting any organizational prefix, which can be
        used to create directories, e.g. ocds_bid_extension

        Experimental
        """
        return self._repository_property('name')

    @property
    def repository_user(self):
        """
        Returns the user or organization to which the extension's repository belongs, e.g. open-contracting-extensions

        Experimental
        """
        return self._repository_property('user')

    @property
    def repository_user_page(self):
        """
        Returns the URL to the landing page of the user or organization to which the extension's repository belongs,
        e.g. https://github.com/open-contracting-extensions

        Experimental
        """
        return self._repository_property('user_page')

    @property
    def repository_html_page(self):
        """
        Returns the URL to the landing page of the extension's repository, e.g.
        https://github.com/open-contracting-extensions/ocds_bid_extension

        Experimental
        """
        return self._repository_property('html_page')

    @property
    def repository_url(self):
        """
        Returns the URL of the extension's repository, in a format that can be input to a VCS program without
        modification, e.g. https://github.com/open-contracting-extensions/ocds_bid_extension.git

        Experimental
        """
        return self._repository_property('url')

    def _repository_full_name(self, parsed, config):
        return re.match(config['full_name:pattern'], parsed.path).group(1)

    def _repository_name(self, parsed, config):
        return re.match(config['name:pattern'], parsed.path).group(1)

    def _repository_user(self, parsed, config):
        return re.match(config['user:pattern'], parsed.path).group(1)

    def _repository_user_page(self, parsed, config):
        return config['html_page:prefix'] + self._repository_user(parsed, config)

    def _repository_html_page(self, parsed, config):
        return config['html_page:prefix'] + self._repository_full_name(parsed, config)

    def _repository_url(self, parsed, config):
        return config['url:prefix'] + self._repository_full_name(parsed, config) + config['url:suffix']

    def _repository_property(self, prop):
        parsed = urlparse(self.base_url)
        config = self._configuration(parsed)
        if config:
            return getattr(self, '_repository_' + prop)(parsed, config)
        raise NotImplementedError("can't determine {} from {}".format(prop, self.base_url))

    def _configuration(self, parsed):
        # Multiple websites are implemented to explore the robustness of the approach.
        #
        # Savannah has both cgit and GitWeb interfaces on the same domain, e.g.
        # "https://git.savannah.gnu.org/cgit/aspell.git/plain/COPYING?h=devel"
        # "https://git.savannah.gnu.org/gitweb/?p=aspell.git;a=blob_plain;f=COPYING;h=b1e3f5a2638797271cbc9b91b856c05ed6942c8f;hb=HEAD"
        #
        # If all interfaces could be disambiguated using the domain alone, we could implement the lookup of the
        # configuration as a dictionary. Since that's not the case, the lookup is implemented as a method.
        netloc = parsed.netloc
        if netloc == 'bitbucket.org':
            # A base URL may look like: https://bitbucket.org/facebook/hgsql/raw/default/
            return {
                'full_name:pattern': r'\A/([^/]+/[^/]+)',
                'name:pattern': r'\A/[^/]+/([^/]+)',
                'user:pattern': r'\A/([^/]+)',
                'html_page:prefix': 'https://bitbucket.org/',
                'url:prefix': 'https://bitbucket.org/',
                'url:suffix': '.git',  # assumes Git not Mercurial, which can't be disambiguated using the base URL
            }
        elif netloc == 'raw.githubusercontent.com':
            # Sample base URL: https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/v1.1.3/
            return {
                'full_name:pattern': r'\A/([^/]+/[^/]+)',
                'name:pattern': r'\A/[^/]+/([^/]+)',
                'user:pattern': r'\A/([^/]+)',
                'html_page:prefix': 'https://github.com/',
                'url:prefix': 'git@github.com:',
                'url:suffix': '.git',
            }
        elif netloc == 'gitlab.com':
            # A base URL may look like: https://gitlab.com/gitlab-org/gitter/env/raw/master/
            return {
                'full_name:pattern': r'\A/(.+)/raw/',
                'name:pattern': r'/([^/]+)/raw/',
                'user:pattern': r'\A/([^/]+)',
                'html_page:prefix': 'https://gitlab.com/',
                'url:prefix': 'https://gitlab.com/',
                'url:suffix': '.git',
            }
