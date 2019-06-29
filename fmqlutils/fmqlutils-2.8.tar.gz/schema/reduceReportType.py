#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import re
import json
from collections import defaultdict
from datetime import datetime
import logging

from ..transformer.transform import Transformer
from ..reporter.reportUtils import reportAbsAndPercent

"""
Using data, defines a type according to the presence and (selectively) the frequency distribution of the values of properties. Optionally splits on the values of one or more nominal properties to distinguish finer 'subtypes'.

REM: VistA typing/files/collections n enums etc often too broad, too narrow or muddy.
(Sub)Typing pictures VistA but often needs better categorization/groupings, things
refined from reframing the data first and this utility does allow for that.

TODO: 
- in general: see one use of u' below. Consider that everywhere OR from __future__ import unicode_literals but the latter may need stricters formats (442:8927/items that tries this)
- see below: separation of reporter/jsonschema etc [will move reporter into reporter module and go to making simple site] generation from type info
  
Arguments:
- subTypeProps: one or more properties used to subtype by. Note that
pointer label is used for pointer properties
- createDateProp: isolates the property that designates the creation date of a record
- maxNominalValues: for pointer or literals - by default won't be counted once
distinct value count exceeds this threshold. Ensures type reduction doesn't become
a large restatement of the records 
- countDateMonth: by default only counts dates by year
- forceCountPointerTypes: these pointer values are counted even if they exceed the maxNominalValues threshold.
- forceCountProperties: applies to both POINTER and LITERAL (usually enums) properties. Usually just for enums but may be used for variable pointer pointers too
- deidentifyPointerTypes: remove label from these (PATIENT set by default)

Note that there is a default set of FORCE_COUNTED PTER TYPEs covering user (200),
locations and patient.
"""
DEFAULT_MAX_NOMINAL_VALUES = 60 # maxNominalValues=60 as 55 is # dialogs of 100
DEFAULT_FORCE_COUNT_PTER_TYPES = ["4", "44", "200"] # user, location, patient
USER_NAME_TYPES = ["220_5"]
DEFAULT_FORCE_COUNT_PTER_TYPES.extend(USER_NAME_TYPES)
PATIENT_NAME_TYPES = ["2", "9000001", "55", "63", "70", "631", "665", "690", "790", "38_1"] # mainly dinumed, 2005 as its label has id info
DEFAULT_FORCE_COUNT_PTER_TYPES.extend(PATIENT_NAME_TYPES)

