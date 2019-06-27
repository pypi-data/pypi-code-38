"""
This version write files one row at a time
"""
import lxml.etree as etree
import csv, os, zipfile, itertools, time, sys

#script should divide xml into smaller files by all dimensions except second to last one

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

def getVariables(structureFile):
    """
    Function to get key concepts from structure file.
    :param structureFile: Full file name of structure file (including full path)
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

def writeToDataFile(fullRow, outputFolder, fileName):
    """
    Write final table to csv file.
    :param fullRow: One row of a file to be written
    :param outputFolder: Output folder
    :param fileName: Desired filename
    :return: None
    """

    print('Adding row!')
    if int((time.time() - startTime)/120) == 0:
        print("Program is running for {} seconds.".format(int(time.time() - startTime)))
    else:
        print("Program is running for {} minutes.".format(int((time.time() - startTime)/60)))

    with open(outputFolder + fileName +'.csv', 'a', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(fullRow)

def writeToMetaFile(header, outputFolder, fileName):
    """
    Write data about variables in files
    :param header: Header of the table
    :param outputFolder: Output folder
    :param fileName: File name of the file to be written
    :return: None
    """
    print("Writing metadata file!")
    with open(outputFolder + 'metadata.csv', 'a', newline='') as fp:
        a=csv.writer(fp, delimiter=',')
        a.writerows(header[1:]) # write all lines but first
    print("Done!")

def divideFile(outputFolder, catalogueId, genericFile, structureFile):
    """
    Divide file into separate tables
    :param catalogueId: Id of catalogue
    :param genericFile: File name of generic file (including full path)
    :param structureFile: File name of structure file (including full path)
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
    tableRow = []

    #create header and write it as a first line of file
    header = ['Geo_FIPS']
    for varName in conceptValues[variableForFile]:
        header.append(catalogueId + '_' + varName)
    countNumberOfVars = 1 #counter for number of variables, it will be used to limit number of columns in row
    for table in tableList:
        countRows = 0 # counter for rows, used to insert correct geo Fips, reset after each table
        fileName = (catalogueId + '_' + '_'.join([conceptValues[conceptsForTables[int(index)]][int(t)-1] for index, t in enumerate(table)]) + '_' + '_'.join([conceptValuesDesc[conceptsForTables[int(index)]][int(t)] for index, t in enumerate(table)])).replace('-','_')
        print("Preparing file {}".format(fileName))
        sourceFileForParsing = etree.iterparse(genericFile)
        writeToDataFile(header, outputFolder, fileName)

        sourceFileForParsing = iter(sourceFileForParsing)
        event, root = next(sourceFileForParsing) #get root element so we can clean the tree later

        for event, element in sourceFileForParsing:
            if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and element.attrib['concept'] != 'GEO' and element.attrib['concept'] != variableForFile :
                createName.append(element.attrib['value'])
                element.clear()
            elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series':
                createName = []
                element.clear()
            if createName == list(table): # table will be populated only if this line evaluates to true, if data is missing from table, start from here
                if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}ObsValue':
                    if len(tableRow) < len(conceptValues[variableForFile]): # check if row values are filled for all variables
                        tableRow.append(element.attrib['value'])
                        countNumberOfVars += 1
                    elif len(tableRow) == len(conceptValues[variableForFile]):
                        tableRow.insert(0, conceptValues['GEO'][countRows])
                        writeToDataFile(tableRow, outputFolder, fileName)
                        tableRow = []
                        countRows += 1
                        countNumberOfVars = 0
                element.clear()
            root.clear()

        headerDesc = [] #description of header variables
        for varName in conceptValuesDesc[variableForFile]:
            headerDesc.append(varName)

    writeToMetaFile(list(zip(header,headerDesc)), outputFolder, fileName)


def menu():
    print("Usage: canadian_SDMX source_folder output_folder catalogue_id")

def main():
    parameters = ['c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\', 'z:\\Canadian Census\\Misc\\', '98-314-XCB2011041']
    sourceFolder = parameters[0]
    outputFolder = parameters[1]
    catalogueId  = parameters[2]
    genericFile = sourceFolder + 'Generic_'+ catalogueId +'.xml'
    structureFile = sourceFolder + 'Structure_'+ catalogueId +'.xml'

    divideFile(outputFolder, catalogueId, genericFile, structureFile)



if __name__ == '__main__':
    startTime = time.time()
    main()

