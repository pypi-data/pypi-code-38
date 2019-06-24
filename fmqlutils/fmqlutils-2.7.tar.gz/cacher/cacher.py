#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re 
import sys
import json
import shutil
from datetime import datetime
from collections import OrderedDict, defaultdict
import logging
from ..fmqlIF.fmqlIF import FMQLRESTIF, FMQLBrokerIF
from cacherUtils import FMQLReplyStore, cacheFileToStore, ensureCacheLocations, configLogging, DATAV1_LOCN_TEMPL, SCHEMA_LOCN_TEMPL, LOG_LOCN_TEMPL

"""
Basic FileMan data and schema cacher using FMQL.

TODO: FMQLSchemaStore to parallel FMQLReplyStore (may become FMQLDataStore)

Background: FileMan doesn't have enough indexes to support analytics. To fully analyze
data must first be cached. It can then be processed in a different DB (ex/ Mongo) or just
from disk.

Cache to "/data/vista/{stationNumber}/DataV1/" which it will create if it is absent

To test:
- du -h /data/{SYSTEM}/Data[V2] and /Schema
- old 2 download has 'File 2, limit 500 : all 1032150 of file 2 in 4:49:22.820342'

Invoke: 

    > nohup python -u cacher.py VISTACONFIG > nohupVISTA.out & and tail -f nohupVISTA.out; monitor with ps -aux, kill with kill -9 {pid}

or 'python cacher.py VISTACONFIG [SCHEMA]'

Note: all functions here are driven from Cacher config
"""

# ########################## Data #########################

