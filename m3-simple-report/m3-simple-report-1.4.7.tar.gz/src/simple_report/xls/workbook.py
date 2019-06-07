# coding: utf-8
from __future__ import absolute_import

from uuid import uuid4

from xlrd.sheet import Sheet
from xlutils.filter import XLWTWriter
import xlrd

from simple_report.converter.abstract import FileConverter
from simple_report.core.exception import SectionNotFoundException
from simple_report.core.exception import SheetNotFoundException
from simple_report.xls.cursor import CursorXLS
from simple_report.xls.section import Section


class WorkbookSheet():

    # спец. символ конца строки
    END_STRING = '\n'

    def __init__(self, sheet, writer):
        assert isinstance(sheet, Sheet), 'sheet must be xlrd.sheet.Sheet instance'

        self.sheet = sheet
        self.writer = writer
        self.cursor = CursorXLS()
        self.sections = {}
        self.formula_id_dict = {}

    def get_section(self, name):
        """
         Получение секции по имени
        :param name: имя секции
        :result: секция
        """
        assert name, 'Section name is empty'
        if name not in self.sections:
            begin = end = None

            begin_section_text = '+' + name
            end_section_text = '-' + name

            # Получаем все примечания.
            # sheet.cell_note_map представляет собой словарь
            # { (colx, coly): note_instance }
            notes = self.sheet.cell_note_map

            for (note_coord, note) in notes.items():
                # При составлении шаблона, разработчик может после имени секции вставить символ конца
                # строки. В этом случае, данная секция не будет найдена. Поэтому необходимо данный
                # символ обрезать.
                note_text = note.text[:-1] if note.text[-1] == WorkbookSheet.END_STRING else note.text

                if note_text == begin_section_text:
                    begin = note_coord

                elif note_text == end_section_text:
                    end = note_coord

                elif (
                    note_text.lstrip().startswith(begin_section_text) and
                    note_text.rstrip().endswith(end_section_text)
                ):
                    # Является ли данная ячейка смерженной.
                    row_coord, column_coord = note_coord
                    for merged_cell in self.sheet.merged_cells:
                        # Смерженная ячейка представленна в виде списка из 4 элементов
                        # (clo, rlo) - координаты левой верхней ячейки данной смерженной ячейки
                        # chi - количество колонок в смерженной ячейке
                        # rli - количество строк в смерженной ячейке
                        rlo, rhi, clo, chi = merged_cell
                        if column_coord == clo and row_coord == rlo:
                            # Сохраняем начало и конец смерженной ячейки
                            begin = (clo, rlo)
                            end = (chi - 1, rhi - 1)
                            break

                    if not (begin and end):
                        begin = end = note_coord

            if not (begin and end):
                raise SectionNotFoundException('Section named %s has not been found' % name)
            self.sections[name] = Section(self, name, begin, end, self.writer)
        return self.sections[name]

    def get_sections(self):
        """
         Получение всех секций
        :result: словарь секций
        """
        return self.sections

    def get_name(self):
        """
         Получение названия листа
        :result: название листа
        """
        return self.sheet.name


