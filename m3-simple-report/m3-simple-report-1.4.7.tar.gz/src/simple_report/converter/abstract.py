# coding: utf-8
from __future__ import absolute_import

import os

from simple_report.utils import FileProxy


class FileConverterException(Exception):
    """
    """


class FileConverter(object):
    u"""
    Конвертирует файл из одного формата в другой
    """

    # open xml formats
    DOCX = 'docx'
    XLSX = 'xlsx'

    HTML = 'html'
    DOC = 'doc'
    XLS = 'xls'
    PDF = 'pdf'
    RTF = 'rtf'

    # OpenOffice Formats
    ODT = 'odt'
    ODS = 'ods'
    ODF = 'odf'

    def __init__(self):
        self.file = self.ext = None

    def build(self, to_format):
        u"""
        Метод должен исходя из исходного типа документа и требуемого типа
        найти метод у себя и вызвать его. Если этого метода нет - должно
        генериться исключение.
        """
        assert self.ext and self.file, 'File and extension must be define'

        if self.ext == to_format:
            return self.file.get_path()
        else:
            return self.convert(to_format)

    def convert(self, to_format):
        """

        """
        if to_format == self.XLSX:
            func = self.__dict__.get('xlsx2%s' % to_format)
        else:
            func = self.__dict__.get('%s2xlsx' % to_format)

        if callable(func):
            return func()
        else:
            raise FileConverterException(
                'Converter %s not supported format "%s"' % (self.__class__.__name__, to_format))

    def set_src_file(self, src_file):
        """

        """
        assert isinstance(src_file, FileProxy)
        self.file = src_file
        self.ext = src_file.get_file_name().split(os.path.extsep)[-1] # Расширение файла