class SubTypeReducer(Transformer):
    
    def __init__(self, typId, subTypeProps, createDateProp="", maxNominalValues=DEFAULT_MAX_NOMINAL_VALUES, countDateMonth=False, forceCountPointerTypes=DEFAULT_FORCE_COUNT_PTER_TYPES, forceCountProperties=[], deidentifyPointerTypes=PATIENT_NAME_TYPES):
    
        self.__typId = typId
        self.__subTypeProps = subTypeProps
        self.__createDateProp = createDateProp
        self.__maxNominalValues = maxNominalValues
        self.__countDateMonth = countDateMonth
        self.__forceCountPointerTypes = set(forceCountPointerTypes)
        self.__forceCountProperties = set(forceCountProperties)
        self.__deidentifyPointerTypes = set(deidentifyPointerTypes)
        
        self.__typeReducers = {}
        # minimal for 'all' option as sub types have details
        self.__allTypeReducer = TypeReducer(
            self.__typId, 
            createDateProp=self.__createDateProp, 
            maxNominalValues=self.__maxNominalValues, 
            countDateMonth=False, 
            forceCountPointerTypes=[], 
            forceCountProperties=[],
            deidentifyPointerTypes=self.__deidentifyPointerTypes
        ) 
                    
    def transform(self, resource):
        # for all
        self.__allTypeReducer.transform(resource)  
        
        # will create a (Sub)TypeReducer for any combos seen - REM: pointer label used
        pieces = ["-".join(self.__subTypeProps)]
        for stp in self.__subTypeProps:      
            if stp not in resource:
                stpv = "**NOVALUE**"
            elif re.search(r':p', stp):
                stpv = "**HASVALUE**" 
            else:
                if isinstance(resource[stp], dict):
                    if "value" in resource[stp]: # will only split by year
                        stpv = resource[stp]["value"].split("-")[0]
                    elif "label" in resource[stp]:
                        stpv = "{} [{}]".format(resource[stp]["label"], resource[stp]["id"])
                    else: # should never happen
                        raise Exception("Expect structured value of sub type property {} to be a POINTER or DATE (Year)".format(stp))
                elif isinstance(resource[stp], bool):
                    stpv = str(resource[stp])
                elif len(resource[stp].split(":")) == 2: # enum (allows more complex : to stay)
                    stpv = resource[stp].split(":")[1]
                else:
                    stpv = resource[stp]
            pieces.append(re.sub(r' ', '_', stpv))
        subTypeId = ":".join(pieces)
        typeReducer = self.__lookupSubTypeReducer(subTypeId)
        typeReducer.transform(resource)
        
    def reductions(self):
        results = []
        allReduction = self.__allTypeReducer.reduction()
        results.append(allReduction)
        allTotal = allReduction["_total"]
        for subTypeId in self.__typeReducers:
            reduction = self.__typeReducers[subTypeId].reduction()
            reduction["_subTypeId"] = subTypeId
            reduction["_numberFiltered"] = allTotal - reduction["_total"]
            results.append(reduction)
        return results
        
    def __lookupSubTypeReducer(self, subTypeId):
    
        if subTypeId not in self.__typeReducers:
            self.__typeReducers[subTypeId] = TypeReducer(
                self.__typId, 
                createDateProp=self.__createDateProp, 
                maxNominalValues=self.__maxNominalValues, 
                countDateMonth=self.__countDateMonth, 
                forceCountPointerTypes=self.__forceCountPointerTypes, 
                forceCountProperties=self.__forceCountProperties, 
                deidentifyPointerTypes=self.__deidentifyPointerTypes
            )
            
        return self.__typeReducers[subTypeId]
                            
