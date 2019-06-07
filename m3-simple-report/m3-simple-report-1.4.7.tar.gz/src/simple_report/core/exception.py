# coding: utf-8
from __future__ import absolute_import

import abc

import six


class AbstractSectionException(six.with_metaclass(abc.ABCMeta, Exception)):
    """
    Абстрактный класс для исключений, которые возникают при работе с секциями
    """

class SectionException(AbstractSectionException):
    """
    Исключение работы с секциями
    """


class SectionNotFoundException(AbstractSectionException):
    """
    Исключение - секция не найдена
    """


class SheetException(six.with_metaclass(abc.ABCMeta, Exception)):
    """
    Абстрактный класс для исключений, которые возникают при работе с листами таблицы
    """


class SheetNotFoundException(SheetException):
    """
    Исключение "Лист не найден"
    """


class SheetDataException(SheetException):
    """
    Ошибка данных.
    """

class XLSReportWriteException(Exception):
    """
    Ошибка вывода в отчетах XLS
    """

class XLSXReportWriteException(Exception):
    """
    Ошибка вывода в отчетах XLSX
    """

class WrongDocumentType(Exception):
    """
    Ошибка формата документа
    """
    # Например, в Word-документе не предусмотрена генерация таблиц
