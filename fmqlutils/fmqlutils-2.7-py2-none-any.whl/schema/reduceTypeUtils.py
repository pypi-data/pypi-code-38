#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import re
import json
from collections import OrderedDict
from datetime import datetime
import logging

from reduceReportTypes import TYPEREDUCE_LOCN_TEMPL

"""
Expect 1 ALL (returned first) and many sub's all of one property
"""
def splitTypeDatas(stationNo, typ, reductionLabel="", expectSubTypeProperty=""):
    typeDatas = json.load(open(TYPEREDUCE_LOCN_TEMPL.format(stationNo, "") + "{}{}Reduction.json".format(typ, reductionLabel)))
    if isinstance(typeDatas, dict): # old and dictionary only of ALL
        return typeDatas, []
    allTypeDatas = [typeData for typeData in typeDatas if "_subTypeId" not in typeData]
    if len(allTypeDatas):
        if len(allTypeDatas) != 1:
            raise Exception("Expect one and only one ALL type data in a type data list")
    allTypeData = allTypeDatas[0]
    subTypeDatas = [typeData for typeData in typeDatas if "_subTypeId" in typeData]
    if len(subTypeDatas):
        subTypeProp = subTypeDatas[0]["_subTypeId"].split(":")[0]
        if expectSubTypeProperty and subTypeProp != expectSubTypeProperty:
            raise Exception("Expect sub type prop \"{}\" and many splits but got \"{}\"".format(expectSubTypeProperty, subTypeProp))
    elif expectSubTypeProperty:
        raise Exception("No sub type datas but expect {} as sub type property".format(expectSubTypeProperty))
    return allTypeData, subTypeDatas
    
"""
Check Data: array of fileType and what's needed (array)
... ALL | TYPE | {REDUCTIONLABEL}

Ex/ [{"fileType": "3_081", "check": "TYPE"}]
"""
def checkDataPresent(stationNumber, dataToCheck):
    hasAll = True
    for dataInfo in dataToCheck:
        ftyp = dataInfo["fileType"]
        if not isinstance(dataInfo["check"], list):
            dataInfo["check"] = [dataInfo["check"]]
        checked = {}
        for toCheck in dataInfo["check"]:
            if toCheck == "ALL":
                # note: doesn't check completeness. One will do!
                fl = DATA_LOCN_TEMPL.format(stationNumber) + "{}-0.zip".format(ftyp)
                if not os.path.isfile(fl):
                    checked[toCheck] = False
                    hasAll = False
                else:
                    checked[toCheck] = True
                continue
            reductionLabel = toCheck if toCheck != "TYPE" else ""
            fl = TYPEREDUCE_LOCN_TEMPL.format(stationNumber, "") + "{}{}Reduction.json".format(ftyp, reductionLabel)
            if not os.path.isfile(fl):
                checked[toCheck] = False
                hasAll = False
            else:
                checked[toCheck] = True
        del dataInfo["check"]
        dataInfo["checked"] = checked
    return hasAll, dataToCheck
    
"""
Convenience function for manipulating type reductions

Note: no need for singleValueCount as if singleValue => red[prop]["count"] has value
"""
def singleValue(typeRed, prop, ifMissingValue=""):
    if prop not in typeRed:
        if ifMissingValue:
            return ifMissingValue
        raise Exception("Unexpected missing property {} of reduction".format(prop))
    if not ("byValueCount" in typeRed[prop] and len(typeRed[prop]["byValueCount"].keys()) == 1):
        raise Exception("Unexpected > 1 value for prop {} of reduction".format(prop))
    return typeRed[prop]["byValueCount"].keys()[0]
    
"""
TMP til finished: move reductions and their reports to new form

1. SO Reductions from custom directory to Base Directory keeping SO as qualifier
2. Base Reports from type{}.txt to {}Report.txt
3. SO Reports from custom directory to {}SOReport.txt
4. Delete custom SO Reduction and Report Directories
... once done, drop {} from TYPEREDUCE_LOCN_TEMPL and its sibling 
"""
    