class Workbook(object):

    def __init__(self, ffile, *args, **kwargs):
        """
        """

        self.workbook = xlrd.open_workbook(ffile.file, formatting_info=True)

        self.xlwt_writer = XLWTWriter()
        self.xlwt_writer.start()
        self.xlwt_writer.workbook(self.workbook, '%s.xls'%uuid4())

        self.sheets = self._sheet_list()

        if self.sheets:
            pass
            # self.init_active_sheet()
        else:
            raise SheetNotFoundException('Sheets not found')

        for k, v in kwargs.items():
            setattr(self, k, v)

    def init_active_sheet(self):
        """
         инициализация активного листа
        :result: None
        """
        self._active_sheet = self.sheets[0]
        self.xlwt_writer.sheet(self._active_sheet.sheet, self._active_sheet.sheet.name)

    def configure_writer(self):
        """
        Настройка конфигураций writer-а
        """

        if hasattr(self, 'fit_num_pages'):
            self.xlwt_writer.wtsheet.fit_num_pages = self.fit_num_pages

        if hasattr(self, 'portrait_orientation'):
            self.xlwt_writer.wtsheet.portrait = self.portrait_orientation

        if hasattr(self, 'fit_width_to_pages'):
            self.xlwt_writer.wtsheet.fit_width_to_pages = self.fit_width_to_pages

        if hasattr(self, 'fit_height_to_pages'):
            self.xlwt_writer.wtsheet.fit_height_to_pages = self.fit_height_to_pages
        else:
            # По-умолчанию, указываем значение 0, для того, чтобы не запихивать огромный отчет на одну страницу.
            self.xlwt_writer.wtsheet.fit_height_to_pages = 0

        if hasattr(self, 'header_str'):
            self.xlwt_writer.wtsheet.header_str = self.header_str
        else:
            #
            self.xlwt_writer.wtsheet.header_str = (u'')

        if hasattr(self, 'footer_str'):
            self.xlwt_writer.wtsheet.footer_str = self.footer_str
        else:
            #
            self.xlwt_writer.wtsheet.footer_str = (u'&P из &N')

    def get_section(self, name):
        """
         Получение секции по имени
        :param name: имя секции
        :result: секция
        """
        if not hasattr(self, '_active_sheet'):
            self._active_sheet = self.sheets[0]
            self.xlwt_writer.sheet(self._active_sheet.sheet, self._active_sheet.sheet.name)
        return self._active_sheet.get_section(name)

    def get_sections(self):
        """
         Получение всех секций
        :result: словарь с секциями
        """

        workbook_sections = {}

        for sheet in self.sheets:
            workbook_sections.update(sheet.get_sections())

        return workbook_sections

    @property
    def active_sheet(self):
        return self._active_sheet

    @active_sheet.setter
    def active_sheet(self, value):
        assert isinstance(value, int)
        try:
            self._active_sheet = self.sheets[value]
        except IndexError:
            raise SheetNotFoundException('Sheet not found')

        try:
            self.xlwt_writer.sheet(self._active_sheet.sheet, self.get_sheet_name())
            # Проставляем номер листа в выходном документе.
            # Для этого берём номер соответствующего узла из шаблона и прибавляем 1, т.к.
            # нумерация с нуля.
            self.xlwt_writer.wtsheet.start_page_number = self.xlwt_writer.rdsheet.number + 1
            # Настраиваем writer для работы с новым листом.
            self.configure_writer()
        except ValueError:
            return

    def _sheet_list(self):
        all_sheets = self.workbook._sheet_list

        sheet_list = []
        for sheet in all_sheets:
            sheet_list.append(WorkbookSheet(sheet, self.xlwt_writer))

        return sheet_list

    def get_sheet_name(self):
        return self.active_sheet.get_name()

    def build(self, dest_file):
        """
         Сборка книги
        :param dest_file: выходной путь
        :result: None
        """

        self.configure_writer()

        dest_file_name = dest_file.file

        self.xlwt_writer.finish()

        # Получаем формат файла
        dest_file_format = dest_file_name.split('.')[-1]

        # Если не xls, то проставляем явно.
        if dest_file_format != FileConverter.XLS:
            dest_file_name = '%s.%s' % (dest_file_name, FileConverter.XLS)

        # self.xlwt_writer.output имеет вид
        # [('выходной файл1', Workbook1), ('выходной файл2', Workbook2), ... ]
        # Для данного Workbook выбираем первый кортеж
        ouput_file, workbook = self.xlwt_writer.output[0]
        workbook.save(dest_file_name)

    def write_sheet_count(self):
        """
        Подсчитываем количество листов в которых есть секции
        (другими словами в них будет производиться запись)
        """

        # Берём листы из шаблона
        read_sheets = self.xlwt_writer.rdbook._sheet_list

        return len([read_sheet for read_sheet in read_sheets if read_sheet.cell_note_map])
