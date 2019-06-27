import getGeosForR as ggfr
from getStructure import getStructure
import csv,  os

def getDescriptionsFromStructureFile(sourceFolder):
    """
    List all structure files in folder and get descriptions (from name tag in header)
    :param sourceFolder: Full path to source folder
    :return: List of catalogue ids and corresponding descriptions
    """
    print("Geting descriptions from structure files!")
    os.chdir(sourceFolder)
    filesInDir = os.listdir()
    descriptions = []
    for i in filesInDir:
        if i.startswith('Structure'):
            structure = getStructure(i)
            descriptions.append([i.replace('Structure_','').replace('.xml',''),structure.header.headerData['NameEn']])
    print("Done!")
    return descriptions


if __name__ == '__main__':
    sourceFolder = 'C:\\Canadian census downloaded files NHS\\'
    outputFolder = 'C:\\Canadian census downloaded files NHS\\'

    ggfr.unpackStructureFiles(sourceFolder, outputFolder)
    descriptions = getDescriptionsFromStructureFile(sourceFolder)
    with open(outputFolder + 'descriptionsForCatalogueIds.csv', 'w') as file:
        writer = csv.writer(file, delimiter = ',')
        for i in descriptions:
            writer.writerow(i)
    ggfr.cleanDirectory(outputFolder)