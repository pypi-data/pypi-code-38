"""
This returns object of structure type from structure file.

TESTED FOR CANADIAN CENSUS AND OECD DATA!!!!

"""
import lxml.etree as etree

class CompactSeries:
    def __init__(self, series, values):
        self.series = series
        self.values = values

class Header:
    headerData = {
    'headerAttrib' : {},
    'id' : '',
    'test' : '',
    'truncated' : '',
    'prepared' : '',
    'senderid' : '',
    'senderNameEn' : '',
    'senderNameFr' : ''}

    # def __init__(self, headerData):
    #     self.headerData = headerData

class Name:
    xml_lang = ''
    text = ''

nesto = Header()

class Attribute:
    codelist = ''
    conceptRef = ''
    assignmentStatus = ''
    attachmentLevel = ''
    isTimeFormat = ''

class TextFormat:
    textType = ''

class PrimaryMeasure:
    conceptRef = ''
    textFormat = TextFormat()

class TimeDimension:
    codelist = ''
    conceptRef = ''

class Dimension:
    codelist = ''
    conceptRef = ''

class Components:
    dimension = [Dimension()]
    timeDimension = TimeDimension()
    primaryMeasure = PrimaryMeasure()
    attribute = [Attribute()]
    textFormat = [TextFormat()]

############## KeyFamilies ################

class KeyFamily:
    id = ''
    agencyID = ''
    name = [Name()]
    components = Components()

class KeyFamilies:
    keyfamily = KeyFamily()

############### concepts ################

class Concept:
    name = [Name()]
    text = ''

class Concepts:
    id = ''
    agencyID = ''
    concept = [Concept()]

class Description:
    xml_lang = ''
    text = ''

class AnnotationTitle:
    text = ''

class AnnonationType:
    text = ''

class AnnotationText:
    xml_lang = ''
    text = ''

class Annotation: # Added for canadian
    annotationtitle = ''
    annotationtype = ''
    annotationtext = ''
    annotationtext = [AnnotationText()]

class Annotations: #Added for canadian
    annotation = [Annotation()]

class Code:
    value = ''
    parentCode = ''
    description = [Description()]
    annotations = Annotations()

class CodeList:
    id = ''
    agencyID = ''
    name = [Name()]
    code = [Code()]

class CodeLists:
    codelist = [CodeList()]

############### concepts ################

class Concepts:
    concept = [Concept()]

class Concept:
    id = ''
    agencyID = ''
    name = [Name]

class Structure:
    header = [Header()]
    codelists = [CodeLists()]
    concepts = [Concepts()]
    keyfamilies = [KeyFamilies()]


#
# class Structure:
#     structureHeader = {}
#     mainProperty = {} # this will hold CodeList, Concepts, KeyFamilies or whatever is on the 2nd level


