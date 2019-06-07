# coding: utf-8
from __future__ import absolute_import

import copy
import os

from lxml.etree import SubElement
from lxml.etree import tostring
import six

from simple_report.core.exception import SectionException
from simple_report.core.exception import SectionNotFoundException
from simple_report.core.xml_wrap import CommonProperties
from simple_report.core.xml_wrap import OpenXMLFile
from simple_report.core.xml_wrap import ReletionOpenXMLFile
from simple_report.docx.drawing import DocxImage
from simple_report.docx.drawing import insert_image


class Wordprocessing(ReletionOpenXMLFile):
    """
    Основной файл формата DOCX
    """
    NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

    # Узел контекста document
    # .// рекурсивно спускаемся к потомкам в поисках
    # <ns:p><ns:r><ns:t></ns:t></ns:r></ns:p>
    XPATH_QUERY = './/{0}:p/{0}:r/{0}:t'
    TABLES_QUERY = './/{0}:tbl'
    TABLE_TEXT_NODE_QUERY = './/{0}:tc/{0}:p/{0}:r/{0}:t'

    def __init__(self, tags, *args, **kwargs):
        super(Wordprocessing, self).__init__(*args, **kwargs)

        self.tags = tags
        self.table_sections = {}

    def build(self):
        """
        Сборка файла
        """
        with open(self.file_path, 'wb') as f:
            f.write(
                tostring(self._root, encoding='utf-8', xml_declaration=True)
            )

    def set_params(self, params):
        """
         Подстановка параметров
        :param params: параметры подстановки
        :result: None
        """
        #
        self.merge_same_nodes()
        text_nodes = self._root.xpath(
            self.XPATH_QUERY.format('w'), namespaces={'w': self.NS_W}
        )
        self._set_params(text_nodes, params, self.doc_rels)

    def get_signature(self, node):
        signature = []
        for subnode in list(node):
            if subnode.tag != '{%s}lang' % self.NS_W:
                signature.append((subnode.tag, sorted(subnode.items())))
        return signature

    def merge_same_nodes(self):
        """
         Слияние одинаковых нод - нужно, т.к. редакторы DOCX
        привносят свои специфичные изменения, которые нам не нужны
        :result:
        """
        paragraphs = list(self._root.xpath(
            './/{0}:p'.format('w'), namespaces={'w': self.NS_W}
        ))

        t_tag = '{%s}t' % self.NS_W
        r_tag = '{%s}r' % self.NS_W
        rpr_tag = '{%s}rPr' % self.NS_W
        tab_tag = '{%s}tab' % self.NS_W
        for paragraph in paragraphs:
            par_nodes = list(paragraph)
            old_signature = None
            signature = None
            old_node = None

            for par_node in par_nodes:
                if par_node.tag != r_tag:
                    old_node = None
                    continue
                for node in list(par_node):
                    if node.tag == rpr_tag:
                        old_signature = signature
                        signature = self.get_signature(node)
                    elif node.tag == tab_tag:
                        old_node = None
                    elif node.tag == t_tag:
                        if old_node is not None and old_signature == signature:
                            # delete r node
                            old_node[1].text = old_node[1].text + node.text
                            paragraph.remove(par_node)
                        else:
                            old_node = (par_node, node)

    @classmethod
    def split_into_paragraphs(cls, text_node, text_rows):
        """
            Разбивает текущий текст на несколько параграфов
            (для отображения текста в несколько строчек)
        """
        text_node.text = text_rows[0]
        paragraph = list(
            text_node.iterancestors(
                '{' + Wordprocessing.NS_W + '}p'))[0]

        for text in text_rows[1:]:
            p_copy = copy.copy(paragraph)
            paragraph.addnext(p_copy)
            t_node = p_copy.find(
                './/{0}:r/{0}:t'.format('w'),
                namespaces={'w': Wordprocessing.NS_W}
            )
            t_node.text = text
            paragraph = p_copy
            
    @classmethod
    def _set_params(cls, text_nodes, params, doc_rels=None):

        def sorting_key(item):
            key, _ = item
            if not isinstance(key, six.string_types):
                return 1
            return -len(key)

        for node in text_nodes:
            for key_param, value in sorted(six.iteritems(params), key=sorting_key):
                if key_param in node.text:
                    text_to_replace = '#%s#' % key_param
                    if text_to_replace in node.text:
                        if isinstance(value, DocxImage):
                            insert_image(
                                node, value, text_to_replace, doc_rels)
                        else:
                            node.text = node.text.replace(
                                text_to_replace, six.text_type(value))
                    else:
                        node.text = node.text.replace(
                            key_param, six.text_type(value))
                    
                    # Проверим наличие символов новой строки в тексте
                    text_rows = node.text.split('\n')
                    if len(text_rows) > 1:
                        cls.split_into_paragraphs(node, text_rows)
                        
    def get_all_parameters(self):
        """
        Получение всех параметров
        """
        text_nodes = self._root.xpath(
            self.XPATH_QUERY.format('w'), namespaces={'w': self.NS_W})

        for node in text_nodes:
            if (
                len(node.text) > 0 and
                node.text[0] == '#' and
                node.text[-1] == '#'
            ):
                yield node.text

    def get_tables(self):
        """
        Получаем таблицы в DOCX
        """

        return self._root.findall(
            self.TABLES_QUERY.format('w'), namespaces={'w': self.NS_W}
        )

    def set_docx_table_sections(self):
        """
         установка секций таблиц в документах DOCX
        :result: None
        """
        tables = self.get_tables()
        for table in tables:
            text_nodes = table.findall(
                '{0}:tr'.format('w'),
                namespaces={'w': self.NS_W}
            )
            section = Section(table)
            section_name = None
            rows_to_delete = []
            for row_node in text_nodes:
                col_nodes = row_node.findall(
                    self.TABLE_TEXT_NODE_QUERY.format('w'),
                    namespaces={'w': self.NS_W}
                )
                if not col_nodes:
                    continue
                col_nodes_text = u''.join(x.text for x in col_nodes)
                if col_nodes_text and col_nodes_text[:2] == '#!':
                    section_name = col_nodes_text[2:]
                    if section_name in self.table_sections:
                        raise SectionException(
                            ('Section named {0} has been found '
                             'more than 1 time in docx table').format(
                                section_name
                            )
                        )
                    rows_to_delete.append(row_node)
                elif col_nodes_text and col_nodes_text[-2:] == '!#':
                    self.table_sections[section_name] = section
                    section_name = None
                    section = Section(table)
                    rows_to_delete.append(row_node)
                elif section_name:
                    section.append(copy.copy(row_node))
                    rows_to_delete.append(row_node)
            for row_node in rows_to_delete:
                row_node.getparent().remove(row_node)

    def get_section(self, section_name):
        """
         Получение секции таблицы в документе DOCX по имени
        :param section_name: имя секции
        :result: секция
        """
        if not self.table_sections:
            self.set_docx_table_sections()
        section = self.table_sections.get(section_name)
        section.doc_rels = self.doc_rels
        if section is None:
            raise SectionNotFoundException(
                'Section named {0} has not been found'.format(section_name)
            )
        return section