class TypeReducer(Transformer):

    def __init__(self, typId, reductionLabel="", createDateProp="", maxNominalValues=DEFAULT_MAX_NOMINAL_VALUES, countDateMonth=False, forceCountPointerTypes=DEFAULT_FORCE_COUNT_PTER_TYPES, forceCountProperties=[], deidentifyPointerTypes=PATIENT_NAME_TYPES):
    
        self.__typId = typId
        self.__createDateProp = createDateProp
        self.__maxNominalValues = maxNominalValues
        self.__countDateMonth = countDateMonth
        self.__forceCountPointerTypes = set(forceCountPointerTypes)
        self.__forceCountProperties = set(forceCountProperties)
        self.__deidentifyPointerTypes = set(deidentifyPointerTypes)

        self.__dontCountLiteralProp = set()
        self.__distinctPointerValuesByProp = defaultdict(lambda: set())
        self.__typeData = {"_total": 0, "_id": typId}
        if reductionLabel: # REM: filter can make a different subset
            self.__typeData["_reductionLabel"] = reductionLabel
        if createDateProp and not callable(createDateProp):
            self.__typeData["_createDateProp"] = createDateProp

    def transform(self, resource):
        self.__reduce(resource, self.__typeData)
        
    def reductions(self):
        return [self.__typeData]

    def reduction(self):
        return self.__typeData

    """
    Works for both contained resources and resources
    """
    def __reduce(self, resource, typeData, parentPropPath=""):

        def isPointer(value):
            if len(value.keys()) == 0:
                return False # shouldn't happen but some synthesized has {} value
            if len(set(value.keys()) - set(["id", "sameAs", "sameAsLabel", "label"])):
                return False
            return True
        
        def typeProp(value): # WHAT ABOUT BOOLEAN?
            if isinstance(value, bool):
                return "BOOLEAN"
            if isinstance(value, int):
                return "INTEGER"
            if isinstance(value, dict):
                if "value" in value:
                    return "DATE"
                elif isPointer(value):
                    return "POINTER"
                else: # assuming - and needn't have an 'id'
                    return "OBJECT"
            if isinstance(value, list):
                return "LIST" # TODO - simple list work ie/ not {"x": y ...} but [y ...]
            return "LITERAL"

        def getDateValueAsString(dtValue):
            # allowing for {u'type': u'xsd:dateTime', u'value': datetime.datetime(1996, 8, 28, 2, 3, 58)}
            # ... deprecated now - will remove with Mongo import update
            if isinstance(dtValue, datetime):
                dtValue = dtValue.isoformat()
                return dtValue
            if re.match(r'\d\d\d\d\-\d\d\-\d\d', dtValue):
                yr = int(dtValue.split("-")[0])
                if yr < 1800 or yr > 2100:
                    return ""
                return dtValue # could still be corrupt
            return ""

        def getCreateDate(resource, createDateProp):
            if not createDateProp:
                return ""
            if callable(createDateProp):
                return createDateProp(resource) 
            # Allow for real date and a pointer who's label is a date!
            if createDateProp in resource and isinstance(resource[createDateProp], dict):
                if "value" in resource[createDateProp]:
                    return getDateValueAsString(resource[createDateProp]["value"])
                elif "label" in resource[createDateProp]:
                    return getDateValueAsString(resource[createDateProp]["label"])
            return ""
    
        # at start, assume all literals are enums AND handle booleans here too
        def countByLiteralValue(qprop, propInfo, litValue): 
            if qprop in self.__dontCountLiteralProp:
                return
            # First exclusion: if long then a real literal and not just a value 
            # (NOTE: bool's fall in here too)
            if isinstance(litValue, basestring) and qprop not in self.__forceCountProperties and len(litValue.split(" ")) > 5:
                self.__dontCountLiteralProp.add(qprop)
                if "byValueCount" in propInfo:
                    del propInfo["byValueCount"]
                return
            if "byValueCount" not in propInfo:
                propInfo["byValueCount"] = { litValue: 1 }
                return
            if litValue not in propInfo["byValueCount"]:
                # second exclusion - too many but can force a pass 
                if qprop not in self.__forceCountProperties and len(propInfo["byValueCount"]) == self.__maxNominalValues:
                    self.__dontCountLiteralProp.add(qprop)
                    del propInfo["byValueCount"]
                    return 
                propInfo["byValueCount"][litValue] = 0
            propInfo["byValueCount"][litValue] +=1

        def countByPointerValue(qprop, propInfo, ptrValue):
            """
            Either 
            - count distinct values (if large number) OR
            - count by if:
              - small as acts as enum (ie/ <= enum threshold)
              - forced to count (usually for 200/2)
            - accounts for multiple prop and parent prop having same name by using
            qprop to track size
              
            TODO: 
            - distinct pointer values by prop could get big for self references of
            big types (2005 to 2005 etc). May need cut off there too
            - reconsider vptr with other overwhelming 200 or 4 etc (may never happen)
            """
            sptrValue = ptrValue
            if re.search(r'\[', ptrValue):
                sptrValue = re.search(r'\[([^\]]+)', ptrValue).group(1)
            MAX_RANGE_COUNT = 1000000 # for 2005 to 2005 etc.
            if qprop in self.__distinctPointerValuesByProp:
                if "rangeCount" in propInfo:
                    self.__distinctPointerValuesByProp[qprop].add(sptrValue)
                    if len(self.__distinctPointerValuesByProp[qprop]) == MAX_RANGE_COUNT:
                        logging.debug("Property {} has too big a range - >={:,} - so not even counting that".format(qprop, MAX_RANGE_COUNT))
                        del propInfo["rangeCount"]
                        self.__distinctPointerValuesByProp[qprop] == None
                    else: 
                        propInfo["rangeCount"] = len(self.__distinctPointerValuesByProp[qprop])
                return
            if "byValueCount" not in propInfo:
                propInfo["byValueCount"] = { ptrValue: 1 }
                return
            if ptrValue not in propInfo["byValueCount"]:
                ptrType = sptrValue.split("-")[0]
                """ 
                VPTRs present difficulties - if just a few of forced pointer then will
                fail to count em unless appear in first set
                
                TODO: may renew and simply record those forced - effected 442096
                """
                if not (qprop in self.__forceCountProperties or ptrType in self.__forceCountPointerTypes) and len(propInfo["byValueCount"]) == self.__maxNominalValues:
                    self.__distinctPointerValuesByProp[qprop] = set([
                        re.search(r'\[([^\]]+)', ptrValue).group(1) if re.search(r'\[', ptrValue) else ptrValue for ptrValue in propInfo["byValueCount"]])
                    propInfo["rangeCount"] = len(self.__distinctPointerValuesByProp[qprop])
                    del propInfo["byValueCount"]
                    logging.debug("Property {} is too big for byValueCount - just measure range".format(qprop))
                    return 
                propInfo["byValueCount"][ptrValue] = 0
            propInfo["byValueCount"][ptrValue] +=1
            
        # as opposed to reduction of all sresources, this establishes number per parent
        def countListValueByLength(propInfo, listValue):
            if "byValueCount" not in propInfo:
                propInfo["byValueCount"] = {}
            if len(listValue) in propInfo["byValueCount"]:
                propInfo["byValueCount"][len(listValue)] += 1
                return
            propInfo["byValueCount"][len(listValue)] = 1

        def countDateValue(propInfo, dtValue):
            """
            Break by Year
            """
            dtValueS = getDateValueAsString(dtValue)
            if dtValueS == "":
                return
            if self.__countDateMonth:
                dtToCount = dtValueS.split("-")[0] + "-" + dtValueS.split("-")[1]
            else:
                dtToCount = int(dtValueS.split("-")[0])
            if "byValueCount" not in propInfo:
                propInfo["byValueCount"] = {}
            if dtToCount in propInfo["byValueCount"]:
                propInfo["byValueCount"][dtToCount] += 1
            else:
                propInfo["byValueCount"][dtToCount] = 1

        typeData["_total"] += 1
        
        if "_firstIEN" not in typeData and len(set(resource.keys()).intersection(["_id", "id"])):
            idProp = "id" if "id" in resource else "_id"
            self.__typeData["_firstIEN"] = resource[idProp].split("-")[1]
                    
        # only applies to LIST props - full ones filled in below
        if "fmqlStopped" in resource:
            for propStopped in resource["fmqlStopped"]:
                if propStopped not in typeData:
                    typeData[propStopped] = { "count": 0, "type": "LIST"}
                typeData[propStopped]["count"] += 1
                if "cstopped" not in typeData[propStopped]:
                    typeData[propStopped]["cstopped"] = 1
                else:
                    typeData[propStopped]["cstopped"] += 1
        
        dateValues = []
        for prop in [key for key in resource.keys() if key not in ["id", "_id", "type", "label", "ien", "fmqlStopped"]]: 

            value = resource[prop] 

            if prop not in typeData:
                typeData[prop] = { "count": 1, "type": typeProp(value) }
                # if createDateProp - record first and last prop
            else:
                typeData[prop]["count"] += 1

            info = typeData[prop]
            
            qprop = prop if parentPropPath == "" else parentPropPath + "/" + prop

            # Not full proof as create date property may be absent
            # TODO FIX: flipped may not be in order ... need to fix first/last
            createDate = getCreateDate(resource, self.__createDateProp)
            if createDate:
                if "_firstCreateDate" not in typeData:
                    typeData["_firstCreateDate"] = createDate 
                    typeData["_numberPerCreateDay"] = {}
                if "firstCreateDate" not in info:
                    info["firstCreateDate"] = createDate 
                info["lastCreateDate"] = createDate 
                typeData["_lastCreateDate"] = createDate 

            # If info type not same as value type:
            # - [TODO] neither LITERAL
            # - info type is not LITERAL - skip and record bad literal
            # - info type is LITERAL - reset info with bad literal
            typ = typeProp(value)
            if typ != info["type"]:
                if info["type"] != "LITERAL":
                    if "badLiteralValues" not in info:
                        info["badLiteralValues"] = 0
                    info["badLiteralValues"] += 1
                    continue
                info = { "count": 1, "type": typ, "badLiteralValues": info["count"] }
                typeData[prop] = info
                
            if typeData[prop]["type"] == "LITERAL" or typeData[prop]["type"] == "BOOLEAN":
                countByLiteralValue(qprop, typeData[prop], value)
                continue
                
            if typeData[prop]["type"] == "POINTER":
                if "rangeTypes" not in typeData[prop]:
                    typeData[prop]["rangeTypes"] = [] # Allow variable ptr
                rangeType = value["id"].split("-")[0]
                if rangeType not in typeData[prop]["rangeTypes"]:
                    typeData[prop]["rangeTypes"].append(rangeType)
                ptrType = value["id"].split("-")[0]
                if "label" in value and ptrType not in self.__deidentifyPointerTypes:
                    ptrValue = u'{} [{}]'.format(value["label"], value["id"])
                else:
                    ptrValue = value["id"]
                countByPointerValue(qprop, typeData[prop], ptrValue)
                continue
                
            if typeData[prop]["type"] == "LIST":
                countListValueByLength(typeData[prop], value)
                if "reduction" not in typeData[prop]:
                    typeData[prop]["reduction"] = {"_total": 0}
                spropPath = prop if parentPropPath == "" else parentPropPath + "/" + prop
                for sresource in resource[prop]:
                    self.__reduce(sresource, typeData[prop]["reduction"], spropPath)
                continue
                
            if typeData[prop]["type"] == "DATE":
                countDateValue(typeData[prop], value["value"])
                dateValues.append((prop, value["value"]))

        # Post 1: first and last date values seen
        if len(dateValues) > 1: # capture which date property is first/last. Can vary. (effects Orders etc)
            if "_firstDateProps" not in typeData:
                typeData["_firstDateProps"] = {}
                typeData["_lastDateProps"] = {}
            dateValues = sorted(dateValues, key=lambda x: x[1])
            if dateValues[0][0] not in typeData["_firstDateProps"]:
                typeData["_firstDateProps"][dateValues[0][0]] = 0 
            typeData["_firstDateProps"][dateValues[0][0]] += 1
            if dateValues[-1][0] not in typeData["_lastDateProps"]:
                typeData["_lastDateProps"][dateValues[-1][0]] = 0
            typeData["_lastDateProps"][dateValues[-1][0]] += 1
                    
