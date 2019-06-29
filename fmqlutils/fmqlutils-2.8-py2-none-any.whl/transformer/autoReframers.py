#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json
from datetime import datetime
import re
from collections import defaultdict, OrderedDict
from shutil import copy2
import random
import logging

from transform import Transformer, SchemaBasedTransformer

"""
Basic transforms that are either [1] schema independent (ex/ make properties camel case) or [2] completely and
independently guided by schema (ex/ boolean codes or group properties by location)

Configurable reframes (those requiring manual specification) such as "pruning properties" or "promoting significant
multiples" or grouping properties into subobjects using location (gotta name the subobject prop!) are in 
ConfigurableTransforms 

NOTE: some of these (use urns, embed station number etc) may go into V2 and V2er
"""

"""
Background: FMQL uses underscore form (x_yz) for property names. This leaves
camel case form (xYz) for reframeed, normalized data.

Transform: turn underscore property names into camel case equivalents  

Issue: street_addr_1 goes to streetAddr_1 ... consider streetAddr1
"""
class CamelCaseProperties(Transformer):

    def __init__(self):
        ID = "CamelCaseProperties"
        DESCRIPTION = "Turn _ form of DM in FMQL fileman data into camel case form"
        super(CamelCaseProperties, self).__init__(ID, DESCRIPTION) # TODO: add if Order independent

    def transform(self, record):

        trecord = OrderedDict() # Preserve order as transform 

        # Simple - nothing special for id, label etc and not suppressing ien here
        for prop in record:
            mprop = CamelCaseProperties.toCamelcase(prop) if re.search(r'\_', prop) else prop
            # dive into list of contained objects - won't dive into list of dates or list of pointers
            if self._isContainedObjectList(record[prop]):
                trecord[mprop] = []
                for srecord in record[prop]:
                    trecord[mprop].append(self.transform(srecord))
                continue
            trecord[mprop] = record[prop]

        return trecord

    @staticmethod
    def toCamelcase(string):
        if string[0] == "_":
            string = string[1:] # clipping it off! ex _test in 68
        string = string[0].lower() + string[1:]  # lowercase first
        return re.sub(
        r'[\_]+(?P<first>[a-z])',              # match spaces followed by \w
        lambda m: m.group('first').upper(),    # get following \w and upper()
        string)

"""
Move ids to URN form based on station number of vista (if local) and explicit identification of national entities
"""
class URNIds(Transformer):

    def __init__(self, stationNumber, nationalFMTypes=set()):
        ID = "URNIds"
        DESCRIPTION = "Turn all ids into URN form"
        super(URNIds, self).__init__(ID, DESCRIPTION)
        self.__stationNumber = stationNumber
        self.__nationalFMTypes = nationalFMTypes

    def transform(self, record):

        def toURN(fmId):
            fmType = fmId.split("-")[0]
            if fmType in self.__nationalFMTypes:
                return "urn:national:{}".format(re.sub(r'\-', ":", fmId))
            return "urn:vista:{}:{}".format(self.__stationNumber, re.sub(r'\-', ":", fmId)) 

        for prop in record:
            if prop in ["id", "_id"]:
                record[prop] = toURN(record[prop])
                continue
            if self._isPointer(record[prop]):
                record[prop]["id"] = toURN(record[prop]["id"])
                continue
            if self._isPointerList(record[prop]):
                for pvalue in record[prop]:
                    pvalue["id"] = toURN(pvalue["id"])
                continue
            # Dive down
            if self._isContainedObjectList(record[prop]):
                for srecord in record[prop]:
                    self.transform(srecord)

        return record

"""
Adding Station Number property to all Local (non National) Objects
"""
class AddStationNumberProperty(Transformer):

    def __init__(self, stationNumber):
        ID = "AddStationNumberProperty"
        DESCRIPTION = "Add station number property explicitly - makes multi-VISTA database easy to query"
        super(AddStationNumberProperty, self).__init__(ID, DESCRIPTION)
        self.__stationNumber = stationNumber

    def transform(self, record):
        idProp = "id" if "id" in record else "_id"
        if not re.match(r'urn:', record[idProp]):
            raise Exception("Station Number must come after URN transform")
        if re.search(r':national:', record[idProp]):
            return record # no need for local station if national file
        record["localStationNumber"] = int(self.__stationNumber)
        return record