class DocumentRelsXMLFile(OpenXMLFile):
    NS = ""
    FILENAME = "document.xml.rels"

    def __init__(self, tags, *args, **kwargs):
        super(DocumentRelsXMLFile, self).__init__(*args, **kwargs)
        file_path = os.path.join(
            self.current_folder,
            'word',
            '_rels',
            self.file_name
        )
        self._root = None
        self.max_rid = 0
        max_rid = 0
        if os.path.exists(file_path):
            self._root = self.from_file(file_path)
            for child in self._root:
                attrib = dict(child.attrib)
                rid = attrib.get('Id', '')
                if rid.startswith('rId'):
                    max_rid = max([max_rid, int(rid[3:])])
        self.max_rid = max_rid

    def next_rid(self):
        self.max_rid = self.max_rid + 1
        return "rId%s" % self.max_rid

    @classmethod
    def create(cls, folder, tags):
        """
         Получение экземпляра класса
        :param cls: класс
        :param folder: путь до директории с распакованным XML-документом
        :param tags: теги
        :result: Экземпляр класса
        """

        reletion_path = os.path.join(folder, 'word', '_rels', cls.FILENAME)
        rel_id = None # Корневой файл связей
        file_name = cls.FILENAME
        return cls(tags, rel_id, folder, file_name, reletion_path, )

    def build(self):
        with open(self.file_path, 'wb') as file_:
            file_.write(
                tostring(self._root, encoding='utf-8', xml_declaration=True)
            )



