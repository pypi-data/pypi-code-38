# coding: utf-8
from __future__ import absolute_import

from abc import ABCMeta
from abc import abstractmethod
import os

from lxml.etree import parse
import six


class OpenXMLFile(six.with_metaclass(ABCMeta, object)):
    """
    Файл XML в структуре OpenXML
    """

    NS = None

    def __init__(self, rel_id, folder, file_name, file_path):
        self.reletion_id = rel_id
        self.current_folder = folder
        self.file_name = file_name
        self.file_path = file_path
        self._root = self.from_file(file_path)

    def _get_path(self, target):
        """
         получение путей файла
        :param target: целевой путь
        :result: относительный путь, название файла, полный путь

            """
        split_path = os.path.split(target)
        relative_path = os.path.join(self.current_folder, *split_path[:-1])
        abs_path = os.path.join(relative_path, split_path[-1])

        return relative_path, split_path[-1], abs_path


    def get_root(self):
        """
         Получение корневого элемента
        :result: корневой элемент
        """
        return self._root

    @classmethod
    def from_file(cls, file_path):
        """
         Парсинг файла
        :param cls:
        :param file_path: путь до файла
        :result: корневой элемент
        """
        assert file_path
        with open(file_path) as f:
            return parse(f).getroot()


    @classmethod
    def create(cls, *args, **kwargs):
        """
        Инстанцирование класса
        """
        return cls(*args, **kwargs)


class ReletionOpenXMLFile(six.with_metaclass(ABCMeta, OpenXMLFile)):
    """
    Файл связей
    """

    RELETION_EXT = '.rels'
    RELETION_FOLDER = '_rels'

    def __init__(self, *args, **kwargs):
        super(ReletionOpenXMLFile, self).__init__(*args, **kwargs)

        assert not self.file_name is None

        rel_path = os.path.join(self.current_folder, self.RELETION_FOLDER, self.file_name + self.RELETION_EXT)

        self._reletion_root = None # Если остальные листы в документе не используются, то стилей для них нет
        if os.path.exists(rel_path):
            self._reletion_root = self.from_file(rel_path)


class CommonProperties(six.with_metaclass(ABCMeta, ReletionOpenXMLFile)):
    u"""
    Общие настройки

    Находит папку _rels и парсит файл .rels в нем
    """

    #
    NS = "http://schemas.openxmlformats.org/package/2006/relationships"

    #
    APP_TYPE = None

    def __init__(self, tags, *args, **kwargs):
        super(CommonProperties, self).__init__(*args, **kwargs)

        self.tags = tags

        self.core = self.app = self.main = None
        self.walk()


    def walk(self):
        """
        Проход по корневому элементу
        """
        for elem in self._root:
            param = (elem.attrib['Id'], elem.attrib['Target'])
            if elem.attrib['Type'] == ReletionTypes.MAIN:
                self.main = self._get_app_common(*param)

            elif elem.attrib['Type'] == ReletionTypes.APP:
                self.app = self._get_app(*param)

            elif elem.attrib['Type'] == ReletionTypes.CORE:
                self.core = self._get_core(*param)


    def _get_app(self, _id, target):
        """
        """
        return App.create(_id, *self._get_path(target))

    def _get_core(self, _id, target):
        """
        """
        return Core.create(_id, *self._get_path(target))

    @classmethod
    def create(cls, folder, tags):
        """
         Получение экземпляра класса
        :param cls: класс
        :param folder: путь до директории с распакованным XML-документом
        :param tags: теги
        :result: Экземпляр класса
        """

        reletion_path = os.path.join(folder, cls.RELETION_FOLDER, cls.RELETION_EXT)
        rel_id = None # Корневой файл связей
        file_name = '' # Не имеет названия, т.к. состоит из расширения .rels
        return cls(tags, rel_id, folder, file_name, reletion_path, )


    @abstractmethod
    def _get_app_common(self, *args):
        """
        """


class App(OpenXMLFile):
    """
    """


class Core(OpenXMLFile):
    """
    """


class ReletionTypes(object):
    """
    Типы связей
    """
    MAIN = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    APP = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
    CORE = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"

    WORKSHEET = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
    WORKBOOK_STYLE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"

    SHARED_STRINGS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings"

    COMMENTS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
    DRAWING = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/vmlDrawing"

    CALC_CHAIN = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/calcChain"
