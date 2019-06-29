#!/usr/bin/env python
# -*- coding: utf8 -*-

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU Affero General Public License version 3 (AGPL) 
# as published by the Free Software Foundation.
# (c) 2018 caregraf
#

import os
import re
import json
from collections import defaultdict
from datetime import datetime
from collections import OrderedDict
import logging

"""
Takes whole Reply

If want V2 stand alone:

    for i, fl in enumerate(os.listdir(dm1Location), 1):
        oldReply = json.load(open(dm1Location + fl), object_pairs_hook=OrderedDict)
        newReply = v1To2Transformer.transformReply(oldReply)
        json.dump(newReply, open(dm2Location + fl, "w"), indent=4)

"""
class OldReplyToNew:

    def __init__(self):
        self.__recordTransformer = OldRecordToNew()
        
    def transformReply(self, reply):
        
        # TODO: make new form including cnode settings
        nreply = OrderedDict()
        for key in reply:
            if key == "count": 
                continue # don't want count
            if key == "results":
                nreply[key] = []
                continue
            # This will include queryTook, queryComplete if there in V1
            nreply[key] = reply[key]
        
        for result in reply["results"]:
            nresult = self.__recordTransformer.transform(result)
            if not nresult:
                raise Exception("Couldn't transform (cstopped)", json.dumps(result))
            nreply["results"].append(nresult)
        
        return nreply

