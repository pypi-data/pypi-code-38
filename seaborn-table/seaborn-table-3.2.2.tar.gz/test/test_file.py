import unittest

from seaborn_table.table import main as cli_converter
from test.support import BaseTest


class FileConversionTest(BaseTest):
    def file_conversion(self, source, dest):
        source_file = self.test_data_path('test_file.%s' % source)
        expected_file = self.test_data_path('test_file.%s' % dest)
        result_file = self.test_data_path('_%s'%source, 'test_file.%s' % dest)
        cli_converter(source_file, result_file)
        self.assert_result_file(expected_file, result_file,
                                "Failure converting %s into %s"%(source, dest))
        self.remove_file(result_file)

    def test_txt_to_md(self):
        self.file_conversion('txt', 'md')

    def test_txt_to_csv(self):
        self.file_conversion('txt', 'csv')

    def test_txt_to_txt(self):
        self.file_conversion('txt', 'txt')

    def test_txt_to_html(self):
        self.file_conversion('txt', 'html')

    def test_txt_to_grid(self):
        self.file_conversion('txt', 'grid')

    def test_txt_to_json(self):
        self.file_conversion('txt', 'json')

    def test_txt_to_rst(self):
        self.file_conversion('txt', 'rst')

    def test_txt_to_psql(self):
        self.file_conversion('txt', 'psql')

    def test_csv_to_md(self):
        self.file_conversion('csv', 'md')

    def test_csv_to_csv(self):
        self.file_conversion('csv', 'csv')

    def test_csv_to_txt(self):
        self.file_conversion('csv', 'txt')

    def test_csv_to_html(self):
        self.file_conversion('csv', 'html')

    def test_csv_to_grid(self):
        self.file_conversion('csv', 'grid')

    def test_csv_to_json(self):
        self.file_conversion('csv', 'json')

    def test_csv_to_rst(self):
        self.file_conversion('csv', 'rst')

    def test_csv_to_psql(self):
        self.file_conversion('csv', 'psql')

    def test_md_to_md(self):
        self.file_conversion('md', 'md')

    def test_md_to_csv(self):
        self.file_conversion('md', 'csv')

    def test_md_to_txt(self):
        self.file_conversion('md', 'txt')

    def test_md_to_html(self):
        self.file_conversion('md', 'html')

    def test_md_to_grid(self):
        self.file_conversion('md', 'grid')

    def test_md_to_json(self):
        self.file_conversion('md', 'json')

    def test_md_to_rst(self):
        self.file_conversion('md', 'rst')

    def test_md_to_psql(self):
        self.file_conversion('md', 'psql')

    def test_grid_to_md(self):
        self.file_conversion('grid', 'md')

    def test_grid_to_grid(self):
        self.file_conversion('grid', 'grid')

    def test_grid_to_csv(self):
        self.file_conversion('grid', 'csv')

    def test_grid_to_html(self):
        self.file_conversion('grid', 'html')

    def test_grid_to_txt(self):
        self.file_conversion('grid', 'txt')

    def test_grid_to_json(self):
        self.file_conversion('grid', 'json')

    def test_grid_to_rst(self):
        self.file_conversion('grid', 'rst')

    def test_grid_to_psql(self):
        self.file_conversion('grid', 'psql')

    def test_json_to_md(self):
        self.file_conversion('json', 'md')

    def test_json_to_json(self):
        self.file_conversion('json', 'json')

    def test_json_to_csv(self):
        self.file_conversion('json', 'csv')

    def test_json_to_html(self):
        self.file_conversion('json', 'html')

    def test_json_to_txt(self):
        self.file_conversion('json', 'txt')

    def test_json_to_grid(self):
        self.file_conversion('json', 'grid')

    def test_json_to_rst(self):
        self.file_conversion('json', 'rst')

    def test_json_to_psql(self):
        self.file_conversion('json', 'psql')

    def test_rst_to_md(self):
        self.file_conversion('rst', 'md')

    def test_rst_to_json(self):
        self.file_conversion('rst', 'json')

    def test_rst_to_csv(self):
        self.file_conversion('rst', 'csv')

    def test_rst_to_html(self):
        self.file_conversion('rst', 'html')

    def test_rst_to_txt(self):
        self.file_conversion('rst', 'txt')

    def test_rst_to_grid(self):
        self.file_conversion('rst', 'grid')

    def test_rst_to_rst(self):
        self.file_conversion('rst', 'rst')

    def test_rst_to_psql(self):
        self.file_conversion('rst', 'psql')

    def test_psql_to_md(self):
        self.file_conversion('psql', 'md')

    def test_psql_to_json(self):
        self.file_conversion('psql', 'json')

    def test_psql_to_csv(self):
        self.file_conversion('psql', 'csv')

    def test_psql_to_html(self):
        self.file_conversion('psql', 'html')

    def test_psql_to_txt(self):
        self.file_conversion('psql', 'txt')

    def test_psql_to_grid(self):
        self.file_conversion('psql', 'grid')

    def test_psql_to_rst(self):
        self.file_conversion('psql', 'rst')

    def test_psql_to_psql(self):
        self.file_conversion('psql', 'psql')


if __name__ == '__main__':
    unittest.main()
