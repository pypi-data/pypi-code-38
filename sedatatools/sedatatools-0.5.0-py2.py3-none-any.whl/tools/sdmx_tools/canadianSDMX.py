"""
4.01
Working version that separates SDMX files into separate text files
"""
import sys
import os, csv
import lxml.etree as etree
import itertools
import fileinput
import time
from sys import stdout
import optparse
from sys import argv
sys.path.insert(0, 'C:/Users/Datasoft/AppData/Local/Programs/Python/Python35/Lib')

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
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Description' and inCodeLists and ('{http://www.w3.org/XML/1998/namespace}lang' not in element.attrib or element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en'):
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

def createTables(structureFile, genericFile, catalogueId, eliminateDim, tableDim, varDim, outputFolder, metaVar):
    """
    Main function for data extract from SDMX file.
    It writes values to a text file as soon as it gets it.
    :param structureFile: Full path to the structure file
    :param genericFile:  Full path to the generic file
    :param catalogueId: Catalogue Id e.g. '98-314-XCB2011041'
    :param eliminateDim: List of dimensions which needs to be eliminated from data (set to total)
    :param tableDim: List of dimensions to use for table creation
    :param varDim: List of dimensions which will be represented as variables in tables
    :param outputFolder: Output folder for newly created tables
    :param metaVar: Flag, whether to write or not file with variable descriptions. Default is to write.
    :return: None
    """
    structure = getConceptValuesFromStructures(structureFile)
    structureDesc = getConceptValuesFromStructuresDesc(structureFile)

    print("Creating tables with headers!")
    #create files with headers
    catalogueId = catalogueId.replace('-','')
    if len(varDim) > 1: # in case that vars should be crated from many dimensions, create all combinations
        nrDim = list(itertools.product(*[structure[i] for i in varDim]))
        desc = list(itertools.product(*[structureDesc[i] for i in varDim]))
        desc = ['_'.join(i) for i in desc]
        nrDim = ['_'.join(vars) for vars in nrDim]
        header = [catalogueId + '_' + i for i in nrDim]
    else:
        header = [catalogueId + '_' + i for i in structure[''.join(varDim)]]
        desc = [i for i in structureDesc[''.join(varDim)]]
    header.insert(0, "Geo")
    if metaVar == True:
        createMetadataforVars(header[1:], desc, outputFolder)

    # create table names
    fileList = list(itertools.product(*[structureDesc[i] for i in tableDim]))
    keys = ['_'.join(name) for name in fileList]
    for key in keys:
        state[key] = None #state dictionary is initiated here
    for name in fileList:
         with open(outputFolder + catalogueId + '_' + '_'.join(name) + '.txt','w', newline='') as writeFile:
            writeFile.write(','.join(header))

    #print('Done! {}'.format(time.time()- startTime)) TODO remove after its not needed anymore
    print("Fill tables with values!")
    createPosition = [] #this will store exact position where value must be written
    tableName = []
    sourceFileForParsing = etree.iterparse(genericFile)
    value = 0
    excludeNode = False
    sourceFileForParsing = iter(sourceFileForParsing)
    event, root = next(sourceFileForParsing) #get root element so we can clean the tree later

    for event, element in sourceFileForParsing:
        if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and element.attrib['concept'] in eliminateDim and element.attrib['value'] != '1': #changed == to in to work with lists
            excludeNode = True
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value' and element.attrib['concept'] not in eliminateDim: #changed != to not in to work with lists
            createPosition.append(element.attrib['value'])
            if element.attrib['concept'] in tableDim:
                tableName.append(structureDesc[element.attrib['concept']][structure[element.attrib['concept']].index(element.attrib['value'])])
            element.clear()
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}ObsValue':
            value = element.attrib['value']
            element.clear()
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series': #when end Series tag found write to db and cleanup everything
            row = structure['GEO'].index(createPosition[0])+1 # create position is a list that contains location of field to write
            geo = structure['GEO'][row-1]
            tableName = '_'.join(tableName)
            if excludeNode == False:
                writeToTable(tableName, geo, value, outputFolder, catalogueId) # TODO  col removed from argument list
            tableName = []
            createPosition = []
            value = 0
            excludeNode = False
        element.clear()
        root.clear()
    # print('Done! '.format(time.time()- startTime)) TODO remove after its not needed anymore

def writeToTable(tableName, geo, value, outputFolder, catalogueId):
    """
    Write into separate txt files.
    It writes values one at the time, one after another in the same line with comma between them.
    It tracks the state of the geography for particular table and switch to the new line when it changes
    :param tableName: Name of the table to be written.
    :param geo: Geo value (FIPS)
    :param value: Value for record that needs to be written.
    :param outputFolder: Full path of the output folder.
    :return:
    """
    #startFuncTime = time.time()
    with open(outputFolder + catalogueId + '_' + tableName + '.txt', 'a', newline='') as writefile:
        if state[tableName] == geo:
            writefile.write(str(value) + ',')
        else:
            writefile.write('\n')
            writefile.write(geo+',')
            writefile.write(str(value) + ',')
    state[tableName]= geo
    #print('running {} sec total'.format(time.time()-startTime)) #TODO remove when sure it works

