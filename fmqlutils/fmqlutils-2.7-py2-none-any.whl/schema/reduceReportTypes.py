#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import re
import json
from collections import OrderedDict
from datetime import datetime
import logging

from .. import VISTA_DATA_BASE_DIR
from ..cacher.cacherUtils import FMQLReplyStore, FilteredResultIterator, BASE_LOCN_TEMPL, DATA_LOCN_TEMPL
from reduceReportType import TypeReducer, SubTypeReducer, reportReductions, DEFAULT_FORCE_COUNT_PTER_TYPES

DATAREDUCTION_LOCN_TEMPL = BASE_LOCN_TEMPL + "DataReductions/"
TYPEREDUCE_LOCN_TEMPL = DATAREDUCTION_LOCN_TEMPL + "Types{}/"
REPORTS_LOCN_TEMPL = BASE_LOCN_TEMPL + "Reports/"
TYPEREPORT_LOCN_TEMPL = REPORTS_LOCN_TEMPL + "Types{}/"

"""
As command, fmqltyper

Same pattern as v2er, cacher, using 
- [a] /data/vista/{STATIONNO}/... locations for reductions and reports and 
- [b] taking a configuration from the location the runtime runs from. 
- [c] that 'local' location is usually just a place for these configurations
- [d] onAndAfterDay/upToDay rely on create property and if set, want a "reductionLabel" to differentiate them

TODO:
- try yaml config https://pyyaml.org/wiki/PyYAMLDocumentation as can embed code 
easily ie/ include custom filters/enhancers inline so no need for custom ie/ can't
now invoke dynamically in command line
- for now, using print, not logging. May move over to one pattern 
"""

def reduceReportTypes(stationNumber, types, dataLocnTempl, forceRedo=False, createDate={}, reductionLabel="", subTypeProps={}, forceCountPointerTypesExtra={}, forceCountProperties={}, onAndAfterDay="", upToDay="", countDateMonth=False, customEnhancers={}):

    start = datetime.now()
    
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)    
    ch = logging.StreamHandler(sys.stdout)
    format = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(format)
    log.addHandler(ch)
    
    # Used to ensure 
    def ensureLocation(locn):
        if not os.path.isdir(locn):
            os.mkdir(locn)
        return locn
    ensureLocation(DATAREDUCTION_LOCN_TEMPL.format(stationNumber))
    ensureLocation(REPORTS_LOCN_TEMPL.format(stationNumber))
                    
    typesAndDates = dict((typId, createDate[typId] if typId in createDate else "") for typId in types)
    
    if onAndAfterDay:
        try:
            onAndAfterDay = datetime.strptime(onAndAfterDay, "%Y-%m-%d")
        except:
            raise Exception("Invalid 'on and after day': {}".format(onAndAfterDay))

    if upToDay:
        try:
            upToDay = datetime.strptime(upToDay, "%Y-%m-%d")
        except:
            raise Exception("Invalid 'up to day': {}".format(upToDay))
            
    if (upToDay or onAndAfterDay) and reductionLabel == "":
        raise Exception("You must name the reduction ('reductionLabel') for time limited ('onAndAfterDay'/'upToDay') reductions")
        
    def getCreateDay(resource, createDateProp):
        value = resource[createDateProp]["value"] if "value" in resource[createDateProp] else resource[createDateProp]["label"]
        dateValue = value.split("T")[0]
        try:
            dtValue = datetime.strptime(dateValue, "%Y-%m-%d")
        except: # ex/ of 9000010_23 SPO with YR-MTH-00 in Visit
            log.debug("Can't get create day as its date has invalid value: {}".format(dateValue))
            return None
        return dtValue
    
    logging.info("About to reduce (and report) on {} types, starting at {} [PID {}]".format(len(typesAndDates), start, os.getpid()))

    count = 0 # allow for 0 - no i defined
    filtered = 0      
    dataLocn = dataLocnTempl.format(stationNumber)  
    for i, typId in enumerate(sorted(typesAndDates, key=lambda x: float(re.sub(r'\_', '.', x))), 1):
            
        reductionLocn = ensureLocation(TYPEREDUCE_LOCN_TEMPL.format(stationNumber, ""))
        redFFL = "{}/{}{}Reduction.json".format(reductionLocn, typId, reductionLabel)
        
        if forceRedo == False and os.path.isfile(redFFL):
            logging.info("Not reducing (and reporting) {} as already exists and NOT forceredo".format(typId))
            continue

        logging.info("Reducing (and reporting) {}".format(typId))
        
        if onAndAfterDay:
            store = FMQLReplyStore(dataLocn)
            startAtReply = store.firstReplyFileOnOrAfterCreateDay(typId, typesAndDates[typId], onAndAfterDay)
            if startAtReply == "":
                logging.info("** Exiting: can't find Reply to start at on and after day {}, create property {}".format(onAndAfterDay, typesAndDates[typId]))
                break
            logging.debug("Configuring Iterator for on and after time: on or after day {}, create property {}, starting at reply {}".format(onAndAfterDay, typesAndDates[typId], startAtReply))
        else:
            startAtReply = ""
        resourceIter = FilteredResultIterator(dataLocn, typId, isOrdered=False, startAtReply=startAtReply)
        fcpts = DEFAULT_FORCE_COUNT_PTER_TYPES
        if typId in forceCountPointerTypesExtra:
            fcpts.extend(forceCountPointerTypesExtra[typId])
        fcps = forceCountProperties[typId] if typId in forceCountProperties else []
        if typId in subTypeProps: 
            if isinstance(subTypeProps[typId], list):
                stps = subTypeProps[typId]
            else:
                stps = [subTypeProps[typId]]
            logging.info("Subtyping by '{}'".format("-".join(stps)))
            rtr = SubTypeReducer(typId, createDateProp=typesAndDates[typId], subTypeProps=stps, forceCountPointerTypes=fcpts, forceCountProperties=fcps, countDateMonth=countDateMonth)
        else:
            rtr = TypeReducer(typId, createDateProp=typesAndDates[typId], forceCountPointerTypes=fcpts, forceCountProperties=fcps, countDateMonth=countDateMonth)
        customEnhancer = None
        if typId in customEnhancers:
            customEnhancer = customEnhancers[typId]
            
        msgThres = 50000 
        upToDayStopped = False   
        for i, resource in enumerate(resourceIter, 1):
            count += 1
            if i % msgThres == 0:
                logging.debug("Checked {} more resources for total of {:,}, so far filtered {:,}, now in reply {} - {}".format(msgThres, i, filtered, resourceIter.currentReplyFile(), datetime.now() - start))
            idProp = "id" if "id" in resource else "_id"
            if customEnhancer:
                resource = customEnhancer.enhance(resource)
                if not resource:
                    filtered += 1
                    continue
            if onAndAfterDay or upToDay:
                if typesAndDates[typId] not in resource:
                    filtered += 1
                    continue
                createDay = getCreateDay(resource, typesAndDates[typId])
                if not createDay:
                    filtered += 1
                    continue
                if onAndAfterDay and createDay < onAndAfterDay:
                    filtered += 1
                    continue
                if upToDay and createDay >= upToDay:
                    logging.debug("Stopped at 'up to day' {} for createDay {}".format(upToDay, createDay))
                    upToDayStopped = True
                    break 
            rtr.transform(resource)
            
        pattData = rtr.reductions()
        for red in pattData:
            red["_stationNumber"] = stationNumber
            if reductionLabel:
                red["_label"] = reductionLabel
        logging.debug("Finished processing {:,} resources, {:,} explicitly filtered - now serializing result".format(count, filtered))
        json.dump(pattData, open(redFFL, "w")) 

        logging.debug("Finished serializing at {} - now reporting result".format(datetime.now() - start))     
        reportLocn = ensureLocation(TYPEREPORT_LOCN_TEMPL.format(stationNumber, ""))
        reportReductions(pattData, "{}/{}{}Report.txt".format(reportLocn, typId, reductionLabel))
            
    logging.info("Finished processing {}, explicitly filtered {} at {} in {}".format(count, filtered, datetime.now(), datetime.now() - start))

