import os
from lxml import etree
from .exceptions import *


class EdoChecker:
    def __init__(self, *, root):
        self.parser = etree.XMLParser(encoding='cp1251', remove_comments=True)
        self.root = root

        # Компендиум проверочных схем
        self.compendium = dict()

        # Данные файла
        self.filename = None
        self.xml_content = None

    def setup_compendium(self):
        self.compendium = dict()

        comp_root = os.path.join(self.root, 'compendium')
        for root, dirs, files in os.walk(comp_root):
            for file in files:
                filename = file.split('.')[0]
                with open(os.path.join(root, file), 'r',
                          encoding='cp1251') as handler:
                    try:
                        xsd_name = '_'.join(filename.split('_')[:2])
                        xsd_content = etree.parse(handler, self.parser).getroot()
                        xsd_scheme = etree.XMLSchema(xsd_content)
                        self.compendium[xsd_name] = xsd_content, xsd_scheme
                    except etree.XMLSyntaxError as ex:
                        raise XsdSchemeError(ex)

    def check_file(self, input):
        self.filename = input.filename
        self.xml_content = input.xml_obj

        input.verify_result = dict()

        input.verify_result['result'] = 'passed'
        input.verify_result['sch_asserts'] = []
        input.verify_result['xsd_asserts'] = []

        # Определение проверочной схемы
        prefix = '_'.join(self.filename.split('_')[:2])
        if 'mark' in prefix.lower() or 'pros' in prefix.lower():
            prefix = prefix[:-4]
        xsd_content, xsd_scheme = self.compendium[prefix]

        # Проверка имени файла
        filename = self.filename.split('.')[0]
        attr_filename = self.xml_content.attrib['ИдФайл']
        if filename != attr_filename:
            input.verify_result['result'] = 'failed_sch'
            input.verify_result['sch_asserts'].append((
                'Проверка имени файла на соответствие значению атрибута @ИдФайл',
                '0400400007',
                f'Имя файла обмена {self.filename} не совпадает со значением '
                f'элемента ИдФайл {attr_filename}'
            ))

        # Проверка по xsd
        try:
            xsd_scheme.assertValid(self.xml_content)
        except etree.DocumentInvalid:
            input.verify_result['result'] = 'failed_xsd'
            for error in xsd_scheme.error_log:
                input.verify_result['xsd_asserts']\
                    .append(f'{error.message} (строка {error.line})')

        return
