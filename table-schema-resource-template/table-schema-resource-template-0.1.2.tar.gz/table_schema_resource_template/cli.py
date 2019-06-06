#!/usr/bin/env python3

"""
Generate a resource file template from a Table Schema JSON file.
"""

import argparse
import locale
import sys
from pathlib import Path

import tableschema
from tableschema import Schema

XLSX_FORMAT = "xlsx"
FORMATS = [XLSX_FORMAT]


def generate_xlsx(schema: Schema, output_file: Path):
    import xlsxwriter
    with xlsxwriter.Workbook(str(output_file)) as workbook:
        worksheet = workbook.add_worksheet()
        for index, field in enumerate(schema.fields):
            worksheet.write(0, index, field.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('table_schema_json', help='path or URL of Table Schema JSON file')
    parser.add_argument('output', type=Path, help='path of output file')
    parser.add_argument('-f', '--format', default=XLSX_FORMAT, help='format of output file')
    args = parser.parse_args()

    if args.format not in FORMATS:
        parser.error("Format \"{}\" not supported. Supported formats: {}".format(
            args.format, ", ".join(map(lambda s: '"{}"'.format(s), FORMATS))))

    try:
        schema = Schema(args.table_schema_json)
    except tableschema.exceptions.LoadError:
        parser.error("Can't load schema from \"{}\"".format(args.table_schema_json))

    if args.format == XLSX_FORMAT:
        generate_xlsx(schema=schema, output_file=args.output)


if __name__ == '__main__':
    sys.exit(main())
