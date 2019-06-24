#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
from datetime import datetime
import math
from collections import OrderedDict
import json

"""
Utilities for better handling RPC Arguments and creating RPC requests
"""

"""
- rpcArgTs: arguments can have template values that start with '$'
     ex/ $PATIENTIEN
- tAssigns: assign values to those templates
     ex/ "PATIENTIEN": 25
"""
def fillTemplateArguments(rpcArgTs, tAssigns):

    def makeTemplConcrete(tValue):
        tMatch = re.match(r'\$([A-Z]+)$', tValue)
        if tMatch:
            templVal = tMatch.group(1)
            if templVal not in tAssigns:
                raise Exception("Unexpected template value {}".format(templVal))
            return tAssigns[templVal]
        return tValue

    def mapDictValue(dictValue):
        for prop in dictValue:
            if isinstance(dictValue[prop], dict):
                raise Exception("Dont expect dict in dict")
            if isinstance(dictValue[prop], list):
                dictValue[prop] = mapListValue(dictValue[prop])
                continue
            dictValue[prop] = makeTemplConcrete(dictValue[prop])
        return dictValue

    def mapListValue(listValue):
        nlistValue = []
        for val in listValue:
            if isinstance(val, list):
                raise Exception("Dont expect list in list")
            if isinstance(val, dict):
                nlistValue.append(mapDictValue(val))
                continue
            nlistValue.append(makeTemplConcrete(val))
        return nlistValue

    return mapListValue(rpcArgTs)

"""
For display results - shift 
"""
def shiftMultiLineString(val):
    NEW_LINE = '\r\n';
    shifted = '';
    for line in val.split(NEW_LINE):
        shifted += '\t' + line + '\n';
    return shifted;

"""
RPC LIST (2)

'normal' languages distinguish lists/arrays (indexed values) and dictionaries (key:value). MUMPS doesn't and the RPC 
broker protocol is very "MUMPSY".

What would typically be rendered as:

     { "KEY1": "VALUE1" ... }

is serialized as ...

     { '"KEY1"': "VALUE1" ... } <---- note the key1 is quoted

And 

     [ "VALUE1" ... ]

is serialized as ...

     { "1": "VALUE1" ... }

In combination ...

    { "KEY1": [ "VALUE1" ... ] ... }

is serialized as ...

    { 
        '"KEY1",0': "1"
        '"KEY1",1': "VALUE1" 
    }

This utility will render dictionaries and lists and list values into a form suitable for the broker protocol
"""
def toRPCListForm(value):

    if not (isinstance(value, list) or isinstance(value, dict)):
        return value

    nvalue = OrderedDict()

    # Note: not doing list of list 
    if isinstance(value, list):
        for i, li in enumerate(value, 1):
            nvalue[str(i)] = li
        return nvalue

    # dict
    for key in value:
        if isinstance(value[key], list):
            nlvalue = toRPCListForm(value[key])
            nvalue['"{}",{}'.format(key, 0)] = len(value[key])
            for idx in nlvalue:
                nvalue['"{}",{}'.format(key, idx)] = nlvalue[idx] 
            continue
        nvalue['"{}"'.format(key)] = str(value[key])

    return nvalue  

"""
FileMan has its own date time form - 2018 = 38, 1918 = 28 etc

Ex/ datetime.now() [default] or datetime(2013, 9, 30, 7, 6, 5)

Ex of return form: 3180403.170544
"""
def toFMDateTime(value=None):
    if not value:
        value = datetime.now()
    fmYear = (int(math.floor(value.year / 100) - 17) * 100) + (value.year % 100)
    fmDate = "{}{:02d}{:02d}".format(fmYear, value.month, value.day)
    fmTime = "{:02d}{:02d}{:02d}".format(value.hour, value.minute, value.second)
    return "{}.{}".format(fmDate, fmTime)

"""
Captures to inputs
"""
def captureToSequence(captureFile, maps, excludePoll=True):
    capture = json.load(open(captureFile))
    sequenceData = OrderedDict([("description", "From {}".format(captureFile)), ("sequence", [])])
    rpcNames = set()

    # won't work for "3170207.200921^25^5;89^10^62*97:63"
    def mapToTemplate(value):
        if isinstance(value, dict):
            return value # can't map
        nvals = []
        for val in value.split("^"):
            if val in maps:
                nvals.append(maps[val])
            else:
                nvals.append(val)
        return "^".join(nvals)

    for cinfo in capture:
        targs = [mapToTemplate(arg) for arg in cinfo["input"]]
        rpcInfo = OrderedDict([("name", cinfo["name"]), ("args", targs)])
        if excludePoll and cinfo["name"] == "ORWCV POLL":
            continue
        rpcNames.add(cinfo["name"])
        sequenceData["sequence"].append(rpcInfo)
    print "Writing out Sequence from capture {} - rpcs {}".format(captureFile, rpcNames)
    json.dump(sequenceData, open("FROMCAPTURE_{}.json".format(captureFile.split(".")[0]), "w"), indent=4)

# ########################### Test and Example ######################

def main():

    maps = {"62": "63", "25": "25"} # could go to templ values too
    captureToSequence("capture-p3vitals.txt", maps)
    captureToSequence("capture-p3problems.txt", maps)
    return

    print
    print "SIMPLE:"
    print
    print toRPCListForm(["ONE", "TWO", "THREE"])
    print
    print toRPCListForm({"k1": "ONE", "k2": "TWO"})
    print
    print toRPCListForm({"k1": "ONE", "k2": "TWO", "k3": ["3ONE", "3TWO", "3THREE"]}) 
    print
    print

    print
    print "REAL FROM ALLERGY SAVE:"
    regularFormAllergyDetails = {
        "GMRAGNT": "SULFAPYRIDINE^88;PS(50.416,",
        "GMRATYPE": "D^Drug",
        "GMRASYMP": ["39^ANXIETY^^^"],
        "GMRAOBHX": "h^HISTORICAL"
    }
    print toRPCListForm(regularFormAllergyDetails)
    print

    print
    print "REAL FROM PROBLEM:" 
    regularFormProblemDetails = [
        'GMPFLD(.01)="521774^R69."', 
        'GMPFLD(.03)="0^"',
        'GMPFLD(.08)="3170316"'
    ]
    print toRPCListForm(regularFormProblemDetails)
    print

if __name__ == "__main__":
    main()

