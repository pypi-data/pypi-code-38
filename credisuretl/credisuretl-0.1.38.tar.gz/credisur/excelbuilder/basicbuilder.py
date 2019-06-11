def null_item_mapper(item, key):
    return item[key]


class BasicBuilder:

    def __init__(self, data_list, columns_configuration=None):
        self.data_list = data_list
        self.headers = []
        self.column_mappings = {}
        self.header_row = 1
        self.first_data_row = 2

        self.manual_values = {}

        if columns_configuration:
            self.configure_columns(columns_configuration)

    def set_header_row(self, header_row):
        self.header_row = header_row

    def set_first_data_row(self, data_row):
        self.first_data_row = data_row

    def add_header(self, column_letter, title):
        self.headers.append({"column_letter": column_letter, "title": title})

    def map_column(self, column_letter, item_key, mapper=null_item_mapper):
        self.column_mappings[column_letter] = {'key': item_key, 'mapper': mapper}

    def configure_column(self, column_letter, title, item_key):
        self.add_header(column_letter, title)
        self.map_column(column_letter, item_key)

    def configure_columns(self, list_of_columns):
        for column_configuration in list_of_columns:
            self.configure_column(*column_configuration)

    def set_manual_cell(self, cell_position, cell_value):
        self.manual_values[cell_position] = cell_value

    def build_sheet_data(self):
        sheet_data = {}

        sheet_data.update(self.__build_headers())
        sheet_data.update(self.__build_data_rows())
        sheet_data.update(self.manual_values)

        return sheet_data

    def __build_headers(self):
        headers_map = {}

        for header in self.headers:
            cell = self.__get_cell_location(header['column_letter'], self.header_row)
            headers_map[cell] = header['title']

        return headers_map

    def __build_data_rows(self):
        rows_map = {}

        for index, item in enumerate(self.data_list):
            row_num = str(index + self.first_data_row)

            for column_letter, item_key_and_mapper in self.column_mappings.items():
                cell = self.__get_cell_location(column_letter, row_num)

                item_mapper = item_key_and_mapper['mapper']
                item_key = item_key_and_mapper['key']

                rows_map[cell] = item_mapper(item, item_key)

        return rows_map

    def __get_cell_location(self, header, row):
        return ("%s%s" % (header, row))
