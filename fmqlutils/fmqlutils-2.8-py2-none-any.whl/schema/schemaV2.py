#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json
from datetime import datetime
import re

"""
TMP: Makes V2 Schema

- id is type of data ex/ PATIENT-2
- keep fmId for easy, unambig lookup (called fmId)
- location in properties as need (called fmLocation)
... note: all the fmX makes it easy to split out a DM without the fm
"""
def generateSchemaSummary(schemaLocn, tmpWorkingLocation):

    reducedDefns = []
    reducedDefnsByFMId = {}
    mpropsByChildFMId = {}
    RESERVED_PROPS = ["id", "_id", "type", "value", "parent", "label", "ien"] # to match new form (ex/ type in 19 qualified)
    for sfl in os.listdir(schemaLocn):
        if not re.match(r'SCHEMA', sfl):
            continue
        schemaJSON = json.load(open(schemaLocn + sfl))
        info = {"fmId": schemaJSON["number"], "properties": []}
        info["id"] = schemaJSON["name"] + "-" + re.sub(r'\.', '_', schemaJSON["number"])
        reducedDefnsByFMId[schemaJSON["number"]] = info
        if "parent" in schemaJSON:
            info["parentFMId"] = schemaJSON["parent"]
            if len(schemaJSON["fields"]) == 1:
                info["isSingleton"] = True
        if "description" in schemaJSON:
            info["description"] = schemaJSON["description"]["value"]
        for fieldInfo in schemaJSON["fields"]:
            if "location" not in fieldInfo:
                continue # computed prop
            pred = fieldInfo["pred"]
            # See that 44: "type2"/ 19: "type4" is captured and now flattened in transforms
            if pred in RESERVED_PROPS: # to match V2 qualification
                pred = "{}_{}".format(pred, re.sub(r'\.', '_', fieldInfo["number"]))
            if re.match(r'\d', pred): # applied in v2er too don't want numbers starting properties
                pred = "_" + pred
            propInfo = {"id": pred, "fmId": fieldInfo["number"], "fmLocation": fieldInfo["location"], "fmFlags": fieldInfo["flags"]} # want locn for grouping
            if pred != fieldInfo["pred"]:
                propInfo["origPred"] = fieldInfo["pred"]
            info["properties"].append(propInfo)
            # ****** fill in type for all - embed enum here that will use in FMQL
            propInfo["type"] = "TO BE FILLED IN"
            if fieldInfo["type"] == "9": # Multiple - only see fmId
                mpropsByChildFMId[fieldInfo["details"]] = fieldInfo["pred"]
                propInfo["type"] = "MULTIPLE" # need to spec 'multiple' below
                propInfo["fmChildId"] = fieldInfo["details"]
                continue
            # For Older FMQL too (as its data will have boolean
            if fieldInfo["type"] in ["3", "12"]: # boolean is codes too
                codesIE = [codeIE for codeIE in fieldInfo["details"].split(";") if codeIE != ""]
                propInfo["type"] = "CODES_BOOLEAN" if fieldInfo["type"] == "12" else "CODES"
                propInfo["range"] = codesIE
                continue
        reducedDefns.append(info)

    # Fill in holes in hierarchy - multiple gets parent's full id and property; parent gets multiple's id
    for info in reducedDefns:
        if "parentFMId" in info:
            pinfo = reducedDefnsByFMId[info["parentFMId"]]
            info["parent"] = pinfo["id"]
            info["parentProperty"] = mpropsByChildFMId[info["fmId"]] # want children to have parent property (do in FM schema too)
        for propInfo in info["properties"]:
            if "type" in propInfo and propInfo["type"] == "MULTIPLE":
                if propInfo["fmChildId"] not in reducedDefnsByFMId:
                    propInfo["bad"] = True
                    print "*** Saw bad property - multiple has invalid range: {}", propInfo
                else:
                    propInfo["childId"] = reducedDefnsByFMId[propInfo["fmChildId"]]["id"]

    json.dump(reducedDefns, open(tmpWorkingLocation + "schemaSummary.json", "w"))

    return reducedDefns 
