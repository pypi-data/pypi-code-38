# coding: utf-8
import os

from simple_report.report import SpreadsheetReport


class TestPagebreaks(object):
    dst_dir = test_files = None

    def test_pagebreaks(self):
        test_file = self.test_files['test-pagebreaks.xlsx']

        test_res = os.path.join(self.dst_dir, 'res-pagebreaks.xlsx')
        if os.path.exists(test_res):
            os.remove(test_res)

        self.assertEqual(os.path.exists(test_res), False)

        result = self.create_pagebreaks_report(test_file, test_res)

        self.check_pagebreaks_results(result)

        self.assertEqual(os.path.exists(test_res), True)


    def create_pagebreaks_report(self, temp_path, res_path):
        section_params = {}
        report = SpreadsheetReport(temp_path)

        # проверим начальное количество разделителей
        rb = report.workbook.get_rowbreaks()
        self.assertEqual(len(rb), 0)

        cb = report.workbook.get_colbreaks()
        self.assertEqual(len(cb), 0)

        section = report.get_section(u'line')
        for i in range(20):
            section.flush(section_params)

        bottom_section = report.get_section(u'bottom')
        for i in range(2):
            bottom_section.flush(section_params)

        report.build(res_path)

        return report

    def check_pagebreaks_results(self, report):

        # проверим конечное количество разделителей
        rb = report.workbook.get_rowbreaks()
        self.assertEqual(len(rb), 4)

        cb = report.workbook.get_colbreaks()
        self.assertEqual(len(cb), 2)

        return report
