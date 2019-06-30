import xml.etree.ElementTree as ET
from google_sheets import GoogleSheets
from project import Project
import fileutils
import validator_localization
from validate import print_log


class Locale:

    def __init__(self):
        self.values = ['', '']


def convert_to_table():
    locales = {}
    keys = []

    for i, lang in enumerate(['en', 'ru']):
        filepath = '{}/Resources/lang/{}.xml'.format(fileutils.root_dir, lang)
        root = ET.parse(filepath).getroot()
        dict_ = root.find('dict')
        key = ''
        value = ''
        for child in dict_:
            if child.tag == 'key':
                key = child.text
            elif child.tag == 'string':
                value = child.text
                if key and value and len(key) and len(value):
                    if key not in locales:
                        locale = Locale()
                        locales[key] = locale
                    locales[key].values[i] = value
                    # print len(locales), len(locales[key].values), locales[key], key, value

                    if key not in keys:
                        keys.append(key)
                    key = ''
                    value = ''

    for key in keys:
        print key + '\t' + '\t'.join(locales[key].values)


def download(document_id):

    languages = ['EN', 'RU', 'DE', 'FR', 'IT']

    gs = GoogleSheets(CLIENT_SECRET_FILE=Project.instance.gg_secret_file)
    gs.set_document(document_id)
    raw = gs.read_range(gs.get_sheet_titles()[0], 'A1', 'Z')
    header = raw[0]
    data = raw[1:]

    for lang in languages:
        if lang not in header:
            print '  - Skip [{}]'.format(lang)
            continue
        locales = []
        index_id = header.index('ID')
        index_lg = header.index(lang)
        for line in data:
            id = line[index_id]
            lg = line[index_lg]
            locale = Locale()
            locales.append([id, lg])

        lg = ''
        for item in locales:
            id = item[0]
            locale = item[1]
            if not id:
                continue
            lg += '        <key>{}</key><string>{}</string>\n'.format(id, locale.encode('utf-8'))
        lg = '<plist version="1.0">\n    <dict>\n' + lg + '    </dict>\n</plist>'
        fileutils.write('{}/Resources/lang/{}.xml'.format(fileutils.root_dir, lang.lower()), lg)
        print '  - Download [{}] finished'.format(lang)

    print_log(validator_localization, 'Validate localization:')
