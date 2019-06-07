# coding: utf-8
from __future__ import absolute_import

from collections import namedtuple
from datetime import datetime
from tempfile import gettempdir
import os
import re
import shutil
import sys
import uuid
import zipfile

from six.moves import range


class FileException(Exception):
    u"""
    Исключение работы с файл-прокси
    """


class ZipFileAdapter(object):
    """
    Из-за того, что в версии начиная с 2.7 модуль zipfile умеет работать
    с менеджером контекста, а вот ниже версии - не умеет.
    Будем поддерживать версию 2.6
    """

    def __init__(self, *args, **kwargs):
        self.z_file = zipfile.ZipFile(*args, **kwargs)

        self.old = False
        # Проверка версии в питоне
        if sys.version_info < (2, 7):
            self.old = True

    def __enter__(self):
        if self.old:
            return self.z_file
        else:
            return self.z_file.__enter__()

    def __exit__(self, *args, **kwargs):
        if self.old:
            return self.z_file.close()
        else:
            return self.z_file.__exit__(*args, **kwargs)


class ZipProxy(object):
    u"""
    Распаковка/упаковка Open XML
    """

    @classmethod
    def _extract(cls, src_file_path, dst_files_path):
        """
        Распаковывает zip файл
        
        :param src_file_path: путь до исходного файла
        :type src_file_path: str
        :param dst_files_path: путь до выходного файла/директории
        :type dst_files_path: str
        
        """
        with ZipFileAdapter(src_file_path) as zip_file:
            zip_file.extractall(dst_files_path)

    @classmethod
    def _pack(cls, dst_file_path, src_files_path):
        """
        Запаковывает zip файл
        
        :param dst_file_path: путь до выходного файла
        :type dst_file_path: str
        :param src_files_path: путь до директории с входными файлами
        :type src_files_path: str
        """
        with ZipFileAdapter(dst_file_path, 'w') as zip_file:
            for root, _, file_names in os.walk(src_files_path):
                for file_name in file_names:
                    # Абсолютный путь до файла
                    abs_path = os.path.join(root, file_name)

                    # Путь до директории
                    dir_path = abs_path[len(src_files_path) + len(os.sep):]

                    zip_file.write(
                        abs_path, dir_path, compress_type=zipfile.ZIP_DEFLATED)

    @classmethod
    def extract(cls, src_file):
        """
        Распаковывает zip архив во временную папку
        
        :param src_file: путь до архива
        :type src_file: str
        """
        assert isinstance(src_file, FileProxy)

        #
        extract_folder = os.path.join(gettempdir(),
            '_'.join([str(uuid.uuid4())[:8], src_file.get_file_name()]))

        cls._extract(src_file.get_path(), extract_folder)

        return extract_folder

    @classmethod
    def pack(cls, dst_file, extract_folder):
        """
        Запаковывает директорию в архив и удаляет ее
        
        :param dst_file: выходной файл
        :type dst_file: FileProxy
        :param extract_folder: исходная директория
        :type extract_folder: str
        """
        assert isinstance(dst_file, FileProxy)
        cls._pack(dst_file.get_path(), extract_folder)
        shutil.rmtree(extract_folder)


class FileProxy(object):
    u"""
    Прокси работы с файлами
    """

    def __init__(self, file_like_object, new_file=False):
        """
        
        :param file_like_object: Путь до файла
        :type file_like_object: str
        :param new_file: создавать ли новый файл?
        :type new_file: bool
        """
        if isinstance(file_like_object, FileProxy):
            file_like_object = file_like_object.file

        self.is_file_like_object = False
        if hasattr(file_like_object, 'read'):
            raise FileException("File like object temporarily not supported.")

        if not os.path.exists(file_like_object) and not new_file:
            raise FileException('File "%s" not found.' % file_like_object)

        if not os.path.isfile(file_like_object) and not new_file:
            raise FileException('"%s" is not file' % file_like_object)

        self.file = file_like_object

    def get_path(self):
        u"""
        Возвращает путь до файла
        """
        return self.file

    def get_file_like_object(self):
        u"""
        Возвращает открытый файл
        """
        return self.file

    def get_file_name(self):
        u"""
        Возвращает только имя файла
        """
        if self.is_file_like_object:
            file_name = self.file.name
        else:
            file_name = self.file

        return os.path.split(file_name)[-1]


