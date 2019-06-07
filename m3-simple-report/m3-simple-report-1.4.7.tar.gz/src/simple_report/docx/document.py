# coding: utf-8
from __future__ import absolute_import

from simple_report.core.document_wrap import DocumentOpenXML
from simple_report.docx.wordprocessing_ml import CommonPropertiesDOCX
from simple_report.docx.wordprocessing_ml import ContentTypesXMLFile
from simple_report.docx.wordprocessing_ml import DocumentRelsXMLFile


class DocumentDOCX(DocumentOpenXML):
    """
    Отчет в формате docx
    """

    def __init__(self, *args, **kwargs):
        super(DocumentDOCX, self).__init__(*args, **kwargs)
        self.common_properties = CommonPropertiesDOCX.create(
            self.extract_folder, self._tags
        )
        self.content_types = ContentTypesXMLFile.create(
            self.extract_folder, self._tags
        )
        self.main_rels = DocumentRelsXMLFile.create(
            self.extract_folder, self._tags
        )
        self.word.doc_rels = self.main_rels

    @property
    def word(self):
        return self.common_properties.main

    def build(self, dst_file):
        """
        Сборка отчета

        :param: dst_file: путь до выходного файла
        :type: dst_file: str
        """
        self.word.build()
        self.content_types.build()
        self.main_rels.build()
        super(DocumentDOCX, self).build(dst_file)

    def set_params(self, *args, **kwargs):
        """
        Установка параметров отчета
        """
        self.word.set_params(*args, **kwargs)

    def get_all_parameters(self):
        """
        Получение всех параметров
        """
        return self.word.get_all_parameters()

    def get_section(self, section_name):
        """
        Получение секции из таблицы в docx

        :param: section_name: название секции
        :type: section_name: str
        """
        return self.word.get_section(section_name)
