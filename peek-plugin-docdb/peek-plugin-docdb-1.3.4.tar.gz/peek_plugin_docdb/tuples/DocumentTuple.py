from typing import Dict

from peek_plugin_docdb._private.PluginNames import docDbTuplePrefix
from peek_plugin_docdb._private.storage.DocDbDocumentTypeTuple import \
    DocDbDocumentTypeTuple
from peek_plugin_docdb._private.storage.DocDbModelSet import DocDbModelSet
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class DocumentTuple(Tuple):
    """ Document Tuple

    This tuple is the publicly exposed Document

    """
    __tupleType__ = docDbTuplePrefix + 'DocumentTuple'

    #:  The unique key of this document
    key: str = TupleField()

    #:  The model set of this document
    modelSet: DocDbModelSet = TupleField()

    #:  The document type
    documentType: DocDbDocumentTypeTuple = TupleField()

    #:  The document data
    document: Dict = TupleField()
