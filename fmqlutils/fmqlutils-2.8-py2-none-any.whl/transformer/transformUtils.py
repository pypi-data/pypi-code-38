#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json
from datetime import datetime
import re
from collections import defaultdict, OrderedDict
from shutil import copy2
import random

"""
A series of utilities to use when building Transforms

TODO: refine
"""

"""
Pass in schema definition and get (in json) a definition of location-based groupings

Note (from PATIENT-2) - some relevant ...

	.11
		street_address_line_1
		zip4
		street_address_line_2
		street_address_line_3
		city
		state
		zip_code
		county
		province
		postal_code
		country
		address_change_dt_tm
		address_change_source
		address_change_site
		bad_address_indicator
		address_change_user

        20
                date_esig_last_changed
                signature_block_printed_name
                signature_block_title
                electronic_signature_code

Some not ...

	NAME
		name_components
		kname_components
		k2name_components
		fathers_name_components
		mothers_name_components
		mothers_maiden_name_components
		ename_components
		e2name_components
		dname_components

"""
def groupPropertiesByLocation(schemaInfo):
    byLoc = defaultdict(list)
    for propInfo in schemaInfo["properties"]:
        fmLocation = propInfo["fmLocation"]
        fmLocFirst = fmLocation.split(";")[0]
        if fmLocFirst == "" or fmLocFirst == "0": # 0; are of all sorts
            continue
        byLoc[fmLocFirst].append(propInfo)
    # cull if not > 1
    byLoc = dict((loc, byLoc[loc]) for loc in byLoc if len(byLoc[loc]) > 1)
    return byLoc

"""
Fits with schema form needed for FMQL (vs one passed now)
"""
def generateVDMSummary(systemName, systemStationNumber):

    reducedDefns = []
    mpropsByChildId = {}
    schemaLocn = "/data/{}/JSON/".format(systemName)
    for sfl in os.listdir(schemaLocn):
        if not re.match(r'SCHEMA', sfl):
            continue
        schemaJSON = json.load(open(schemaLocn + sfl))
        info = {"id": schemaJSON["number"], "label": schemaJSON["name"]}
        if "parent" in schemaJSON:
            info["parent"] = schemaJSON["parent"]
            if len(schemaJSON["fields"]) == 1:
                info["isSingleton"] = True
        if "description" in schemaJSON:
            info["description"] = schemaJSON["description"]["value"]
        for fieldInfo in schemaJSON["fields"]:
            if fieldInfo["type"] == "9":
                mpropsByChildId[fieldInfo["details"]] = fieldInfo["pred"]
        reducedDefns.append(info)

    reducedDefnsById = dict((info["id"], info) for info in reducedDefns)

    # tops will get one or more child singleton paths (rem: no multiple types
    # in JSON
    for info in reducedDefns:
        if "parent" in info and "isSingleton" in info:
            pinfo = info
            path = []
            while True:
                if "parent" not in pinfo:
                    break
                path.insert(0, mpropsByChildId[pinfo["id"]])
                pinfo = reducedDefnsById[pinfo["parent"]]
            if "singletonPaths" not in pinfo:
                pinfo["singletonPaths"] = []
            pinfo["singletonPaths"].append("/".join(path))

    json.dump(reducedDefns, open("defnsCache/vdmSummary{}.json".format(systemStationNumber), "w"))

"""
Was part of generic walker on Cache - sub classing records based on filter functions and nature of properties. 

TODO: make into property based transformer/subsetter 
"""
class ResourceSubTypeFilter:

    def __init__(self, fmType=""):
        self.__fmType = fmType # allows you to avoid suffix of type
        self.__propertyValueRestrictions = {}
        self.__hasOneOfProperties = None
        self.__hasAllOfProperties = None
        self.__hasNoneOfProperties = None
        self.__filterFuncs = None

    def __str__(self):
        mu = ""
        if len(self.__propertyValueRestrictions):
            mu += "(" + " & ".join((p.split("-")[0] + "=" + str(v)) for p, v in self.__propertyValueRestrictions.iteritems()) + ")"
        def addMUPropSet(label, st, separate):
            smu = ""
            if not st: 
                return ""
            if separate:
                smu += " & " 
            smu += label + "(" + ", ".join(p.split("-")[0] for p in st) + ")"
            return smu
        mu += addMUPropSet("oneOf", self.__hasOneOfProperties, (mu != ""))
        mu += addMUPropSet("allOf", self.__hasAllOfProperties, (mu != ""))
        mu += addMUPropSet("noneOf", self.__hasNoneOfProperties, (mu != ""))
        if self.__filterFuncs:
            if mu:
                mu += " & " 
            mu += " & ".join("filter(" + ffInfo["descr"] + ")" for ffInfo in self.__filterFuncs)
        return mu

    def __suffixProperty(self, property):
        if not re.search(r'\-', property):
            return property + "-" + self.__fmType
        if not re.search(self.__fmType + "$", property):
            raise Exception("Property <" + property + "> must end in fmType " + self.__fmType)
        return property

    def restrictPropertyValue(self, property, value):
        self.__propertyValueRestrictions[self.__suffixProperty(property)] = value

    def hasOneOfProperties(self, properties):
        self.__hasOneOfProperties = set(self.__suffixProperty(property) for property in properties)

    def hasNoneOfProperties(self, properties):
        self.__hasNoneOfProperties = set(self.__suffixProperty(property) for property in properties)

    def hasAllOfProperties(self, properties):
        self.__hasAllOfProperties = set(self.__suffixProperty(property) for property in properties)

    def setFilterFuncs(self, ffInfos): # takes resource
        self.__filterFuncs = ffInfos

    def filter(self, resource):
        for property, value in self.__propertyValueRestrictions.iteritems():
            if property not in resource:
                return False
            if resource[property] != value:
                return False
        if self.__hasOneOfProperties and len(self.__hasOneOfProperties & set(resource.keys())) == 0:
            return False
        if self.__hasNoneOfProperties and len(self.__hasNoneOfProperties & set(resource.keys())) != 0:
            return False # EIE stuff
        if self.__hasAllOfProperties and not self.__hasAllOfProperties.issubset(set(resource.keys())):
            return False
        if self.__filterFuncs:
            for ffInfo in self.__filterFuncs:
                if not ffInfo["func"](resource):
                    return False
        return True

"""
VISTA dates 'spread' as always using $NOW so exact === won't catch <=> dates.
"""
def dateDiffOverThreshold(dt1, dt2, threshold):
    try:
        dtDiff = datetime.strptime(dt2, "%Y-%m-%dT%H:%M:%S") - datetime.strptime(dt1, "%Y-%m-%dT%H:%M:%S")
    except:
        print "can't diff", dt1, dt2
        return True
    if dtDiff.total_seconds() > threshold:
        return True
    return False