# ############################# Driver ####################################

"""
Form of configs

    {
        "stationNumber": "999",
        "types": ["2"],
        "createDateByType": {"2": "date_entered_into_file" },
        "forceRedo": False
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

    # "types": [], "createDateByType": {"{TYPE}": "{creation_date_property}" ...}
    # ... if don't set "types" then all types will be used
    if "types" not in config or len(config["types"]) == 0:
        dataLocn = DATA_LOCN_TEMPL.format(stationNumber)    
        print "Typing ALL available data as no subset specified"
        types = FMQLReplyStore(dataLocn).availableTypes()
    else:
        types = config["types"]
            
    reduceReportTypes(
        stationNumber, 
        types,
        dataLocnTempl=DATA_LOCN_TEMPL if "dataLocationTemplate" not in config else config["dataLocationTemplate"], # rarely used and may nix
        forceRedo=(True if ("forceRedo" in config and config["forceRedo"] == True) else False),
        subTypeProps=(config["subTypeProps"] if "subTypeProps" in config else {}),
        createDate=({} if "createDate" not in config else config["createDate"]), 
        onAndAfterDay=(config["onAndAfterDay"] if "onAndAfterDay" in config else ""),
        upToDay=(config["upToDay"] if "upToDay" in config else ""),
        reductionLabel=(config["reductionLabel"] if "reductionLabel" in config else ""),
        countDateMonth=(True if "countDateMonth" in config and config["countDateMonth"] else False),
        forceCountProperties=(config["forceCountProperties"] if "forceCountProperties" in config else {}), 
        forceCountPointerTypesExtra=(config["forceCountPointerTypesExtra"] if "forceCountPointerTypesExtra" in config else {})
    )
        
if __name__ == "__main__":
    main()
    
