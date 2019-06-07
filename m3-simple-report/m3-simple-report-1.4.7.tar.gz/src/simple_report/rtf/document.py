# coding: utf-8
from __future__ import absolute_import

from simple_report.core.document_wrap import BaseDocument
from simple_report.rtf.api import convert_dict
from simple_report.rtf.api import do_replace
from simple_report.rtf.parser import normalize_rtf


class DocumentRTF(BaseDocument):
    """
    Обертка для документов в формате RTF
    """

    def __init__(self, src_file, tags):
        self.rtf_string = normalize_rtf(src_file.file)
        #self.rtf_string = self.rtf_string.replace('\\langfe2052', '\\langfe1049')
        self.params = {}

    def build(self, dst_file):
        """
        Построение отчета - заполнение данными
        """
        with open(dst_file.file, 'wb') as report:
            new_text = do_replace(self.rtf_string, self.converted_dictionary)
            report.write(new_text)

    def set_params(self, params):
        """
        Подстановка параметров
        :param params: словарь с параметрами отчета
        :result: None
        """
        assert isinstance(params, dict), 'wrong params type'
        self.converted_dictionary = convert_dict(params)
