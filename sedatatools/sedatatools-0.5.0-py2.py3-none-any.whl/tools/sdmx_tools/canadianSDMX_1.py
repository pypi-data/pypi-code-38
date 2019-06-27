"""
This version works for files for up to 1GB in size, doesn't work for larger files (cca 100 GB)
It first creates full table with data and then populate the csv file
"""

import lxml.etree as etree
import csv, os, zipfile
import itertools
#script should divide xml into smaller files by all dimensions except second to last one

def getConceptValuesFromStructuresDesc(structureFile):
    """
    This will return only DESCRIPTIONS of a concept e.g. Sex -> Total, M, F
    :param structureFile:
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
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Name' and element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and not inConcepts:
            listOfVariables.append(element.text.strip().replace(' ','_'))
        elif event == 'start' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Description' and inCodeLists and element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en':
            if element.text != None:
                listOfVariables.append(element.text.strip().replace(' ','_'))
        elif event == 'start' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concepts':
            inConcepts = True
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concepts':
            inConcepts = False
    print("Done!")
    return conceptValues


def getConceptValuesFromStructures(structureFile):
    """
    This will return values of a concept e.g. Sex -> 1, 2, 3
    CHECK FOR POSSIBILITY OF INCLUDING THIS LOGIC IN PREVIOUS FUNCTION TO COLLECT ALL DATA IN ONE PASS
    :param structureFile:
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

def getVariables(structureFile):
    """
    Function to get key concepts from structure file
    :return: Key concepts from structure file in form of a dictionary
    """
    print("Geting Concepts data (data about dimensions) from structure file: ")
    sourceFileForParsing = etree.iterparse(structureFile,events =  ('start', 'end'))
    concepts = [] # main dictionary to keep key concepts
    for event, elem in sourceFileForParsing:
        if event == "end" and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concept':
            concepts.append(elem.attrib['id'])
        elif event == "end" and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Concepts':
            break
    print("Done!")
    return concepts


def writeToDataFile(fullTable, fileName):
    """
    write final table to csv file
    :param fullTable: data for writing
    :param fileName: Desired filename
    :return: None
    """
    print("Writing file {}!!!".format(fileName))

    with open(outputFolder + fileName +'.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(fullTable)
    print("Done!")

def writeToMetaFile(header, fileName):
    print("Writing metadata file!")
    with open(outputFolder + 'metadata.csv', 'a', newline='') as fp:
        a=csv.writer(fp, delimiter=',')
        a.writerows(header[1:]) # write all lines but first
    print("Done!")

def divideFile(genericFile):
    """
    Divide file into separate tables
    :param genericFile: File name
    :return: None
    """
    print("Starting to dismember SDMX into smaller tables!")
    conceptValues = getConceptValuesFromStructures(structureFile)
    conceptValuesDesc = getConceptValuesFromStructuresDesc(structureFile)

    tableList = [] #this will be a list of a tables for export
    tableListNames = [] #this will be a list of table names for export

    variableConcept = getVariables(structureFile) # this is the concept which will be variable inside a file
    variableForFile = variableConcept[len([variable for variable in variableConcept if not variable.startswith('OBS')])-2] # find variable by removing the OBS vars and then length of remainder -2

    conceptsForTables = [variable for variable in variableConcept if not variable.startswith('OBS') and variable != variableForFile and variable != 'GEO' and variable != 'TIME'] # find variables for table generation
    lists = [] # this will hold a list of lists with values for table names
    for concept in conceptsForTables:
        lists.append([conceptList for conceptList in conceptValues[concept]])
    tableList = list(itertools.product(*lists)) # create list with all possible combinations of variables
    #tableList = [''.join(x) for x in tableList] # and then concatenate it
    createName = []
    fullTable = []
    print(len(tableList))
    for table in tableList:
        fileName = (catalogueId + '_' + '_'.join([conceptValues[conceptsForTables[int(index)]][int(t)-1] for index, t in enumerate(table)]) + '_' + '_'.join([conceptValuesDesc[conceptsForTables[int(index)]][int(t)] for index, t in enumerate(table)])).replace('-','_')
        print("Preparing file {}".format(fileName))
        sourceFileForParsing = etree.iterparse(genericFile)
        for event, element in sourceFileForParsing:
            if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and element.attrib['concept'] != 'GEO' and element.attrib['concept'] != variableForFile :
                createName.append(element.attrib['value'])
            elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series':
                createName = []
            if createName == list(table): # table will be populated only if this line evaluates to true, if data is missing from table, start from here
                if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}ObsValue':
                    fullTable.append(element.attrib['value'])
            element.clear()
        fullTable = list(zip(*[iter(fullTable)]*len(conceptValues[variableForFile]))) #split values into as many columns as there is Age categories
        fullTable = [list(y) for y in fullTable]
        fullTable = list(zip(conceptValues['GEO'], fullTable)) # insert rownames
        header = ['Geo_FIPS']
        for varName in conceptValues[variableForFile]:
            header.append(catalogueId + '_' + varName)

        headerDesc = [] #description of header variables
        for varName in conceptValuesDesc[variableForFile]:
            headerDesc.append(varName)

        fullTable = [[y[0]]+list(y[1]) for y in fullTable] # flatten array by rows
        fullTable.insert(0, header)
        #generate file name, since there can be unknown number of dimension it takes some weird logic to create all combination
        writeToDataFile(fullTable, fileName)
        fullTable = []
    writeToMetaFile(list(zip(header,headerDesc)), fileName)

if __name__ == '__main__':
    outputFolder =  'z:\\Canadian Census\\Misc\\' #'z:\\Canadian Census\\exported tables\\'
    catalogueId = '98-314-XCB2011041' #'98-311-XCB2011023' '98-312-XCB2011041' '98-313-XCB2011025'
    genericFile = 'c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\Generic_'+ catalogueId +'.xml'
    structureFile = 'c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\Structure_'+ catalogueId +'.xml'
    conceptValues = getConceptValuesFromStructures(structureFile) # this will return dictionary of values for dims/tables
    conceptValuesDesc = getConceptValuesFromStructuresDesc(structureFile) # this will return dictionary of descriptions for dims/tables
    divideFile(genericFile)
