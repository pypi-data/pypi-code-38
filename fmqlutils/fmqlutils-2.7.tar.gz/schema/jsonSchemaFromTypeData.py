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
import shutil

"""
From type data summary (transformers.TypeFromData), generate MongoDB supported JSON Schema definition

Outside package that checks schema: https://pypi.org/project/jsonschema/

** Sibling of upcoming jsonSchemaFromFMQLSchema **

Some Links:
- https://docs.mongodb.com/manual/core/schema-validation/
- https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/#op._S_jsonSchema
- https://tools.ietf.org/html/draft-zyp-json-schema-04
- https://tools.ietf.org/html/draft-fge-json-schema-validation-00
- https://docs.mongodb.com/manual/reference/operator/query/type/#document-type-available-types
- https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/
"""
def toJSONSchemaMongo(typeData):

    # Choice is to list forms (can have mix of local and national) and make IEN
    # permissive if not INT
    # ... was an ex of 120_51-SPO2%
    def makeIdRegExp(patterns):
        pMUs = []
        for p in patterns:
            if len(patterns[p]) > 1 or patterns[p].keys()[0] != "INT":
                ienMU = ".+" # int or completely permissive
            else:
                ienMU = "\d+"
            pMUs.append("{}:{}".format(re.sub(r'urn:', '', p), ienMU))
        return "urn:{}$".format(pMUs[0] if len(pMUs) == 1 else "({})".format("|".join(sorted(pMUs))))

    POINTER_DEFN = OrderedDict([("type", "object"), ("properties", OrderedDict([("id", OrderedDict([("type", "string"), ("pattern", "")])), ("label", {"type": "string"})])), ("required", ["id", "label"])])

    BASE_DEFN_PROPS = OrderedDict([("_id", OrderedDict([("type", "string"), ("pattern", makeIdRegExp(typeData["id"]))])), ("label", {"type": "string"}), ("type", {"type": "string"})])

    """
    Just do Objects first
    """
    def createObjectDefinition(count, propInfos, level=0, parentQProp="", problemPropInfos={}):

        def pointerPropDefn(propInfo):
            defn = copy.deepcopy(POINTER_DEFN)
            defn["properties"]["id"]["pattern"] = makeIdRegExp(propInfo["pointerPatterns"])
            return defn

        properties = OrderedDict() if parentQProp else BASE_DEFN_PROPS
        # https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/#op._S_jsonSchema (interplay bsonType/type)
        simpleType = {
            "STRING": "string",
            "INTEGER": "number", # or int (32 bit) for bson
            "BOOLEAN": "boolean" # bool for bson
        }
        # Note: for VAM, need to add localStationNumber? iff local (ie/ not nationals)
        required = [] if parentQProp else ["_id", "label", "type"]
        for qprop in propInfos:
            noSl = len(qprop.split("/")) - 1
            if noSl != level:
                continue
            if parentQProp and not re.match(parentQProp, qprop):
                continue
            propInfo = propInfos[qprop]
            if "allTypesSeen" in propInfo:
                problemPropInfos[qprop] = propInfo
                continue
            prop = qprop.split("/")[-1]
            pcount = propInfo["count"]
            if pcount == count:
                required.append(prop)
            if propInfo["type"] in simpleType:
                defn = {"type": simpleType[propInfo["type"]]}
                properties[prop] = defn
                continue
            # Only basic or simple type that has to be bsontype
            if propInfo["type"] == "DATETIME":
                defn = {"bsonType": "date"}
                properties[prop] = defn
                continue
            if propInfo["type"] == "POINTER":
                properties[prop] = pointerPropDefn(propInfo)
                continue
            if propInfo["type"] == "ENUM":
                defn = {"enum": sorted([enumValue for enumValue in propInfo["enumValues"]])}
                properties[prop] = defn
                continue
            if propInfo["type"] == "OBJECT":
                properties[prop] = createObjectDefinition(pcount, propInfos, level+1, qprop, problemPropInfos=problemPropInfos)
                continue
            if re.match(r'\[', propInfo["type"]):
                if re.search(r'OBJECT', propInfo["type"]):
                    items = createObjectDefinition(propInfo["elementCount"], propInfos, level+1, qprop, problemPropInfos=problemPropInfos)
                elif re.search(r'ENUM', propInfo["type"]):
                    items = {"enum": sorted([enumValue for enumValue in propInfo["enumValues"]])}
                elif re.search(r'POINTER', propInfo["type"]):
                    items = pointerPropDefn(propInfo)
                else:
                    items = {"type": simpleType[re.search(r'\[([^\]]+)\]', propInfo["type"]).group(1)]}
                properties[prop] = OrderedDict([("type", "array"), ("items", items)])

        defn = OrderedDict([("type", "object"), ("properties", properties), ("additionalProperties", False)])
        if len(required):
            defn["required"] = required
        return defn

    totalRecords = typeData["count"]
    # Can't magically make booleans into strings where not already. Schema could become permissive but values would still vary. Need to correct.
    problemPropInfos = {}
    defn = createObjectDefinition(typeData["count"], typeData["properties"], problemPropInfos=problemPropInfos)
    if len(problemPropInfos):
        print "Can't generate Schema as ambiguous type for one or more properties:"
        for qprop in problemPropInfos:
            print "{} - {}. Can't do schema".format(qprop, json.dumps(problemPropInfos[qprop]))
        raise Exception("Stopping as {} problem properties".format(len(problemPropInfos)))
    return defn

