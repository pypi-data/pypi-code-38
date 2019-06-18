# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def create_rest_table(data, headers):
    """
    Create a ReST table from data. The data should be a list of columns and the
    headers should be a list of column names.

    :param list data: List of lists/tuples representing the columns
    :param list headers: List of strings for the column names
    :returns: a string representing the table in ReST
    :rtype: str
    """
    # Data should be a list of columns
    if len(data) != len(headers):
        raise ValueError('Number of columns should match the number of header values')

    # Get size of strings per column
    sizes = [max(len(x) for x in col) for col in data]
    sizes = [max(s, len(h)) for s, h in zip(sizes, headers)]

    table_line = ' '.join('=' * s for s in sizes)
    format_base = ' '.join('{{line[{}]:<{}}}'.format(n, s) for n, s in enumerate(sizes))

    table = [
        table_line,
        format_base.format(line=headers),
        table_line
    ]

    # Iterate transposed data
    table.extend(format_base.format(line=line) for line in zip(*data))
    table.append(table_line)

    return '\n'.join(table)