"""
Obfuscate 100 digit NPI
... first of a series of obfuscators
"""
class ObfuscateNPI200(Transformer):

    def __init__(self):
        ID = "ObfuscateNPI"
        DESCRIPTION = "If realish dataset, obfuscates NPI"
        super(ObfuscateNPI200, self).__init__(ID, DESCRIPTION)
        self.__seen = set()
        self.__mismatchPersons = set()
                
    """
    npi top level property and inside 
    """
    def transform(self, record):
        idProp = "id" if "id" in record else "_id"
        if not re.match(r'200\-', record[idProp]):
            return record
        if "npi" not in record:
            return record
        tnpi = record["npi"]
        rnpi = self._randNPI()
        record["npi"] = rnpi
        if "effective_date_time" in record:
            for edt in record["effective_date_time"]:
                if "npi" not in edt:
                    continue
                if edt["npi"] != tnpi:
                    self.__mismatchPersons.add(record[idProp])
                edt["npi"] = rnpi
        return record   

    def seen(self):
        return self.__seen

    def mismatchPersons(self): # different NPI from main NPI in EDT
        return self.__mismatchPersons
                  
    def _randNPI(self):
        npi = ''.join(["%s" % random.randint(0, 9) for num in range(0, 10)])
        if npi in self.__seen:
            return self._randNPI()
        self.__seen.add(npi)
        return npi 

"""
Flatten Multiples (contained objects):
- remove their ien
- remove empty lists ie [] (happens with stopped cnodes in v2) 
  ... TODO: monitor
- if only one 'proper' property ("Singleton Multiple") then reduce to simple list
          from [{pred: value}, {pred: value} ...] to [value, value ...]

TODO: see match of mult prop and contained prop (associations/associations) or not
as pattern and its effect. ie/ only flatten if the same? reverse ex is 50_68's secondaryVaDrugClass
is multiple ... should be secondaryVaDrugClasses or 8989_51's keyword, should be keywords
"""
class FlattenMultiples(SchemaBasedTransformer):

    def __init__(self, schemaInfos):
        ID = "FlattenMultiples"
        DESCRIPTION = "Flatten Multiples/Contained Object Lists if singletons and remove ien and empty lists"
        super(FlattenMultiples, self).__init__(schemaInfos, ID, DESCRIPTION)
        # May change to only keep one type at a time 
        self.__multiplePPathsByType = defaultdict(dict)
        # Trace singletons
        self.__singletonsSeenByType = defaultdict(list)

    def transform(self, record):
        schemaInfo = self._lookupSchemaInfo(record["type"])
        if not schemaInfo: 
            raise Exception("Can't find schema definition of {}".format(record["type"]))
        if schemaInfo["id"] not in self.__multiplePPathsByType:
            self.__isolateMultiplePPaths(schemaInfo["id"], schemaInfo)
        if len(self.__multiplePPathsByType[schemaInfo["id"]]) == 0:
            return record
        self.__reframe(record, self.__multiplePPathsByType[schemaInfo["id"]])
        return record

    def reportSingletonsSeen(self):
        return self.__singletonsSeenByType

    def __reframe(self, record, multiplePaths, ppath=[]):
        for prop in record:
            # Set path
            tppath = ppath[:]
            tppath.append(prop)
            # Flatten completely if singleton
            if "/".join(tppath) not in multiplePaths:
                continue
            # Corruption of old data - ex/ 50/*atc cannister overwriting mult atc canister
            if not isinstance(record[prop], list):
                continue
            # Nix ien
            for srecord in record[prop]:
                if "ien" in srecord: # allow for it to be missing
                    del srecord["ien"]
            # Clean out empty members
            # ... empty value (ex/ 50_606-26 in FOIA jan 18) means invalid value (usually pointer) for only property
            record[prop] = [srecord for srecord in record[prop] if len(srecord.keys()) > 0]
            if len(record[prop]) == 0:
                del record[prop]
                continue
            # Flatten completely if singleton
            if multiplePaths["/".join(tppath)] == 1:
                record[prop] = [srecord[srecord.keys()[0]] for srecord in record[prop]]
                continue # don't expect multiple in multiple
            for srecord in record[prop]:
                self.__reframe(srecord, multiplePaths, tppath)
        return record

    # if mult and note no props (so can isolate singletons)
    def __isolateMultiplePPaths(self, topType, schemaInfo, ppath=[]):
        for propInfo in schemaInfo["properties"]:
            tppath = ppath[:]
            tppath.append(propInfo["id"])
            if propInfo["type"] != "MULTIPLE":
                continue
            if "bad" in propInfo:
                continue
            mschemaInfo = self._lookupSchemaInfo(propInfo["childId"])
            self.__multiplePPathsByType[topType]["/".join(tppath)] = len(mschemaInfo["properties"])
            if len(mschemaInfo["properties"]) == 1:
                self.__singletonsSeenByType[topType].append("/".join(tppath))
            # Dive
            self.__isolateMultiplePPaths(topType, mschemaInfo, tppath)

