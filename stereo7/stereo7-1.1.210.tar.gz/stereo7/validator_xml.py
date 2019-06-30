import fileutils
import xml.etree.ElementTree as ET
import os

current_file = ''
logs = []

# TODO: add validate spine atlases


def find_file(path):
    search_paths = ['', 'lite/', 'pro/', 'steam/', 'islanddefense', 'islanddefensepro', 'steampunkpro']
    for search_path in search_paths:
        if search_path + path in fileutils.resources:
            return True
    return False


def validate_xmlnode(xmlnode):
    if xmlnode.tag == 'node':
        for name in xmlnode.attrib:
            value = xmlnode.attrib[name]
            validate_property(name, value)
    for child in xmlnode:
        validate_xmlnode(child)
    return True


def validate(file):
    try:
        global current_file
        current_file = file
        tree = ET.parse(fileutils.root_dir + '/Resources/' + file)
        root = tree.getroot()
        validate_xmlnode(root)
    except ET.ParseError as e:
        logs.append('Parsing xml error: [{}]. {}'.format(file, e.message))


def validate_property(name, value):
    if '##' in value:
        return True

    result = True
    msg = '{} [{}] not found in Resources'

    if name in ['image', 'imageN', 'imageS', 'imageD']:
        if '::' not in value:
            result = not value or value in fileutils.images or find_file(value)
        else:
            atlas = value[0: value.find('::')]
            frame = value[value.find('::') + 2:]
            result = atlas in fileutils.spriteframes and frame in fileutils.spriteframes[atlas]
            if not result:
                msg = 'spriteframe [{}] not found in atlas [{}]'.format(value, atlas)
    elif value.endswith('.png') or value.endswith('.jpg'):
        if name == 'pair':
            k = value.find(':')
            if k == -1:
                msg = 'Not found divider fro property [pair] = [{}]'.format(value)
                result = False
            icon = value[k + 1:]
            if '::' not in value:
                result = not icon or icon in fileutils.images or find_file(icon)
            else:
                atlas = icon[0: icon.find('::')]
                frame = icon[icon.find('::') + 2:]
                result = atlas in fileutils.spriteframes and frame in fileutils.spriteframes[atlas]
                if not result:
                    msg = 'spriteframe [{}] not found in atlas [{}]'.format(value, atlas)

    if name == 'template':
        result = value in fileutils.xmls or find_file(value)
    if name == 'font' or name == 'fontttf':
        result = value in fileutils.fonts or find_file(value)
    if name == 'spineSkeleton':
        result = value in fileutils.resources or find_file(value) or value == ''
    if name == 'spineAtlas':
        result = value in fileutils.resources or find_file(value) or value == ''
        if result and value != '':
            result, msg = validate_atlas(value)

    if not result:
        print msg
        logs.append(('Error in file [{}]: ' + msg).format(current_file, name, value))

    return result


def validate_atlas(file):
    image = open(fileutils.root_dir + '/Resources/' + file).read().strip().split('\n')[0].strip()
    folder = os.path.dirname(file)
    image = folder + '/' + image
    return image in fileutils.images, 'image [{}] for atlas [{}] not founded'.format(image, file)
