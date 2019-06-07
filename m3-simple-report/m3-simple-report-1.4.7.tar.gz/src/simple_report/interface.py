# coding: utf-8
from __future__ import absolute_import

from abc import ABCMeta
from abc import abstractmethod

import six


class IReport(object):
    def show(self, *args, **kwargs):
        """
        Deprecated: use build
        """
        self.build(*args, **kwargs)

    @abstractmethod
    def build(self, *args, **kwargs):
        u"""
        Построение отчета  
        """


class IDocumentReport(six.with_metaclass(ABCMeta, IReport)):
    @abstractmethod
    def build(self, dst_file_path, params, file_type):
        """
        Генерирует выходной файл в нужном формате
        
        :param dst_file_path: путь до выходного файла
        :type dst_file_path: str
        :param params: словарь ключ: параметр в шаблоне,
                       значение: заменяющая строка
                
        :type params: dict
        :param file_type: тип файла
        :type file_type: str
        """

    @abstractmethod
    def get_all_parameters(self):
        u"""
        Возвращает все параметры документа
        """


class ISpreadsheetReport(six.with_metaclass(ABCMeta, IReport)):
    @abstractmethod
    def get_sections(self):
        u"""
        Возвращает все секции
        """

    @abstractmethod
    def get_section(self, section_name):
        """
        Возвращает секцию по имени
        
        :param section_name: имя секции
        :type section_name: str
        """

    @abstractmethod
    def build(self, dst_file_path, file_type):
        """
        Генерирует выходной файл в нужном формате
        
        :param dst_file_path: путь до выходного файла
        :type dst_file_path: str
        :param file_type: тип файла
        :type file_type: str
        """


class ISpreadsheetSection(six.with_metaclass(ABCMeta, object)):
    VERTICAL = 0
    HORIZONTAL = 1
    RIGHT_UP = 2
    LEFT_DOWN = 3
    RIGHT = 4
    HIERARCHICAL = 5

    @abstractmethod
    def flush(self, params, oriented=LEFT_DOWN):
        """
        Записать данные в секцию
        
        :param params: словарь параметров
        :type params: dict
        :param oriented: направление вывода секций
        :type oriented: int
        """


    @abstractmethod
    def get_all_parameters(self):
        u"""
        Возвращает все параметры секции
        """
