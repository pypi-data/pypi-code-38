import sys
import unittest

from seaborn_table.table import SeabornTable, UNICODE, BASESTRING
from test.support import BaseTest, FormatMixin


class QuoteNumbersTest(BaseTest, FormatMixin):
    def validate_test_condition(self, source):
        table = self.get_base_table()
        table.map(lambda x: UNICODE(x))
        result_file = self.test_data_path('_quote_numbers',
                                          'test_quote.%s' % source)
        table.obj_to_file(result_file, quote_numbers=False)
        expected_file = self.test_data_path('expected',
                                            'test_quote.%s' % source)
        self.assert_result_file(expected_file, result_file)
        self.remove_file(result_file)


class EvalCellsFalseTest(BaseTest, FormatMixin):
    def validate_test_condition(self, source):
        file_path = self.test_data_path('test_file.%s' % source)
        table = SeabornTable.file_to_obj(eval_cells=False, file_path=file_path)
        assert isinstance(table[0]['TU'], BASESTRING)

    def test_html(self):
        unittest.skip("uncomment after implementing html_to_obj")


class InsertPopRemoveColumnTest(BaseTest, FormatMixin):
    def validate_test_condition(self, source):
        table = self.get_base_table()
        table.insert(0, 'remove_column')
        table.insert(None, 'pop_empty_columns')
        table.remove_column('remove_column')
        table.pop_empty_columns()
        result_file = self.test_data_path('_column_results',
                                          'test_file.%s' % source)
        table.obj_to_file(result_file)
        expected_file = self.test_data_path('test_file.%s' % source)
        self.assert_result_file(expected_file, result_file)
        self.remove_file(result_file)


class MultipleSavesTests(BaseTest, FormatMixin):
    def validate_test_condition(self, source):
        table = self.get_base_table()
        answers = table.obj_to_type(source).split('\n')
        results = table.obj_to_type(source).split('\n')
        for answer, result in zip(answers, results):
            self.assertEqual(answer, result)


class HeaderOnlyTest(BaseTest, FormatMixin):
    def validate_test_condition(self, source):
        expected = SeabornTable(columns=[
            'TEST COL 1', 'TEST COL TWO', 'LAST COL'])
        text = expected.obj_to_type(source)
        result = SeabornTable.type_to_obj(source, text=text)
        expected_file = self.test_data_path('expected', 'header_only.%s'%source)
        result_file = self.test_data_path('_header_only',
                                          'header_only.%s' % source)
        expected.obj_to_file(expected_file)
        result.obj_to_file(result_file)
        self.assert_result_file(expected_file, result_file)
        self.remove_file(result_file)
        self.assertEqual(expected, result)

    def test_html(self):
        unittest.skip("uncomment after implementing html_to_obj")


class SharedColumnTest(BaseTest, FormatMixin):
    SHARED_LIMIT = 0
    BASENAME = 'test_share_columns_0.%s'

    def validate_test_condition(self, source):
        tables = [SeabornTable.file_to_obj(
            file_path=self.test_data_path('test_share_columns_%s.rst' % i))
            for i in range(4)]
        for table in tables:
            table.share_column_widths(tables, self.SHARED_LIMIT)
        basename = self.BASENAME%source
        expected_file = self.test_data_path('expected', basename)
        result_file = self.test_data_path('_shared', basename)
        with open(result_file, 'w') as fn:
            for table in tables:
                text = table.obj_to_type(source) + u'\n\n'
                if sys.version_info[0] == 2:
                    text = text.encode('utf-8')
                fn.write(text)
        self.assert_result_file(expected_file, result_file)
        self.remove_file(result_file)

    def test_html(self):
        unittest.skip("Not Applicable")

    def test_json(self):
        unittest.skip("Not Applicable")


class SharedColumnLimitTest(SharedColumnTest):
    SHARED_LIMIT = 10
    BASENAME = 'test_share_columns_10.%s'


class SharedColumnLimitTest(SharedColumnTest):
    SHARED_LIMIT = None
    BASENAME = 'test_share_columns_0.%s'


if __name__ == '__main__':
    unittest.main()
