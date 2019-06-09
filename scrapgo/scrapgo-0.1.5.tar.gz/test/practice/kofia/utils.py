from collections import OrderedDict


def parse_record(soup, tag, column_mapping, many=True):
    records = [
        OrderedDict(
            (column_mapping.get(r.name, r.name), r.text)
            for r in r.children
            if r.name in column_mapping
        )
        for r in soup(tag)
    ]
    if many is True:
        return records
    if records:
        return records[0]
    return {}
