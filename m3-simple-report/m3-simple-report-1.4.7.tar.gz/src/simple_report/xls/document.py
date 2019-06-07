# coding: utf-8
from __future__ import absolute_import

import xlrd

from simple_report.core.document_wrap import BaseDocument
from simple_report.core.document_wrap import SpreadsheetDocument
from simple_report.xls.output_options import XSL_OUTPUT_SETTINGS
from simple_report.xls.workbook import Workbook


class DocumentXLS(BaseDocument, SpreadsheetDocument):
    """
    Обертка для отчетов в формате XLS
    """

    def __init__(self, ffile, tags=None, **kwargs):
        self.file = ffile
        self._workbook = Workbook(ffile, **kwargs)

    @property
    def workbook(self):
        """
         Получение рабочей книги
        :result: рабочая книга
        """
        return self._workbook

    def build(self, dst):
        """
         Сборка отчета
        :param dst: путь до выходного файла
        :result:
        """
        self._workbook.build(dst)

    def __setattr__(self, key, value):

        if key in XSL_OUTPUT_SETTINGS:
            setattr(self._workbook, key, value)
        else:
            super(DocumentXLS, self).__setattr__(key, value)
