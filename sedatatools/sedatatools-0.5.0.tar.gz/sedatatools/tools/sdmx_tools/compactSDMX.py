"""
FINISH WHEN NEEDED!
DEVELOPMENT ABORTED DUE TO THE NEWLY DEVELOPED SITUATION
"""

from getStructure import getStructure
import lxml.etree as etree
import time
import sys
from getStructure import getStructure

def checkIfCompact(compactFile):
    """
    Check if provided file is compact SDMX, in case it's not then exit.
    :param compactFile:
    :return:
    """
    sourceFileForParsing = etree.iterparse(compactFile)
    for event, element in sourceFileForParsing:
        if element.tag == '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}CompactData':
            print('Not a compact SDMX file, exiting!')
            sys.exit()

def getAttributes(structureFile):
    """
    Get list of attibutes to separate them with values
    :param structureFile: Full path to structure file
    :return:
    """
    startStructure = time.time()
    struct = getStructure(structureFile)
    print("Got structure in {}".format(time.time() - startStructure))
    attribs = []
    for i in struct.keyfamilies.keyfamily.components.attribute:
        attribs.append(i.conceptRef)
    return attribs

def writeFile(fileName, value):
    with open('c:\\Projects\\ContentProduction\\Canadian Census\\scripts\\CanadianSDMX\\data\\test_ouput\\' + fileName + '.t', 'a') as fileWrite:
        fileWrite.write(value)

def parseCompact(compactFile, structureFile):
    datanspc = '{http://oecd.stat.org/Data}' # data namespace
    msgnspc = '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}'
    series = {}
    observations = {}
    values = []
    attributes = getAttributes(structureFile)
    startTime = time.time()
    print("Started parsing!")
    sourceFileForParsing = etree.iterparse(compactFile)
    for event, element in sourceFileForParsing:
        if element.tag == datanspc + 'Series' and event == 'end':
            series = [element.attrib[i] for i in element.attrib if i not in attributes]
        elif element.tag == datanspc + 'Obs' and event == 'end':
            observations = element.attrib
            # values.append([series,observations])
            writeFile('_'.join(series) + observations['TIME'], observations['OBS_VALUE'])
            series = {}
            observations = {}
    print("Done in {}".format(time.time() - startTime))

if __name__ == '__main__':

    structureFile = 'C:\\SDMX\\OECD\\compact\\DataStructureDefinition.xml'
    compactFile = 'C:\\SDMX\\OECD\\compact\\DataCompact.xml'
    #checkIfCompact(compactFile)
    getAttributes(structureFile)
    parseCompact(compactFile, structureFile)
    print("ne")
