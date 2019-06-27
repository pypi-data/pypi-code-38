"""
This version is obsolete
"""

import lxml.etree as etree
import csv, os, zipfile

inputDir = 'c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\' #"c:\\Canadian census downloaded files\\" ##TODO uncomment this "c:\\downloaded files_FOR_TESTING_ONLY\\"
outputDir = "c:\\Users\\Datasoft\\PycharmProjects\\CanadianSDMX\\"
finalStructureMetadataFile = 'structure_metadata_file.txt'

genericFile = 'c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\Generic_98-313-XCB2011025.xml'
structureFile = 'c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\Structure_98-313-XCB2011025.xml'



def getCodeListDataFromStructure(structureFile):
    """
    :param structureFile - name of the file for which the structure has to be extracted
    :return: dictionary containing data
    """
    print("Geting Codelist data from structure file:")
    sourceFileForParsing = etree.iterparse(structureFile, events =  ('start', 'end', 'start-ns', 'end-ns'))
    namespaceList =[]
    codeLists = {}
    listOfCodelists = [] # create list of all Codelists in the document
    inCodelists = True # control if inside CodeLists
    for event, elem in sourceFileForParsing:
        #generate list of namespaces
        if event == 'end' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}CodeList':
            inCodelists = False
        if event == 'start-ns' and inCodelists:
            namespaceList.append(elem)
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}CodeList' and inCodelists:
            keyForCodelists = elem.attrib['id']
            codeLists[keyForCodelists] = []
            codeListsAttribute = []
            attribOccurenceAT = 0 # helper var to always select first occurence of the attrubute Annotation type
            attribOccurenceATxt = 0 # helper var to always select first occurence of the attrubute Annotation text
            codeLists[keyForCodelists].append(elem.attrib['agencyID'])
            listOfCodelists.append(elem.attrib['id'])
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common}Code' and inCodelists:
            codeLists[keyForCodelists].append(elem.attrib['value'])
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Description' and inCodelists:
            codeLists[keyForCodelists].append(elem.text)
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Name' and elem.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and inCodelists:
            codeLists[keyForCodelists].append(elem.text)
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common}AnnotationTitle' and inCodelists:
            codeLists[keyForCodelists].append(elem.text)
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common}AnnotationType' and attribOccurenceAT == 0 and inCodelists:
            codeLists[keyForCodelists].append(elem.text)
            attribOccurenceAT += 1
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common}AnnotationText' and attribOccurenceATxt == 0 and elem.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and inCodelists:
            codeLists[keyForCodelists].append(elem.text)
            attribOccurenceATxt += 1
    print("Done!")
    return codeLists

def writeCodeListDataFromStructure():
    """
    :return: write text file with data from structure file
    """
    print("Writing CodeList data from structure file into {}:".format(outputDir + finalStructureMetadataFile))
    os.chdir(inputDir)
    filesInDirectory = os.listdir()
    #first extract all structure files
    for fileName in filesInDirectory:
        if fileName.endswith(".zip"):
            filesInZip = zipfile.ZipFile(fileName)
            for packedFile in filesInZip.namelist():
                if 'Structure' in packedFile :
                    filesInZip.extract(packedFile)
    #read structure files
    nodes = {}
    # TODO: uncomment line below and delete line after that
    #filesInDirectory = os.listdir() # list files in a directory once more to find unpacked xml files
    filesInDirectory = structureFile
    for fileName in filesInDirectory:
        if fileName.endswith(".xml"):
            nodes = getCodeListDataFromStructure(fileName)
            #write the result into file
            if finalStructureMetadataFile in filesInDirectory:
                os.unlink(outputDir + finalStructureMetadataFile) #delete the file if it already exists
            writer = csv.writer(open(outputDir + finalStructureMetadataFile,'a', encoding='utf8'))
            for key, value in nodes.items():
                for i in value:
                    writer.writerow([fileName, key, i],)
    # clean after you process upacked files
    filesInDirectory = os.listdir()
    # for fileName in filesInDirectory: #TODO check if there is need to delete extracted files
    #     if fileName.endswith(".xml"):
    #         os.remove(fileName)
    print("Done!")


def getVariables(structureFile):
    """
    Function to get key concepts from structure file
    :return: Key concepts from structure file in form of a dictionary
    """
    print("Geting Concepts data (data about dimensions) from structure file: ")
    sourceFileForParsing = etree.iterparse(structureFile,events =  ('start', 'end', 'start-ns', 'end-ns'))
    inConcepts = False

    concepts = {} # main dictionary to keep key concepts
    key = ''
    for event, elem in sourceFileForParsing:
        if event == "start" and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Concepts':
            inConcepts = True
        elif event == "start" and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concept' and inConcepts:
            key = elem.attrib['id']
        elif event == "start" and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Name' and elem.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and inConcepts:
            concepts[key] = elem.text
        elif event == "end" and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Concepts':
            inConcepts = False
    print("Done!")
    return concepts

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
            listOfVariables.append(element.text)
        elif event == 'start' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Description' and inCodeLists and element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en':
            listOfVariables.append(element.text)
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
    print("Done!")
    return conceptValues


