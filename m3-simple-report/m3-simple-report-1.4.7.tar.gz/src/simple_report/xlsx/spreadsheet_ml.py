# coding: utf-8
from __future__ import absolute_import

import os
import re

from lxml.etree import QName
from lxml.etree import fromstring
from lxml.etree import tostring

from simple_report.core.exception import SectionException
from simple_report.core.exception import SectionNotFoundException
from simple_report.core.exception import SheetNotFoundException
from simple_report.core.shared_table import SharedStringsTable
from simple_report.core.xml_wrap import CommonProperties
from simple_report.core.xml_wrap import OpenXMLFile
from simple_report.core.xml_wrap import ReletionOpenXMLFile
from simple_report.core.xml_wrap import ReletionTypes
from simple_report.utils import get_addr_cell
from simple_report.xlsx.cursor import Cursor
from simple_report.xlsx.section import Section
from simple_report.xlsx.section import SheetData


class Comments(OpenXMLFile):
    u"""
    Комментарии в XLSX
    """
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    NS_XDR = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"

    section_pattern = re.compile(u'[\+|\-]+[A-Za-zА-яА-я0-9_]+')

    def __init__(self, sheet_data, *args, **kwargs):
        """
        
        :param sheet_data: данные для листа 
        :type sheet_data: xlsx.section.SheetData
        """
        super(Comments, self).__init__(*args, **kwargs)

        assert isinstance(sheet_data, SheetData)
        self._sheet_data = sheet_data

        self.sections = {}

        self.comment_list = self._root.find(QName(self.NS, 'commentList'))
        self._create_section()

        # Проверка, правильно ли указаны секции и есть ли конец секции
        self._test_sections()


    def _test_sections(self):
        u"""
        Проверка секций на валидность
        """
        for section_object in self.sections.values():
            if not section_object.name or not section_object.begin or not section_object.end:
                raise ValueError("Bad section: %s" % section_object)

    def _parse_sections(self, comment_list):
        """
        Распознаем секции
        
        :param comment_list: Список комментариев
        :type comment_list: iterable
        """

        for comment in comment_list:
            cell = comment.get('ref')
            for text in comment:
                for r in text:
                    for t in r.findall(QName(self.NS, 't')):
                        yield t.text, cell


    def _create_section(self):
        u"""
        Создание объектов секций из комментариев
        """
        for section in  self._parse_sections(self.comment_list):
            self._add_section(section)

    def _add_section(self, values):
        text = values[0]
        cell = values[1]

        values = self.section_pattern.findall(text)
        addr = get_addr_cell(cell)
        for value in values:
            section_name = self._get_name_section(value)

            # Такой объект должен быть
            if value.startswith('-'):
                # Такой элемент уже должен быть
                if not self.sections.get(section_name):
                    raise SectionException('Start section "%s" not found' % section_name)

                section = self.sections[section_name]

                # Второго конца быть не может
                if section.end:
                    raise SectionException('For section "%s" more than one ending tag' % section_name)

                section.end = addr
            else:
                # Второго начала у секции быть не может
                if self.sections.get(section_name):
                    raise SectionException('For section "%s" more than one beging tag' % section_name)

                self.sections[section_name] = Section(self._sheet_data, section_name, begin=addr)

    def _get_name_section(self, text):
        """
        Возвращает из наименования ++A - название секции
        
        :param text: комментарий
        :type text: basestring
        """
        for i, s in enumerate(text):
            if s.isalpha():
                return text[i:]
        else:
            raise SectionException('Section name bad format "%s"' % text)

    def get_section(self, section_name):
        """
        Получение секции по имени
        
        :param section_name:
        :type section_name:
        """
        try:
            section = self.sections[section_name]
        except KeyError:
            raise SectionNotFoundException('Section "%s" not found' % section_name)
        else:
            return section

    def get_sections(self):
        u"""
        Получение всех секций
        """
        return self.sections

    @classmethod
    def create(cls, cursor, *args, **kwargs):
        return cls(cursor, *args, **kwargs)

    def build(self):
        u"""
        Сборка файла с комментариями, предварительно удалив их
        """
        if len(self.comment_list) > 0:
            self.comment_list.clear()

        with open(self.file_path, 'wb') as f:
            f.write(
                tostring(self._root, encoding='utf-8', xml_declaration=True)
            )