def reportReductions(typeDatas, outputFileName): # may get big
    try:
        os.remove(outputFileName) 
    except:
        pass
    if len(typeDatas) == 0:
        return # nothing to report
    flOut = open(outputFileName, "a")
    if len(typeDatas) == 1:
        flOut.write(reportReduction(typeDatas[0]))
        flOut.close()
        return
    allTypeDatas = [typeData for typeData in typeDatas if "_subTypeId" not in typeData]
    if len(allTypeDatas):
        if len(allTypeDatas) != 1:
            raise Exception("Expect one and only one ALL type data in a type data list")
        flOut.write("# All/Summary Report\n\n")
        flOut.write(reportReduction(allTypeDatas[0]))
    subTypeDatas = [typeData for typeData in typeDatas if "_subTypeId" in typeData]
    subTypeProp = subTypeDatas[0]["_subTypeId"].split(":")[0]
    flOut.write("\n\n# {:,} Sub Reports split by property \"{}\"\n\n".format(len(subTypeDatas), subTypeProp))
    for typeData in subTypeDatas:
        flOut.write(reportReduction(typeData))
    flOut.write("\n\n")
    flOut.close()

def reportReduction(typeData): # can use for a pass 2 as self contained

    def dtDelta(first, then): # Crude now - TODO more on timedelta, divmod and total_seconds 
        # delta = datetime.strptime(re.sub(r'Z$', '', then), "%Y-%m-%dT%H:%M:%S" ) - datetime.strptime(re.sub(r'Z$', '', first), "%Y-%m-%dT%H:%M:%S" )
        delta = int(then.split("-")[0]) - int(first.split("-")[0])
        return delta

    idMU = typeData["_id"] if "_label" not in typeData else "{} ({})".format(typeData["_id"], typeData["_label"])
    if "_subTypeId" in typeData:
        subTypeProp = typeData["_subTypeId"].split(":")[0]
        subTypeValue = typeData["_subTypeId"][len(subTypeProp) + 1:] # allow ':' prop val
        idMU += " property \"{}\" value \"{}\"".format(subTypeProp, subTypeValue)
    mu = "## {} Report\n\n".format(idMU)
    total = typeData["_total"]
    if "_numberFiltered" in typeData:
        filtered = typeData["_numberFiltered"]
        complete = total + filtered
        mu += "Total Selected: {}\n".format(reportAbsAndPercent(typeData["_total"], complete))
        mu += "Filtered: {}\n".format(reportAbsAndPercent(filtered, complete))
    else:
        mu += "Total: {:,}\n".format(total)
    if "_firstIEN" in typeData:
        mu += "First IEN: {}\n".format(typeData["_firstIEN"])
        
    # TODO: consider putting back once Filters back in ie/ what do Filters remove?
    if "_removedProps" in typeData: # like removedThresholds, from reducePass2Pass
        mu += "Properties Removed: {}\n".format(", ".join(typeData["_removedProps"]))
    if "_removedThresholds" in typeData:
        mu += "Thresholds Removed: {}\n".format(typeData["_removedThresholds"])
        
    if "_firstCreateDate" in typeData:
        mu += "Create Date Property: {}\n".format(typeData["_createDateProp"])
        mu += "First Create Date: {}\n".format(typeData["_firstCreateDate"])
        mu += "Last Create Date: {}\n".format(typeData["_lastCreateDate"])
        delta = dtDelta(typeData["_firstCreateDate"], typeData["_lastCreateDate"])
        if delta != 0:
            mu += "Span: {} years\n".format(delta)
    # prop that is the first or last date can vary
    if "_firstDateProps" in typeData:
        mu += "Order of Date Values (first/last dates):\n"
        mu += "\tFirsts:\n"
        for dp in sorted(typeData["_firstDateProps"].keys(), key=lambda x: typeData["_firstDateProps"][x], reverse=True):
            mu += "\t\t{} - {:,}\n".format(dp, typeData["_firstDateProps"][dp])  
        mu += "\tLasts:\n"
        for dp in sorted(typeData["_lastDateProps"].keys(), key=lambda x: typeData["_lastDateProps"][x], reverse=True): 
            mu += "\t\t{} - {:,}\n".format(dp, typeData["_lastDateProps"][dp])
    mu += "Properties:\n"
    atThreshold = 0 
    # .99999 (as using 'in between thresholds' is a bit of a kludge but ...) - can use in pass 2 reasoning for filter out edge edge
    thresholds = [1.0, 0.9999999999999, 0.99, 0.95, 0.9, 0.8, 0.5, 0.25, 0.1, 0.05]
    currentThresholdIndex = 0
    for j, prop in enumerate(sorted([key for key in typeData if not re.match(r'\_', key)], key=lambda x: typeData[x]["count"], reverse=True), 1):
        level = float(typeData[prop]["count"])/float(total)
        thresholdIndex = [i for i, t in enumerate(thresholds) if level <= t][-1] 
        if thresholdIndex != currentThresholdIndex:
            currentThresholdIndex = thresholdIndex
            mu += "\n\t------------- {}% cut off ------------------------\n".format(int(thresholds[thresholdIndex] * 100) if thresholdIndex > 1 else 100)
        propTypeMU = typeData[prop]["type"]
        mu += "\t{}. {} - {} - {:,} ({:.0%}){}{}\n".format(j, prop, propTypeMU, typeData[prop]["count"], float(typeData[prop]["count"])/float(total), (" - " + ", ".join(typeData[prop]["rangeTypes"]) if "rangeTypes" in typeData[prop] else ""), (" - " + typeData[prop]["firstCreateDate"].split("-")[0] + " --> " + typeData[prop]["lastCreateDate"].split("-")[0]) if "firstCreateDate" in typeData[prop] else "")
        if "badLiteralValues" in typeData[prop]:
            mu += "\t\t** Bad Literal Values: {}\n".format(typeData[prop]["badLiteralValues"])
        # enum | pointer | date | list - order by key if int - otherwise by value
        if "byValueCount" in typeData[prop]:  
            for j, enumValue in enumerate(sorted(typeData[prop]["byValueCount"], key=lambda x: x if isinstance(x, int) else typeData[prop]["byValueCount"][x], reverse=True), 1):
                if j > DEFAULT_MAX_NOMINAL_VALUES:
                    mu += "\t\t... only showing top {} of {}\n".format(DEFAULT_MAX_NOMINAL_VALUES, len(typeData[prop]["byValueCount"]))
                    break
                mu += u'\t\t{}. {} - {:,} ({:.1%})\n'.format(j, enumValue, typeData[prop]["byValueCount"][enumValue], float(typeData[prop]["byValueCount"][enumValue])/float(typeData[prop]["count"]))
        elif "rangeCount" in typeData[prop]: # big range pointer
            mu += "\t\tRange Count: {}\n".format(typeData[prop]["rangeCount"])
        if typeData[prop]["type"] == "LIST":
            FLIP_CANDIDATE_VARIETY = 50 # ie/ variability of size
            FLIP_CANDIDATE_SIZE = 10 # absolute size
            if "cstopped" in typeData[prop]: # only LIST
                mu += "\t\t**CSTOPed [FLIP CANDIDATE]: {:,} ({:.1%})\n".format(typeData[prop]["cstopped"], float(typeData[prop]["cstopped"])/float(typeData[prop]["count"]))
            elif len(typeData[prop]["byValueCount"]) > FLIP_CANDIDATE_VARIETY and sum(1 for listLen in typeData[prop]["byValueCount"] if int(listLen) > FLIP_CANDIDATE_SIZE):
                mu += "\t\t**FLIP CANDIDATE based on variety of lengths and size\n"
    mu += "\n\n"
    return mu
    
def thresholdProps(typeData):
    thresholds = [1.0, 0.99, 0.95, 0.9, 0.8, 0.5, 0.25, 0.1, 0.05]
    currentThresholdIndex = 0
    byThreshold = defaultdict(list)
    total = typeData["_total"]
    for j, prop in enumerate(sorted([key for key in typeData if not re.match(r'\_', key)], key=lambda x: typeData[x]["count"], reverse=True), 1):
        level = float(typeData[prop]["count"])/float(total)
        thresholdIndex = [i for i, t in enumerate(thresholds) if level <= t][-1]
        if thresholdIndex != currentThresholdIndex:
            currentThresholdIndex = thresholdIndex
        byThreshold[thresholds[currentThresholdIndex]].append(prop)
    return byThreshold