"""
Booleans from one and two value codes

Must be combos: 0:N, N:N, N:NO, 0:0 and 1:Y, Y:Y, Y:YES, 1:1

So this excludes exs like:
    1:ASK, 0:DON'T ASK
    0:NO MENUS GENERATED, 1:YES, MENUS GENERATED

Note that it also suppresses bad booleans ie/ if property should be boolean but value doesn't
fit expected range, then the assertion is suppressed.

Note: was in FMQL v1.* but too much of a heuristic to be baked into MUMPS
"""
class BooleanTwoValueCodes(SchemaBasedTransformer):

    def __init__(self, schemaInfos, suppressBadBooleans=True):
        ID = "BooleanTwoValueCodes"
        DESCRIPTION = "Turn one and two value YES/NO codes into Booleans. Also gather changed properties which are candidates for 'isX' form"
        super(BooleanTwoValueCodes, self).__init__(schemaInfos, ID, DESCRIPTION)
        self.__booleanPPathsByType = {}
        self.__badBooleanAssertions = defaultdict(dict)

    def transform(self, record):
        idProp = "id" if "id" in record else "_id"
        self.__topRecordId = record[idProp]
        schemaInfo = self._lookupSchemaInfo(record["type"])
        if not schemaInfo:
            return record
        if schemaInfo["id"] not in self.__booleanPPathsByType:
            self.__booleanPPathsByType[schemaInfo["id"]] = []
            self.__isolateBooleanPPaths(schemaInfo["id"], schemaInfo)
        if len(self.__booleanPPathsByType[schemaInfo["id"]]) == 0:
            return record
        self.__reframe(record, self.__booleanPPathsByType[schemaInfo["id"]])
        return record

    def reportData(self):
        return self.__badBooleanAssertions

    def __reframe(self, record, booleanPaths, ppath=[]):
        for prop in record:
            # Set path
            tppath = ppath[:]
            tppath.append(prop)
            if self._isContainedObjectList(record[prop]):
                for srecord in record[prop]:
                    self.__reframe(srecord, booleanPaths, tppath)
                continue
            # allow for DM 1 form where already boolean!
            tppaths = "/".join(tppath)
            if tppaths in booleanPaths and not isinstance(record[prop], bool):
                # Be strict as possible to have non valid value! Will log that and pass on
                if re.match(r'[1Y]', record[prop]):
                    record[prop] = True
                elif re.match(r'[0N]', record[prop]):
                    record[prop] = False
                else:
                    logging.info("[{}] Bad boolean assertion {}:{}".format(self.__id, tppaths, record[prop]))
                    self.__badBooleanAssertions[self.__topRecordId][tppaths] = record[prop]
                    if self.__suppressBadBooleans:
                        del record[prop]
        return record

    def __isolateBooleanPPaths(self, topType, schemaInfo, ppath=[]):
        for propInfo in schemaInfo["properties"]:
            tppath = ppath[:]
            tppath.append(propInfo["id"])
            if propInfo["type"] == "MULTIPLE" and "bad" not in propInfo:
                mschemaInfo = self._lookupSchemaInfo(propInfo["childId"])
                self.__isolateBooleanPPaths(topType, mschemaInfo, tppath)
                continue
            # 1 or 2 value Code - Note: shouldn't see DM V1 'boolean' as it is typed CODES_BOOLEAN
            if not (propInfo["type"] == "CODES" and len(propInfo["range"]) < 3):
                continue
            upperValues = [code.upper() for code in propInfo["range"]]
            if sum(1 for code in upperValues if code in set(["Y:YES", "N:NO", "1:YES", "0:NO", "Y:Y", "N:N", "0:0", "1:1"])) == len(upperValues):
                self.__booleanPPathsByType[topType].append("/".join(tppath))

"""
Flatten coded values IVALUE:EVALUE to EVALUE
"""
class FlattenCodesToExternals(SchemaBasedTransformer):

    def __init__(self, schemaInfos):
        ID = "FlattenCodesToExternals"
        DESCRIPTION = "Flatten codes from IVALUE:EVALUE to EVALUE"
        super(FlattenCodesToExternals, self).__init__(schemaInfos, ID, DESCRIPTION)
        self.__codePPathsByType = {}

    def transform(self, record):
        schemaInfo = self._lookupSchemaInfo(record["type"])
        if not schemaInfo:
            return record
        if schemaInfo["id"] not in self.__codePPathsByType:
            self.__codePPathsByType[schemaInfo["id"]] = []
            self.__isolateCodePPaths(schemaInfo["id"], schemaInfo)
        if len(self.__codePPathsByType[schemaInfo["id"]]) == 0:
            return record
        self.__reframe(record, self.__codePPathsByType[schemaInfo["id"]])
        return record

    def __reframe(self, record, codePaths, ppath=[]):
        for prop in record:
            # Set path
            tppath = ppath[:]
            tppath.append(prop)
            if self._isContainedObjectList(record[prop]):
                for srecord in record[prop]:
                    self.__reframe(srecord, codePaths, tppath)
                continue
            # allow for codes already turned into bools
            if "/".join(tppath) in codePaths and not isinstance(record[prop], bool) and re.search(r':', record[prop]):
                record[prop] = record[prop].split(":")[1]
        return record

    def __isolateCodePPaths(self, topType, schemaInfo, ppath=[]):
        for propInfo in schemaInfo["properties"]:
            tppath = ppath[:]
            tppath.append(propInfo["id"])
            if propInfo["type"] == "MULTIPLE" and "bad" not in propInfo:
                mschemaInfo = self._lookupSchemaInfo(propInfo["childId"])
                self.__isolateCodePPaths(topType, mschemaInfo, tppath)
                continue
            if propInfo["type"] != "CODES":
                continue
            self.__codePPathsByType[topType].append("/".join(tppath))

