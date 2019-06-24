#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import re
import json
from datetime import datetime
from collections import defaultdict, OrderedDict
import copy
import logging

from transform import SchemaBasedTransformer
from autoReframers import CamelCaseProperties

"""
Though a "transformers" by class, it doesn't transform. It derives type (data) from instance data. 

Note: for specialized MDM's (no DM), you can pass in enum and other
identifiers - otherwise rely on Enum designations in VistA's native schema

Use: make Mongo-friendly JSON Schema
Storage: usually with data of its type in /data/vista/{ssn}/...

TODO:
- add min, max for cardinality
- add unique for contents of lists
- report to diff Types from Data and/or suggest outliers like non float/int IENs or
numeric enum values mixed with alphanum etc
"""
class TypeFromData(SchemaBasedTransformer):

    def __init__(self, schemaInfos, enumsPerMDMType={}):
        ID = "TypeFromData"
        DESCRIPTION = "Make schema from data"
        super(TypeFromData, self).__init__(schemaInfos, ID, DESCRIPTION)

        # Can pass in explicit - otherwise comes from schema definition of types
        self.__enumsPerType = enumsPerMDMType

        """
        Qualified properties by type
        """
        self.__data = OrderedDict() 

    def transform(self, record):
        typ = record["type"]
        if typ not in self.__enumsPerType:
            schemaInfo = self._lookupSchemaInfo(typ)
            if not schemaInfo:
                raise Exception("No schema info for {} and enums not given explicitly".format(typ))
            self.__isolateCodePPaths(schemaInfo["id"], schemaInfo)
        self.__countProps(typ, record)

    def __urnPattern(self, urnId, soFar):
        pieces = urnId.split(":")
        lastPiece = urnId.split(":")[-1]
        lastPieceMatch = None
        # really broad alphanum appears in 19 - allowing ANY
        for lastPieceCMatch in [("\d+$", "INT"), ("[\d\.]+$", "FLOAT"), ("[\dA-Z]+$", "ALPHANUM"), (".+$", "ANY")]:
            if re.match(lastPieceCMatch[0], lastPiece):
                lastPieceMatch = lastPieceCMatch[1] 
                break
        del pieces[-1]
        base = ":".join(pieces)
        if len(pieces) == 4: # vista:local form
            pieces[2] = "\d+" # station is numeric
            base = ":".join(pieces)
        if base not in soFar:
            soFar[base] = {}
        if lastPieceMatch not in soFar[base]:
            soFar[base][lastPieceMatch] = 0
        soFar[base][lastPieceMatch] += 1

    def __countProps(self, typ, record, mqprop=""):

        """
        Note that property order is preserved if JSON of records preserved order but that order is decided largely by
        the first records passed in. An alternative could preserve order but also bucket by frequency 
        """
        if typ not in self.__data:
            self.__data[typ] = OrderedDict([("id", OrderedDict()), ("count", 1), ("properties", OrderedDict())])
            self.__urnPattern(record["id"], self.__data[typ]["id"])
        elif mqprop == "":
            self.__data[typ]["count"] += 1
            self.__urnPattern(record["id"], self.__data[typ]["id"])

        def typeSimple(svalue):
            if isinstance(svalue, bool):
                propType = "BOOLEAN"
            # not seen in exs as currently transform ints to strings by default for safety
            elif isinstance(svalue, int):
                propType = "INTEGER"
            elif isinstance(svalue, unicode):
                propType = "STRING"
            else:
                raise Exception("Unexpected simple list value: {} - {} - {}".format(json.dumps(record, indent=4), prop, json.dumps(record[prop][0])))
            return propType

        for prop in record:

            # Leaving in ien as needed in Concept/Synonym (may revisit)
            # Leaving in label in embedded object as needed in concept synoymn
            if prop in ["id", "type"]:
                continue
            if mqprop == "" and prop == "label":
                continue

            qprop = prop if not mqprop else "{}/{}".format(mqprop, prop)

            if self._isPointer(record[prop]):
                self.__recordProp(typ, qprop, "POINTER")
                self.__urnPattern(record[prop]["id"], self.__data[typ]["properties"][qprop]["pointerPatterns"])
                continue

            if self._isPointerList(record[prop]):
                self.__recordProp(typ, qprop, "[POINTER]")
                pps = self.__data[typ]["properties"][qprop]["pointerPatterns"]
                for ptrRef in record[prop]:
                    ptr = ptrRef["id"]
                    self.__urnPattern(ptr, pps)
                continue

            if self._isDateTime(record[prop]):
                self.__recordProp(typ, qprop, "DATETIME")
                continue

            if self._isContainedObject(record[prop]):
                self.__recordProp(typ, qprop, "OBJECT")
                self.__countProps(typ, record[prop], qprop)
                continue

            if self._isContainedObjectList(record[prop]):
                self.__recordProp(typ, qprop, "[OBJECT]")
                for element in record[prop]:
                    self.__data[typ]["properties"][qprop]["elementCount"] += 1
                    self.__countProps(typ, element, qprop)
                continue

            if isinstance(record[prop], list):
                if typ in self.__enumsPerType and qprop in self.__enumsPerType[typ]:
                    self.__recordProp(typ, qprop, "[ENUM]")
                    for value in record[prop]:
                        if value not in self.__data[typ]["properties"][qprop]["enumValues"]:
                            self.__data[typ]["properties"][qprop]["enumValues"][value] = 0
                        self.__data[typ]["properties"][qprop]["enumValues"][value] += 1
                else:
                    stype = typeSimple(record[prop][0])
                    self.__recordProp(typ, qprop, "[{}]".format(stype))
                self.__data[typ]["properties"][qprop]["elementCount"] += len(record[prop])
                continue

            if typ in self.__enumsPerType and qprop in self.__enumsPerType[typ]:
                self.__recordProp(typ, qprop, "ENUM")
                if record[prop] not in self.__data[typ]["properties"][qprop]["enumValues"]:
                    self.__data[typ]["properties"][qprop]["enumValues"][record[prop]] = 0
                self.__data[typ]["properties"][qprop]["enumValues"][record[prop]] += 1
                continue

            self.__recordProp(typ, qprop, typeSimple(record[prop]))

        return record

    def __recordProp(self, typ, qprop, propType):
        if qprop not in self.__data[typ]["properties"]:
            self.__data[typ]["properties"][qprop] = OrderedDict([("count", 0), ("type", propType)])
            if re.match(r'\[', propType):
                self.__data[typ]["properties"][qprop]["elementCount"] = 0
            if re.search(r'ENUM', propType):
                self.__data[typ]["properties"][qprop]["enumValues"] = {}
            if re.search(r'POINTER', propType):
                self.__data[typ]["properties"][qprop]["pointerPatterns"] = {}
        self.__data[typ]["properties"][qprop]["count"] += 1
        # This should NOT happen - ie pipeline should enforce one type BUT allowing for it - schema will default to STRING
        if self.__data[typ]["properties"][qprop]["type"] != propType:
            if "allTypesSeen" not in self.__data[typ]["properties"][qprop]:
                self.__data[typ]["properties"][qprop]["allTypesSeen"] = [self.__data[typ]["properties"][qprop]["type"]]
            if propType not in self.__data[typ]["properties"][qprop]["allTypesSeen"]:
                self.__data[typ]["properties"][qprop]["allTypesSeen"].append(propType)
            logging.debug("** warning: > 1 property type - {} - {} - for {}".format(qprop, self.__data[typ]["properties"][qprop]["allTypesSeen"], typ))

    def schemaFromData(self):
        return self.__data

    def __isolateCodePPaths(self, topType, schemaInfo, ppath=[]):
        for propInfo in schemaInfo["properties"]:
            tppath = ppath[:]
            # must make sure camel case
            prop = CamelCaseProperties.toCamelcase(propInfo["id"])
            tppath.append(prop)
            if propInfo["type"] == "MULTIPLE" and "bad" not in propInfo:
                mschemaInfo = self._lookupSchemaInfo(propInfo["childId"])
                self.__isolateCodePPaths(topType, mschemaInfo, tppath)
                continue
            if propInfo["type"] != "CODES":
                continue
            if topType not in self.__enumsPerType:
                self.__enumsPerType[topType] = []
            self.__enumsPerType[topType].append("/".join(tppath))

