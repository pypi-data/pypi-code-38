""" Excel uploader module
"""
from xlrd import open_workbook

from core_module_excel_uploader_app.views.forms import ExcelUploaderForm
from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.builtin.popup_module import AbstractPopupModule
from core_parser_app.tools.modules.views.module import AbstractModule
from xml_utils.xsd_tree.xsd_tree import XSDTree


class ExcelUploaderModule(AbstractPopupModule):
    """ Excel Uploader Module
    """

    def __init__(self):
        """ Initialize module
        """
        self.table = None
        self.table_name = None

        AbstractPopupModule.__init__(self, button_label='Upload Excel File',
                                     scripts=['core_module_excel_uploader_app/js/excel_uploader.js'],
                                     styles=['core_module_excel_uploader_app/css/excel_uploader.css'])

    def _get_popup_content(self):
        """ Return popup content

        Returns:

        """
        return AbstractModule.render_template('core_module_excel_uploader_app/excel_uploader.html',
                                              {'form': ExcelUploaderForm()})

    def _retrieve_data(self, request):
        """ Return module's data

        Args:
            request:

        Returns:

        """
        data = ''
        if request.method == 'GET':
            if 'data' in request.GET:
                xml_table = XSDTree.fromstring("<table>" + request.GET['data'] + "</table>")

                self.table_name = 'name'
                self.table = {
                    'headers': [],
                    'values': []
                }

                headers = xml_table[0]
                for header in headers.iter('column'):
                    self.table['headers'].append(header.text)

                values = xml_table[1]

                for row in values.iter('row'):
                    value_list = []

                    for data in row.iter('column'):
                        value_list.append(data.text)

                    self.table['values'].append(value_list)
                data = ExcelUploaderModule.extract_xml_from_table(self.table_name, self.table)
        elif request.method == 'POST':
            form = ExcelUploaderForm(request.POST, request.FILES)
            if not form.is_valid():
                raise ModuleError('Data not properly sent to server. Please set "file" in POST data.')

            try:
                input_excel = request.FILES['file']
                book = open_workbook(file_contents=input_excel.read())
                sheet = book.sheet_by_index(0)

                self.table = {
                    'headers': [],
                    'values': []
                }

                for row_index in range(sheet.nrows):
                    row_values = []

                    for col_index in range(sheet.ncols):
                        cell_text = str(sheet.cell(row_index, col_index).value)

                        if row_index == 0:
                            self.table['headers'].append(cell_text)
                        else:
                            row_values.append(cell_text)

                    if len(row_values) != 0:
                        self.table['values'].append(row_values)

                self.table_name = str(input_excel)
            except:
                pass

            data = ExcelUploaderModule.extract_xml_from_table(self.table_name, self.table)

        return data

    def _render_data(self, request):
        """ Return module's data rendering

        Args:
            request:

        Returns:

        """
        if self.data is None:
            return 'No file selected'

        return ExcelUploaderModule.extract_html_from_table(self.table_name, self.table)

    @staticmethod
    def is_table_valid(table_name, table):
        """ Check if table is valid

        Args:
            table_name:
            table:

        Returns:

        """

        if table_name is None:
            return False

        if type(table) != dict:
            return False

        table_keys_set = set(table.keys())

        if len(table_keys_set.intersection(('headers', 'values'))) != 2:
            return False

        return True

    @staticmethod
    def extract_xml_from_table(table_name, table):
        """ Transform table into XML string

        Args:
            table_name:
            table:

        Returns:

        """
        if not ExcelUploaderModule.is_table_valid(table_name, table):
            return ""

        root = XSDTree.create_element("table")
        root.set("name", table_name)
        header = XSDTree.create_sub_element(root, "headers")
        values = XSDTree.create_sub_element(root, "rows")

        col_index = 0
        for header_name in table['headers']:
            header_cell = XSDTree.create_sub_element(header, 'column')

            header_cell.set('id', str(col_index))
            header_cell.text = header_name

            col_index += 1

        row_index = 0
        for value_list in table['values']:
            value_row = XSDTree.create_sub_element(values, 'row')
            value_row.set('id', str(row_index))
            col_index = 0

            for value in value_list:
                value_cell = XSDTree.create_sub_element(value_row, 'column')

                value_cell.set('id', str(col_index))
                value_cell.text = value

                col_index += 1

            row_index += 1

        xml_string = XSDTree.tostring(header)
        xml_string += XSDTree.tostring(values)

        return xml_string

    @staticmethod
    def extract_html_from_table(table_name, table):
        """ Transform table into HTML string

        Args:
            table_name:
            table:

        Returns:

        """
        if not ExcelUploaderModule.is_table_valid(table_name, table):
            return "Table has not been uploaded or is not of correct format."

        table_element = XSDTree.create_element("table")
        table_element.set('class', 'table table-striped excel-file')
        header = XSDTree.create_sub_element(table_element, "thead")
        header_row = XSDTree.create_sub_element(header, "tr")

        for header_name in table['headers']:
            header_cell = XSDTree.create_sub_element(header_row, 'th')
            header_cell.text = header_name

        values = XSDTree.create_sub_element(table_element, "tbody")

        for value_list in table['values']:
            value_row = XSDTree.create_sub_element(values, 'tr')

            for value in value_list:
                value_cell = XSDTree.create_sub_element(value_row, 'td')
                value_cell.text = value

        div = XSDTree.create_element("div")
        div.set('class', 'excel_table')
        div.append(table_element)

        return XSDTree.tostring(div)
