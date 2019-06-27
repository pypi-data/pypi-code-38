"""
This will retrieve all geography levels for all catalogue numbers in source directory.
"""
from getStructure import getStructure
import csv, zipfile, os

def unpackStructureFiles(inputFolder = 'C:\\Canadian census downloaded files\\', outputFolder = 'C:\\Canadian census downloaded files\\'):
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

def cleanDirectory(outputFolder):
    for file in os.listdir():
        if file.endswith('.xml'):
            os.remove(file)


def getSumLevs(structureFile, catalogueId ):
    struct = getStructure(structureFile)
    geos = struct.codelists.codelist
    sumlevs = ['Canada']
    for codes in geos:
        if codes.id == 'CL_GEO':
            for code in codes.code:
                if code.annotations.annotation[0].annotationtext[0].text not in sumlevs:
                    sumlevs.append(code.annotations.annotation[0].annotationtext[0].text)
    sumlevs = [[catalogueId,i] for i in sumlevs]
    return sumlevs

def write(sumlev):
    with open('geoDivisionsByCatalogueID.txt', 'a') as fileWrite:
        writer = csv.writer(fileWrite, delimiter = ',')
        for i in sumlev:
            writer.writerow(i)

if __name__ == '__main__':

    sourceFolder = 'C:\\Canadian census downloaded files\\'
    outputFolder = 'C:\\Canadian census downloaded files\\'
    #structureFile = 'c:/Projects/ContentProduction/Canadian Census/scripts/CanadianSDMX/data/Structure_98-314-XCB2011016.xml'

    unpackStructureFiles()
    structureFilesList = os.listdir(outputFolder)
    structureFilesList = [i for i in structureFilesList if i.endswith('.xml')]
    for file in structureFilesList:
        catalogueId = file.replace(sourceFolder,'').replace('.xml','').replace('Structure_','')
        write(getSumLevs(file, catalogueId))

    cleanDirectory(outputFolder)
