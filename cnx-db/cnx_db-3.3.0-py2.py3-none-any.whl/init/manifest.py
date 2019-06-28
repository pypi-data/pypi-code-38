# -*- coding: utf-8 -*-
"""\
Manifest marker files (``manifest.json``) are placed in a schema's directory
to properly order the schema files into a linear format that can be loaded
into the database.

"""
import os
import json


SCHEMA_MANIFEST_FILENAME = 'manifest.json'


def _read_schema_manifest(manifest_filepath):
    with open(os.path.abspath(manifest_filepath), 'r') as fp:
        raw_manifest = json.load(fp)
    manifest = []
    relative_dir = os.path.abspath(os.path.dirname(manifest_filepath))
    for item in raw_manifest:
        if isinstance(item, dict):
            file = item['file']
        else:
            file = item
        if os.path.isdir(os.path.join(relative_dir, file)):
            next_manifest = os.path.join(
                relative_dir,
                file,
                SCHEMA_MANIFEST_FILENAME)
            manifest.append(_read_schema_manifest(next_manifest))
        else:
            manifest.append(os.path.join(relative_dir, file))
    return manifest


def _compile_manifest(manifest, content_modifier=None):
    """Compile a given ``manifest`` into a sequence of schema items.

    Apply the optional ``content_modifier`` to each file's contents.
    """
    items = []
    for item in manifest:
        if isinstance(item, list):
            items.extend(_compile_manifest(item, content_modifier))
        else:
            with open(item, 'r') as fp:
                content = fp.read()
            if content_modifier:
                content = content_modifier(item, content)
            items.append(content)
    return items


def get_schema(schema_directory):
    """Return the current schema."""
    manifest_filepath = os.path.join(schema_directory,
                                     SCHEMA_MANIFEST_FILENAME)
    schema_manifest = _read_schema_manifest(manifest_filepath)

    # Modify the file so that it contains comments that say it's origin.
    def file_wrapper(f, c):
        return "-- FILE: {0}\n{1}\n-- \n".format(f, c).encode('utf-8')

    return _compile_manifest(schema_manifest, file_wrapper)


__all__ = ('get_schema')