def getStructure(structureFile):
    """
    This will create object of Structure type.
    param: Full path to structure file.
    :return: Object of type structure
    """
    sourceFileForParsing = etree.iterparse(structureFile, events = ('start','end'))
    # inHeaderTag = True
    headerData = {}
    names = [] # temp variables for use later during parsing
    descriptions = []
    codes = []
    codelistList = []
    conceptsList = []
    dimensions = []
    attributes = []
    annotationsList = []
    annotationtexts = []
    inSender = False
    msgns = '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}'
    structns = '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}'
    commonns = '{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common}'
    for event, element in sourceFileForParsing:
        if element.tag == msgns + 'Structure' and event == 'end':
            headerData['structureAttribs'] = element.attrib
        elif element.tag == msgns + 'Header' and event == 'end':
            headerData['headerAttrib'] = list(element.attrib)
            header = Header()
            header.headerData = headerData
        elif element.tag == msgns + 'ID' and event == 'end':
            headerData['id'] = element.text
        elif element.tag == msgns + 'Test' and event == 'end':
            headerData['test'] = element.text
        elif element.tag == msgns + 'Truncated' and event == 'end':
            headerData['truncated'] = element.text
        elif element.tag == msgns + 'Prepared' and event == 'end':
            headerData['prepared'] = element.text
        elif element.tag == msgns + 'Sender' and event == 'start':
            inSender = True
        elif element.tag == msgns + 'Sender' and event == 'end':
            headerData['senderId'] = element.attrib['id']
        elif element.tag == msgns + 'Name' and event == 'end':
            if element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and not inSender:
                headerData['NameEn'] = element.text
            elif element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'fr' and not inSender:
                headerData['NameFr'] = element.text
            elif element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'en' and inSender: # novo bilo if
                headerData['senderNameEn'] = element.text
            elif element.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'fr' and inSender:
                headerData['senderNameFr'] = element.text
        elif element.tag == msgns + 'CodeLists' and event == 'end':
            code.description = descriptions
            codelist.name = names
            codelists = CodeLists()
            codelists.codelist = codelistList
            names = []
            descriptions = []
            code = Code()
            codelist = CodeList()
            codelistList = []
        elif element.tag == structns + 'CodeList' and event == 'end':
            codelist = CodeList()
            codelist.id = element.attrib['id']
            codelist.agencyID = element.attrib['agencyID']
            codelist.code = codes
            codelist.name = names
            codes = []
            names = []
            annotation = []
            codelistList.append(codelist)
        elif element.tag == structns + 'Name' and event == 'end':
            name = Name()
            name.xml_lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            name.text = element.text
            names.append(name)
        elif element.tag == structns + 'Code' and event == 'end':
            code = Code()
            code.value = element.attrib['value']
            if 'parentCode' in element.attrib.keys():
                code.parentCode = element.attrib['parentCode']
            code.description = descriptions
            if 'annotations' in locals(): # check if variable exists, neccessary for structures without annotations
                code.annotations = annotations
            descriptions = []
            codes.append(code)
        elif element.tag == structns + 'Description' and event == 'end':
            description = Description()
            if 'http://www.w3.org/XML/1998/namespace/lang' in element.nsmap.keys():
                description.xml_lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            description.text = element.text
            descriptions.append(description)
        elif element.tag == commonns + 'Annotation' and event == 'end':
            annotation = Annotation()
            annotation.annotationtitle = annotationtitle
            annotation.annotationtype = annotationtype
            annotation.annotationtext = annotationtexts
            annotationsList.append(annotation)
            annotationtexts = []
        elif element.tag == structns + 'Annotations' and event == 'end':
            annotations = Annotations()
            annotations.annotation = annotationsList
            annotationsList = []
        elif element.tag == commonns + 'AnnotationTitle' and event == 'end':
            annotationtitle = AnnotationTitle()
            annotationtitle = element.text
        elif element.tag == commonns + 'AnnotationType' and event == 'end':
            annotationtype = AnnonationType()
            annotationtype = element.text
        elif element.tag == commonns + 'AnnotationText' and event == 'end':
            annotationtext = AnnotationText()
            if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
                annotationtext.xml_lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            annotationtext.text = element.text
            annotationtexts.append(annotationtext)
        elif element.tag == msgns + 'Concepts' and event == 'end':
            concepts = Concepts()
            concepts.concept = conceptsList
            conceptsList = []
        elif element.tag == structns + 'Concept' and event == 'end':
            concept = Concept()
            concept.agencyID = element.attrib['agencyID']
            concept.id = element.attrib['id']
            concept.name = names
            conceptsList.append(concept)
            names = []
        elif element.tag == msgns + 'KeyFamilies' and event == 'end':
            keyfamilies = KeyFamilies()
            keyfamilies.keyfamily = keyfamily
        elif element.tag == structns + 'KeyFamily' and event == 'end':
            keyfamily = KeyFamily()
            keyfamily.id = element.attrib['id']
            keyfamily.agencyID = element.attrib['agencyID']
            keyfamily.components = component
            keyfamily.name = names
        elif element.tag == structns + 'Components' and event == 'end':
            component = Components()
            component.dimension = dimensions
            component.timeDimension = timedimension
            component.primaryMeasure = primarymeasure
            component.attribute = attributes
        elif element.tag == structns + 'Dimension' and event == 'end':
            dimension = Dimension()
            dimension.codelist = element.attrib['codelist']
            dimension.conceptRef = element.attrib['conceptRef']
            dimensions.append(dimension)
        elif element.tag == structns + 'TimeDimension' and event == 'end':
            timedimension = TimeDimension()
            if 'codelist' in element.attrib:
                timedimension.codelist = element.attrib['codelist']
            timedimension.conceptRef = element.attrib['conceptRef']
        elif element.tag == structns + 'PrimaryMeasure' and event == 'end':
            primarymeasure = PrimaryMeasure()
            primarymeasure.conceptRef = element.attrib['conceptRef']
            primarymeasure.textFormat = textformat
        elif element.tag == structns + 'TextFormat' and event == 'end':
            textformat = TextFormat()
            textformat.textType = element.attrib['textType']
        elif element.tag == structns + 'Attribute' and event == 'end':
            attribute = Attribute()
            attribute.codelist = element.attrib['codelist']
            attribute.conceptRef = element.attrib['conceptRef']
            attribute.assignmentStatus = element.attrib['assignmentStatus']
            attribute.attachmentLevel = element.attrib['attachmentLevel']
            if 'isTimeFormat' in element.attrib.keys():
                attribute.isTimeFormat = element.attrib['isTimeFormat']
            else:
                attribute.isTimeFormat = None
            attributes.append(attribute)

    structure = Structure()
    structure.header = header
    structure.codelists = codelists
    structure.concepts = concepts
    structure.keyfamilies = keyfamilies
    return structure


def main():
    #struct = getStructure('C:\\SDMX\\OECD\\compact\\DataStructureDefinition.xml')
    struct = getStructure('c:/Projects/ContentProduction/Canadian Census/scripts/CanadianSDMX/data/Structure_98-314-XCB2011016.xml')# namespace lang error??
    #struct = getStructure('c:/Projects/ContentProduction/Canadian Census/scripts/CanadianSDMX/data/Structure_98-312-XCB2011031.xml')
    print("nesto")
if __name__ == '__main__':
    main()