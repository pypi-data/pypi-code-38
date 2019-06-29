#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import json
import shutil
from datetime import datetime
import re
from collections import defaultdict, OrderedDict
import logging

from cacherUtils import FMQLReplyStore, V1RecordToV2, ensureCacheLocations, DATAV1_LOCN_TEMPL, DATA_LOCN_TEMPL, LOG_LOCN_TEMPL

"""
Turn FMQL v1.* form replies to v2 form 
- supports both zip and "raw" JSON caches, for both source and target
  - REM: v1 is zip or json; v2 can be either, set with 'useZip'
- will restart where it left off or rebuild from scratch
- notes any transformation errors (shouldn't happen)

TODO: once flipper in, allow to apply flipper AFTER doing transform basic
ie/ pipeline
"""
def toV2Data(stationNumber, onlyTypes=None, forceRedo=False, useZip=True, forMongo=True):

    ensureCacheLocations(stationNumber)

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)    
    ch = logging.StreamHandler(sys.stdout)
    format = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(format)
    log.addHandler(ch)

    systemId = stationNumber
    logging.info("V2ing Data of VistA {} [PID {}]".format(systemId, os.getpid()))
    
    v1ReplyStore = FMQLReplyStore(DATAV1_LOCN_TEMPL.format(stationNumber), isOrdered=True)
    logging.info("Started Reply Cache V1 - uses {} - total replies {}".format("ZIP" if v1ReplyStore.usesZip() else "JSON", v1ReplyStore.totalReplies()))
        
    v2ReplyStore = FMQLReplyStore(DATA_LOCN_TEMPL.format(stationNumber), useZip=useZip)
    logging.info("Started Reply Cache V2 - uses {} - total replies {}".format("ZIP" if v2ReplyStore.usesZip() else "JSON", v2ReplyStore.totalReplies()))
    
    start = datetime.now()
    logging.info("Starting transformation of V1 to V2 Data at {}".format(str(start)))

    # May be .zip even if v1 is json
    existingReplyFiles = set(v2ReplyStore.replyFiles())
    def excludeV2AlreadyReply(replyFile):
        if replyFile in existingReplyFiles:
            logging.info("{} Being Skipped as already V2 (no forceRedo)".format(replyFile))
            return True
        return False
        
    replyIterator = v1ReplyStore.iterator(onlyTypes=onlyTypes, excludeRepliesFilter=excludeV2AlreadyReply if not forceRedo else None)
    problems = []
    overallWStops = {}
    ortn = V1RecordToV2(forMongo=forMongo)
    transformed = 0
    transformedRecords = 0
    startT = datetime.now() # start before iteration
    for reply in replyIterator.next():
        
        nreply = OrderedDict([("results", [])])
        for nrProp in reply:
            if nrProp in ["count", "results"]:
                continue
            nreply[nrProp] = reply[nrProp]
                
        for record in reply["results"]:
            try: 
                nrecord = ortn.transform(record)
                transformedRecords += 1
                nreply["results"].append(nrecord)
                if "fmqlHasStops" in nrecord:
                    if "fmqlHasStops" not in nreply:
                        nreply["fmqlHasStops"] = -1
                    if nreply["fmqlHasStops"] < nrecord["fmqlHasStops"]:
                        nreply["fmqlHasStops"] = nrecord["fmqlHasStops"]
            except Exception as e:
                logging.exception(e)
                logging.info("EXCEPTION transforming in {}".format(record["uri"]["value"]))
                problems.append(record["uri"]["value"])
                continue
        
        nreplyFile = v2ReplyStore.flush(nreply)
        # Want to know if results in reply embed stop information
        if "fmqlHasStops" in nreply:
            overallWStops[nreplyFile] = nreply["fmqlHasStops"]
        transformed += 1
        logging.info("{}. Transformed and Flushed {} in {} out of {}".format(transformed, nreplyFile, str(datetime.now() - startT), str(datetime.now() - start)))
        startT = datetime.now()
        
    timeTaken = str(datetime.now() - start)
    if len(overallWStops) == 0:
        logging.info("Ending transformation - {:,} records in {:,} replies, problem {}, NO STOPS, over {}".format(transformedRecords, transformed, len(problems), timeTaken))
    else:
        logging.info("Ending transformation - {:,} records in {:,} replies, problem {}, w/stop(s) {:,}, max stopped length {:,}, over {}".format(transformedRecords, transformed, len(problems), len(overallWStops), max(overallWStops[rf] for rf in overallWStops), timeTaken))

# ############################# Driver ####################################

"""
Form of configs

    {
        "stationNumber": "999",
        "included": ["2"],
        "forceRedo": False,
        "forMongo": True
    }
    
"""
def main():

    if len(sys.argv) < 2:
        print "need to specify configuration ex/ {VISTAAB}.json - exiting"
        return

    configBase = sys.argv[1].split(".")[0]

    if not os.path.isfile("{}.json".format(configBase)):
        print "No config file {}.json - exiting".format(configBase)
        return

    config = json.load(open("{}.json".format(configBase)), object_pairs_hook=OrderedDict)

    if "stationNumber" not in config:
        print "No station number in configuration - exiting"
        return
    stationNumber = config["stationNumber"]

    if "included" not in config or len(config["included"]) == 0:
        types = None
    else:
        types = config["included"]
        
    forceRedo = True if "forceRedo" in config and config["forceRedo"] == True else False
    forMongo = False if "forMongo" in config and config["forMongo"] == False else True
    
    toV2Data(stationNumber, onlyTypes=types, forceRedo=forceRedo, forMongo=forMongo)

if __name__ == "__main__":
    main()
