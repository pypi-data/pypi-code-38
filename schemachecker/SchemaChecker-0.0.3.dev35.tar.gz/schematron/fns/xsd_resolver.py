import os
from database import db
from lxml import etree


class TestResolver(object):
    def __init__(self, xsd_content, xml_content, xml_file):
        self.xsd_schema = xsd_content
        self.xml_obj = xml_content
        self.filename = xml_file


def _return_error(text):
    return f'\u001b[31mError. {text}.\u001b[0m'


def _get_xml_info(xml_file, xml_content):
    xml_info = {}
    document_node = xml_content.find('Документ')
    if document_node is not None:
        xml_info['knd'] = document_node.get('КНД', None)
        if not xml_info['knd']:
            xml_info['knd'] = document_node.get('Индекс', None)
        if not xml_info['knd']:
            xml_info['knd'] = xml_content.xpath('//Документ/ОписПерСвед/@КНД')[0]
        xml_info['version'] = xml_content.attrib.get('ВерсФорм')
    else:
        # Ошибка, элемент "Документ" не найден
        raise Exception(f'Элемент "Документ" в файле '
                        f'{xml_file} не найден')
    return xml_info


async def _get_xsd_scheme(xml_info):
    query = '''SELECT xsd
            FROM documents
            WHERE knd = $1
            AND version = $2'''

    return await db.fetchval(query, xml_info['knd'], xml_info['version'])


async def get_xsd_file(xml_path, xsd_root):
    parser = etree.XMLParser(encoding='cp1251', remove_comments=True)
    xml_file = os.path.basename(xml_path)

    # Формирование результата
    result = {'file': xml_path,
              'result': 'failed',
              'description': '',
              'asserts': []}

    with open(xml_path, 'rb') as xml_file_handler:
        try:
            xml_content = etree.fromstring(xml_file_handler.read())
        except etree.XMLSyntaxError:
            print('Error xml file parsing:', xml_path)
            return TestResolver(None, None, None)

    try:
        xml_info = _get_xml_info(xml_file, xml_content)
    except Exception as ex:
        # Ошибка при получении информации (КНД, версия и т.д.)
        print(_return_error(ex))
        result['description'] = _return_error(ex)
        return TestResolver(None, None, None)
        # return result

    try:
        xsd_file = await _get_xsd_scheme(xml_info)
    except Exception as ex:
        # Ошибка при получении имени xsd схемы из БД
        print(_return_error(f'Ошибка при получении имени xsd схемы из'
                            f' БД при проверке файла {xml_file}: {ex}.'))
        result['description'] = f'Ошибка при получении имени xsd ' \
                                f'схемы из БД при проверке файла {xml_file}.'
        return TestResolver(None, None, None)
        # return result

    if not xsd_file:
        # На найдена xsd схема для проверки
        print('_' * 80)
        print('FILE:', xml_file)
        print(_return_error(f'Не найдена xsd схема для проверки '
                            f'файла {xml_file}.'))
        result['description'] = f'Не найдена xsd схема для проверки файла {xml_file}.'
        return TestResolver(None, None, None)
        # return result

    result['xsd_scheme'] = xsd_file

    try:
        with open(os.path.join(xsd_root, result['xsd_scheme']),
                  'r', encoding='cp1251') as xsd_file_handler:
            xsd_content = etree.parse(xsd_file_handler, parser).getroot()
        resolver = TestResolver(xsd_content, xml_content, xml_file)
        return resolver
    except FileNotFoundError as ex:
        return TestResolver(None, None, None)