"""
Remove meta "fmqlStopped"
"""
class SuppressStopped(Transformer):

    def __init__(self):
        ID = "SuppressStopped"
        DESCRIPTION = "Remove 'stopped' annotation"
        super(SuppressStopped, self).__init__(ID, DESCRIPTION)

    def transform(self, record):

        for stopProp in ["fmqlStopped", "fmqlHasStops"]:
            if stopProp in record:
                del record[stopProp]
            
        for prop in record:
            if not self._isContainedObjectList(record[prop]):
                continue
            for srecord in record[prop]:
                self.transform(srecord)

        return record

"""
Grouping under locations unless already multiples where they group as usual. Applies
to large flat objects like Patient. 

TODO: 
- schema to change so it has camel case already ie/ make part of schema per se and not a CamelCaseTransformer to decide
- move pnameMap to camelcasers ie/ option to do explicitly too
- multiples map (ie/ go down)
"""
class ByLocationReframer(SchemaBasedTransformer):

    def __init__(self, schemaInfos, locationGroupNames, skipLocns=["0"], pnameMap={}, dictTo1List=False, suppressIfNoLocnMap=False):
        ID = "ByLocationReframer"
        DESCRIPTION = "Reframe patient based on Location"
        super(ByLocationReframer, self).__init__(schemaInfos, ID, DESCRIPTION)
        self.__locationGroupNames = locationGroupNames
        self.__skipLocns = skipLocns
        self.__pnameMap = pnameMap
        self.__suppressIfNoLocnMap = suppressIfNoLocnMap
        self.__dictTo1List = dictTo1List # rather than x: {}, x: [{}]
        
        self.__unmappedLocnsSeen = defaultdict(int)
        
    def transform(self, record):
        return self.__transform(record)
        
    def __transform(self, record, plocnPlace=""):
        schemaInfo = self._lookupSchemaInfo(record["type"])
        if not schemaInfo: 
            raise Exception("Can't find schema definition of {}".format(record["type"]))
        idProp = "id" if "id" in record else "_id"
        newRecord = OrderedDict([(idProp, record[idProp]), ("type", record["type"]), ("label", record["label"])])
        for propDefn in schemaInfo["properties"]:
            # grouping under place (which may be renamed)
            if "ccid" not in propDefn: # not yet in schema info at start
                ccPropId = CamelCaseProperties.toCamelcase(propDefn["id"])
                propDefn["ccid"] = ccPropId
            if propDefn["ccid"] not in record:
                continue
            nccid = propDefn["ccid"] if propDefn["ccid"] not in self.__pnameMap else self.__pnameMap[propDefn["ccid"]]
            if propDefn["type"] == "MULTIPLE":
                newRecord[nccid] = record[propDefn["ccid"]]
                continue # only top level
            locnPlace = propDefn["fmLocation"].split(";")[0]
            if locnPlace in self.__skipLocns: # often leave 0; alone
                newRecord[nccid] = record[propDefn["ccid"]]
                continue
            if locnPlace in self.__locationGroupNames: # assuming ONLY at top level?
                locnPlace = self.__locationGroupNames[locnPlace]
            else: 
                self.__unmappedLocnsSeen[locnPlace] += 1
                if self.__suppressIfNoLocnMap: # still record seen but don't map
                    continue
            if locnPlace not in newRecord:
                newRecord[locnPlace] = [OrderedDict()] if self.__dictTo1List else OrderedDict()
            if self.__dictTo1List:
                newRecord[locnPlace][0][nccid] = record[propDefn["ccid"]]  
            else:
                newRecord[locnPlace][nccid] = record[propDefn["ccid"]]                  
        # TODO: may need to change to make the group an array of one - see ex in Schema
        return newRecord
        
    def reportUnmappedLocations(self):
        return self.__unmappedLocnsSeen
        
