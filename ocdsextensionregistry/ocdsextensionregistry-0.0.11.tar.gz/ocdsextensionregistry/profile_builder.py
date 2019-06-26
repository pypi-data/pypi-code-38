import csv
import json
import logging
import os
import re
from collections import OrderedDict
from io import BytesIO, StringIO
from zipfile import ZipFile
from urllib.parse import urljoin

import json_merge_patch
import requests

from .codelist import Codelist
from .extension_registry import ExtensionRegistry
from .util import json_loads

logger = logging.getLogger('ocdsextensionregistry')


class ProfileBuilder:
    def __init__(self, standard_tag, extension_versions, registry_base_url=None, schema_base_url=None):
        """
        Accepts an OCDS version and a dictionary of extension identifiers and versions, and initializes a reader of the
        extension registry.
        """
        self.standard_tag = standard_tag
        self.extension_versions = extension_versions
        self._file_cache = {}
        self.schema_base_url = schema_base_url

        # Allows setting the registry URL to e.g. a pull request, when working on a profile.
        if not registry_base_url:
            registry_base_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/master/'

        self.registry = ExtensionRegistry(registry_base_url + 'extension_versions.csv')

    def extensions(self):
        """
        Returns the matching extension versions from the registry.
        """
        for identifier, version in self.extension_versions.items():
            yield self.registry.get(id=identifier, version=version)

    def release_schema_patch(self):
        """
        Returns the consolidated release schema patch.
        """
        profile_patch = OrderedDict()

        # Replaces `null` with sentinel values, to preserve the null'ing of fields by extensions in the final patch.
        for extension in self.extensions():
            data = re.sub(r':\s*null\b', ': "REPLACE_WITH_NULL"', extension.remote('release-schema.json'))
            json_merge_patch.merge(profile_patch, json_loads(data))

        return json_loads(json.dumps(profile_patch).replace('"REPLACE_WITH_NULL"', 'null'))

    def patched_release_schema(self):
        """
        Returns the patched release schema.
        """
        content = self.get_standard_file_contents('release-schema.json')
        patched = json_merge_patch.merge(json_loads(content), self.release_schema_patch())
        if self.schema_base_url:
            patched['id'] = urljoin(self.schema_base_url, 'release-schema.json')

        return patched

    def release_package_schema(self):
        """
        Returns a release package schema. If `schema_base_url` was provided, updates schema URLs.
        """
        data = json_loads(self.get_standard_file_contents('release-package-schema.json'))

        if self.schema_base_url:
            data['id'] = urljoin(self.schema_base_url, 'release-package-schema.json')
            data['properties']['releases']['items']['$ref'] = urljoin(self.schema_base_url, 'release-schema.json')

        return data

    def standard_codelists(self):
        """
        Returns the standard's codelists as Codelist objects.
        """
        codelists = OrderedDict()

        # Populate the file cache.
        self.get_standard_file_contents('release-schema.json')

        # This method shouldn't need to know about `_file_cache`.
        for path, content in self._file_cache.items():
            name = os.path.basename(path)
            if 'codelists' in path.split(os.sep) and name:
                codelists[name] = Codelist(name)
                codelists[name].extend(csv.DictReader(StringIO(content)), 'OCDS Core')

        return list(codelists.values())

    def extension_codelists(self):
        """
        Returns the extensions' codelists as Codelist objects.

        The extensions' codelists may be new, or may add codes to (+name.csv), remove codes from (-name.csv) or replace
        (name.csv) the codelists of the standard or other extensions.

        Codelist additions and removals are merged across extensions. If new codelists or codelist replacements differ
        across extensions, an error is raised.
        """
        codelists = OrderedDict()

        # Keep the original content of codelists, to compare across extensions.
        originals = {}

        for extension in self.extensions():
            # We use the "codelists" field in extension.json (which standard-maintenance-scripts validates). An
            # extension is not guaranteed to offer a download URL, which is the only other way to get codelists.
            for name in extension.metadata.get('codelists', []):
                content = extension.remote('codelists/' + name)

                if name not in codelists:
                    codelists[name] = Codelist(name)
                    originals[name] = content
                elif not codelists[name].patch:
                    assert originals[name] == content, 'codelist {} differs across extensions'.format(name)
                    continue

                codelists[name].extend(csv.DictReader(StringIO(content)), extension.metadata['name']['en'])

        # If a codelist replacement (name.csv) is consistent with additions (+name.csv) and removals (-name.csv), the
        # latter should be removed. In other words, the expectations are that:
        #
        # * A codelist replacement shouldn't omit added codes.
        # * A codelist replacement shouldn't include removed codes.
        # * If codes are added after a codelist is replaced, this should result in duplicate codes.
        # * If codes are removed after a codelist is replaced, this should result in no change.
        #
        # If these expectations are not met, an error is raised. As such, profile authors only have to handle cases
        # where codelist modifications are inconsistent across extensions.
        for codelist in list(codelists.values()):
            basename = codelist.basename
            if codelist.patch and basename in codelists:
                name = codelist.name
                codes = codelists[basename].codes
                if codelist.addend:
                    for row in codelist:
                        code = row['Code']
                        assert code in codes, '{} added by {}, but not in {}'.format(code, name, basename)
                    logger.info('{0} has the codes added by {1} - ignoring {1}'.format(basename, name))
                else:
                    for row in codelist:
                        code = row['Code']
                        assert code not in codes, '{} removed by {}, but in {}'.format(code, name, basename)
                    logger.info('{0} has no codes removed by {1} - ignoring {1}'.format(basename, name))
                del codelists[name]

        return list(codelists.values())

    def patched_codelists(self):
        """
        Returns patched and new codelists as Codelist objects.
        """
        codelists = OrderedDict()

        for codelist in self.standard_codelists():
            codelists[codelist.name] = codelist

        for codelist in self.extension_codelists():
            if codelist.patch:
                basename = codelist.basename
                if codelist.addend:
                    # Add the rows.
                    codelists[basename].rows.extend(codelist.rows)
                    # Note that the rows may not all have the same columns, but DictWriter can handle this.
                else:
                    # Remove the codes. Multiple extensions can remove the same codes.
                    removed = codelist.codes
                    codelists[basename].rows = [row for row in codelists[basename] if row['Code'] not in removed]
            else:
                # Set or replace the rows.
                codelists[codelist.name] = codelist

        return list(codelists.values())

    def get_standard_file_contents(self, basename):
        """
        Returns the contents of the file within the standard.

        Downloads the given version of the standard, and caches the contents of files in the schema/ directory.
        """
        if not self._file_cache:
            url = 'https://codeload.github.com/open-contracting/standard/zip/' + self.standard_tag
            response = requests.get(url)
            response.raise_for_status()
            zipfile = ZipFile(BytesIO(response.content))
            names = zipfile.namelist()
            path = 'standard/schema/'
            start = len(names[0] + path)
            for name in names[1:]:
                if path in name:
                    self._file_cache[name[start:]] = zipfile.read(name).decode('utf-8')

        return self._file_cache[basename]
