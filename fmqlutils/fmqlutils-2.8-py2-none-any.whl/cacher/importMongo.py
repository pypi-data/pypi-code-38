#!/usr/bin/env python
# -*- coding: utf8 -*- 

import os
import json
from datetime import datetime, date, tzinfo, timedelta
import re
from collections import defaultdict, OrderedDict
try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")
from pprint import pprint
    
"""
TODO: may move to a __Howto Wiki__

Imports Dataset into Mongo, making selective data changes and adds Indexes

1. Walk /data/vista/
2. 

Uses same configuration as Cacher and recordWalker can walk Mongo as easily as it walks JSON in the File System.

Could change to directly cache into Mongo

TODO:
- remove zip

KEY ... see http://api.mongodb.com/python/1.7/api/pymongo/son.html ... ordered dictionary support
-----
NOTE: https://stackoverflow.com/questions/23001156/how-to-get-ordered-dictionaries-in-pymongo orderdict just as good
... better as C
... see MongoClient(document_class=OrderedDict)

Before running:
- INSTALL MongoDB from http://docs.mongodb.org/manual/installation/ and its Python package, pyMongo from http://api.mongodb.org/python/current/installation.html
- create the database directory 'mdb'
- run Mongo:
  > mongod --dbpath mdb & 

TO IMPROVE: 
- use station number ie/ fixed arrangement of ZIPs expected ... zipped stations.
- ... expect DS at level /data/vista with vista999.zip etc
"""

"""
    For Clone: 
    
    104K	mdb/diagnostic.data
    300M	mdb/journal
    1.1G	mdb
    
    ... 
       
	__Storage Size__ 672.5078125 MiB - __Objects__ 7,104,448 - __Collections__ 280
"""
def importMeta(systemStationNo): 

    MONGODB_URI = 'mongodb://localhost' # :27017/smsdb
    try:
        client = MongoClient(MONGODB_URI)
    except Exception, err:
        print 'Error: %s' % err
        print '... is mongoDB installed and running at', MONGODB_URI
        return

    # NB: mongo daemon is using directory /mdb (see command to run above)
    # ... this is a DB within that directory.
    mongoDBName = "mdb{}".format(systemStationNo)   

    db = client[mongoDBName]
    print "Using Mongo DB", db.name # can use client.database_names() to see all db's
    
    metaZip = "Datasets/{}/metaDS{}.zip".format(systemStationNo, systemStationNo)
    
    zf = zipfile.ZipFile(metaZip, "r")
    # primary/secondary and files broken by type inside
    flsByCatagByTyp = defaultdict(lambda: defaultdict(list))
    for info in zf.infolist():
        flf = info.filename
        if not re.search(r'\.json$', flf):
            continue
        pOrSSearch = re.search(r'\/([ps]\w+)\/', flf)
        if not pOrSSearch:
            continue
        pOrS = pOrSSearch.group(1)
        fl = flf.split("/")[2]
        flsByCatagByTyp[pOrS][fl.split("-")[1]].append(fl)
    print
    print "Categories and types:"
    for catag in flsByCatagByTyp:
        print "\t{} - {}".format(catag, len(flsByCatagByTyp[catag]))
    print
    
    collNames = [collInfo["name"] for collInfo in db.command('listCollections')["cursor"]["firstBatch"]]
    print "Before Import - collections:", collNames
    print

    # Primary/Secondary
    for catag in flsByCatagByTyp:
    
        print "Category: {}".format(catag)
    
        for i, typ in enumerate(sorted(flsByCatagByTyp[catag].keys(), key=lambda x: float(re.sub(r'\_', '.', x))), 1):

            # Note: if don't drop indexes then stats shows 'indexSize' 
            if typ in collNames:
                print "\tpurging contents of pre-existing MongoDB collection {}".format(typ)
                db.drop_collection(typ)     
                # or drop_indexes and remove   
                        
            print "\t{}. loading type collection {}".format(i, typ)
            coll = db[typ] # identify collection with typ (757 etc)
        
            flLoadedSoFar = 0
    
            for j, fl in enumerate(sorted(flsByCatagByTyp[catag][typ], key=lambda x: int(x.split("-")[2].split(".")[0])), 1):

                print "\t\tloading latest JSON {} ...".format(fl)
                try:
                
                    flJSON = json.loads(zf.read("{}/{}/{}".format("metaDS{}".format(systemStationNo), catag, fl)), object_pairs_hook=OrderedDict)
                    
                except:
                    
                    print "\t\tCouldn't read JSON from zip"
                    raise
                            
                # Reframing for Mongo (note: in JS, fit through mongoose first)
                flJSONR = [prepareRecordForMongo(record) for record in flJSON]
                                                                                                                        
                start = datetime.now()
                try:
                    coll.insert(flJSONR)
                except Exception as e:
                    print "\tFile {} too big or records buggy - skipping".format(fl)
                    raise e # let's stop and fix
                else:
                    flLoadedSoFar += len(flJSONR)
                    if flLoadedSoFar != coll.count():
                        raise Exception("Expect number loaded to equal quantity of JSON processed")
                        
            print "\tCollection", typ, "now has", coll.count(), "members"
            print "\tLoad of {} records took {}".format(len(flJSONR), datetime.now() - start)
            print
            
    print "Loaded {} types".format(i)
                        
    print
    print "... done: Mongo stats now"
    stats = db.command("dbstats", scale=1048576) # 1024 x 1024
    dbStorageSize = stats["storageSize"] # MiB 
    dbObjects = stats["objects"]
    dbCollections = stats["collections"]
    print "\t__Storage Size__ {} MiB - __Objects__ {:,} - __Collections__ {}\n\n".format(dbStorageSize, dbObjects, dbCollections)
    print
    print 
    
