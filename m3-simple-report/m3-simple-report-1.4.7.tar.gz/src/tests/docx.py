# coding: utf-8
import os
import unittest

from simple_report.docx.drawing import DocxImage
from simple_report.report import DocumentReport
from simple_report.xlsx.spreadsheet_ml import SectionException
from simple_report.xlsx.spreadsheet_ml import SectionNotFoundException


LOREM_IPSUM = (
    'Lorem ipsum dolor sit amet, consectetur adipisicing elit, '
    'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
    'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris '
    'nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in '
    'reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla '
    'pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa '
    'qui officia deserunt mollit anim id est laborum.'
)


class TestLinuxDOCX(unittest.TestCase):
    """

    """

    def setUp(self):
        self.src_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_data',
            'linux',
            'docx'
        )
        self.dst_dir = self.src_dir

        self.test_files = dict([(path, os.path.join(self.src_dir, path))
                                for path in os.listdir(self.src_dir)
                                if path.startswith('test')])

    def test_simple_docx(self):
        """
        """

        template_name = 'test-sluzh.docx'
        path = self.test_files[template_name]
        doc = DocumentReport(path)

        res_file_name = 'res-' + template_name
        dst = os.path.join(self.dst_dir, res_file_name)

        doc.build(dst, {'Employee_name': u'Иванова И.И.',
                        'region_name': u'Казань'})
        self.assertEqual(os.path.exists(dst), True)

    def test_spreadsheet_docx(self):
        """
        Текст внутри таблицы
        """

        template_name = 'test_spreadsheet.docx'
        path = self.test_files[template_name]
        doc = DocumentReport(path)

        res_file_name = 'res-' + template_name
        dst = os.path.join(self.dst_dir, res_file_name)

        tag1 = doc.get_all_parameters().next()
        self.assertEqual(tag1, '#sometext#')

        doc.build(dst, {'sometext': u'Некий текст'})
        self.assertEqual(os.path.exists(dst), True)

    def test_picture_docx(self):
        """
        Текст внутри прямоугольника
        """

        template_name = 'test_rect.docx'
        path = self.test_files[template_name]
        doc = DocumentReport(path)

        res_file_name = 'res-' + template_name
        dst = os.path.join(self.dst_dir, res_file_name)

        tags = []
        for tag in doc.get_all_parameters():
            tags.append(tag)

        self.assertFalse(tags[0] != '#brandgroupname#'
                         and tags[0] != '#category#')
        self.assertFalse(tags[1] != '#brandgroupname#'
                         and tags[1] != '#category#')

        doc.build(dst, {'brandgroupname': u'Брэнд', 'category': u'Категория'})
        self.assertEqual(os.path.exists(dst), True)

    def test_picture_shape(self):

        template_name = 'test_pict_shape_2.docx'
        path = self.test_files[template_name]

        res_file_name = 'res-pict_shape.docx'
        dst = os.path.join(self.dst_dir, res_file_name)

        report = DocumentReport(path)
        params = {}

        params['fname'] = '1'
        params['sname'] = '2'
        params['pname'] = '3'
        params['issued_by'] = '4'
        params['date_of_birth'] = '5'

        params['date_start_day'] = '6'
        params['date_start_month'] = '7'
        params['date_start_year'] = '8'
        params['date_start'] = '9'
        params['date_end_day'] = '10'
        params['date_end_month'] = '11'
        params['date_end_year'] = '12'
        params['date_end'] = '13'
        params['region_number'] = '14'
        params['date_start_plus'] = '15'
        params['date_start_plus_day'] = '16'
        params['date_start_plus_month'] = '17'
        params['date_start_plus'] = '18'
        params['date_start_plus_year'] = '19'
        params['habaddr'] = '20'
        params['regaddr1'] = '21'
        params['regaddr2'] = '22'
        params['regaddr3'] = '23'
        params['inspect1'] = '24'
        params['inspect2'] = '25'
        params['is_AI'] = u"AI"
        params['is_AII'] = u"AII"
        params['is_AIII'] = u"AIII"
        params['is_AIV'] = u"AIV"
        params['is_B'] = u"B"
        params['is_C'] = u"C"
        params['is_D'] = u"D"
        params['is_E'] = u"E"
        params['is_F'] = u"F"
        params['#komment#'] = 'd'

        report.build(dst, params)

        self.assertEqual(os.path.exists(dst), True)

    def test_tables_flush(self):
        template_name = 'test_table.docx'
        path = self.test_files[template_name]

        res_file_name = 'res-table_flush.docx'
        dst = os.path.join(self.dst_dir, res_file_name)

        report = DocumentReport(path)
        # report.set_docx_table_sections()
        s1 = report.get_section('section1')
        s2 = report.get_section('section2')
        s2.flush({'test': u'Lorem ipsum'})
        s1.flush({
            'test_table_row1col1': u'Hello',
            'test_table_row1col2': u'simple_report',
            'test_table_row1col3': u'user',
            'test_table_row1col4': LOREM_IPSUM,
        })
        params = {}
        report.build(dst, params)

    def test_table_section_double(self):
        template_name = 'test_table_double_section.docx'
        path = self.test_files[template_name]

        report = DocumentReport(path)
        try:
            report.get_section('section1')
        except SectionException:
            pass
        else:
            raise Exception('Docx tables sections doubling test failed')

    def test_divisible_keys(self):
        template_name = 'test_divisibles.docx'
        path = self.test_files[template_name]
        report = DocumentReport(path)
        res_file_name = 'res-divisibles.docx'
        dst = os.path.join(self.dst_dir, res_file_name)
        params = {
            "tasks": "",
            "kind_tostring": u"документарная и выездная",
            "normative_list": "",
            "finish_date": "13.12.2012",
            "expert_list": "",
            "docs": "",
            "num": "1",
            "purpose": "",
            "address": u"420101, Респ Татарстан (Татарстан), г Казань, ул Карбышева, д. 37, кв. 44",
            "events": "",
            "subject3": "x",
            "articles": "",
            "inspectors_list": "",
            "supervisionobj_name": u"Малыши и малышки",
            "oyear": 2013,
            "type_tostring": u"внеплановая",
            "start_date": "14.02.2013",
            "subject1": "x",
            "subject2": "x",
            "oday": 21,
            "subject4": "x",
            "subject5": "x",
            "subject6": "x",
            "subject7": "x",
            "authority_parent": "",
            "omonth": 3
        }
        report.build(dst, params)

    def test_flush_order(self):
        template_name = 'test_flush_order.docx'
        path = self.test_files[template_name]
        report = DocumentReport(path)
        res_file_name = 'res-flush_order.docx'
        dst = os.path.join(self.dst_dir, res_file_name)
        params = {
            "example": "output_one",
            "example_two": "ouput_two",
            "example_two_three": "output_two_three",
            "exampl": "no_output"
        }
        report.build(dst, params)

    def test_tabs(self):
        template_name = 'test_tabs.docx'
        path = self.test_files[template_name]
        report = DocumentReport(path)
        res_file_name = 'res-tabs.docx'
        dst = os.path.join(self.dst_dir, res_file_name)
        params = {
            "tfoms_to": "TFOMS",
            "tfoms_to_address": "TFOMS_ADDRESS",
            "tfoms_to_director_fio": "TFOMS_TO_DIR_FIO"
        }
        report.build(dst, params)

    def test_insert_picture(self):
        template_name = 'test_insert_image.docx'
        path = self.test_files[template_name]
        report = DocumentReport(path)
        res_file_name = 'res-insert-image.docx'
        dst = os.path.join(self.dst_dir, res_file_name)
        params = {
            "test": u"Тестовый комментарий",
            "image": DocxImage(
                self.test_files['test_insert_image.jpg'],
                3,
                2
            ),
            "tfoms_to_director_fio": "TFOMS_TO_DIR_FIO"
        }
        report.build(dst, params)

    def test_table_insert_picture(self):
        template_name = 'test_table.docx'
        path = self.test_files[template_name]

        res_file_name = 'res-table-image.docx'
        dst = os.path.join(self.dst_dir, res_file_name)

        report = DocumentReport(path)
        # report.set_docx_table_sections()
        s1 = report.get_section('section1')
        s2 = report.get_section('section2')
        s2.flush(
            {
                'test': DocxImage(
                    self.test_files['test_insert_image.jpg'], 3, 2
                )
            }
        )
        s1.flush({
            'test_table_row1col1': u'Hello',
            'test_table_row1col2': u'simple_report',
            'test_table_row1col3': DocxImage(
                self.test_files['test_table_image.gif'], 3.5, 2.5
            ),
            'test_table_row1col4': LOREM_IPSUM,
        })
        params = {}
        report.build(dst, params)

if __name__ == '__main__':
    unittest.main()