class ColumnHelper(object):
    """
    Существенно облегчает работу с ячейками

    По данными ('ALC'), ('AVB') возврашает итератор по диапазону ячеек
    ('ALC', 'ALD', 'ALE', ..., 'AVA', 'AVB')

    Так же умеет работать, если переданы данные: ('A'), ('ALP')

    """

    @classmethod
    def number_to_column(cls, n):
        """
        Преобразует номер колонки в ее строковое представление
        :param n: номер колонки
        :type n: int
        """
        return (
            ~n and cls.number_to_column(n // 26 - 1) + chr(65 + n % 26) or ''
        )

    @classmethod
    def column_to_number(cls, index):
        """
        Преобразует строковое представление колонки в число
        
        :param index: номер
        :type index: int
        """
        s = 0
        pow_ = 1
        for letter in index[::-1]:
            d = int(letter, 36) - 9
            s += pow_ * d
            pow_ *= 26
            # excel starts column numeration from 1
        return s - 1

    @classmethod
    def get_range(cls, begin, end):
        u"""
        Итератор, выдающий строковые представления колонок между
        начальной и конечной колонкой 
        
        :param begin: строковое представление начальной колонки
        :type begin: str
        :param end: строковое представление конечной колонки
        :type end: str
        """
        for i in range(cls.column_to_number(begin), cls.column_to_number(end) + 1):
            yield cls.number_to_column(i)

    @classmethod
    def add(cls, column, i):
        """
        Добавляет к колонке column i колонок
        
        :param column: строковое представление колонки
        :type column: str
        :param i: число дополнительных колонок
        :type i: int
        """
        return cls.number_to_column(cls.column_to_number(column) + i)

    @classmethod
    def difference(cls, col1, col2):
        """
        Разница (расстояние) между двумя колонками
        
        :param col1: строковое представление первой колонки
        :type col1: str
        :param col2: строковое представление второй колонки
        :type col2: str
        """
        return cls.column_to_number(col1) - cls.column_to_number(col2)


def get_addr_cell(text):
    """
    Возвращает адрес ячейки
    То есть из представления 'AZ12' выдается ('AZ', 12)
    
    :param text: полное строковое представление ячейки
    :type text: str
    """
    for i, s in enumerate(text):
        if s.isdigit():
            return text[:i], int(text[i:])
    else:
        raise ValueError('Addr cell is bad format value "%s"' % text)


def date_to_float(date):
    """
    Конвертирует дату в число с плавающей точкой относительно 1900 года

    Значение даты OLE-автоматизации реализовано как число с плавающей запятой,
    равное количеству дней, прошедших с полуночи 30 декабря 1899 г.
    Например, полночь 31 декабря 1899 г. представляется числом 1,0;
    06:00 1 января 1900 г. — числом 2,25;
    полночь 29 декабря 1899 г. — числом 1,0
    и 06:00 29 декабря 1899 г. — числом 1,25.

    http://msdn.microsoft.com/ru-ru/library/system.datetime.tooadate%28v=vs.90%29.aspx

    ps: Спасибо Вадиму, который предотвратил распространение кастылей,
    типо кастомного форматирования параметров
    
    :param date: Дата-время
    :type date: datetime.datetime
    """
    assert isinstance(date, datetime)

    date_1900 = datetime(1899, 12, 30)

    days = abs((date - date_1900).days)

    hours = date.time().hour - date_1900.time().hour

    minute = date.time().minute - date_1900.time().minute

    return days + (hours + minute / 60.0) / 24.0


FormulaWriteExcel = namedtuple('FormulaWriteExcel',
                                ['formula_id', 'excel_function', 'ranged'],
                                verbose=False)

class FormulaWriteExcelFromStr:
    """
    Для переноса текстовой формулы из Python в Excel по принципу "как есть",
    Но не стоит забывать об особенностях, например, что ";" при перечислении
    образуется с помощью ",", а если использовано будет в строке ";",
    то в Excel получим "|". По-хорошему этот перенос для простой арифметики
    """
    def __init__(self, text):
        self.text = text


def split_string(string, line_length):
    u"""
    Разбить строку на подстроки, по возможности, не превышающие заданной длины.

    :param basestring string: разбиваемая строка
    :param int line_length: желаемая длина подстроки
    :return: список подстрок строки
    :rtype: list
    """
    name_words = string.split()
    lines = [[]]
    cur_line_length = 0
    for word in name_words:
        if cur_line_length and cur_line_length + 1 + len(word) > line_length:
            lines.append([])
            cur_line_length = len(word)
        else:
            cur_line_length += len(word) + 1
        lines[-1].append(word)

    return [u' '.join(line) for line in lines]