"""
- id to _id
- leaving pointer as is
- native date (a/c for 24:00:00)

Note: expect prior clean up so no {} or [{}] values

Note: extra check for 'value'/'type' combo -- 81 has a member with 'value' property.
Shouldn't happen ie/ should reserve the word
"""
def prepareRecordForMongo(record, timeZone):

    def toMongoDate(dtStr):
        dtStr = re.sub(r'Z$', '', dtStr)
        if not re.search(r'T', dtStr):
            # removed: .date() as can't encode .date
            return datetime.strptime(dtStr, "%Y-%m-%d")
        else:
            # if 24:00 - turn to 00:00 (24:00 is <=> in ISO 8601 but go to 00:00)
            if re.search(r'T24:00:00', dtStr):
                dt = datetime.strptime(dtStr.split("T")[0], "%Y-%m-%d")
                dt = dt + timedelta(days=1)
            else:
                dt = datetime.strptime(dtStr, "%Y-%m-%dT%H:%M:%S")
            return dt.replace(tzinfo=timeZone) # ex/ TZ_MOUNTAIN

    def isDateValue(value):
        if isinstance(value, dict) and len(value.keys()) == 2 and "type" in value and "value" in value:
            return True
        return False

    for prop in record.keys():

        if prop == "id":
            record["_id"] = record["id"]
            del record["id"]
            continue

        if isDateValue(record[prop]):
            record[prop] = toMongoDate(record[prop]["value"])
            continue

        if isinstance(record[prop], list):

            # CSTOPPED usually - shouldn't be here but leaving for now
            if len(record[prop]) == 0:
                continue

            if not isinstance(record[prop][0], dict): # just strings/numbers
                continue

            if isDateValue(record[prop][0]): # list of dates
                record[prop] = [toMongoDate(pvalue["value"]) for pvalue in record[prop]]
                continue

            for srecord in record[prop]:
                prepareRecordForMongo(srecord, timeZone)

    return record
        
# ############################## Date Time (timezone) #####################

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt
    
# In the US, DST starts at 2am (standard time) on the first Sunday in April.
DSTSTART = datetime(1, 4, 1, 2)
# and ends at 2am (DST time; 1am standard time) on the last Sunday of Oct.
# which is the first Sunday on or after Oct 25.
DSTEND = datetime(1, 10, 25, 1)

class USTimeZone(tzinfo):

    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find first Sunday in April & the last in October.
        start = first_sunday_on_or_after(DSTSTART.replace(year=dt.year))
        end = first_sunday_on_or_after(DSTEND.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

TZ_EASTERN = USTimeZone(-5, "Eastern",  "EST", "EDT")
TZ_CENTRAL = USTimeZone(-6, "Central",  "CST", "CDT")
TZ_MOUNTAIN = USTimeZone(-7, "Mountain", "MST", "MDT")
TZ_PACIFIC = USTimeZone(-8, "Pacific",  "PST", "PDT")  

""" 
Makes About and QA's db load too ie/ after db load make about
"""
def qaDBPostImport(stationId):

    db = mdb(stationId)

    collNames = [collInfo["name"] for collInfo in db.command('listCollections')["cursor"]["firstBatch"]]
    print collNames
    
    for i, resource in enumerate(db[collNames[0]].find(), 1):
        pprint(resource)
        print
        if i > 10:
            break
            
    # Ensure Ref with _ (from VDM) is replaced by / properly in 9999
    print db["8989_5"].find_one({"parameter.label": "ORK SYSTEM ENABLE/DISABLE"})
    print
    print db["8989_51"].find_one({"label": "ORK SYSTEM ENABLE/DISABLE"})
                        
# ############################# Driver ####################################

def main():

    importMeta("9999")
    qaDBPostImport("9999")
    
if __name__ == "__main__":
    main()
