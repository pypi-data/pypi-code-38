import os
from os.path import isfile, isdir
import xml.etree.ElementTree as ET
import xml.dom.minidom
import hashlib


root_dir = '.'
ignore_folders = []
resources = []
xmls = []
images = []
atlases = []
fonts = []
spriteframes = {}
atlas_names = {}
unused = []


def createDir(path):
    if not os.path.exists(path):
        print 'Create directory [{}]'.format(path)
        os.makedirs(path)


def createDirForFile(file):
    dir = file
    if '/' not in dir:
        return
    k = dir.rindex('/')
    dir = dir[:k]
    createDir(dir)


def _getFilesList(path, prefix='', recursive=True):
    try:
        list = os.listdir(path)
        listFiles = []
        for i in list:
            if recursive and isdir(path + i):
                result = _getFilesList(path + i + "/", prefix + i + "/")
                for r in result:
                    listFiles.append(r)
            if isfile(path + i):
                listFiles.append(prefix + i)
        return listFiles
    except OSError as e:
        print '============================'
        print "Except: I/O error({0}): {1}".format(e.errno, e.strerror)
        print 'FileUtils::_getFilesList({}, {})'.format(path, prefix)
        print '============================'
        return []


def getFoldersList(path):
    try:
        list = os.listdir(path)
        foldersFiles = []
        for i in list:
            if isdir(path + i) and i[0] != '.':
                foldersFiles.append(i)
        return foldersFiles
    except OSError as e:
        print '============================'
        print "Except: I/O error({0}): {1}".format(e.errno, e.strerror)
        print 'FileUtils::getFoldersList({})'.format(path)
        print '============================'
        return []


def getFilesList(path, recursive=True):
    if not path.endswith('/'):
        path += '/'
    return _getFilesList(path, "", recursive)


def write(file, data, silent=False):
    createDirForFile(file)
    exist = isfile(file)
    if not exist or open(file).read() != data:
        if not silent:
            log_title = 'update' if exist else 'create'
            print log_title, file
        open(file, 'w').write(data)


def getSize(file):
    return os.path.getsize(file)


def save_xml(file, root, sorting_func=None, silent=False):
    buffer = ET.tostring(root)
    xml_ = xml.dom.minidom.parseString(buffer)
    if sorting_func:
        sorting_func(xml_)
    buffer = xml_.toprettyxml(encoding='utf-8')
    lines = buffer.split('\n')
    buffer = ''
    for line in lines:
        if line.strip():
            buffer += line + '\n'
    write(file, buffer, silent)


def inspectResources():
    root = root_dir + '/Resources/'
    global resources
    resources = getFilesList(root)
    for file in resources:
        ignore = False
        for folder in ignore_folders:
            ignore = ignore or file.startswith(folder + '/')
        if ignore:
            resources.remove(file)
            continue
        if file.endswith('.xml'):
            xmls.append(file)
        elif file.endswith('.plist'):
            atlases.append(file)
        elif file.endswith('.png') or file.endswith('.jpg'):
            images.append(file)
        elif file.endswith('.ttf') or file.endswith('.fnt'):
            fonts.append(file)
    parse_atlases()


def parse_atlases():
    def critical_error(msg):
        print msg
        print '\n All atlases:\n\n', '\n'.join(atlases)
        exit(-1)

    def parse_atlas_name():
        # from code:
        atlas_names['images/other.plist'] = 'other'
        atlas_names['images/logo.plist'] = 'logo'
        main_resources = 'ini/title/layer.xml'
        if main_resources not in xmls:
            main_resources = 'ini/maings/mainlayer.xml'
        if main_resources in xmls:
            xmlroot = ET.parse(root_dir + '/Resources/' + main_resources).getroot()
            xml_ress = xmlroot.find('resources').find('atlases')
            for xml_res in xml_ress:
                path = xml_res.attrib['path']
                name = xml_res.attrib['name']
                if path not in atlases:
                    critical_error('Critical Error: atlas {} not found \n'.format(path))
                atlas_names[path] = name
        else:
            print 'Warning: cannot find file with mainpack resources'
        if 'ini/gamescene/resources.xml' in xmls:
            xmlroot = ET.parse(root_dir + '/Resources/ini/gamescene/resources.xml').getroot()
            xml_ress = xmlroot.find('resources')
            for child in xml_ress:
                if child.tag != 'resoucre':
                    continue
                for xml_res in child:
                    path = xml_res.attrib['path']
                    name = xml_res.attrib['name']
                    if path not in atlases:
                        critical_error('Critical Error: atlas {} not found \n'.format(path))
                        exit(-1)
                    atlas_names[path] = name
        else:
            print 'Warning: cannot find file with mainpack resources'

    parse_atlas_name()
    for file in atlases:
        if file not in atlas_names:
            unused.append(file)
            continue
        atlas_name = atlas_names[file]
        if atlas_name not in spriteframes:
            spriteframes[atlas_name] = []
        xmlroot = ET.parse(root_dir + '/Resources/' + file).getroot()
        dict_ = xmlroot.find('dict')
        br = False
        for child in dict_:
            if child.tag == 'dict' and br:
                for framexml in child:
                    if framexml.tag == 'key':
                        frame = framexml.text
                        spriteframes[atlas_name].append(frame)
                break
            if child.tag == 'key' and child.text == 'frames':
                br = True


def getMd5File(file):
    m = hashlib.md5()
    m.update(open(file, 'rb').read())
    return str(m.hexdigest())
