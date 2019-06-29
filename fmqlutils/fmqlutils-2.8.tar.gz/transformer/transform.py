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
import zipfile
 
def transform(transformerPipeline, fmqlReplyIterator, mdmDir, qualType=True, zipResults=True):
    
    countByType = defaultdict(int)
    noRecordsSeen = 0
    REPORT_THRESHOLD = 100000

    for reply in fmqlReplyIterator.next():
    
        mrecords = []
        
        for record in reply["results"]:

            mrecord = transformerPipeline.transform(record)
            if mrecord:
                mrecords.append(mrecord)
                
            noRecordsSeen += 1
            if (noRecordsSeen % REPORT_THRESHOLD) == 0:
                logging.debug("transformed {} more records - {} so far".format(REPORT_THRESHOLD, noRecordsSeen))

        if len(mrecords) == 0:
            continue
        
        if qualType: # use {TYPE}-{FMID}-# form ie/ prefix with type
            typPrefix = re.sub(r'[\/ ]', '_', mrecords[0]["type"])
        else:
            typPrefix = mrecords[0]["type"].split("-")[1] 

        if zipResults:
            mfl = "{}-{}.{}".format(typPrefix, reply["fmql"]["AFTERIEN"], "zip")
            zfName = "{}/{}".format(mdmDir + "/", mfl)
            zf = zipfile.ZipFile(zfName, "w", zipfile.ZIP_DEFLATED, allowZip64=True)
            jfl = re.sub(r'zip$', 'json', mfl)
            zf.writestr(jfl, json.dumps(mrecords))
        else:
            mfl = "{}-{}.{}".format(typPrefix, reply["fmql"]["AFTERIEN"], "json")                    
            logging.debug("Flushed {} into {}".format(len(mrecords), mfl))
            json.dump(mrecords, open(mdmDir + "/" + mfl, "w"), indent=4)
        
        countByType[mrecords[0]["type"]] += len(mrecords)
        
    return countByType

"""
Base class for all transformers
"""
class Transformer(object):

   def __init__(self, id, description=""):
       self.__id = id
       self.__description = description
       logging.debug("Initialized Transformer {} - {}".format(id, description))

   def id(self):
       return self.__id

   def description(self):
       return self.__description

   def transform(self):
       pass

   # ############### Value Typers - DM/MDM has specific framing. Can tell type from value without schema #######

   """
   A pointer list means a list of > 0 values which are pointers
   """
   def _isPointerList(self, value):
       if not isinstance(value, list): 
           return False
       if len(value) == 0:
           return False
       return self._isPointer(value[0])

   def _isPointer(self, value):
       if not isinstance(value, dict):
           return False
       return "id" in value and ((len(value) == 1) or (len(value) == 2 and "label" in value))
  
   """
   A value of a list is a contained object iff it is a dict and not a date or pointer
   """
   def _isContainedObjectList(self, value): 
       if not isinstance(value, list):
           return False
       if len(value) == 0:
           return False
       return self._isContainedObject(value[0])

   def _isContainedObject(self, value): 
       return isinstance(value, dict) and not (self._isPointer(value) or self._isDateTime(value))

   """
   Date
   """
   def _isDateTime(self, value):
       if not isinstance(value, dict):
           return False
       return (len(value.keys()) == 2 and "value" in value and "type" in value)

"""
It has the whole hierarchal schema - can therefore instantiate pipeline in one go

WARNING: schema-based transformers MUST COME BEFORE any transformer that renames properties (Camel case
or Custom nice namers). They rely on transformed data having schema property names
"""
class SchemaBasedTransformer(Transformer):

    def __init__(self, schemaInfos, id, description=""):
        super(SchemaBasedTransformer, self).__init__(id, description)
        self.__schemaInfosById = dict((schemaInfo["id"], schemaInfo) for schemaInfo in schemaInfos)

    def _lookupSchemaInfo(self, id): # ex/ PATIENT-2
        if id in self.__schemaInfosById:
            return self.__schemaInfosById[id]
        return None


"""
Apply registered transformers in order
"""
class TransformerPipeline: 

    def __init__(self, transformers):
        self.__transformers = transformers
        logging.debug("Transformer pipeline initialized with {} transformers - {}".format(len(transformers), ", ".join([transformer.id() for transformer in transformers])))
        
    def descriptions(self): # return transformer descriptions (use in README/reports)
        return [(transformer.id(), transformer.description()) for transformer in self.__pipeline]
    
    def transform(self, record):
        for transformer in self.__transformers:
            record = transformer.transform(record)
            if not record:
                break
        return record
