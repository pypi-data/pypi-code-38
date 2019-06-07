# coding: utf-8
from __future__ import absolute_import

from lxml.etree import Element
from lxml.etree import SubElement
from lxml.etree import _Element
import six


class SharedStringsTable(object):
    """
    Таблица общих строк
    """

    def __init__(self, root):
        """
        """
        # Ключами являются строки, индексами значения
        self.new_elements_dict = {}
        self.new_elements_list = []
        self._new_elements_dict = {}

        assert isinstance(root, _Element)
        #assert 'count' in root.attrib # TODO: Разобраться почему нет в виндовых шаблонах
        #assert 'uniqueCount' in root.attrib # TODO: Разобраться почему нет в виндовых шаблонах
        assert  hasattr(root, 'nsmap')

        self.nsmap = root.nsmap
        self.uniq_elements = self.count = 0

        self.elements = [''.join(t.text or '' for t in si) for si in root]


    def get_new_index(self, value_string):
        """
        Возвращаем индекс нового элемента таблицы shared string
        Ищем в множестве, иначе получаем нелинейное время flush секции
        """

        new_index = self._new_elements_dict.get(value_string)
        if new_index is None:
            new_index = self.uniq_elements
            self.new_elements_list.append(value_string)
            self._new_elements_dict[new_index] = value_string
            self.uniq_elements += 1

        return str(new_index)

    def get_new_index_old(self, value_string):
        """
        Возвращаем индекс нового элемента таблицы shared string
        """

        try:
            new_index = self.new_elements_list.index(value_string)
        except ValueError:
            new_index = self.uniq_elements
            self.new_elements_list.append(value_string)
            self.uniq_elements += 1

        return str(new_index)

    def get_value(self, index):
        """
        
        :param index: индекс
        :result: значение ячейки по индексу
        """
        return self.elements[index]

    def to_xml(self):
        u"""
         Переводит таблицу в xml
        :result: корневой узел xml
        """
        root = Element('sst', {'count': str(len(self.new_elements_list)),
                               'uniqueCount': str(self.uniq_elements)},
            nsmap=self.nsmap)

        for elem in self.new_elements_list:
            si = SubElement(root, 'si')
            t = SubElement(si, 't')
            t.text = six.text_type(elem)

        return root
