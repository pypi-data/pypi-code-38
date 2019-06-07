import csv
from io import StringIO


def csv_processor(input, options=None):
    options = options or {}

    delimiter = options.get('delimiter', ';')
    reader = csv.reader(StringIO(input.decode('utf-8')), delimiter=delimiter)

    result = []

    headers = []
    header = options.get('header', False)

    for parts in reader:
        if header and not headers:
            headers = list(map(lambda x: x, parts))
            continue

        if header:
            row = {}
            for i, part in enumerate(parts):
                row[headers[i]] = part

            result.append(row)
        else:
            result.append(list(map(lambda x: x, parts)))

    return result
