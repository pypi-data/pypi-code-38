"""
Working version that separates SDMX files into separate files
"""

import dbf
import sys
import os, csv
import lxml.etree as etree
import itertools
import fileinput
import time
from sys import stdout
def getConceptValuesFromStructuresDesc(structureFile):
    """
    This will return only DESCRIPTIONS of a concept e.g. Sex -> Total, M, F
    :param structureFile: Full file name of structure file (including full path)
    :return: Dictionary with dim name as a key and possible outcomes as values, first element of the value list is a name of a dimension
    """
    print("Geting the list of possible values with descriptions for dimensions and tables!")
    listOfVariables = []
    conceptValues = {}
    key = None
    inCodeLists = False
    inConcepts = False

    #get concept names to replace its codelists name
    sourceFileForParsing = etree.iterparse(structureFile, events = ('start', 'end'))
    codelistToConcept = {}
    for event, element in sourceFileForParsing:
        if event == 'end' and (element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Dimension' or element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Attribute'):
            codelistToConcept[element.attrib['codelist']] = element.attrib['conceptRef']

    #first create list of possible CodeList descriptions in form CL_NAME -> Possible descriptions
    sourceFileForParsing = etree.iterparse(structureFile, events = ('start', 'end'))
    for event, element in sourceFileForParsing:
        if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}CodeList':
            inCodeLists = True
            key = codelistToConcept[element.attrib['id']] # take value from codelistToConcept end set it as a key
            if listOfVariables != None:
                conceptValues[key] = listOfVariables
                key = None
                listOfVariables = []
        # elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Name' and element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and not inConcepts:
        #     listOfVariables.append(element.text.strip().replace(' ','_'))
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Description' and inCodeLists and element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en':
            if element.text != None:
                listOfVariables.append(element.text.strip().replace(' ','_'))
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concepts':
            inConcepts = True
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concepts':
            inConcepts = False
    print("Done!")
    return conceptValues


def getConceptValuesFromStructures(structureFile):
    """
    This will return values of a concept e.g. Sex -> 1, 2, 3
    CHECK FOR POSSIBILITY OF INCLUDING THIS LOGIC IN PREVIOUS FUNCTION TO COLLECT ALL DATA IN ONE PASS
    :param structureFile: Full file name of structure file (including full path)
    :return: Dictionary with dim name as a key and possible outcomes as values, first element of the value list is a name of a dimension
    """
    print("Geting the list of possible values for dimensions and tables!")
    listOfVariables = []
    conceptValues = {}
    key = None
    inCodeLists = False
    inConcepts = False

    #get concept names to replace its codelists name
    sourceFileForParsing = etree.iterparse(structureFile, events = ('start', 'end'))
    codelistToConcept = {}
    for event, element in sourceFileForParsing:
        if event == 'end' and (element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Dimension' or element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Attribute'):
            codelistToConcept[element.attrib['codelist']] = element.attrib['conceptRef']

    #first create list of possible CodeList values in form CL_NAME -> Possible values
    sourceFileForParsing = etree.iterparse(structureFile, events = ('start', 'end'))
    for event, element in sourceFileForParsing:
        if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}CodeList':
            inCodeLists = True
            key = codelistToConcept[element.attrib['id']] # take value from codelistToConcept end set it as a key
            if listOfVariables != None:
                conceptValues[key] = listOfVariables
                key = None
                listOfVariables = []
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Code' and not inConcepts:
            listOfVariables.append(element.attrib['value'])
        elif event == 'start' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concepts':
            inConcepts = True
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concepts':
            inConcepts = False
    print('Done!')
    return conceptValues


def createTables(structureFile, genericFile, catalogueId):
    structure = getConceptValuesFromStructures(structureFile)
    structureDesc = getConceptValuesFromStructuresDesc(structureFile)

    eliminateDim = 'HLnDr'
    tableDim = ['HLnBDr','Sex']
    varDim = 'MTNDr'

    print("Creating tables with headers!")
    #create files with headers
    catalogueId = catalogueId.replace('-','')
    header = [catalogueId+ '_' + i for i in structure[varDim]]
    header.insert(0, "Geo_FIPS")

    fileList = list(itertools.product(*[structureDesc[i] for i in tableDim]))
    keys = ['_'.join(name) for name in fileList]
    for key in keys:
        state[key] = None
    for name in fileList:
         with open('data/txt_export/' + '_'.join(name) + '.txt','w', newline='') as writeFile:
            writeFile.write(','.join(header))

    print('Done! {}'.format(time.time()- startTime))
    print("Fill tables with values!")
    createPosition = [] #this will store exact position where value must be written
    tableName = []
    sourceFileForParsing = etree.iterparse(genericFile)
    value = 0
    excludeNode = False
    sourceFileForParsing = iter(sourceFileForParsing)
    event, root = next(sourceFileForParsing) #get root element so we can clean the tree later

    for event, element in sourceFileForParsing:
        if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and element.attrib['concept'] == eliminateDim and element.attrib['value'] != '1':
            excludeNode = True
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and element.attrib['concept'] != eliminateDim:
            createPosition.append(element.attrib['value'])
            if element.attrib['concept'] == 'HLnBDr' or element.attrib['concept'] == 'Sex':
                tableName.append(structureDesc[element.attrib['concept']][structure[element.attrib['concept']].index(element.attrib['value'])])
            element.clear()
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}ObsValue':
            value = element.attrib['value']
            element.clear()
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series': #when end Series tag found write to db and cleanup everything
            row = structure['GEO'].index(createPosition[0])+1 # in case you need it you can send it to a writetable function
            geo = structure['GEO'][row-1]
            col = structure['MTNDr'].index(createPosition[2])+1 # this should be calculated automaticali
            tableName = tableName[1] + '_' + tableName[0] #quick fix for switching vars in table names, create stable logic later !!!
            if excludeNode == False:
                writeToTable(tableName, geo, col, value)
            tableName = []
            createPosition = []
            value = 0
            excludeNode = False
        element.clear()
        root.clear()
    print('Done! '.format(time.time()- startTime))


def writeToTable(tableName, geo, col, value):
    #startFuncTime = time.time()
    with open('data/txt_export/' + tableName + '.txt', 'a', newline='') as writefile:
        if state[tableName] == geo:
            writefile.write(str(value) + ',')
        else:
            print('Next row')
            writefile.write('\n')
            writefile.write(geo+',')
            writefile.write(str(value) + ',')
    state[tableName]= geo
    print('running {} sec total'.format(time.time()-startTime))


def main():
    parameters = ['c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\', 'c:\\Projects\\ContentProduction\\Canadian Census\\data\\txt_export\\', '98-314-XCB2011041']
    sourceFolder = parameters[0]
    outputFolder = parameters[1]
    catalogueId  = parameters[2]
    genericFile = sourceFolder + 'Generic_'+ catalogueId +'.xml'
    structureFile = sourceFolder + 'Structure_'+ catalogueId +'.xml'
    createTables(structureFile, genericFile, catalogueId)

if __name__ == '__main__':
    startTime = time.time()
    state = {}
    main()