# coding: utf-8
import os
import unittest

from simple_report.converter.abstract import FileConverter
from simple_report.report import DocumentReport
from simple_report.rtf.document import DocumentRTF


__author__ = 'khalikov'


class TestRTF(unittest.TestCase):
    """
    Тесты отчетов в формате RTF
    """

    # Разные директории с разными файлами под linux и под windows
    #SUBDIR = ''

    def setUp(self):
        self.src_dir = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'test_data',
            'rtf'
        )
        self.dst_dir = self.src_dir

        self.test_files = dict([
            (path, os.path.join(self.src_dir, path)) for path in os.listdir(
                self.src_dir
            ) if path.startswith('test')
        ])

    #def test_libreoffice_replace(self):
    #    src_file = self.test_files['test_roll.rtf']
    #    dst_file = os.path.join(self.dst_dir, 'res_roll.rtf')
    #
    #    doc = DocumentReport(src_file, wrapper=DocumentRTF, type=FileConverter.RTF)
    #
    #    doc.build(
    #        dst_file,
    #        {'Employee_na32': u'Иванов И.И.',
    #         'region_name': u'Казань',
    #         'test': 'adsgh'},
    #        file_type=FileConverter.RTF
    #    )

    def test_word_replace(self):
        src_file = self.test_files['test-sluzh.rtf']
        dst_file = os.path.join(self.dst_dir, 'res-sluzh.rtf')

        doc = DocumentReport(src_file, wrapper=DocumentRTF, type=FileConverter.RTF)

        doc.build(
            dst_file,
            {'Employee_name': u'Иванов И.И.',
             #'region_name': u'Казань',
             'test': 'adsgh'},
            file_type=FileConverter.RTF
        )
