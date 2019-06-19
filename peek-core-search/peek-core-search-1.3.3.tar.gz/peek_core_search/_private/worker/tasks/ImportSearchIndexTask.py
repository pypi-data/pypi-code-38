import logging
import logging
import string
from collections import namedtuple
from datetime import datetime
from typing import List, Set

import pytz
from sqlalchemy import select

from peek_plugin_base.worker import CeleryDbConn
from peek_core_search._private.storage.SearchIndex import SearchIndex
from peek_core_search._private.storage.SearchIndexCompilerQueue import \
    SearchIndexCompilerQueue
from peek_core_search._private.worker.tasks._CalcChunkKey import makeSearchIndexChunkKey

logger = logging.getLogger(__name__)

ObjectToIndexTuple = namedtuple("ObjectToIndexTuple", ["id", "props"])


def removeObjectIdsFromSearchIndex(deletedObjectIds: List[int]) -> None:
    pass


def reindexSearchObject(objectsToIndex: List[ObjectToIndexTuple]) -> None:
    """ Reindex Search Object

    :param objectsToIndex: Object To Index
    :returns:
    """

    searchIndexTable = SearchIndex.__table__
    queueTable = SearchIndexCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    newSearchIndexes = []
    objectIds = []
    searchIndexChunksToQueue = set()

    for objectToIndex in objectsToIndex:
        newSearchIndexes.extend(_indexObject(objectToIndex))
        objectIds.append(objectToIndex.id)

    newIdGen = CeleryDbConn.prefetchDeclarativeIds(SearchIndex, len(newSearchIndexes))
    for newSearchIndex in newSearchIndexes:
        newSearchIndex.id = next(newIdGen)
        searchIndexChunksToQueue.add(newSearchIndex.chunkKey)

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()
    try:

        results = conn.execute(select(
            columns=[searchIndexTable.c.chunkKey],
            whereclause=searchIndexTable.c.objectId.in_(objectIds)
        ))

        for result in results:
            searchIndexChunksToQueue.add(result.chunkKey)

        if objectIds:
            conn.execute(searchIndexTable
                         .delete(searchIndexTable.c.objectId.in_(objectIds)))

        if newSearchIndexes:
            logger.debug("Inserting %s SearchIndex", len(newSearchIndexes))
            inserts = [o.tupleToSqlaBulkInsertDict() for o in newSearchIndexes]
            conn.execute(searchIndexTable.insert(), inserts)

        if searchIndexChunksToQueue:
            conn.execute(
                queueTable.insert(),
                [dict(chunkKey=k) for k in searchIndexChunksToQueue]
            )

        if newSearchIndexes or searchIndexChunksToQueue or objectIds:
            transaction.commit()
        else:
            transaction.rollback()

        logger.debug("Inserted %s SearchIndex keywords in %s",
                     newSearchIndexes, (datetime.now(pytz.utc) - startTime))

    except:
        transaction.rollback()
        raise

    finally:
        conn.close()


# stopwords = set()  # nltk.corpus.stopwords.words('english'))
# stopwords.update(list(string.punctuation))
#
# from nltk import PorterStemmer
#
# stemmer = PorterStemmer()


# from nltk.stem import WordNetLemmatizer
#
# lemmatizer = WordNetLemmatizer()


def _splitKeywords(keywordStr:str) -> Set[str] :
    # Lowercase the string
    keywordStr = keywordStr.lower()

    # Remove punctuation
    tokens = ''.join([c for c in keywordStr if c not in string.punctuation])

    tokens = set([w.strip() for w in tokens.split(' ') if w.strip()])
    return tokens


def _indexObject(objectToIndex: ObjectToIndexTuple) -> List[SearchIndex]:
    """ Index Object

    This method creates  the "SearchIndex" objects to insert into the DB.

    Because our data is not news articles, we can skip some of the advanced
    natural language processing (NLP)

    We're going to be indexing things like unique IDs, job titles, and equipment names.
    We may add exclusions for nuisance words later on.

    """
    searchIndexes = []

    for propKey, text in objectToIndex.props.items():
        for token in _splitKeywords(text):
            searchIndexes.append(
                SearchIndex(
                    chunkKey=makeSearchIndexChunkKey(token),
                    keyword=token,
                    propertyName=propKey,
                    objectId=objectToIndex.id
                )
            )

    return searchIndexes

#
# if __name__ == '__main__':
#     objectToIndex = ObjectToIndexTuple(
#         id=1,
#         key='COMP3453453J',
#         props={
#             'alias': 'AB1345XXX',
#             'name': 'Hello, this is tokenising, strings string, child children'
#         }
#     )
#     print(_indexObject(objectToIndex))


