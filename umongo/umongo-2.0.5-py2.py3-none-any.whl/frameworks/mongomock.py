from mongomock.database import Database
from mongomock.collection import Cursor

from .pymongo import PyMongoBuilder, PyMongoDocument, BaseWrappedCursor
from ..document import DocumentImplementation


# Mongomock aims at working like pymongo


class WrappedCursor(BaseWrappedCursor, Cursor):
    __slots__ = ()


class MongoMockDocument(PyMongoDocument):
    __slots__ = ()
    cursor_cls = WrappedCursor
    opts = DocumentImplementation.opts


class MongoMockBuilder(PyMongoBuilder):
    BASE_DOCUMENT_CLS = MongoMockDocument

    @staticmethod
    def is_compatible_with(db):
        return isinstance(db, Database)
