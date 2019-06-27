from lxml import etree as ET
import os

path_file = input("Enter path: ")

if os.path.exists(path_file):
    print("This is the path you've provided: " + path_file)
else:
    print("The system cannot find the path specified: " + path_file)

listofxml = os.listdir(path_file)

#listofxml = os.listdir('C:/Dingo_Maps_Script/test')


for xmlfile in listofxml:
    if xmlfile.endswith('.xml'):
        tree = ET.parse(xmlfile)

        se_layers = tree.xpath('/Map/Sources/Source/Layers/Layer/@id')

        matching_with_se_layers = tree.xpath('/Map/Layers/Layer/@sourceLayer')

        matching_all = tree.find('/Map/Layers/Layer')

        matching_with_se_items = tree.xpath('/Map/Layers/Layer/AutoSource/Item/@sourceLayer')

        se_layers_label = tree.xpath('/Map/Sources/Source/Layers/Layer/Datasets/Dataset/@columns')

#test 1: Are all se layers listed in layer elements:

        #found = False

        for elem in se_layers:
            if elem not in matching_with_se_layers and elem not in matching_with_se_items:
                print(xmlfile+ ': Test 1: '+elem+ ' does not exist in any source layer.')
        #         found = True
        #         break
        #
        # if not found:
        #     print(xmlfile+ ': Test 1: All elements exist in source layers.')

#test 2: Are all se layers labels same as in sourcelayers in its textfield labels:

        dict_source_layer ={}

        for el in tree.findall('Layers')[0].findall('Layer'):
            if 'sourceLayer' in el.attrib:
                if 'textField' in el.find('Layout').attrib:
                    dict_source_layer[el.attrib['sourceLayer']] = el.find('Layout').attrib['textField']

        dict_source_layer_new = {}
        for k, v in dict_source_layer.items():
            dict_source_layer_new[k] = v.replace('{', '').replace('}', '')

        dict_se_layer = {}

        for elem in tree.findall('Sources')[0].findall('Source')[1].findall('Layers')[0].findall('Layer'):
            dict_se_layer[elem.attrib['id']] = elem.findall('Datasets')[0].find('Dataset').attrib['columns']

        for k,v in dict_se_layer.items():
            for k1,v1 in dict_source_layer_new.items():
                if k1 == k and (v1 not in v or v1 == ''):
                    print("{}: Test 2: For SourceLayer: {}, textField tag doesn't contain either part or the whole text of this value: {} from Sources element.".format(xmlfile, k, dict_se_layer[k]))