class SharedStrings(OpenXMLFile):
    u"""
    XML-файл с общими строками, на каждую из которых могут ссылаться из
    других xml-файлов XLSX
    """
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

    def __init__(self, *args, **kwargs):
        super(SharedStrings, self).__init__(*args, **kwargs)
        self.table = SharedStringsTable(self._root)

    def build(self):
        u"""
        Сборка файла
        """
        new_root = self.table.to_xml()
        with open(self.file_path, 'wb') as f:
            f.write(
                tostring(new_root, encoding='utf-8', xml_declaration=True)
            )


class WorkbookSheet(ReletionOpenXMLFile):
    u"""
    Лист книги документа в формате XLSX
    """

    NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


    def __init__(self, shared_table, tags, name, sheet_id,
            *args, **kwargs):
        """
        
        :param shared_table:
        :type shared_table:
        :param tags:
        :type tags:
        :param name:
        :type name:
        :param sheet_id:
        :type sheet_id:
        """
        super(WorkbookSheet, self).__init__(*args, **kwargs)
        self.name = name
        self.sheet_id = sheet_id

        # Первый элемент: начало вывода по вертикали, второй по горизонтали
        self.sheet_data = SheetData(self._root,
            cursor=Cursor(),
            ns=self.NS,
            shared_table=shared_table,
            tags=tags,
            )

        self.drawing, self.comments = self.walk_reletion()


    def walk_reletion(self):
        """
        """
        drawing = comments = None
        if not self._reletion_root is None:
            for elem in self._reletion_root:
                param = (elem.attrib['Id'], elem.attrib['Target'])
                if elem.attrib['Type'] == ReletionTypes.DRAWING:
                    drawing = self._get_drawing(*param)

                elif elem.attrib['Type'] == ReletionTypes.COMMENTS:
                    comments = self._get_comment(*param)

        return drawing, comments


    def _get_comment(self, rel_id, target):
        u"""
        Получение объекта комментария
        """
        return Comments.create(self.sheet_data, rel_id, *self._get_path(target))

    def _get_drawing(self, rel_id, target):
        u"""
        Unused
        """

    def __str__(self):
        res = [u'Sheet name "{0}":'.format(self.name)]
        if self.comments:
            for section in self.sections:
                res.append(u'\t %s' % section)
        return u'\n'.join(res).encode('utf-8')


    def __repr__(self):
        return self.__str__()

    @property
    def sections(self):
        return self.comments.get_sections()


    def get_section(self, name):
        u"""
        Получение секции по имени
        """
        return self.comments.get_section(name)

    def get_sections(self):
        u"""
        Получение всех секций
        """
        return self.sections

    def build(self):
        u"""
        Сборка xml-файла
        """
        new_root = self.sheet_data.new_sheet()

        with open(self.file_path, 'wb') as f:
            f.write(
                tostring(new_root, encoding='utf-8', xml_declaration=True)
            )

        if self.comments:
            self.comments.build()

    def get_rowbreaks(self):
        return self.sheet_data.get_rowbreaks()

    def get_colbreaks(self):
        return self.sheet_data.get_colbreaks()


class WorkbookStyles(OpenXMLFile):
    """
    Unused
    """


