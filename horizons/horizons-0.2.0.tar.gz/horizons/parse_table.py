import re


def parse_table(table_lines):
    """Parse lines into a table.

    Table example:

    ```txt
      ID#      Name                               Designation  IAU/aliases/other
      -------  ---------------------------------- -----------  -------------------
            0  Solar System Barycenter                         SSB
            1  Mercury Barycenter
    ```

    :param table_lines: A list of strings that make up a table

    :return: A list of dictionaries where the keys are the header names and the values are the stripped contents for
        each table row.
    """
    dash_line = table_lines[1]
    matches = list(re.finditer(r"(-+\s)", dash_line))

    name_line = table_lines[0]
    names = []
    for m in matches:
        name = name_line[m.start():m.end() - 1].strip()
        names.append(name)

    table = []
    for line in table_lines[2:]:
        item = {}
        for i, m in enumerate(matches):
            content = line[m.start():m.end() - 1].strip()
            item[names[i]] = content
        table.append(item)

    return table
