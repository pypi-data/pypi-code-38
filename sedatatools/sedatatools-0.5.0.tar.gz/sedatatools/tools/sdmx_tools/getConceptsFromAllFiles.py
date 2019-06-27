"""
This will extract all structure files in archives in output directory, list concepts with possible values,
write it to a file and the delete all extracted files.
"""

import sys, os
import zipfile
from canadianSDMX import getConceptValuesFromStructuresDesc

def unpackStructureFiles(inputFolder = 'C:\\Canadian census downloaded files NHS\\', outputFolder = 'C:\\Canadian census downloaded files NHS\\'):
    """
    Extract Structure files from input directory into output directory
    :param inputFolder: Full path to input directory
    :param outputFolder: Full path to output directory
    :return: None
    """
    print("Unzipping structure files!")
    os.chdir(inputFolder)
    filesInDirectory = os.listdir()
    for packedFile in filesInDirectory:
        if packedFile.endswith('.ZIP'):
            zippedData = zipfile.ZipFile(packedFile)
            filesInZip = zippedData.namelist() #check which files are inside archive
            for fileName in filesInZip:
                if fileName.startswith('Structure'):
                    zippedData.extract(fileName, path = outputFolder)
    print("Done.")

def writeToTable(outputFolder, line):
    """
    Write to csv file.
    :param outputFolder: Full path to output directory
    :param line: Line to be written
    :return: None
    """
    with open(outputFolder + 'concepts_table.csv', 'a') as writeFile:
        writeFile.writelines(line)

def cleanDirectory(outputFolder):
    for file in os.listdir():
        if file.endswith('.xml'):
            os.remove(file)

if __name__ == '__main__':
    sourceFolder = 'C:\\Canadian census downloaded files NHS\\'
    outputFolder = 'C:\\Canadian census downloaded files NHS\\'
    #genericFile = sourceFolder + 'Generic_'+ catalogueId +'.xml'
    #structureFile = sourceFolder + 'Structure_'+ catalogueId +'.xml'

    unpackStructureFiles()
    structureFilesList = os.listdir(outputFolder)
    structureFilesList = [i for i in structureFilesList if i.endswith('.xml')]
    for file in structureFilesList:
        for key, value in getConceptValuesFromStructuresDesc(file).items():
            if key != 'GEO':
                writeToTable(outputFolder, 'CatId: {}, Key: {}, Values {}\n'.format(file[-21:-4] , key, ','.join(value)))
                print(file[-21:-4] , key, ','.join(value))

    cleanDirectory(outputFolder)

