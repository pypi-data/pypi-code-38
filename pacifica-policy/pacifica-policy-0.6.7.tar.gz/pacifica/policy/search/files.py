#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class FilesRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'mtime', 'ctime', 'keyword',
        'name', 'subdir', 'size', 'hashsum', 'hashtype',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**file_obj):
        """Return string for object id."""
        return text_type('files_{_id}').format(**file_obj)

    @staticmethod
    def updated_date(**file_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**file_obj)

    @staticmethod
    def created_date(**file_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**file_obj)

    @staticmethod
    def display_name(**file_obj):
        """Return the string to render display_name."""
        return text_type('{subdir}/{name}').format(**file_obj)

    @staticmethod
    def mtime(**file_obj):
        """Return the string to render mtime."""
        return text_type('{mtime}').format(**file_obj)

    @staticmethod
    def ctime(**file_obj):
        """Return the string to render mtime."""
        return text_type('{ctime}').format(**file_obj)

    @staticmethod
    def name(**file_obj):
        """Return the string to render mtime."""
        return text_type('{name}').format(**file_obj)

    @staticmethod
    def subdir(**file_obj):
        """Return the string to render mtime."""
        return text_type('{subdir}').format(**file_obj)

    @staticmethod
    def size(**file_obj):
        """Return the string to render size."""
        return text_type('{size}').format(**file_obj)

    @staticmethod
    def hashsum(**file_obj):
        """Return the string to render hashsum."""
        return text_type('{hashsum}').format(**file_obj)

    @staticmethod
    def hashtype(**file_obj):
        """Return the string to render hashtype."""
        return text_type('{hashtype}').format(**file_obj)

    @staticmethod
    def keyword(**file_obj):
        """Return the rendered string for keywords."""
        return text_type(' ').join(text_type('{subdir}/{name}').format(**file_obj).split('/'))

    # this is needed because it is abastract but it's never called
    @classmethod
    def get_transactions(cls, **_kwargs):  # pragma: no cover
        """Just return empty for this."""
        return []
