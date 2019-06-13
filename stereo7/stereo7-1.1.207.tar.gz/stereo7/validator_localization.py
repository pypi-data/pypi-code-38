import xml.etree.ElementTree as ET
import game
import os
import fileutils

logs = []


class Key:

    def __init__(self):
        self.id = ''
        self.value = {}


class Localization:

    def __init__(self):
        self.lang = ''
        self.keys = {}


localizations = []
all_keys = {}
all_ids = []


def log(msg):
    logs.append(msg)


def validate():
    result = True
    parse()
    count = len(localizations)
    for key in all_keys:
        if len(all_keys[key]) != count:
            without = []
            without.extend(all_ids)
            for id in all_keys[key]:
                without.remove(id)
            log('Error: key [{}] have not locations: [{}]'.format(key, ', '.join(without)))
            result = False
    for localization in localizations:
        for key in localization.keys:
            value = localization.keys[key]
            if not value.strip():
                log('Warning: [{}][{}] is empty'.format(localization.id, key))
    return result


def parse():
    root = ET.parse(fileutils.root_dir + '/Resources/lang/lang.xml').getroot().find('languages')
    for child in root:
        localization = Localization()
        for id in child.attrib:
            localization.id = id
            all_ids.append(id)
            break
        localizations.append(localization)

    for localization in localizations:
        file = fileutils.root_dir + '/Resources/lang/{}.xml'.format(localization.id)
        if not os.path.isdir(file):
            continue
        root = ET.parse(file).getroot().find('dict')
        key = ''
        value = ''
        for i, child in enumerate(root):
            if i % 2 == 0:
                key = child.text
            else:
                value = child.text
                if value is None:
                    value = ''
                localization.keys[key] = value.encode('utf-8')
                if key not in all_keys:
                    all_keys[key] = {}
                all_keys[key][localization.id] = value
