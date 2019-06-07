# coding: utf-8
from __future__ import absolute_import

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

import six

from simple_report.utils import ZipProxy


class BaseDocument(six.with_metaclass(ABCMeta, object)):
    """
    Базовый класс для всех документов
    """

    @abstractmethod
    def build(self):
        """
         Сборка документа
        :result:
        """


class SpreadsheetDocument(six.with_metaclass(ABCMeta, object)):

    @abstractproperty
    def workbook(self):
        """
        Рабочая книга
        """

    def get_sections(self):
        """
        Возвращает все секции в шаблоне
        """
        return self.workbook.get_sections()

    def get_section(self, name):
        """
        Возвращает секцию по названию шаблона
        """
        return self.workbook.get_section(name)

    @property
    def sheets(self):
        """
        Листы отчета
        """
        return self.workbook.sheets


class DocumentOpenXML(six.with_metaclass(ABCMeta, BaseDocument)):
    u"""
    Базовый класс для работы со структурой open xml
    """

    def __init__(self, src_file, tags):
        self.extract_folder = ZipProxy.extract(src_file)

        self._tags = tags # Ссылка на тэги

    def build(self, dst_file):
        """
        Сборка отчета
        """
        ZipProxy.pack(dst_file, self.extract_folder)
