import csv
import json
import os
from collections import OrderedDict
from contextlib import contextmanager

from .profile_builder import ProfileBuilder

VALID_FIELDNAMES = ('Code', 'Title', 'Description', 'Extension')


def build_profile(basedir, standard_tag, extension_versions, registry_base_url=None, schema_base_url=None):
    """
    Pulls extensions into a profile.

    - Merges extensions' JSON Merge Patch files for OCDS' release-schema.json (schema/profile/release-schema.json)
    - Writes extensions' codelist files (schema/profile/codelists)
    - Patches OCDS' release-schema.json with extensions' JSON Merge Patch files (schema/patched/release-schema.json)
    - Patches OCDS' codelist files with extensions' codelist files (schema/patched/codelists)
    - Updates the "codelists" field in extension.json

    The profile's codelists exclude deprecated codes and add an Extension column.

    `basedir` is the profile's schema/ directory.
    """
    @contextmanager
    def open_file(name, mode='r'):
        """
        Creates the directory if it doesn't exist.
        """
        os.makedirs(os.path.dirname(name), exist_ok=True)

        f = open(name, mode)
        try:
            yield f
        finally:
            f.close()

    def write_json_file(data, *parts):
        with open_file(os.path.join(basedir, *parts), 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, separators=(',', ': '))
            f.write('\n')

    def write_codelist_file(codelist, fieldnames, *parts):
        with open_file(os.path.join(basedir, *parts, 'codelists', codelist.name), 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(codelist)

    builder = ProfileBuilder(standard_tag, extension_versions, registry_base_url, schema_base_url)
    extension_codelists = builder.extension_codelists()
    directories_and_schemas = {
        'profile': {
            'release-schema.json': builder.release_schema_patch(),
        },
        'patched': {
            'release-schema.json': builder.patched_release_schema(),
            'release-package-schema.json': builder.release_package_schema(),
        }
    }

    # Write the JSON Merge Patch and JSON Schema files.
    for directory, schemas in directories_and_schemas.items():
        for filename, schema in schemas.items():
            write_json_file(schema, directory, filename)

    # Write the extensions' codelists.
    for codelist in extension_codelists:
        write_codelist_file(codelist, codelist.fieldnames, 'profile')

    # Write the patched codelists.
    for codelist in builder.patched_codelists():
        codelist.add_extension_column('Extension')
        codelist.remove_deprecated_codes()
        fieldnames = [fieldname for fieldname in codelist.fieldnames if fieldname in VALID_FIELDNAMES]
        write_codelist_file(codelist, fieldnames, 'patched')

    # Update the "codelists" field in extension.json.
    with open(os.path.join(basedir, 'profile', 'extension.json')) as f:
        metadata = json.load(f, object_pairs_hook=OrderedDict)

    codelists = [codelist.name for codelist in extension_codelists]

    if codelists:
        metadata['codelists'] = codelists
    else:
        metadata.pop('codelists', None)

    write_json_file(metadata, 'profile', 'extension.json')
