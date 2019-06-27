# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.supporting_classes.enums import Choose
import random
from ibm_ai_openscale.utils import *
import math


class Table:
    def __init__(self, header, records, list_columns=None, date_field_name='created'):
        validate_type(header, "header", list, True)
        validate_type(records, "records", list, True)
        validate_type(list_columns, "list_columns", list, False)
        validate_type(date_field_name, "date_field_name", str, True)

        self.header = header
        self.list_columns = list_columns
        self.records = records
        self.date_field_name = date_field_name

    def get_record(self, choose=None, **kwargs):
        validate_type(choose, "choose", str, False)

        records = self.records

        for key in kwargs.keys():
            records = list(filter(lambda r: r[self.header.index(key)] == kwargs[key], records))

        if len(records) == 0:
            raise ClientError('No element found')
        elif len(records) == 1:
            return records[0]
        else:
            if choose is None:
                raise ClientError('More than one element')
            elif choose == Choose.RANDOM:
                return records[random.randrange(len(records))]
            elif choose == Choose.FIRST:
                return min(records, key=lambda x: x[self.header.index(self.date_field_name)])
            elif choose == Choose.LAST:
                return max(records, key=lambda x: x[self.header.index(self.date_field_name)])
            else:
                raise ClientError('Unexpected \'choose\' value: {}'.format(choose))

    def list(self, column_list=None, limit=None, default_limit=None, sort_by='created', sort_reverse=True,
             filter_setup={}, title=None):
        validate_type(column_list, "column_list", list, False)
        validate_type(limit, "limit", int, False)
        validate_type(default_limit, "default_limit", int, False)
        validate_type(sort_by, "sort_by", str, False)
        validate_type(sort_reverse, "sort_reverse", bool, True)
        validate_type(filter_setup, "filter_setup", dict, True)
        validate_type(title, "title", str, False)

        values = self.records
        header = self.header

        # filter
        for filter_by in filter_setup.keys():
            if filter_by in header:
                column_no = header.index(filter_by)
                values = list(filter(lambda x: x[column_no] == filter_setup[filter_by], values))

        if len(filter_setup) > 0:
            filter_info = "(" + ", ".join(["{}={}".format(filter_name, filter_value.__repr__()) for filter_name, filter_value in filter_setup.items()]) + ")"
            title = title + " " + filter_info

        # sort
        if sort_by is not None and sort_by in header:
            column_no = header.index(sort_by)
            values = sorted(values, key=lambda x: x[column_no], reverse=sort_reverse)

        # apply column list
        if self.list_columns is not None and column_list is None:
            column_list = self.list_columns

        if column_list is not None:
            col_indexes = [self.header.index(col_name) for col_name in column_list]
            header = [header[index] for index in col_indexes]
            values = [[record[index] for index in col_indexes] for record in values]

        # limit
        if limit is None:
            limited_values = values[:default_limit]
        else:
            limited_values = values[:limit]

        if is_ipython():
            self._print_html_table(header, limited_values, title)
        else:
            self._print_text_table(header, limited_values, title)

        if limit is None and default_limit is not None and len(values) > default_limit:
            print('Note: Only first {} records were displayed. To display more use \'limit\' parameter.'.format(
                default_limit))
        elif limit is not None and len(values) > limit:
            print('Note: First {} records were displayed.'.format(limit))

    @staticmethod
    def _get_real_len(column_content):
        return max([len(l) for l in column_content.split('/')])

    @staticmethod
    def _cut_column_content(column_content, length, postfix=''):
        return '\n'.join([l[:length] + postfix if len(l) > length + len(postfix) else l for l in column_content.split('\n')])

    @staticmethod
    def _print_text_table(header, values, title):
        import copy
        original_values = values
        values = copy.deepcopy(values)
        header = copy.deepcopy(header)
        values = [[str(v) for v in row] for row in values]

        from tabulate import tabulate

        import os
        try:
            rows, columns = os.popen('stty size', 'r').read().split()
        except:
            columns = 200

        # shorten too long records
        maximum_content_width = int(columns) - 4 - 3*(len(header) -1)

        columns_width = [0]*len(header)
        final_column_width = [3]*len(header)

        for row in values:
            for index, v in enumerate(row):
                if columns_width[index] < Table._get_real_len(v):
                    columns_width[index] = Table._get_real_len(v)

        for index, h in enumerate(header):
            if columns_width[index] < len(h) + 2:
                columns_width[index] = len(h) + 2

        actual_content_width = sum(columns_width)

        if actual_content_width > maximum_content_width:
            for i in range(len(header)):
                if 'uid' in header[i]:
                    final_column_width[i] = columns_width[i]

            while sum(final_column_width) < maximum_content_width:
                column_to_add = -1
                column_length = 1000
                for i in range(len(header)):
                    if final_column_width[i] < columns_width[i]:
                        if final_column_width[i] < column_length:
                            column_to_add = i
                            column_length = final_column_width[i]

                final_column_width[column_to_add] += 1

            values = [
                [
                    Table._cut_column_content(values[i][j], final_column_width[j] - 3, '...')
                    if (Table._get_real_len(values[i][j]) > final_column_width[j])
                    else original_values[i][j]
                    for j in range(len(values[i]))
                    ] for i in range(len(values))]

            header = [
                    header[j][:final_column_width[j] - 3] + '...'
                    if (len(header[j]) > final_column_width[j])
                    else header[j]
                    for j in range(len(header))
                    ]

        table = tabulate(values, header, tablefmt="fancy_grid")

        if title is not None:
            styled_title = "--- " + title + " ---"
            table_lines = table.splitlines()
            table_length = len(table_lines[0])
            right_spaces_no = math.floor((table_length - len(styled_title)) / 2)
            left_spaces_no = math.ceil((table_length - len(styled_title)) / 2)
            print("\n" + " " * left_spaces_no + styled_title + " " * right_spaces_no)

        print(table)

    @staticmethod
    def _print_html_table(header, values, title):
        from IPython.display import HTML, display

        html = """<HTML>
        <body>
            <h3>{}</h3>
            <table style='border: 1px solid #dddddd; font-family: Courier'>
                {}
                {}
            </table>
        </body>
        </HTML>"""

        tr = "<tr>{}</tr>"
        td = "<td style=\'border: 1px solid #dddddd\'>{}</td>"
        table_header = ''.join(['<th style=\'border: 1px solid #dddddd\'>{}</th>'.format(h) for h in header])

        subitems = [tr.format(''.join([td.format(a) for a in item])) for item in values]
        html_content = html.format(title, table_header, "".join(subitems))
        display(HTML(html_content))