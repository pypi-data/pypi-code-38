# encoding: utf-8

from __future__ import unicode_literals

import pytest

from pymongo.collection import Collection
from mongoengine import Document, StringField

from web.core.context import Context
from web.db.me import MongoEngineConnection
from web.ext.db import DatabaseExtension


class Sample(Document):
	name = StringField()


@pytest.fixture
def db():
	"""Get the mid-request context.db object."""
	
	ctx = Context()
	db = DatabaseExtension(MongoEngineConnection('mongodb://localhost/test'))
	db.start(ctx)
	db.prepare(ctx)
	
	yield ctx.db.default
	
	db.stop(ctx)


class TestMongoEngineConnection(object):
	def test_connection_lifecycle(self, db):
		assert db._connection
	
	def test_private_is_protected(self, db):
		with pytest.raises(AttributeError):
			db._private
		
		with pytest.raises(KeyError):
			db['_private']
	
	def test_collection_access(self, db):
		assert isinstance(db.hello, Collection)
		assert isinstance(db['hello'], Collection)
	
	def test_document_access(self, db):
		assert db.Sample is Sample
		assert db['Sample'] is Sample
	
	def test_missing_document(self, db):
		with pytest.raises(AttributeError):
			db.Example
		
		with pytest.raises(KeyError):
			db['Example']