def listConcepts(genericFile):
    """
    This function parses first serie tag of the generic file to get the concepts in correct order.
    Used generic file instead structure to be sure that order of the concepts is ok.
    :param genericFile: Full path to generic file
    :return: List of concepts in correct order
    """
    sourceFileForParsing = etree.iterparse(genericFile)
    dimList = []
    for event, element in sourceFileForParsing:
        if event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value':
            dimList.append(element.attrib['concept'])
        elif event == 'end' and element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}SeriesKey':
            break
    return dimList

def listConceptsPrint(structureFile, genericFile):
    """
    Print concepts.
    :param structureFile: Full path to concepts file.
    :param genericFile: Full path to generic file.
    :return:
    """
    structureDesc = getConceptValuesFromStructuresDesc(structureFile)
    elements = listConcepts(genericFile)
    for i, elem in enumerate(elements):
        print(i, ':', ' Key: ', elem,' Desc:', structureDesc[elem])

def createMetadataforVars(header, desc, outputFolder):
    """
    Create file that describes variable codes.
    :param header: Header file (it's passed without Geo var)
    :param desc: Descriptions for variables
    :param outputFolder: Full path to output folder
    :return:
    """
    headAndDesc = list(zip(header,desc))
    with open(outputFolder + 'variable_descriptions.txt', 'a') as writeFile:
        for i in headAndDesc:
            writeFile.writelines(','.join(i)+'\n')

def menu():
    """
    Display menu and pass command line parameters.
    :return: Options object with values from cmd
    """

    usage = "(-s, -o, -m are optional): %prog -c arg1 -t arg2 -v arg3 -e arg4 -s arg5 -o arg6 -m arg7"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-c', '--catid', dest = 'catalogueId', help='Catalogue ID', metavar='catalogueId')
    parser.add_option('-t', '--tabledim', dest = 'tableDim', help='Id nr. of the dimensions on which tables will be based on. Use list separated with comma for more than one value e.g. "3, 2, 6" (without doublequotes)', metavar='tableDim')
    parser.add_option('-v', '--vardim', dest = 'varDim', help='Id nr. of the dimension for variables inside of the tables.', metavar='varDim')
    parser.add_option('-e', '--eliminate', dest = 'eliminateDim', help='Id nr. of the dimension which you want to eliminate (set to Total)!', metavar='eliminateDim')
    parser.add_option('-s', '--src', dest = 'sourceFolder', help='Source Folder, default [%default]', metavar='sourceFolder', default = 'c:/Projects/ContentProduction/Canadian Census/scripts/CanadianSDMX/data/')
    parser.add_option('-o', '--out', dest = 'outputFolder', help='Output folder, default [%default]', metavar='outputFolder', default = 'c:/Projects/ContentProduction/Canadian Census/scripts/CanadianSDMX/final output/') # test why it separated files after large job is done
    parser.add_option('-m', '--metadata', dest = 'meta', help='Set "-m False" not to create file with variable descriptions.', metavar='meta', default = True)

    group = optparse.OptionGroup(parser, "List concepts",
                "Example: canadianSDMX -c catalogueId")
    group.add_option('-l', '--list', dest = 'structList', help='Catalogue Id for which to list variable numbers.', metavar='catalogueId')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    return options

def main():
    """
    Main function
    :return:
    """
    opt = menu()
    sourceFolder = opt.sourceFolder
    outputFolder = opt.outputFolder

    if len(argv) == 3 and argv[1] == '-l':
        structureFile = sourceFolder + 'Structure_' + opt.structList + '.xml'
        genericFile = sourceFolder + 'Generic_' + opt.structList + '.xml'
        listConceptsPrint(structureFile, genericFile)
    elif len(argv) not in [1, 2, 3, 7, 9, 11, 13, 15]:
        print("Wrong number of arguments, use -h to get help!")
        sys.exit()
    else:
        catalogueId  = opt.catalogueId
        genericFile = sourceFolder + 'Generic_'+ catalogueId +'.xml'

        if not os.path.isfile(genericFile):
            print('Generic file does not exist on location {}'.format(genericFile))
            sys.exit()
        structureFile = sourceFolder + 'Structure_'+ catalogueId +'.xml'
        if not os.path.isfile(structureFile):
            print('Structure file does not exist on location {}'.format(structureFile))
            sys.exit()

        dimList = listConcepts(genericFile)
        if opt.eliminateDim != None :
            eliminateDim = [dimList[int(i)] for i in opt.eliminateDim.split(',')]
        else:
            eliminateDim = []
        tableDim = [dimList[int(i)] for i in opt.tableDim.split(',')]
        varDim = [dimList[int(i)] for i in opt.varDim.split(',')]
        metaVar = opt.meta

        createTables(structureFile, genericFile, catalogueId, eliminateDim, tableDim, varDim, outputFolder, metaVar)
        print('Done in {}!'.format(time.time()-startTime))

if __name__ == '__main__':
    startTime = time.time() #TODO remove after its not needed anymore
    print('Starting at {}'.format(startTime))
    state = {} # global variable to keep the state (geo) of the row for writing
    main()
