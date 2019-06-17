import os
import BaseXClient
from lxml import etree
from atexit import register
from struct import pack, unpack
from utils import Flock, Logger
from glob import glob
from pprint import pprint


class PfrChecker:
    def __init__(self, *, root):
        self.root = root
        # Корневая директория для файлов валидации
        self.xsd_root = os.path.join(root, 'compendium/pfr/compendium/')
        # Список существующих направлений
        self.directions = ['АДВ+АДИ+ДСВ 1.17.12д',
                           'СЗВ-М+ИС+УПП АФ.2.32д',
                           'ЗНП+ЗДП 2.24д']
        # Направление xml файла:
        # 0 - АДВ, 1 - СЗВ, 2 - ЗНП
        self.direction = 0
        # Справочники для проверок КОРР файлов
        # (нужны для передачи в переменную $dictFile)
        self.dict_file = os.path.join(self.xsd_root,
                                      self.directions[1],
                                      'Справочники/Справочники.xml')
        # Название основного валидационного файла
        self.comp_file = 'ПФР_КСАФ.xml'

        # Название файла ПФР
        self.xml_file = None
        # Содержимое файла
        self.content = None
        # Содержимое файла в виде etree Element
        self.xml_content = None
        # Тип документа (например, АНКЕТА_ЗЛ)
        self.doc_type = None

        # Используемые парсеры
        self.cp_parser = etree.XMLParser(encoding='cp1251',
                                         recover=True,
                                         remove_comments=True)
        self.utf_parser = etree.XMLParser(encoding='utf-8',
                                          recover=True,
                                          remove_comments=True)
        # Текущий парсер
        self.parser = self.utf_parser
        # Текущее пространство имён
        self.nsmap = None
        # Достаём информацию из компендиумов
        self.compendium = list()
        for direction in self.directions:
            with open(os.path.join(self.xsd_root, direction, self.comp_file),
                      'rb') as handler:
                try:
                    self.compendium.append(
                        etree.fromstring(handler.read(),
                                         parser=self.utf_parser)
                    )
                except etree.XMLSyntaxError as ex:
                    print(f'Error xml file parsing: {ex}')

        self.session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

        # Корневая директория BaseX
        self.db_data = os.path.join(root, 'basex/data/')
        # Синхронизация записи в базы данных BaseX
        # для избежания write lock
        with Flock(os.path.join(self.db_data, '.sync')) as fd:
            self.db_num = unpack('I', os.read(fd, 4))[0]
            if self.db_num < os.cpu_count():
                self.db_num += 1
                self.db_root = self.db_data + f'xml_db{self.db_num}'
                os.lseek(fd, 0, os.SEEK_SET)
                os.write(fd, pack('I', self.db_num))
            else:
                raise Exception('Too many BaseX workers')

        # Регистрируем метод финализации
        register(self._finalize)

    def _finalize(self):
        """
        Метод для синхронизации процессов через .sync файл
        при завершении/рестарте
        """
        with Flock(os.path.join(self.db_data, '.sync')) as fd:
            num = unpack('I', os.read(fd, 4))[0]
            if num > 0:
                num -= 1
                os.lseek(fd, 0, os.SEEK_SET)
                os.write(fd, pack('I', num))
            else:
                raise Exception('Incorrect synchronisation value')

        if self.session:
            self.session.close()

    def _get_nonadv_scheme(self, prefix, nsmap):
        """
        Метод для возврата схем для НЕ АДВ направлений
        """
        # Нужен действующий формат со статусом "ПоУмолчанию"
        doc_format = self.compendium[self.direction].xpath(
            f'//d:ТипДокумента[@Код="{prefix}"]//d:Формат'
            f'[@Статус="Действующий" and @ПоУмолчанию="true"]',
            namespaces=nsmap)[0]
        # Путь к валидационной схеме
        schemes = doc_format.xpath('.//d:Валидация/d:Схема/text()',
                                   namespaces=nsmap)
        return schemes, doc_format

    def _get_adv_scheme(self):
        """
        Метод для возврата схем для АДВ направлений
        """
        nsmap = self.xml_content.nsmap
        nsmap['d'] = nsmap.pop(None)

        try:
            self.doc_type = self.xml_content.find('.//d:ТипДокумента',
                                                  namespaces=nsmap).text
        except AttributeError as ex:
            raise Exception('Не определён тип документа')

        try:
            doc_format = self.compendium[self.direction].xpath(
                f'.//d:Валидация[contains(d:ОпределениеДокумента, "{self.doc_type}")]',
                namespaces=self.nsmap)[0]
        except IndexError as ex:
            #TODO: make logger belong to class instance
            logger = Logger(os.path.join(self.root, 'logs/'))
            log = logger.get_logger('pfr_checker')
            log.exception(ex)
            raise

        # Путь к валидационной схеме
        schemes = doc_format.xpath('.//d:Схема/text()', namespaces=self.nsmap)
        return schemes, doc_format

    def _get_schemes(self):
        """
        Метод для получения проверочной схемы для xml файла
        """
        # Префикс файла (СЗВ-М, СТАЖ и т.д.). None для АДВ направлений
        prefix_list = self.xml_file.split('_')
        prefix = None
        self.direction = 0
        if 'СЗВ' in self.xml_file or 'ОДВ' in self.xml_file:
            prefix = prefix_list[3]
            self.direction = 1
        elif 'УППО' in self.xml_file:
            prefix = prefix_list[1]
            self.direction = 1
        elif 'ЗНП' in self.xml_file or 'ЗДП' in self.xml_file:
            prefix = prefix_list[2]
            self.direction = 2

        self.nsmap = self.compendium[self.direction].nsmap
        self.nsmap['d'] = self.nsmap.pop(None)

        # Не АДВ направление, используем префикс для поиска в компендиуме
        if prefix:
            schemes, doc_format = self._get_nonadv_scheme(prefix, self.nsmap)
        # АДВ направление, ищем тип документа в xml файле
        else:
            schemes, doc_format = self._get_adv_scheme()

        for idx, scheme in enumerate(schemes):
            schemes[idx] = scheme.replace('\\', '/')
        return schemes, doc_format

    def _validate_scheme(self, schemes, input):
        """
        Метод для проверки xml файла по xsd схеме
        """
        # Определение типа используемого парсера, для АДВ - cp1251
        if not self.direction:
            self.parser = self.cp_parser

        # Пробегаем по всем .xsd схемам и проверяем файл
        for scheme in schemes:
            with open(os.path.join(self.xsd_root,
                                   self.directions[self.direction],
                                   scheme), 'rb') as xsd_handler:
                try:
                    xsd_content = etree.parse(xsd_handler, self.parser).getroot()
                    xsd_scheme = etree.XMLSchema(xsd_content)
                except etree.XMLSyntaxError as ex:
                    # TODO: logger
                    raise Exception(f'Error xsd file parsing: {ex}')

            try:
                xsd_scheme.assertValid(self.xml_content)
            except etree.DocumentInvalid as ex:
                for error in xsd_scheme.error_log:
                    input.verify_result['xsd_asserts'] \
                        .append(f'{error.message} (строка {error.line})')

                input.verify_result['result'] = 'failed_xsd'
                input.verify_result['description'] = (
                    f'Ошибка при валидации по xsd схеме файла '
                    f'{self.xml_file}.')
                return
            except Exception as ex:
                logger = Logger(os.path.join(self.root, 'logs/'))
                log = logger.get_logger('pfr_misc')
                log.exception(ex)



    def _get_validators(self, doc_format):
        """
        Метод для получения протоколируемых проверок в сценарии
        """
        scenario_file = doc_format.xpath('.//d:Сценарий/text()',
                                         namespaces=self.nsmap)
        # Сценарий проверки не всегда присутствует
        if scenario_file:
            scenario_file = scenario_file[0]
        else:
            #TODO: raise exception
            return

        # Замена слэшей в пути
        scenario_dir = scenario_file.split('\\')[-1].split('.')[0]
        scenario_file = scenario_file[1:].replace('\\', '/')

        # Получение содержимого сценария
        with open(os.path.join(self.xsd_root,
                               self.directions[self.direction],
                               scenario_file), 'rb') as handler:
            try:
                scenario = etree.fromstring(handler.read(),
                                            parser=self.utf_parser)
            except etree.XMLSyntaxError as ex:
                #TODO: raise exception
                print(f'Error scenario file parsing: {ex}')
                return

        nsmap = scenario.nsmap
        nsmap['d'] = nsmap.pop(None)

        # Получение всех протоколируемых проверок
        validators = scenario.xpath(
            '//d:Проверки/d:Проверка[not(@Протоколируемая="0")]',
            namespaces=nsmap
        )
        return validators, scenario_dir, nsmap

    def _checkup_adv(self, checkups, q_nsmap, input):
        """
        Метод для получения результатов проверки (ошибок) для АДВ направлений
        """
        for checkup in checkups:
            code_presence = checkup.find('./d:КодРезультата', namespaces=q_nsmap)
            if len(code_presence):
                code = code_presence.text
            else:
                code = 50
            prot_code = self.doc_type
            description = checkup.find('./d:Описание', namespaces=q_nsmap).text
            results = checkup.findall('.//d:Результат', namespaces=q_nsmap)
            element_objs = []
            for result in results:
                element_path = result.text
                element_objs.append(element_path)
            input.verify_result['xqr_asserts'].append((
                code, prot_code, description, element_objs
            ))

    def _checkup_nonadv(self, checkups, q_nsmap, block_code, input):
        """
        Метод для получения результатов проверки (ошибок) для НЕ АДВ направлений
        """
        for checkup in checkups:
            check_code = checkup.attrib['ID']
            prot_code = '.'.join((block_code, check_code))
            code = checkup.find('./d:КодРезультата', namespaces=q_nsmap).text
            description = checkup.find('./d:Описание', namespaces=q_nsmap).text
            results = checkup.findall('.//d:Результат', namespaces=q_nsmap)
            element_objs = []
            for result in results:
                element_path = result.find('./d:ПутьДоЭлемента',
                                           namespaces=q_nsmap).text
                expected_value = result.find('./d:ОжидаемоеЗначение',
                                             namespaces=q_nsmap).text
                element_name = result.find('./d:Объект/d:Наименование',
                                           namespaces=q_nsmap).text
                element_value = result.find('./d:Объект/d:Значение',
                                            namespaces=q_nsmap).text
                element_objs.append((element_path,
                                     expected_value,
                                     element_name,
                                     element_value))

            input.verify_result['xqr_asserts'].append((
                code, prot_code, description, element_objs
            ))

    def _validate_scenario(self, validators, scenario_dir,
                           nsmap, xml_file_path, input):
        """
        Метод для проверки xml файла по протоколируемым проверкам из сценария
        """
        for validator in validators:
            validator_file = validator.xpath('./d:Файл/text()',
                                             namespaces=nsmap)[0]
            # Используем не .xml файл для проверки, а сразу сырой .xquery
            validator_file = validator_file.split('\\')[-1].split('.')[0] + '.xquery'

            query_file = os.path.join(self.xsd_root,
                                      self.directions[self.direction],
                                      f'XQuery/{scenario_dir}',
                                      validator_file)

            with open(query_file, 'r', encoding="utf-8") as handler:
                query = self.session.query(handler.read())

            # Передача external переменных в xquery запрос
            query.bind('$doc', f'{xml_file_path}')
            # Внешняя переменная dictFile присутствует только в СЗВ направлениях
            if self.direction == 1:
                query.bind('$dictFile', f'{self.dict_file}')

            query_result = query.execute()

            if query_result:
                check_result = etree.fromstring(query_result, parser=self.parser)
                q_nsmap = check_result.nsmap
                q_nsmap['d'] = q_nsmap.pop(None)
                # Запрос возвращает ответ в xml формате, проверяем,
                # вернулась ли ошибка (Результат != 0)
                block_code = check_result.attrib['ID']
                checkups = check_result.xpath(
                    '//d:Проверка[d:РезультатЗапроса/d:Результат[text()!=0]]',
                    namespaces=q_nsmap
                )
                if self.direction:
                    self._checkup_nonadv(checkups, q_nsmap, block_code, input)
                else:
                    self._checkup_adv(checkups, q_nsmap, input)
                # Обнаружили ошибки
                if checkups:
                    input.verify_result['result'] = 'failed_xqr'
                    input.verify_result['description'] = (
                        f'Ошибка при валидации по xquery выражению файла '
                        f'{self.xml_file}.')
            #TODO: check if no result has been returned

    def check_file(self, input, xml_file_path):
        self.xml_file = input.filename
        self.content = input.content
        self.xml_content = input.xml_obj

        input.verify_result = dict()

        input.verify_result['result'] = 'passed'
        input.verify_result['xsd_asserts'] = []
        input.verify_result['xqr_asserts'] = []

        # Получение списка проверочных схем и формата документа
        schemes, doc_format = self._get_schemes()

        # Открытие сессии BaseX
        self.session.execute(f'open xml_db{self.db_num}')

        # Проверка по xsd схеме
        self._validate_scheme(schemes, input)

        # Если проверка по xsd пройдена, проверяем сценарий
        # Получение всех протоколируемых проверок
        validators, scenario_dir, nsmap = self._get_validators(doc_format)

        self._validate_scenario(validators, scenario_dir, nsmap,
                                xml_file_path, input)

class Input:
    def __init__(self, filename, content, data):
        # self.parser = etree.XMLParser(encoding='utf-8',
        #                               recover=True,
        #                               remove_comments=True)
        self.filename = filename
        self.xml_obj = content
        self.content = data

xsd_root = '/home/vasily/PyProjects/FLK/pfr'
# root = '/home/vasily/PyProjects/FLK/pfr/compendium/АДВ+АДИ+ДСВ 1.17.12д/Примеры/ВЗЛ/Входящие'
root = '/home/vasily/PyProjects/FLK/pfr/__test'
# root = '/home/vasily/PyProjects/FLK/pfr/_'
checker = PfrChecker(root=xsd_root)
os.chdir(root)
for file in glob('*'):
    xml_file_path = os.path.join(root, file)
    with open(xml_file_path, 'rb') as handler:
        data = handler.read()
        # xml_content = etree.fromstring(data, parser=checker.cp_parser)
        xml_content = etree.fromstring(data, parser=checker.utf_parser)

        # etree.ElementTree(xml_content).write('/home/vasily/lol.xml', xml_declaration=True, encoding='utf-8')

        input = Input(file, xml_content, data)
        checker.check_file(input, xml_file_path)
        pprint(input.verify_result)