def getMetadataFromGeneric(genericFile):
    """
    Get data from header of a generic file and from a KeyFamilyRef in DataSet
    :param genericFile: Name of a generic file
    :return: Metadata from generic file in form of a dictionary
    """
    print("Geting the metadata from Generic file: ")
    documentMetadata = {}
    inSenderTag = False
    sourceFileForParsing = etree.iterparse(genericFile, events =  ('start', 'end', 'start-ns', 'end-ns'))
    for event, elem in sourceFileForParsing:
        if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}GenericData':
            documentMetadata['GenericData'] = elem.attrib
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}ID':
            documentMetadata['ID'] = elem.text
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Test':
            documentMetadata['Test'] = elem.text
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Name' and elem.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and not inSenderTag:
            documentMetadata['Name'] = elem.text
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Prepared':
            documentMetadata['Prepared'] = elem.text
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Sender':
            inSenderTag = True
        elif event == 'end' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Sender':
            inSenderTag = False
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Name' and elem.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and inSenderTag:
            documentMetadata['SenderName'] = elem.text
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}KeyFamilyRef':
            documentMetadata['KeyFamilyRef'] = elem.text
        elif event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series':
            break
    print("Done!")
    return documentMetadata


def readGeneric(genericFile, tableDimension, summaryDimension, removeDimension):
    """
    Read generic file and get data in form of a multidimensional array
    :param genericFile: file from which is required to get the data
    :return: multidimensional array containing the data
    """
    conceptValues = getConceptValuesFromStructures(structureFile) # this will return dictionary of values for dims/tables
    conceptValuesDesc = getConceptValuesFromStructuresDesc(structureFile) # this will return dictionary of descriptions for dims/tables
    tableList = conceptValues[tableDimension]#.append(tableDimension)
    summaryValuesList = conceptValues[summaryDimension]
    valueForRemoval = conceptValues[removeDimension][0] # this value will not be removed but used to remove all other values in this dimension

    print("Reading the generic file for data: ")

    sourceFileForParsing = etree.iterparse(genericFile, events = ('start','end'))
    inSeriesKey = False
    tableRow = []
    valuesMatch = False
    for table in tableList:
        for summVar in summaryValuesList:
            print(table, summVar, valueForRemoval)
            for event, element in sourceFileForParsing:
                if event == 'start' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value':
                    if element.attrib['concept'] == tableDimension and element.attrib['value'] == tableDimension:
                        valuesMatch = True
                    else:
                        valuesMatch = False
                if event == 'start' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and valuesMatch:
                    tableRow.append(element.attrib['value'])
    print("nesto")

#petlja prije ovog teksta je trebala da gleda u generic file-u kombinaciju vrijednosti koncepata!!!

    # cellValue = []
    # genericData = []
    # inSeries = False
    # sourceFileForParsing = etree.iterparse(genericFile, events = ('start', 'end', 'start-ns', 'end-ns'))
    # for event, elem in sourceFileForParsing:
    #     if event == 'start' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value':
    #       cellValue.append(elem.attrib['value'])
    #       elem.clear()
    #     elif event == 'end' and elem.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series':
    #          genericData.append(cellValue)
    #          cellValue = []
    #          elem.clear()
    # print("Done!")
    # return genericData


def main():

    tableDimension = "Sex" # var to create tables by
    summaryDimension = "AGE"# summary vars
    removeDimension = "CFSTATSIMPLE"

    print("This script is used to parse SDMX into SE tables format!")
    writeCodeListDataFromStructure() # this will be used to pick which tables and which variables to create
                                     # it writes the table in text format with descriptions of a concepts

    #keyConceptsValues = getCodeListDataFromStructure(structureFile) # this are just values for Geos - check if needed
    keyConcepts = getConceptsDataFromStructure(structureFile) # List of key concepts with descriptions, can be used as table/var names
    metadataFromDataFile = getMetadataFromGeneric(genericFile) #Header from generic file, various information
    dataTable = readGeneric(genericFile, tableDimension, summaryDimension, removeDimension)
    print("key concepts", keyConcepts, "metadataFromDataFile", metadataFromDataFile, "dataTable", dataTable)

main()