"""
Looks like a Standard Transformer (as per record) but wouldn't be part of a typical pipeline.
Transformation from old to new FMQL record form would happen during cache iteration.

Uses self explanatory result

NOTE: stopped leads to 'fmqlStopped' property in record entry. REM: stopped is prelude
to flipping or caught in health check and leads to rerun. For now, just note it too.
"""
class OldRecordToNew:

    def __init__(self):

        ID = "OldRecordToNew"
        DESCRIPTION = "From DM V1 to DM V2 - DM in 1 was client-side"
        
    def transform(self, record):
        return self.__reframe(record)
        
    def __newType(self, record):
    
        typV2 = record["uri"]["label"].split("/")[0] + "-" + record["uri"]["value"].split("-")[0]

        # TODO: actually TYPELABEL from reply has correct value (as would schema? ... make schema backed?)
        TYP_MAP = {
            "STATION NUMBER TIME SENSITIVE-389_9": "STATION NUMBER (TIME SENSITIVE)-389_9",
            "ICD OPERATION_PROCEDURE-80_1": "ICD OPERATION/PROCEDURE-80_1",
            "USR AUTHORIZATION_SUBSCRIPTION-8930_1": "USR AUTHORIZATION/SUBSCRIPTION-8930_1",
            "OE_RR REPORT-101_24": "OE/RR REPORT-101_24",
            "OE_RR EPCS PARAMETERS-100_7": "OE/RR EPCS PARAMETERS-100_7",
            "NDC_UPN-50_67": "NDC/UPN-50_67",
            "SERVICE_SECTION-49": "SERVICE/SECTION-49",
            "SIGN_SYMPTOMS-120_83": "SIGN/SYMPTOMS-120_83"
        }
        if typV2 in TYP_MAP:
            typV2 = TYP_MAP[typV2]
            
        return typV2 
        
    def __newProp(self, prop, propValue):
        RESERVED_PROPS = ["id", "_id", "type", "value", "parent", "label", "ien"]
        if prop in RESERVED_PROPS:
            return "{}_{}".format(prop, re.sub(r'\.', '_', propValue["fmId"]))
        # Issue: NCName ::= (Letter | '_') (NCNameChar)* in http://www.w3.org/TR/1999/REC-xml-names-19990114/#NT-NCName BUT JSON allows a number etc first. We insert a _ if there is a number first. TBD: best done in FMQL to be consistent.
        if re.match(r'\d', prop):
            return "_" + prop
        return prop
        
    def __reframe(self, record, isMultiple=False):

        if not isMultiple:
            nrecord = OrderedDict([("id", record["uri"]["value"]), ("type", self.__newType(record))])
            self.__currentRecordId = record["uri"]["value"]
        else:
            ien = record["uri"]["value"].split("-")[1].split("_")[0]
            nrecord = OrderedDict([("ien", ien)])

        for prop in record:

            if prop in ["uri"]:
                continue

            propValue = record[prop]            
            nprop = self.__newProp(prop, propValue)

            # TODO: add to V1.* FMQL to note # of records which caused the CSTOP
            # ... want guidance
            if propValue["type"] == "cnodes": # fmType == "9"
                if "stopped" in propValue:
                    if "fmqlStopped" not in record:
                        nrecord["fmqlStopped"] = []
                    nrecord["fmqlStopped"].append(prop)
                    logging.info("Stopped property {} of {}".format(prop, record["uri"]["value"]))
                    continue
                nrecord[nprop] = []
                for i, srecord in enumerate(propValue["value"], 1):
                    nrecord[nprop].append(self.__reframe(srecord, True))
                continue
                        
            # Note: NOT enforcing a datetime.strptime(dateValue, "%Y-%m-%dT%H:%M:%S") etc
            if propValue["fmType"] == "1": # datetime
                if re.search(r'T00:00:00Z$', propValue["value"]):
                    nvalue = OrderedDict([("value", propValue["value"].split("T")[0] ), ("type", "xsd:date")])
                else:
                    nvalue = OrderedDict([("value", propValue["value"]), ("type", "xsd:dateTime")])
            elif propValue["fmType"] == "2": # treat numeric as literal just in case
                nvalue = propValue["value"]
            # or could just 'ivalue' in record[prop]
            elif propValue["fmType"] == "3": # type is literal
                nvalue = "{}:{}".format(propValue["ivalue"], propValue["value"])
            elif propValue["fmType"] == "4": # literal
                nvalue = propValue["value"]
            # 'datatype': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral too
            elif propValue["fmType"] == "5": 
                nvalue = re.sub(r'\r', '\n', propValue["value"])
            # 6: COMPUTED
            elif propValue["fmType"] in ["7", "8"]:
                nvalue = OrderedDict([("id", propValue["value"]), ("label", propValue["label"].split("/")[1])])
            # 9: MULTIPLE (above)
            elif propValue["fmType"] == "12": # Boolean, datetype == xsd:boolean
                # Fall back to literal (may revisit and suppress)
                if propValue["value"] not in ["true", "false"]:
                    nvalue = propValue["value"]
                else:
                    nvalue = True if propValue["value"] == "true" else False
            # Q C***, K VISTA
            # "10": "MUMPS",
            # "11": "IEN", # IEN match in .001
            else:
                raise Exception("UNEXPECTED TYPE {}".format(propValue["fmType"]))
                
            # Top level record has label <=> first prop (may drop)
            if len(nrecord) == 2 and "type" in nrecord:
                # 8989_5 and  8930_3 have ptr as .01
                if isinstance(nvalue, dict): # pter or date
                    nrecord["label"] = nvalue["label"] if "label" in nvalue else nvalue["value"]
                else: 
                    nrecord["label"] = nvalue
                
            nrecord[nprop] = nvalue
                            
        return nrecord
                
# ############################# Test Driver ####################################

import os
import sys

def main():

    # TODO: need boolean test + need full dateTime plus
    transformer = OldReplyToNew()
    exOldReply = json.load(open("/data/vista/999/DataV1/8930_3-0.json"), object_pairs_hook=OrderedDict)    # change for one with datetime, stop etc etc ie/ add into tests ... and see NMUMPS to make sure 
    print json.dumps(exOldReply, indent=4)
    newReply = transformer.transformReply(exOldReply)
    
    print json.dumps(newReply, indent=4)
        
if __name__ == "__main__":
    main()

