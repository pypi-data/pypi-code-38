"""
This extract all possible combination of values from structure file
"""
import lxml.etree as etree
import csv, os, zipfile, itertools, time, sys
import operator
import functools

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

def getSeriesCombinations(structureFile, outputFolder, catalogueId):
    print('Writing combination file.')
    structuresFromFiles = getConceptValuesFromStructures(structureFile)

    variableConcept = [i for i in getVariables(structureFile) if i != 'TIME' and not i.startswith('OBS')] # list of concepts

    lists = [] # this will hold a list of lists with values for table names
    listFinal = []
    for concept in variableConcept:
        lists.append(structuresFromFiles[concept])
    tableList = itertools.product(*lists) # create list with all possible combinations of variables
    print('Resulting number of combinations will be {}'.format(functools.reduce(operator.mul, [len(i) for i in lists], 1)))

    #write the result
    with open(outputFolder + catalogueId + '_variable_combination_list.csv', 'a', newline='') as fp:
        a=csv.writer(fp, delimiter=',')
        a.writerow(variableConcept)
        for i in tableList:
            a.writerow(list(i))

    return listFinal
    print("Done!")

def menu():
    print("Usage: canadian_SDMX source_folder output_folder catalogue_id")

def main():
    """
    Example files:
    huge (over 100 GB): 98-314-XCB2011041
    large (up to 1 GB):  98-311-XCB2011023
    small ( few hundreds of MBs): 98-312-XCB2011041
    output on prime :'z:\\Canadian Census\\Misc\\'
    :return:
    """

    parameters = ['c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\', 'c:\\Projects\\ContentProduction\\Canadian Census\\', '98-314-XCB2011041']
    sourceFolder = parameters[0]
    outputFolder = parameters[1]
    catalogueId  = parameters[2]
    genericFile = sourceFolder + 'Generic_'+ catalogueId +'.xml'
    structureFile = sourceFolder + 'Structure_'+ catalogueId +'.xml'

    getSeriesCombinations(structureFile, outputFolder, catalogueId)


if __name__ == '__main__':
    startTime = time.time()
    main()