class ContentTypesXMLFile(OpenXMLFile):
    """
    Типы объектов
    """

    NS = 'http://schemas.openxmlformats.org/package/2006/content-types'

    FILENAME = '[Content_Types].xml'

    def __init__(self, tags, *args, **kwargs):
        super(ContentTypesXMLFile, self).__init__(*args, **kwargs)

        assert not self.file_name is None

        file_path = os.path.join(
            self.current_folder,
            self.file_name
        )
        self.types_root = None
        if os.path.exists(file_path):
            self.types_root = self.from_file(file_path)

    def build(self):
        # root = self.types_root.getroot()
        root = self.types_root
        # <Default Extension="jpg" ContentType="image/jpeg" />
        found_jpg = False
        found_png = False
        for child in root:
            if child.tag == '{%s}Default' % self.NS:
                attrib = dict(child.attrib)
                if attrib.get('ContentType') == 'image/jpeg' and attrib.get(
                    'Extension'
                ) == 'jpg':
                    found_jpg = True
                if attrib.get('ContentType') == 'image/png' and attrib.get(
                    'Extension'
                ) == 'png':
                    found_png = True

        if not found_jpg:
            SubElement(
                root, 'Default', attrib={
                    'ContentType': 'image/jpeg',
                    'Extension': 'jpg'
                },
            )
        if not found_png:
            SubElement(
                root, 'Default', attrib={
                    'ContentType': 'image/png',
                    'Extension': 'png'
                },
            )

        with open(self.file_path, 'wb') as f:
            f.write(
                tostring(root, encoding='utf-8', xml_declaration=True)
            )


    @classmethod
    def create(cls, folder, tags):
        """
         Получение экземпляра класса
        :param cls: класс
        :param folder: путь до директории с распакованным XML-документом
        :param tags: теги
        :result: Экземпляр класса
        """

        reletion_path = os.path.join(folder, cls.FILENAME)
        rel_id = None # Корневой файл связей
        file_name = '[Content_Types].xml'
        return cls(tags, rel_id, folder, file_name, reletion_path, )


class CommonPropertiesDOCX(CommonProperties):

    """

    """

    def _get_app_common(self, _id, target):
        """
        """
        return Wordprocessing.create(self.tags, _id, *self._get_path(target))


class Section(object):
    """
    Секция таблицы docx документа. Поддерживает ограниченное число операций
    В частности, строчки таблицы выводятся полностью, т.е. минимальной
    единицей секции является строка таблицы
    """

    def __init__(self, table):
        self._content = []
        self.table = table

    def append(self, table_row):
        self._content.append(table_row)

    def flush(self, params):
        for row in self._content:
            new_row = copy.copy(row)
            text_nodes = new_row.findall(
                './/{0}:tc/{0}:p/{0}:r/{0}:t'.format('w'),
                namespaces={'w': Wordprocessing.NS_W}
            )
            Wordprocessing._set_params(text_nodes, params, self.doc_rels)

            self.table.append(new_row)