class Workbook(ReletionOpenXMLFile):
    u"""
    Книга в формате XLSX
    """
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


    def __init__(self, tags, *args, **kwargs):
        """
        
        :param tags:
        :type tags:
        """
        super(Workbook, self).__init__(*args, **kwargs)

        self.tags = tags

        (
            self.workbook_style,
            tmp_sheets,
            self.shared_strings,
            self.calc_chain
                                ) = self.walk_reletions()
        self.sheets = self.walk(tmp_sheets)

        if self.sheets:
            # По-умолчанию активным считается первый лист
            self._active_sheet = self.sheets[0]
        else:
            raise SheetNotFoundException('Sheets not found')

    def walk_reletions(self):
        u"""
        
        """
        workbook_style = shared_strings = calc_chain = None
        sheets = {}
        for elem in self._reletion_root:
            param = (elem.attrib['Id'], elem.attrib['Target'])
            if elem.attrib['Type'] == ReletionTypes.WORKBOOK_STYLE:
                workbook_style = self._get_style(*param)

            elif elem.attrib['Type'] == ReletionTypes.WORKSHEET:
                sheets[elem.attrib['Id']] = elem.attrib['Target']

            elif elem.attrib['Type'] == ReletionTypes.SHARED_STRINGS:
                shared_strings = self._get_shared_strings(*param)
            elif elem.attrib['Type'] == ReletionTypes.CALC_CHAIN:
                calc_chain = self._get_calc_chain(*param)
                self._reletion_root.remove(elem)

        return workbook_style, sheets, shared_strings, calc_chain

    def walk(self, sheet_reletion):
        """
        """
        sheets = []
        sheets_elem = self._root.find(QName(self.NS, 'sheets'))
        for sheet_elem in sheets_elem:
            name = sheet_elem.attrib['name']
            sheet_id = sheet_elem.attrib['sheetId']
            # state = sheet_elem.attrib['state'] -- В win файле нет такого свойства

            rel_id = sheet_elem.attrib.get(QName(self.NS_R, 'id'))
            target = sheet_reletion[rel_id]
            sheet = self._get_worksheet(rel_id, target, name, sheet_id)
            sheets.append(sheet)

        return sheets

    def _get_style(self, _id, target):
        """
        Unused
        """

    def _get_worksheet(self, rel_id, target, name, sheet_id):
        """
        Получение листа книги
        :param rel_id:
        :type rel_id:
        :param target:
        :type target:
        :param name:
        :type name:
        :param sheet_id:
        :type sheet_id:
        """
        worksheet = WorkbookSheet.create(self.shared_table, self.tags,
            name, sheet_id, rel_id, *self._get_path(target))
        return worksheet

    def _get_shared_strings(self, _id, target):
        """
        Получение общих строк
        
        :param _id: идентификатор строки
        :type _id:
        :param target:
        :type target:
        """

        return SharedStrings.create(_id, *self._get_path(target))

    def _get_calc_chain(self, _id, target):
        return CalcChain.create(_id, *self._get_path(target))

    def get_section(self, name):
        """
        """
        return self._active_sheet.get_section(name)

    def get_sections(self):
        """
        """
        return self._active_sheet.get_sections()

    @property
    def active_sheet(self):
        return self._active_sheet

    @active_sheet.setter
    def active_sheet(self, value):
        assert isinstance(value, int)
        self._active_sheet = self.sheets[value]

    def build(self):
        """
        """
        for sheet in self.sheets:
            sheet.build()

        self.shared_strings.build()
        if self.calc_chain:
            self.calc_chain.build()

    @property
    def shared_table(self):
        return self.shared_strings.table

    def get_rowbreaks(self):
        return self._active_sheet.get_rowbreaks()

    def get_colbreaks(self):
        return self._active_sheet.get_colbreaks()

class CommonPropertiesXLSX(CommonProperties):
    """

    """

    def _get_app_common(self, _id, target):
        """
        """
        return Workbook.create(self.tags, _id, *self._get_path(target))


class CalcChain(OpenXMLFile):
    """
    Цепочка вычислений. Указывает порядок вычислений в ячейках а также
    является кешем значений.
    (http://stackoverflow.com/questions/9004848/working-with-office-open-xml-just-how-hard-is-it)
    Поскольку довольно сложно в автоматическом режиме указывать порядок
    вычисления, просто удаляем файл + ссылки на него.
    Еще 1 плюс такого подхода - больше не должна повторяться ошибка при
    открытии файла в MS Office 2007/2010, шаблон которого был сохранен
    то в Libre/Openoffice, то в MS Office
    """

    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

    def build(self):
        """
        Удаляем файл с цепочкой вычислений
        """
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    @classmethod
    def from_file(cls, file_path):
        assert file_path
        # if os.path.exists(file_path):
        #     with open(file_path) as f:
        #         return parse(f).getroot()
        # else:
        return fromstring("<fake_root/>")
