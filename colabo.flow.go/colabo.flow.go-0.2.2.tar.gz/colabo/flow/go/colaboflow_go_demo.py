# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import print_function

import random

from datetime import datetime
# import dateutil.parser

class ColaboFlowGoDemo():
    goRequestDefault = None
    stubDefault = None

    def __init__(self, flowName="basic-flow"):
        
        print("[ColaboFlowGoDemo] new flow created: %s" % (flowName))
        self.flow = []
        self.flowPointer = 0

    # ---------------------------------------------------------------------------------------
    # NOTE: SEQUENTIAL DATA FLOW: In this scenario, user can describe control flow order,
    # but the data flow HAS to follow the same control-flow 
    # (so data output of action `i` is the input for the action `i+1`)
    # ---------------------------------------------------------------------------------------

    # Add action in a sequence with
    # - action name and 
    # = reference to the function implementing it
    def addActionAsFunction(self, funcRef, actionName):
        action = {
            'name': actionName,
            'funcRef': funcRef
        }
        self.flow.append(action)
        # print(len(self.flow))
        return self

    # runs functions in a sequence
    # data input for the function `i+1` is data output of the function `i`
    def runWithSequentialDataFlow(self, dataIn):
        print("---")
        for action in self.flow:
            print("running action: ", action['name'])
            func = action['funcRef']
            result = func(dataIn)
            print("result: ", result)
            dataIn = result
            print("---")

    # ---------------------------------------------------------------------------------------
    # NOTE: DESCRIPTIVE_DATA_FLOW: In this way data flow doesn't need to follow control flow
    # but it can be described separtelly
    # ---------------------------------------------------------------------------------------

    # Add action in a sequence with
    # - action name
    # - reference to the function implementing it
    # - inputParameterName name that holds the input parameter
    def addActionAsFunctionWithInputParam(self, funcRef, actionName, inputParameterName=None):
        action = {
            'name': actionName,
            'funcRef': funcRef,
            'inputParameterName': inputParameterName
        }
        self.flow.append(action)
        # print(len(self.flow))
        return self

    def runWithDescriptiveDataFlow(self, dataName, dataIn):
        print("---")
        self.results = {}
        self.results[dataName] = dataIn
        for action in self.flow:
            # print("running action: ", action)
            print("running action: ", action['name'])
            func = action['funcRef']
            inputParameterName = action['inputParameterName']
            result = func(self.results[inputParameterName])
            self.results[action['name']] = result
            print("result: ", result)
            print("---")

    # ---------------------------------------------------------------------------------------
    # NOTE: DESCRIPTIVE_MULTIDATA_FLOW: data flow doesn't follow control flow
    # and it can have multiple input datasets
    # ---------------------------------------------------------------------------------------

    # Add action in a sequence with
    # - action name
    # - reference to the function implementing it
    # - inputParameterNames - list of names that hold input parameters
    def addActionAsFunctionWithInputParams(self, funcRef, actionName, inputParameterNames=None):
        action = {
            'name': actionName,
            'funcRef': funcRef,
            'inputParameterNames': inputParameterNames
        }
        self.flow.append(action)
        # print(len(self.flow))
        return self

    def runWithDescriptiveMultiDataFlow(self, dataName, dataIn):
        print("---")
        self.results = {}
        self.results[dataName] = dataIn
        for action in self.flow:
            # print("running action: ", action)
            print("running action: ", action['name'])
            func = action['funcRef']
            inputParameterNames = action['inputParameterNames']
            inputParameters = []
            for inputParameterName in inputParameterNames:
                  inputParameters.append(self.results[inputParameterName])
            result = func(*inputParameters)
            self.results[action['name']] = result
            print("result: ", result)
            print("---")

    # ---------------------------------------------------------------------------------------
    # NOTE: DESCRIPTIVE_MULTIDATAOUTPUT_FLOW: output data flow can have multiple datasets
    # each with its own name
    # ---------------------------------------------------------------------------------------

    # Add action in a sequence with
    # - action name
    # - reference to the function implementing it
    # - inputParameterNames - list of names that hold input parameters
    def addActionAsFunctionWithOutputParams(self, funcRef, actionName, inputParameterNames=None, outputParameterNames=None):
        action = {
            'name': actionName,
            'funcRef': funcRef,
            'inputParameterNames': inputParameterNames,
            'outputParameterNames': outputParameterNames
        }
        self.flow.append(action)
        # print(len(self.flow))
        return self

    def runWithDescriptiveOutDataFlow(self, dataName, dataIn):
        print("---")
        self.results = {}
        self.results[dataName] = dataIn
        for action in self.flow:
            # print("running action: ", action)
            print("running action: ", action['name'])
            func = action['funcRef']
            inputParameterNames = action['inputParameterNames']
            inputParameters = []
            for inputParameterName in inputParameterNames:
                  inputParameters.append(self.results[inputParameterName])
            outputParameterNames = action['outputParameterNames']
            result = func(*inputParameters)
            if outputParameterNames != None and len(outputParameterNames)>1:
                results = result
                print("results: ", results)
                if(len(outputParameterNames) != len(results)):
                    print("Expected number of parameters: %s, but got %s instead" % 
                          (len(outputParameterNames), len(results)))
                for i in range(len(outputParameterNames)):
                    outputParameterName = outputParameterNames[i]
                    result = results[i]
                    self.results[outputParameterName] = result
                    print("result[%s]: %s" % (i, result))
            else:
                print("result: ", result)
                self.results[action['name']] = result
            print("---")
