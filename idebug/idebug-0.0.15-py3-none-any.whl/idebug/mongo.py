
import pandas as pd
import pprint
pp = pprint.PrettyPrinter(indent=2)
from .DataStructure import dframe


def filter_update(filter, update, title='_None'):
    print(f"\n{'*'*60}\n Debug filter, update params  : {title}\n\n\n filter :")
    pp.pprint(filter)
    print(f"\n update :")
    pp.pprint(update)

#============================================================
# https://api.mongodb.com/python/current/api/pymongo/results.html#pymongo.results.UpdateResult
#============================================================

def UpdateResult(clss):
    print(f"\n{'*'*60}\n UpdateResult.acknowledged : {clss.acknowledged}")
    print(f"\n UpdateResult.matched_count : {clss.matched_count}")
    print(f"\n UpdateResult.modified_count : {clss.modified_count}")
    print(f"\n UpdateResult.raw_result : {clss.raw_result}")
    print(f"\n UpdateResult.upserted_id : {clss.upserted_id}")

def UpdateResults(obj):
    docs = []
    for UpdateResult in obj.UpdateResults:
        doc = {
            'acknowledged':UpdateResult.acknowledged,
            'matched_count':UpdateResult.matched_count,
            'modified_count':UpdateResult.modified_count,
            'raw_result':UpdateResult.raw_result,
            'upserted_id':UpdateResult.upserted_id
        }
        docs.append(doc)
    df = pd.DataFrame(docs)
    dframe(df)
    g = df.groupby('modified_count').count()
    dframe(g)

#============================================================
# https://api.mongodb.com/python/current/api/pymongo/results.html#pymongo.results.InsertManyResult
#============================================================

def InsertManyResult(clss):
    print(f"\n{'*'*60}\n InsertManyResult.acknowledged : {clss.acknowledged}")
    print(f"\n InsertManyResult.inserted_ids : {clss.inserted_ids}")

def InsertOneResult(clss):
    print(f"\n{'*'*60}\n InsertOneResult.acknowledged : {clss.acknowledged}")
    print(f"\n InsertOneResult.inserted_id : {clss.inserted_id}")

def DeleteResult(clss):
    print(f"\n{'*'*60}\n DeleteResult.acknowledged : {clss.acknowledged}")
    print(f"\n DeleteResult.deleted_count : {clss.deleted_count}")
    print(f"\n DeleteResult.raw_result : {clss.raw_result}")