# ############################# Example of Use ####################################

def main():

    """
    Want new names/matching (may need to regen data)
    Try Parameters (enum off schema)
    Want DM form generated (ie/ not mongo per se) 
    Add schema gen to meta pipeline 
    """
    MDM_ENUMS = {"CONCEPT-757_01": ["codes/activationDetails/status"]}
    stationNumber = "999"
    DMSCHEMA_LOCN_TEMPLATE = "/data/vista/{}/Schema/"
    DMTEMPWORKING_LOCN_TEMPLATE = "/data/vista/{}/TmpWorking/"
    schemaLocation = DMSCHEMA_LOCN_TEMPLATE.format(stationNumber)
    tmpWorkingLocation = DMTEMPWORKING_LOCN_TEMPLATE.format(stationNumber)
    try:
        schemaSummary = json.load(open(tmpWorkingLocation + "schemaSummary.json"))
    except:
        schemaSummary = generateSchemaSummary(schemaLocation, tmpWorkingLocation)
    sfd = TypeFromData(schemaSummary, MDM_ENUMS)
    NL = "Local"
    onlyType = "19"
    for fl in [fl for fl in os.listdir("/data/vista/999/Meta/{}/".format(NL)) if re.search(r'-{}-'.format(onlyType), fl)]:
        if re.match(r'LexiconWordFrequencies', fl): 
            continue
        print "\tType Reducing file {}".format(fl)
        if re.search(r'json$', fl): 
            records = json.load(open("/data/vista/{}/Meta/{}/{}".format(stationNumber, nl, fl)), object_pairs_hook=OrderedDict)
        else:
            jfl = re.sub(r'zip$', 'json', fl)
            zfName = "/data/vista/{}/Meta/{}/{}".format(stationNumber, nl, fl)
            zf = zipfile.ZipFile(zfName, "r")   
            records = json.loads(zf.read(jfl), object_pairs_hook=OrderedDict)
        records = json.load(open("/data/vista/999/Meta/{}/{}".format(NL, fl)), object_pairs_hook=OrderedDict)
        for record in records: 
            sfd.transform(record)
    data = sfd.schemaFromData()
    json.dump(data, open("TestOutput.json", "w"), indent=4)

if __name__ == "__main__":
    main()
