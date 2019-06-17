import os
import BaseXClient
from lxml import etree
from glob import glob
from pprint import pprint
from time import time
from utils import Translator


class Input:
    def __init__(self, filename, content):
        # self.parser = etree.XMLParser(encoding='utf-8',
        #                               recover=True,
        #                               remove_comments=True)
        self.filename = filename
        self.xml_obj = content


xsd_root = '/home/vasily/PyProjects/FLK/pfr/compendium/АДВ+АДИ+ДСВ 1.17.12д'
root = '/home/vasily/PyProjects/FLK/pfr/compendium/АДВ+АДИ+ДСВ 1.17.12д/Примеры/ВЗЛ/Входящие'
compendium_file = 'ПФР_КСАФ.xml'
xml_file = 'PFR-700-Y-2017-ORG-034-005-000023-DCK-00444-DPT-000000-DCK-00000.xml'

cp_parser = etree.XMLParser(encoding='cp1251',
                            recover=True,
                            remove_comments=True)
# cp_parser.resolvers.add(DTDResolver())

utf_parser = etree.XMLParser(encoding='utf-8',
                             recover=True,
                             remove_comments=True)

# Достаём информацию из компендиума
with open(os.path.join(xsd_root, compendium_file), 'rb+') as handler:
    try:
        compendium = etree.fromstring(handler.read(), parser=utf_parser)
    except etree.XMLSyntaxError as ex:
        print(f'Error xml file parsing: {ex}')
        exit(1)

os.chdir(root)
for file in glob('*'):
    xml_file_path = os.path.join(root, file)
    with open(xml_file_path, 'rb') as handler:
        data = handler.read()
        xml_content = etree.fromstring(data, parser=cp_parser)
        input = Input(xml_file, xml_content)

    nsmap = xml_content.nsmap
    nsmap['d'] = nsmap.pop(None)

    try:
        doc_type = xml_content.find('.//d:ТипДокумента', namespaces=nsmap).text
        print(doc_type)
    except AttributeError as ex:
        print('Не определён тип документа')
        exit(1)

    nsmap = compendium.nsmap
    nsmap['d'] = nsmap.pop(None)

    st = time()
    doc_def = compendium.xpath(
        f'.//d:Валидация[contains(d:ОпределениеДокумента, "{doc_type}")]',
        namespaces=nsmap)[0]
    print('Elapsed time:', time() - st)

    # Путь к валидационной схеме
    schemes = doc_def.xpath('.//d:Схема/text()', namespaces=nsmap)

    # Пути в схемах как в винде, поэтому меняем слэши
    for idx, scheme in enumerate(schemes):
        schemes[idx] = scheme.replace('\\', '/')

    # Работаем с проверяемым .xml файлом
    # Проверка, есть ли уже такой в базе
    # query = self.session.query(f'db:exists("xml_db{self.db_num}", '
    #                            f'"{self.db_root}/{self.xml_file}")')
    # query_result = query.execute()
    # if query_result == 'false':
    #     # Файл не найден, добавляем
    #     self.session.add(f'{self.db_root}/{self.xml_file}',
    #                      self.content.decode('utf-8'))
    # if query:
    #     query.close()


    input.verify_result = dict()

    input.verify_result['result'] = 'passed'
    input.verify_result['xsd_asserts'] = []
    input.verify_result['xqr_asserts'] = []

    # Пробегаем по всем .xsd схемам и проверяем файл
    for scheme in schemes:
        # new_path = Translator.translate('/'.join(scheme.split('/')[1:]))
        # new_scheme = os.path.join('Схемы', new_path)
        with open(os.path.join(xsd_root, scheme), 'rb') as xsd_handler:
            try:
                xsd_content = etree.parse(xsd_handler, cp_parser).getroot()
                xsd_scheme = etree.XMLSchema(xsd_content)
                try:
                    xsd_scheme.assertValid(xml_content)
                except etree.DocumentInvalid as ex:
                    for error in xsd_scheme.error_log:
                        input.verify_result['xsd_asserts'] \
                            .append(f'{error.message} (строка {error.line})')

                    input.verify_result['result'] = 'failed_xsd'
                    input.verify_result['description'] = (
                        f'Ошибка при валидации по xsd схеме файла '
                        f'{file}: {ex}.')
                    # return

            except etree.XMLSyntaxError as ex:
                #TODO: logger
                print(f'Error xsd file parsing: {ex}')
                # return

    # Проверка по xsd пройдена, дальше проверяем сценарий
    scenario_file = doc_def.xpath('.//d:Сценарий/text()', namespaces=nsmap)
    # Сценарий проверки не всегда присутствует
    if scenario_file:
        scenario_file = scenario_file[0]
    else:
        exit(0)
    # Те же танцы с бубнами для слэшей
    scenario_dir = scenario_file.split('\\')[-1].split('.')[0]
    scenario_file = scenario_file[1:].replace('\\', '/')

    # Получение содержимого сценария
    print('_'*80)
    print(xml_file_path)
    with open(os.path.join(xsd_root, scenario_file), 'rb') as handler:
        try:
            scenario = etree.fromstring(handler.read(), parser=utf_parser)
        except etree.XMLSyntaxError as ex:
            print(f'Error scenario file parsing: {ex}')

    # Та же история с пространством имён, не работает с пустыми ключами
    nsmap = scenario.nsmap
    nsmap['d'] = nsmap.pop(None)

    # Получение всех протоколируемых проверок
    validators = scenario.xpath('//d:Проверки/d:Проверка[not(@Протоколируемая="0")]', namespaces=nsmap)

    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    # Проход по всем проверкам
    for validator in validators:
        validator_file = validator.xpath('./d:Файл/text()', namespaces=nsmap)[0]
        # Используем не .xml файл для проверки, а сразу сырой .xquery
        validator_file = validator_file.split('\\')[-1].split('.')[0] + '.xquery'
        query_file = os.path.join(xsd_root, f'XQuery/{scenario_dir}', validator_file)

        with open(query_file, 'r', encoding="utf-8") as handler:
            query = session.query(handler.read())

        # Передача external переменных в xquery запрос
        query.bind('$doc', f'{xml_file_path}')

        query_result = query.execute()

        if query_result:
            check_result = etree.fromstring(query_result, parser=cp_parser)
            q_nsmap = check_result.nsmap
            q_nsmap['d'] = q_nsmap.pop(None)
            # Запрос возвращает ответ в xml формате, проверяем, вернулась ли ошибка (Результат != 0)
            block_code = check_result.attrib['ID']
            checkups = check_result.xpath('//d:Проверка[d:РезультатЗапроса/d:Результат[text()!=0]]',
                                          namespaces=q_nsmap)
            # Обнаружили ошибки
            for checkup in checkups:
                print(etree.tostring(checkup, encoding='utf-8').decode())
                # check_code = checkup.attrib['ID']
                # prot_code = '.'.join((block_code, check_code))
                # code = checkup.find('./d:КодРезультата', namespaces=q_nsmap).text
                description = checkup.find('./d:Описание', namespaces=q_nsmap).text
                results = checkup.findall('.//d:Результат', namespaces=q_nsmap)
                element_objs = []
                for result in results:
                    print(etree.tostring(result, encoding='utf-8').decode())
                    element_path = result.text
                #     element_path = result.find('./d:ПутьДоЭлемента', namespaces=q_nsmap).text
                #     expected_value = result.find('./d:ОжидаемоеЗначение', namespaces=q_nsmap).text
                #     element_name = result.find('./d:Объект/d:Наименование', namespaces=q_nsmap).text
                #     element_value = result.find('./d:Объект/d:Значение', namespaces=q_nsmap).text
                #     element_objs.append((element_path, expected_value, element_name, element_value))
                    element_objs.append(element_path)
                #
                input.verify_result['xqr_asserts'].append((description, element_objs))
                #     code, prot_code, description, element_objs
                # ))
                # input.verify_result['result'] = 'failed_xqr'
                # input.verify_result['description'] = (
                #     f'Ошибка при валидации по xquery выражению файла '
                #     f'{xml_file}.')
    if session:
        session.close()

    pprint(input.verify_result)