def cacheData(config):

    start = datetime.now()
        
    # Note: can raise Exception if can't create/use configured locations - will be caught in invoker 
    ensureCacheLocations(config["stationNumber"])

    configLogging(config["stationNumber"], "cacherLog", config["logLevel"] if "logLevel" in config else "INFO")
    logging.info("caching in {}".format(DATAV1_LOCN_TEMPL.format(config["stationNumber"])))

    systemId = config["stationNumber"] if "name" not in config else "{} [{}]".format(config["name"], config["stationNumber"])
    logging.info("Caching Data of VistA {} [PID {}]".format(systemId, os.getpid()))
    
    fmqlIF = makeFMQLIF(config)
    
    useZip = config["useZip"] if "useZip" in config else True
    # makeDir False as explicitly building below (may change later)
    fmqlReplyStore = FMQLReplyStore(DATAV1_LOCN_TEMPL.format(config["stationNumber"]), isOrdered=True, useZip=useZip, makeDir=False)
    
    trackZeroFile = "{}trackZeroFiles{}.json".format(LOG_LOCN_TEMPL.format(config["stationNumber"]), config["stationNumber"])
    try:
        zeroFiles = json.load(open(trackZeroFile))
    except: 
        zeroFiles = []
        
    excludeTypes = set(config["excluded"]) if "excluded" in config else set()
    includeTypes = set(config["included"]) if "included" in config else None

    #
    # Option of Count Order or Id Order
    #
    # ... may retire: ala FMQLReplyStore, support a Schema Store
    # 
    def filesFromSchema(fmqlEP, schemaCacheLocation, allFiles=False, typeOrder=False):
        """
        From SELECT TYPES - if in cache just load and read. Otherwise cache and
        then load and read.
        """
        query = "SELECT TYPES TOPONLY" # doing TOPONLY and not POPONLY in case POP is wrong
        cacheFile = re.sub(r' ', "_", query) + ".json"
        try:
            reply = json.load(open(schemaCacheLocation + cacheFile), object_pairs_hook=OrderedDict)
        except Exception:
            logging.info("First time through - must (re)cache {} to {} ...".format(query, schemaCacheLocation))
            reply = fmqlEP.invokeQuery(query)
            json.dump(reply, open(schemaCacheLocation + cacheFile, "w"))
        if typeOrder: # used if included explicit - otherwise order biggest first
            oresults = sorted(reply["results"], key=lambda res: float(re.sub(r'\_', '.', res["number"])))
        else:      
            oresults = sorted(reply["results"], key=lambda res: int(res["count"]) if "count" in res else 0, reverse=True)
        filesInOrder = []
        for i, result in enumerate(oresults, 1):
            fileId = re.sub(r'\.', '_', result["number"])
            filesInOrder.append({"id": fileId, "count": 0 if "count" not in result else int(result["count"])})
        logging.info("Returning {} top files - not all will have data".format(len(filesInOrder)))
        return filesInOrder

    j = 0
    defaultLimit = 5000 if "defaultLimit" not in config else config["defaultLimit"]
    defaultCStop = 1000 if "defaultCStop" not in config else config["defaultCStop"]
    problem = False
    typeOrder = True if includeTypes else False # cache in type order if list is explicit
    schemaCacheLocation = SCHEMA_LOCN_TEMPL.format(config["stationNumber"])
    for i, fli in enumerate(filesFromSchema(fmqlIF, schemaCacheLocation, allFiles=False, typeOrder=typeOrder), 1):

        if fli["id"] in excludeTypes:
            logging.debug("{}. File {} expecting count of {} - EXCLUDED SO SKIPPING".format(i, fli["id"], fli["count"]))
            continue

        if fli["id"] in zeroFiles:
            logging.debug("{}. File {} expecting count of {} - KNOWN ZERO SO SKIPPING".format(i, fli["id"], fli["count"]))
            continue

        if includeTypes and fli["id"] not in includeTypes:
            logging.debug("{}. File {} expecting count of {} - NOT IN EXPLICIT INCLUDE LIST SO SKIPPING".format(i, fli["id"], fli["count"]))
            continue

        logging.info("{}. File {} expecting count of {}{}".format(i, fli["id"], fli["count"], " ** Note POP says 0 but trying anyhow" if fli["count"] == 0 else ""))
            
        if "explicitLimits" in config and fli["id"] in config["explicitLimits"]:
            limit = config["explicitLimits"][fli["id"]]
        else:
            limit = defaultLimit

        if "explicitCStops" in config and fli["id"] in config["explicitCStops"]:
            cstop = config["explicitCStops"][fli["id"]]
        else:
            cstop = defaultCStop

        try: # may get license error - make sure save zero files first
            if not cacheFileToStore(fmqlIF, fmqlReplyStore, fli["id"], limit=limit, cstop=cstop, maxNumber=-1):
                zeroFiles.append(fli["id"])
        except Exception, e:
            logging.exception(e)
            problem = True
            break

    timeTaken = str(datetime.now() - start)
    if problem:
        logging.info("Caching finished UNSUCCESSFULLY at {} and took {}".format(datetime.now(), timeTaken))
    else:
        logging.info("Caching finished successfully at {} and took {}".format(datetime.now(), timeTaken))
    json.dump(zeroFiles, open(trackZeroFile, "w"))
    
# ####################### Schema #####################
    
