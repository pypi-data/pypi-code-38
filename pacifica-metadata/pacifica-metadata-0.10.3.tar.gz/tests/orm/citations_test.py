#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the citations ORM object."""
from json import dumps
from pacifica.metadata.orm.citations import Citations
from pacifica.metadata.orm.journals import Journals
from .base_test import TestBase
from .journals_test import SAMPLE_JOURNAL_HASH, TestJournals

SAMPLE_CITATION_HASH = {
    '_id': 43,
    'article_title': 'Applications of Dove-Tail Joints in Log Cabin Constructions',
    'journal': SAMPLE_JOURNAL_HASH['_id'],
    'journal_volume': 43,
    'journal_issue': 42,
    'page_range': '34-45',
    'abstract_text': """
This is a very long abstract about the unique applications of Dove-
Tail joints during a recent construction of a wonderful log cabin in
northern Yukon.
""",
    'xml_text': """<?xml version="1.0" encoding="UTF-8" ?>
<article>
  <abstract>blah blah blah</abstract>
</article>
""",
    'release_authorization_id': 'Released',
    'doi_reference': 'doi:10.1002/0470841559.ch1'
}

SAMPLE_UNICODE_CITATION_HASH = {
    '_id': 43,
    'article_title': u'abcdé',
    'journal': SAMPLE_JOURNAL_HASH['_id'],
    'journal_volume': 43,
    'journal_issue': 42,
    'page_range': '34-45',
    'abstract_text': u"""
This is a very long abstract about the uniqué applications of Dove-
Tail joints during a recent construction of a wonderful log cabin in
northern Yukon.
""",
    'xml_text': u"""<?xml version="1.0" encoding="UTF-8" ?>
<article>
  <abstract>bléh bléh bléh</abstract>
</article>
""",
    'release_authorization_id': 'Released',
    'doi_reference': 'doi:10.1037/rmh0000008',
    'encoding': 'UTF-8'
}


class TestCitations(TestBase):
    """Test the Citations ORM object."""

    obj_cls = Citations
    obj_id = Citations.id

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that Files depend on."""
        journal = Journals()
        TestJournals.base_create_dep_objs()
        journal.from_hash(SAMPLE_JOURNAL_HASH)
        journal.save(force_insert=True)

    def test_citations_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_CITATION_HASH)

    def test_unicode_citations_hash(self):
        """Test the unicode hash base object method."""
        self.base_test_hash(SAMPLE_UNICODE_CITATION_HASH)

    def test_citations_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_CITATION_HASH))

    def test_citations_sexpr_article(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_CITATION_HASH,
            article_title_operator='ILIKE',
            article_title='%Dove%'
        )

    def test_citations_sexpr_abstract(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_CITATION_HASH,
            abstract_operator='ILIKE',
            abstract='%joints%'
        )

    def test_citations_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_CITATION_HASH)

    def test_unicode_citations_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_CITATION_HASH)