# В check_file было:
# Работаем с проверяемым .xml файлом
# Проверка, есть ли уже такой в базе
# query = self.session.query(f'db:exists("xml_db{self.db_num}", '
#                            f'"{self.db_root}/{self.xml_file}")')
# query_result = query.execute()
# if query_result == 'false':
#     # Файл не найден, добавляем
#     encoding = 'utf-8' if self.direction else 'cp1251'
#     self.session.add(f'{self.db_root}/{self.xml_file}',
#                      self.content.decode(encoding))
# if query:
#     query.close()

#
# class Input:
#     def __init__(self, filename, content, data):
#         # self.parser = etree.XMLParser(encoding='utf-8',
#         #                               recover=True,
#         #                               remove_comments=True)
#         self.filename = filename
#         self.xml_obj = content
#         self.content = data
#
# xsd_root = '/home/vasily/PyProjects/FLK/pfr'
# root = '/home/vasily/PyProjects/FLK/pfr/compendium/АДВ+АДИ+ДСВ 1.17.12д/Примеры/ВЗЛ/Входящие'
# checker = PfrChecker(root=xsd_root)
# os.chdir(root)
# for file in glob('*'):
#     xml_file_path = os.path.join(root, file)
#     with open(xml_file_path, 'rb') as handler:
#         data = handler.read()
#         xml_content = etree.fromstring(data, parser=checker.cp_parser)
#         input = Input(file, xml_content, data)
#         checker.check_file(input, xml_file_path)
#         pprint(input.verify_result)
