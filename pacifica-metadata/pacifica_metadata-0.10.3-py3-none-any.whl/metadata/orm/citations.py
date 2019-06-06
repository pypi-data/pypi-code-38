#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Citations model for tracking journal articles."""
from peewee import IntegerField, TextField, CharField, ForeignKeyField
from .journals import Journals
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


# Citations has too many attributes...
# pylint: disable=too-many-instance-attributes
class Citations(CherryPyAPI):
    """
    Citations model tracks metadata for a journal article.

    Attributes:
        +--------------------------+-----------------------------------------+
        | Name                     | Description                             |
        +==========================+=========================================+
        | article_title            | The title of the article                |
        +--------------------------+-----------------------------------------+
        | journal                  | Link to the journal it was published in |
        +--------------------------+-----------------------------------------+
        | journal_volume           | Journal volume for the publication      |
        +--------------------------+-----------------------------------------+
        | journal_issue            | Journal issue for the publication       |
        +--------------------------+-----------------------------------------+
        | page_range               | Pages in issue/volume was the article   |
        +--------------------------+-----------------------------------------+
        | abstract_text            | Abstract from the article in the        |
        |                          | journal                                 |
        +--------------------------+-----------------------------------------+
        | xml_text                 | xml blob for the citation               |
        +--------------------------+-----------------------------------------+
        | release_authorization_id | External link to authorization metadata |
        |                          | about the released article              |
        +--------------------------+-----------------------------------------+
        | doi_reference            | Digital Object Identifier for the       |
        |                          | citation                                |
        +--------------------------+-----------------------------------------+
        | encoding                 | Language this metadata is in not the    |
        |                          | article itself                          |
        +-------------------+------------------------------------------------+
    """

    article_title = TextField(default='')
    journal = ForeignKeyField(Journals, backref='citations')
    journal_volume = IntegerField(default=-1)
    journal_issue = IntegerField(default=-1)
    page_range = CharField(default='')
    abstract_text = TextField(default='')
    xml_text = TextField(default='')
    release_authorization_id = CharField(default='')
    doi_reference = CharField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the citation fields to a serializable hash."""
        exclude_text = flags.get('exclude_text', False)
        obj = super(Citations, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['article_title'] = unicode_type(self.article_title)
        if not exclude_text:
            obj['abstract_text'] = unicode_type(self.abstract_text)
            obj['xml_text'] = unicode_type(self.xml_text)
        # pylint: disable=no-member
        obj['journal'] = int(self.__data__['journal'])
        # pylint: enable=no-member
        obj['journal_volume'] = int(self.journal_volume)
        obj['journal_issue'] = int(self.journal_issue)
        obj['page_range'] = str(self.page_range)
        obj['doi_reference'] = str(self.doi_reference)
        obj['release_authorization_id'] = str(self.release_authorization_id)
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the object into the citation object fields."""
        super(Citations, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if(
            'journal', obj, 'journal',
            lambda: Journals.get(Journals.id == int(obj['journal']))
        )
        for key in ['journal_volume', 'journal_issue']:
            self._set_only_if(key, obj, key, lambda k=key: int(obj[k]))
        for key in ['page_range', 'release_authorization_id', 'encoding',
                    'doi_reference']:
            self._set_only_if(key, obj, key, lambda k=key: str(obj[k]))
        for key in ['article_title', 'xml_text', 'abstract_text']:
            self._set_only_if(
                key, obj, key, lambda k=key: unicode_type(obj[k]))

    @classmethod
    def where_clause(cls, kwargs):
        """Generate the PeeWee where clause used in searching."""
        where_clause = super(Citations, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause,
            kwargs,
            [
                'journal',
                'article_title',
                'journal_volume',
                'journal_issue',
                'page_range',
                'doi_reference',
                'encoding'
            ]
        )