def cacheSchemas(config):

    start = datetime.now()
    
    ensureCacheLocations(config["stationNumber"])
    configLogging(config["stationNumber"], "cacherLog", config["logLevel"] if "logLevel" in config else "DEBUG")

    systemId = config["stationNumber"] if "name" not in config else "{} [{}]".format(config["name"], config["stationNumber"])
    logging.info("Caching Schema of VistA {} [PID {}]".format(systemId, os.getpid()))

    fmqlIF = makeFMQLIF(config)
    
    schemaCacheLocation = SCHEMA_LOCN_TEMPL.format(config["stationNumber"])
    query = "SELECT TYPES"
    try:
        jreply = json.load(open(schemaCacheLocation + "SELECT_TYPES.json"))
    except:
        logging.info("First time through - must (re)cache {} to {} ...".format(query, schemaCacheLocation))
        jreply = fmqlIF.invokeQuery(query)
        json.dump(jreply, open(schemaCacheLocation + "SELECT_TYPES.json", "w"))

    fileIds = [re.sub(r'\.', "_", result["number"]) for result in jreply["results"]]
    logging.info("Must cache schema of {} files".format(len(fileIds)))

    alreadyCached = [re.match(r'SCHEMA\_([^\.]+)', f).group(1) for f in os.listdir(schemaCacheLocation) if os.path.isfile(os.path.join(schemaCacheLocation, f)) and re.search('\.json$', f) and re.match("SCHEMA_", f)]
    for i, fileId in enumerate(fileIds, 1):
        if fileId in alreadyCached:
            logging.info("{}. Schema of {} Already Cached".format(i, fileId))
            continue
        logging.info("{}. Caching Schema of {}".format(i, fileId))
        query = "DESCRIBE TYPE " + fileId
        queryStart = datetime.now()
        jreply = fmqlIF.invokeQuery(query)
        json.dump(jreply, open(schemaCacheLocation + "SCHEMA_" + fileId + ".json", "w"))

    # Phase 2 - cache SELECT TYPE REFS
    alreadyCached = [re.match(r'REFS\_([^\.]+)', f).group(1) for f in os.listdir(schemaCacheLocation) if os.path.isfile(os.path.join(schemaCacheLocation, f)) and re.search('\.json$', f) and re.match("REFS\_", f)]
    for i, fileId in enumerate(fileIds, 1):
        if fileId in alreadyCached:
            logging.info("{}. Refs of {} Already Cached".format(i, fileId))
            continue
        logging.info("{}. Caching Refs of {}".format(i, fileId))
        query = "SELECT TYPE REFS " + fileId
        queryStart = datetime.now()
        jreply = fmqlIF.invokeQuery(query)
        json.dump(jreply, open(schemaCacheLocation + "REFS_" + fileId + ".json", "w"))
        
    timeTaken = str(datetime.now() - start)
    logging.info("Caching SCHEMA/REF finished successfully at {} for {} files and took {}".format(datetime.now(), len(fileIds), timeTaken))
    
# #################### FMQLIF wrapper (schema and data) #######################
    
def makeFMQLIF(config):
    # Should work for CSP and 'regular' REST endpoint
    if "fmqlEP" in config:
        fmqlIF = FMQLRESTIF(config["fmqlEP"], epWord=config["fmqlQuery"])
        logging.info("Using REST Interface {}".format(config["fmqlEP"]))
    else:
        if "broker" not in config:
            raise Exception("Exiting - invalid 'config': neither 'broker' nor REST ('fmqlEP') settings available")
        # Must a/c for cypher in OSEHRA being different than Cypher in regular production VISTA (or maybe not if Vagrant VISTA is changed!)
        osehraVISTA = config["broker"]["osehraVISTA"] if "osehraVISTA" in config["broker"] else False
        fmqlIF = FMQLBrokerIF(config["broker"]["hostname"], config["broker"]["port"], config["broker"]["access"], config["broker"]["verify"], osehraVISTA=osehraVISTA)
        logging.info("Using RPC Broker Interface {}:{}".format(config["broker"]["hostname"], config["broker"]["port"]))
    return fmqlIF

# ############################# Driver ####################################
    
# ./cacher.py {ConfigBase} [SCHEMA] where Config is in ConfigFile.json
def main():

    assert(sys.version_info >= (2,7))

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

    try:
        if len(sys.argv) == 3:
            if sys.argv[2] == "SCHEMA":
                cacheSchemas(config)
            else:
                print "Invalid second argument {} when only SCHEMA|REPORT allowed - exiting".format(sys.argv[2])
        else:
            cacheData(config)
    except Exception, e:
        # common issue is base location doesn't exist or isn't writable
        print "Unable to proceed: {} - exiting".format(str(e))
        return

if __name__ == "__main__":
    main()

