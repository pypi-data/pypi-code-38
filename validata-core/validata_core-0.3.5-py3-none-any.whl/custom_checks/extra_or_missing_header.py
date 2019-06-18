from goodtables.error import Error
from goodtables.registry import check

"""Reimplementation of NonMatchingHeader check, taking into account missing header, extra header and wrong header order."""


@check('extra-or-missing-header', type='custom', context='head')
class ExtraOrMissingHeader(object):
    def __init__(self, **options):
        pass

    def check_headers(self, cells, sample=None):
        errors = []

        field_names = [
            cell['field'].name
            for cell in cells
            if 'field' in cell
        ]
        field_names_set = set(field_names)
        headers = [
            cell['value']
            for cell in cells
            if 'value' in cell
        ]
        headers_set = set(headers)

        for cell in cells:
            if 'value' not in cell:  # cell has been infered, and must not be passed to later checks
                cells.remove(cell)

        missing_headers = field_names_set - headers_set
        if missing_headers:
            errors.append(Error(code='missing-headers',
                                message_substitutions={"headers": sorted(missing_headers)}))

        extra_headers = headers_set - field_names_set
        if extra_headers:
            errors.append(Error(code='extra-headers',
                                message_substitutions={"headers": sorted(extra_headers)}))

        if field_names_set == headers_set and field_names != headers:
            errors.append(Error(code='wrong-headers-order'))

        return errors
